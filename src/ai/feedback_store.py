"""
SQLite-backed feedback memory for scoped learning.

The important invariant: a negative label is wrong for a query/context, not a
global blacklist. Learned patterns carry a scope and are checked against the
current query before affecting ranking.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.logger import log


FEEDBACK_DB_PATH = Path("data") / "marketspy_feedback.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS feedback_events (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,

    query TEXT NOT NULL,
    normalized_query TEXT NOT NULL,
    query_intent TEXT,
    query_constraints_json TEXT,

    product_title TEXT NOT NULL,
    product_url TEXT,
    product_price INTEGER,
    product_store TEXT,
    product_image TEXT,
    product_fingerprint TEXT NOT NULL,
    product_constraints_json TEXT,

    feedback_type TEXT NOT NULL,
    reasons_json TEXT,
    note TEXT,

    learning_scope_hint TEXT,

    decision_source TEXT,
    confidence REAL,
    rule_score REAL,
    semantic_score REAL,
    combined_score REAL,
    learned_adjustment REAL,

    model_used TEXT,
    ai_reason TEXT
);

CREATE TABLE IF NOT EXISTS learned_patterns (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    query_intent TEXT,
    query_key TEXT,
    constraint_key TEXT,

    pattern TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    scope TEXT NOT NULL,

    reason TEXT,
    weight REAL NOT NULL,
    support_count INTEGER NOT NULL,
    negative_count INTEGER NOT NULL,
    positive_count INTEGER NOT NULL,

    applies_when_json TEXT,
    excludes_when_json TEXT
);

CREATE TABLE IF NOT EXISTS product_embeddings_cache (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


FEEDBACK_REASONS_SPEC_MISMATCH = "Spesifikasi tidak sesuai query"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _json_loads(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value))
    except Exception:
        return default


def _db_path() -> Path:
    return Path(FEEDBACK_DB_PATH)


def ensure_feedback_db() -> Path:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    return path


def _connect() -> sqlite3.Connection:
    ensure_feedback_db()
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def normalize_text(value: str | None) -> str:
    value = (value or "").lower()
    value = value.replace("-", " ")
    value = value.replace("_", " ")
    value = value.replace("/", " ")
    value = value.replace("+", " ")
    value = " ".join(value.split())
    return value


def has_laptop_main_evidence(text: str | None) -> bool:
    t = normalize_text(text)

    laptop_words = [
        "laptop",
        "notebook",
    ]
    gaming_series = [
        "rog", "tuf", "loq", "legion", "victus", "omen",
        "nitro", "predator", "msi thin", "msi katana",
        "msi cyborg", "msi bravo", "msi modern",
    ]
    gpu_words = [
        "rtx", "gtx", "geforce", "nvidia",
        "rtx 2050", "rtx2050",
        "rtx 3050", "rtx3050",
        "rtx 4050", "rtx4050",
        "rtx 4060", "rtx4060",
    ]
    cpu_words = [
        "core i5", "core i7", "core i9",
        "intel i5", "intel i7", "intel i9",
        "ryzen 5", "ryzen 7", "ryzen 9",
    ]

    has_laptop = any(word in t for word in laptop_words)
    has_gpu = any(word in t for word in gpu_words)
    has_series = any(word in t for word in gaming_series)
    has_cpu = any(word in t for word in cpu_words)
    primary_accessory_terms = [
        "mouse gaming",
        "keyboard gaming",
        "headset gaming",
        "cooling pad",
        "cooler laptop",
        "stand laptop",
        "tas laptop",
        "sleeve laptop",
        "charger laptop",
        "adaptor laptop",
        "adapter laptop",
        "lcd laptop",
        "baterai laptop",
        "battery laptop",
        "sparepart laptop",
        "skin laptop",
        "sticker laptop",
        "casing laptop",
        "case laptop",
    ]

    has_strong_main_signal = has_gpu or has_series or has_cpu
    if any(t.startswith(term) for term in primary_accessory_terms) and not has_strong_main_signal:
        return False

    accessory_without_strong_signal = [
        "mouse",
        "mouse pad",
        "headset",
        "earphone",
        "webcam",
        "cooling pad",
        "cooler laptop",
        "stand laptop",
        "tas laptop",
        "sleeve laptop",
        "charger laptop",
        "adaptor laptop",
        "adapter laptop",
        "lcd laptop",
        "baterai laptop",
        "battery laptop",
        "sparepart laptop",
        "ram for laptop",
        "ram laptop",
        "sodimm",
        "ddr4",
        "ddr5",
        "ssd laptop",
        "skin laptop",
        "sticker laptop",
        "casing laptop",
        "case laptop",
    ]
    if any(term in t for term in accessory_without_strong_signal) and not has_strong_main_signal:
        return False
    if "keyboard" in t and not has_strong_main_signal:
        keyboard_is_laptop_spec = (
            t.startswith("laptop")
            or t.startswith("notebook")
            or "backlit keyboard" in t
            or "backlite keyboard" in t
        )
        if not keyboard_is_laptop_spec:
            return False

    return (
        has_series
        or has_gpu
        or (has_laptop and has_cpu)
        or (has_laptop and "gaming" in t)
    )


def has_accessory_only_evidence(text: str | None) -> bool:
    t = normalize_text(text)
    accessory_terms = [
        "mouse gaming",
        "keyboard gaming",
        "headset gaming",
        "cooling pad",
        "cooler laptop",
        "stand laptop",
        "tas laptop",
        "sleeve laptop",
        "charger laptop",
        "adaptor laptop",
        "adapter laptop",
        "lcd laptop",
        "baterai laptop",
        "battery laptop",
        "sparepart laptop",
        "skin laptop",
        "sticker laptop",
        "casing laptop",
        "case laptop",
    ]

    if not any(term in t for term in accessory_terms):
        return False
    if has_laptop_main_evidence(t):
        return False
    return True


def make_product_fingerprint(product: dict[str, Any]) -> str:
    title = normalize_text(product.get("title") or product.get("name") or "")
    store = normalize_text(product.get("store") or product.get("shop_name") or product.get("shop") or "")
    price = str(_as_int(product.get("price_value", product.get("price")), 0))
    url = normalize_text(product.get("url") or product.get("product_url") or "")
    base = f"{title}|{store}|{price}|{url}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:24]


def find_first_regex(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def normalize_gpu_model(value: str | None) -> str | None:
    if not value:
        return None
    v = normalize_text(value)
    v = v.replace("rtx ", "rtx")
    v = v.replace("gtx ", "gtx")
    if v.startswith("rtx"):
        number = v.replace("rtx", "").strip()
        return f"rtx {number}" if number else None
    if v.startswith("gtx"):
        number = v.replace("gtx", "").strip()
        return f"gtx {number}" if number else None
    return v or None


def extract_query_constraints(text: str | None) -> dict[str, Any]:
    t = normalize_text(text)
    constraints: dict[str, Any] = {
        "gpu_model": None,
        "cpu_model": None,
        "brand": None,
        "storage": None,
        "ram": None,
        "phone_model": None,
        "category": None,
    }

    gpu_patterns = [
        r"rtx\s?20\d0",
        r"rtx\s?30\d0",
        r"rtx\s?40\d0",
        r"rtx\s?50\d0",
        r"gtx\s?16\d0",
        r"gtx\s?10\d0",
    ]
    ram_patterns = [
        r"\b\d+\s?gb\s?ram\b",
        r"\bram\s?\d+\s?gb\b",
    ]
    storage_patterns = [
        r"\b\d+\s?gb\s?ssd\b",
        r"\b\d+\s?tb\s?ssd\b",
        r"\bssd\s?\d+\s?gb\b",
        r"\bssd\s?\d+\s?tb\b",
    ]
    phone_patterns = [
        r"iphone\s?\d+",
        r"samsung\s?s\d+",
        r"redmi\s?note\s?\d+",
    ]
    cpu_patterns = [
        r"\bcore\s?i[3579][\s]?\d{3,5}[a-z]*\b",
        r"\bi[3579][\s]?\d{3,5}[a-z]*\b",
        r"\bryzen\s?[3579][\s]?\d{3,5}[a-z]*\b",
        r"\bryzen\s?[3579]\b",
    ]
    brand_terms = [
        "asus", "lenovo", "acer", "hp", "msi", "dell", "apple",
        "samsung", "xiaomi", "redmi", "infinix", "oppo", "vivo",
    ]

    gpu = find_first_regex(t, gpu_patterns)
    if gpu:
        constraints["gpu_model"] = normalize_gpu_model(gpu)

    ram = find_first_regex(t, ram_patterns)
    if ram:
        constraints["ram"] = normalize_text(ram)

    storage = find_first_regex(t, storage_patterns)
    if storage:
        constraints["storage"] = normalize_text(storage)

    phone = find_first_regex(t, phone_patterns)
    if phone:
        constraints["phone_model"] = normalize_text(phone)

    cpu = find_first_regex(t, cpu_patterns)
    if cpu:
        constraints["cpu_model"] = normalize_text(cpu)

    for brand in brand_terms:
        if re.search(rf"\b{re.escape(brand)}\b", t):
            constraints["brand"] = brand
            break

    if has_laptop_main_evidence(t):
        constraints["category"] = "laptop"
    elif has_accessory_only_evidence(t):
        constraints["category"] = "accessory"
    elif "laptop" in t or "notebook" in t:
        constraints["category"] = "laptop"
    elif any(x in t for x in ["casing", "case", "softcase", "hardcase", "charger", "mouse", "keyboard"]):
        constraints["category"] = "accessory"

    return constraints


def extract_product_constraints(text: str | None) -> dict[str, Any]:
    return extract_query_constraints(text)


def extract_learning_terms(title: str) -> list[str]:
    t = normalize_text(title)
    words = t.split()
    useful_terms: list[str] = []
    for n in [1, 2, 3]:
        for i in range(len(words) - n + 1):
            gram = " ".join(words[i:i + n])
            if len(gram) >= 3:
                useful_terms.append(gram)

    keep_if_contains = [
        "rtx", "gtx", "geforce", "nvidia",
        "rog", "tuf", "loq", "legion", "victus", "nitro",
        "tas laptop", "mouse", "keyboard", "charger",
        "casing", "softcase", "hardcase",
        "iphone", "laptop", "gaming",
    ]
    return _dedupe_preserve_order(
        term for term in useful_terms if any(k in term for k in keep_if_contains)
    )


def compute_constraint_mismatch_penalty(
    query_constraints: dict[str, Any],
    product_constraints: dict[str, Any],
) -> tuple[float, list[str]]:
    penalty = 0.0
    reasons: list[str] = []

    q_gpu = query_constraints.get("gpu_model")
    p_gpu = product_constraints.get("gpu_model")
    if q_gpu and p_gpu and q_gpu != p_gpu:
        penalty -= 0.45
        reasons.append(f"GPU mismatch: query wants {q_gpu}, product has {p_gpu}")

    q_ram = query_constraints.get("ram")
    p_ram = product_constraints.get("ram")
    if q_ram and p_ram and q_ram != p_ram:
        penalty -= 0.25
        reasons.append(f"RAM mismatch: query wants {q_ram}, product has {p_ram}")

    q_storage = query_constraints.get("storage")
    p_storage = product_constraints.get("storage")
    if q_storage and p_storage and q_storage != p_storage:
        penalty -= 0.25
        reasons.append(f"Storage mismatch: query wants {q_storage}, product has {p_storage}")

    q_phone = query_constraints.get("phone_model")
    p_phone = product_constraints.get("phone_model")
    if q_phone and p_phone and q_phone != p_phone:
        penalty -= 0.40
        reasons.append(f"Phone model mismatch: query wants {q_phone}, product has {p_phone}")

    return penalty, reasons


def save_feedback_event(
    *,
    query: str,
    query_intent: str | None,
    product: dict[str, Any],
    feedback_type: str,
    reasons: list[str] | None = None,
    note: str | None = None,
    learning_scope_hint: str | None = None,
    decision_source: str | None = None,
    confidence: float | None = None,
    rule_score: float | None = None,
    semantic_score: float | None = None,
    combined_score: float | None = None,
    learned_adjustment: float | None = None,
    model_used: str | None = None,
    ai_reason: str | None = None,
) -> dict[str, Any]:
    reasons = reasons or []
    product = product or {}
    title = str(product.get("title") or product.get("name") or "").strip()
    product_url = str(product.get("url") or product.get("product_url") or "").strip()
    product_store = str(product.get("store") or product.get("shop_name") or product.get("shop") or "").strip()
    product_image = str(product.get("image") or product.get("image_url") or product.get("thumbnail") or "").strip()
    product_price = _as_int(product.get("price_value", product.get("price")), 0)
    normalized_query = normalize_text(query)
    query_constraints = extract_query_constraints(query)
    product_constraints = extract_query_constraints(title)
    fingerprint = make_product_fingerprint(
        {
            **product,
            "title": title,
            "store": product_store,
            "url": product_url,
            "price_value": product_price,
        }
    )
    scope_hint_input = str(learning_scope_hint or "").strip().lower()
    if scope_hint_input == "global" and not _is_truly_invalid_product(product):
        scope_hint_input = ""
    scope_hint = scope_hint_input or infer_learning_scope(
        feedback_type=feedback_type,
        reasons=reasons,
        query_constraints=query_constraints,
        product_constraints=product_constraints,
        product=product,
    )
    event_id = str(uuid.uuid4())
    created_at = now_iso()

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO feedback_events (
                id, created_at, query, normalized_query, query_intent, query_constraints_json,
                product_title, product_url, product_price, product_store, product_image,
                product_fingerprint, product_constraints_json, feedback_type, reasons_json,
                note, learning_scope_hint, decision_source, confidence, rule_score,
                semantic_score, combined_score, learned_adjustment, model_used, ai_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                created_at,
                query,
                normalized_query,
                query_intent,
                _json_dumps(query_constraints),
                title,
                product_url,
                product_price,
                product_store,
                product_image,
                fingerprint,
                _json_dumps(product_constraints),
                feedback_type,
                _json_dumps(reasons),
                note or "",
                scope_hint,
                decision_source or product.get("decision_source") or product.get("ai_source") or "",
                _safe_float(confidence if confidence is not None else product.get("confidence")),
                _safe_float(rule_score if rule_score is not None else product.get("rule_score")),
                _safe_float(semantic_score if semantic_score is not None else product.get("semantic_score")),
                _safe_float(combined_score if combined_score is not None else product.get("combined_score")),
                _safe_float(learned_adjustment if learned_adjustment is not None else product.get("learned_adjustment")),
                model_used or product.get("model_used") or product.get("_model") or "",
                ai_reason or product.get("ai_reason") or product.get("reason") or "",
            ),
        )
        conn.commit()

    learning_updated = update_learned_patterns_from_feedback(
        query=query,
        normalized_query=normalized_query,
        query_intent=query_intent,
        query_constraints=query_constraints,
        product=product,
        product_title=title,
        product_fingerprint=fingerprint,
        product_constraints=product_constraints,
        feedback_type=feedback_type,
        reasons=reasons,
        note=note or "",
        learning_scope_hint=scope_hint,
    )
    log(
        "AI_LEARN",
        (
            f"sqlite_feedback_saved type={feedback_type} scope={scope_hint} "
            f"query={normalized_query} fingerprint={fingerprint} learning_updated={learning_updated}"
        ),
        "OK",
    )
    return {"ok": True, "feedback_id": event_id, "learning_updated": learning_updated}


def infer_learning_scope(
    *,
    feedback_type: str,
    reasons: list[str],
    query_constraints: dict[str, Any],
    product_constraints: dict[str, Any],
    product: dict[str, Any],
) -> str:
    if feedback_type == "positive":
        return "exact_query"
    reason_set = set(reasons or [])
    if FEEDBACK_REASONS_SPEC_MISMATCH in reason_set:
        return "query_constraint"
    if "Cuma aksesoris" in reason_set or "Bukan sesuai intent pencarian" in reason_set or "Bukan produk utama" in reason_set:
        return "query_intent"
    if "Produk tidak relevan" in reason_set:
        return "exact_query"
    if "Harga tidak sesuai" in reason_set:
        return "query_constraint" if any(query_constraints.values()) else "exact_query"
    if "Duplikat" in reason_set or "Gambar tidak sesuai" in reason_set:
        return "exact_query"
    if "Data tidak lengkap" in reason_set and _is_truly_invalid_product(product):
        return "global"
    return "exact_query"


def update_learned_patterns_from_feedback(
    *,
    query: str,
    normalized_query: str,
    query_intent: str | None,
    query_constraints: dict[str, Any],
    product: dict[str, Any],
    product_title: str,
    product_fingerprint: str,
    product_constraints: dict[str, Any],
    feedback_type: str,
    reasons: list[str],
    note: str,
    learning_scope_hint: str | None,
) -> bool:
    feedback_type = normalize_text(feedback_type)
    reasons = reasons or []
    reason_text = ", ".join(reasons) or note or feedback_type
    updated = False

    q_gpu = query_constraints.get("gpu_model")
    p_gpu = product_constraints.get("gpu_model")
    if (
        feedback_type == "negative"
        and FEEDBACK_REASONS_SPEC_MISMATCH in reasons
        and q_gpu
        and p_gpu
        and q_gpu != p_gpu
    ):
        updated |= _upsert_pattern(
            query_intent=query_intent,
            query_key=normalized_query,
            constraint_key=f"gpu_model:{q_gpu}",
            pattern=p_gpu,
            pattern_type="penalty",
            scope="query_constraint",
            reason=FEEDBACK_REASONS_SPEC_MISMATCH,
            weight=-0.45,
            positive_delta=0,
            negative_delta=1,
            applies_when={"query_constraints": {"gpu_model": q_gpu}},
            excludes_when={"query_constraints": {"gpu_model": p_gpu}},
        )
        return updated

    terms = _feedback_terms(product_title, product_constraints, reasons)
    if not terms:
        terms = [product_fingerprint] if feedback_type == "negative" else []

    if feedback_type == "positive":
        for term in terms[:8]:
            updated |= _upsert_pattern(
                query_intent=query_intent,
                query_key=normalized_query,
                constraint_key="",
                pattern=term,
                pattern_type="boost",
                scope="exact_query",
                reason=reason_text or "positive",
                weight=0.20,
                positive_delta=1,
                negative_delta=0,
                applies_when={"query": normalized_query},
                excludes_when={},
            )
        for term in terms[:4]:
            updated |= _upsert_pattern(
                query_intent=query_intent,
                query_key=normalized_query,
                constraint_key="",
                pattern=term,
                pattern_type="accept_hint",
                scope="query_intent",
                reason=reason_text or "positive",
                weight=0.08,
                positive_delta=1,
                negative_delta=0,
                applies_when={"query_intent": query_intent},
                excludes_when={},
            )
        return updated

    if feedback_type == "negative":
        scope = learning_scope_hint or "exact_query"
        weight = -0.30
        pattern_type = "penalty"
        if "Cuma aksesoris" in reasons or "Bukan sesuai intent pencarian" in reasons or "Bukan produk utama" in reasons:
            scope = "query_intent"
            pattern_type = "reject_hint"
            weight = -0.35
        elif "Harga tidak sesuai" in reasons:
            scope = "query_constraint" if any(query_constraints.values()) else "exact_query"
            weight = -0.25
        elif "Data tidak lengkap" in reasons and _is_truly_invalid_product(product):
            scope = "global"
            pattern_type = "reject_hint"
            weight = -0.50
        if scope == "query_constraint" and not _primary_constraint_key(query_constraints):
            scope = "exact_query"

        constraint_key = _primary_constraint_key(query_constraints) if scope == "query_constraint" else ""
        applies_when = {"query_constraints": _non_empty_constraints(query_constraints)} if scope == "query_constraint" else {}
        excludes_when: dict[str, Any] = {}
        for term in terms[:8]:
            updated |= _upsert_pattern(
                query_intent=query_intent,
                query_key=normalized_query,
                constraint_key=constraint_key,
                pattern=term,
                pattern_type=pattern_type,
                scope=scope,
                reason=reason_text,
                weight=weight,
                positive_delta=0,
                negative_delta=1,
                applies_when=applies_when,
                excludes_when=excludes_when,
            )
    return updated


def _upsert_pattern(
    *,
    query_intent: str | None,
    query_key: str,
    constraint_key: str,
    pattern: str,
    pattern_type: str,
    scope: str,
    reason: str,
    weight: float,
    positive_delta: int,
    negative_delta: int,
    applies_when: dict[str, Any],
    excludes_when: dict[str, Any],
) -> bool:
    pattern = normalize_text(pattern)
    if not pattern:
        return False
    created_at = now_iso()
    pattern_id = hashlib.sha256(
        f"{query_intent or ''}|{query_key}|{constraint_key}|{pattern}|{pattern_type}|{scope}".encode("utf-8")
    ).hexdigest()[:32]
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO learned_patterns (
                id, created_at, updated_at, query_intent, query_key, constraint_key,
                pattern, pattern_type, scope, reason, weight, support_count,
                negative_count, positive_count, applies_when_json, excludes_when_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                updated_at=excluded.updated_at,
                reason=excluded.reason,
                weight=excluded.weight,
                support_count=learned_patterns.support_count + excluded.support_count,
                negative_count=learned_patterns.negative_count + excluded.negative_count,
                positive_count=learned_patterns.positive_count + excluded.positive_count,
                applies_when_json=excluded.applies_when_json,
                excludes_when_json=excluded.excludes_when_json
            """,
            (
                pattern_id,
                created_at,
                created_at,
                query_intent,
                query_key,
                constraint_key or "",
                pattern,
                pattern_type,
                scope,
                reason,
                weight,
                1,
                negative_delta,
                positive_delta,
                _json_dumps(applies_when),
                _json_dumps(excludes_when),
            ),
        )
        conn.commit()
    return True


def load_learned_patterns(
    query: str,
    query_intent: str | None,
    query_constraints: dict[str, Any] | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    query_constraints = query_constraints or extract_query_constraints(query)
    normalized_query = normalize_text(query)
    rows: list[dict[str, Any]] = []
    try:
        with _connect() as conn:
            result = conn.execute(
                """
                SELECT * FROM learned_patterns
                WHERE scope = 'global'
                   OR (scope = 'exact_query' AND query_key = ?)
                   OR (scope = 'query_intent' AND query_intent = ?)
                   OR scope = 'query_constraint'
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (normalized_query, query_intent, int(limit)),
            )
            rows = [_row_to_dict(row) for row in result.fetchall()]
    except Exception as exc:
        log("AI_LEARN", f"load_learned_patterns_failed error={exc}", "WARN")
        return []
    return [
        row for row in rows
        if pattern_applies(row, query, query_constraints, {"title": row.get("pattern")})
    ]


def pattern_applies(
    pattern: dict[str, Any],
    query: str,
    query_constraints: dict[str, Any],
    product: dict[str, Any] | None = None,
) -> bool:
    scope = pattern.get("scope", "exact_query")
    if scope == "global":
        return True
    if scope == "exact_query":
        return normalize_text(pattern.get("query_key")) == normalize_text(query)
    if scope == "query_constraint":
        applies_when = _json_loads(pattern.get("applies_when_json"), {})
        excludes_when = _json_loads(pattern.get("excludes_when_json"), {})
        required = applies_when.get("query_constraints", {}) if isinstance(applies_when, dict) else {}
        excluded = excludes_when.get("query_constraints", {}) if isinstance(excludes_when, dict) else {}
        for key, expected in required.items():
            if expected and query_constraints.get(key) != expected:
                return False
        for key, excluded_value in excluded.items():
            if excluded_value and query_constraints.get(key) == excluded_value:
                return False
        return True
    if scope == "query_intent":
        try:
            from src.ai.relevance import detect_query_intent

            return pattern.get("query_intent") == detect_query_intent(query)
        except Exception:
            return bool(pattern.get("query_intent"))
    return False


def compute_learned_adjustment(
    query: str,
    query_intent: str | None,
    query_constraints: dict[str, Any],
    product: dict[str, Any],
    learned_patterns: list[dict[str, Any]],
) -> tuple[float, list[dict[str, Any]]]:
    title = normalize_text(product.get("title") or product.get("name") or "")
    query_text = normalize_text(query)
    adjustment = 0.0
    matches: list[dict[str, Any]] = []
    for pattern in learned_patterns:
        p = normalize_text(pattern.get("pattern") or "")
        if not p or p not in title:
            continue
        if (
            pattern.get("scope") == "query_intent"
            and pattern.get("pattern_type") == "accept_hint"
            and p in query_text
        ):
            continue
        if not pattern_applies(pattern, query, query_constraints, product):
            continue
        weight = _safe_float(pattern.get("weight"), 0.0)
        support = _as_int(pattern.get("support_count"), 1)
        effective_weight = weight * 0.5 if support == 1 else weight
        adjustment += effective_weight
        matches.append(
            {
                "pattern": p,
                "scope": pattern.get("scope"),
                "weight": round(effective_weight, 3),
                "reason": pattern.get("reason"),
                "support_count": support,
                "pattern_type": pattern.get("pattern_type"),
            }
        )
    adjustment = max(-0.75, min(0.40, adjustment))
    product["learned_matches"] = matches
    return adjustment, matches


def load_feedback_context(
    query: str,
    query_intent: str | None,
    query_constraints: dict[str, Any] | None = None,
    limit: int = 12,
) -> dict[str, Any]:
    query_constraints = query_constraints or extract_query_constraints(query)
    normalized_query = normalize_text(query)
    positives: list[dict[str, Any]] = []
    negatives: list[dict[str, Any]] = []
    patterns = load_learned_patterns(query, query_intent, query_constraints, limit=limit)
    try:
        with _connect() as conn:
            rows = [
                _row_to_dict(row)
                for row in conn.execute(
                    """
                    SELECT * FROM feedback_events
                    WHERE normalized_query = ? OR query_intent = ?
                    ORDER BY created_at DESC
                    LIMIT 200
                    """,
                    (normalized_query, query_intent),
                ).fetchall()
            ]
    except Exception as exc:
        log("AI_LEARN", f"load_feedback_context_failed error={exc}", "WARN")
        rows = []

    for row in rows:
        row_constraints = _json_loads(row.get("query_constraints_json"), {})
        same_query = row.get("normalized_query") == normalized_query
        same_constraint = _same_primary_constraint(query_constraints, row_constraints)
        compact = _compact_feedback_event(row)
        if row.get("feedback_type") == "positive" and (same_query or row.get("query_intent") == query_intent):
            positives.append(compact)
        elif row.get("feedback_type") == "negative" and (same_query or same_constraint):
            negatives.append(compact)
        if len(positives) + len(negatives) >= limit:
            break

    return {
        "positive_examples": positives[: max(1, limit // 2)],
        "negative_examples": negatives[: max(1, limit // 2)],
        "learned_patterns": patterns[:limit],
        "feedback_examples_loaded": min(limit, len(positives) + len(negatives)),
        "learned_patterns_loaded": len(patterns),
    }


def reset_learning(scope: str = "all", query: str | None = None, constraint_key: str | None = None) -> dict[str, Any]:
    ensure_feedback_db()
    scope = normalize_text(scope or "all")
    deleted_events = 0
    deleted_patterns = 0
    cleared_files: list[str] = []
    with _connect() as conn:
        if scope == "all":
            cur = conn.execute("DELETE FROM feedback_events")
            deleted_events = max(0, cur.rowcount)
            cur = conn.execute("DELETE FROM learned_patterns")
            deleted_patterns = max(0, cur.rowcount)
        elif scope == "query":
            normalized_query = normalize_text(query or "")
            cur = conn.execute("DELETE FROM feedback_events WHERE normalized_query = ?", (normalized_query,))
            deleted_events = max(0, cur.rowcount)
            cur = conn.execute("DELETE FROM learned_patterns WHERE query_key = ?", (normalized_query,))
            deleted_patterns = max(0, cur.rowcount)
        elif scope == "constraint":
            cur = conn.execute("DELETE FROM learned_patterns WHERE constraint_key = ?", (constraint_key or "",))
            deleted_patterns = max(0, cur.rowcount)
        else:
            raise ValueError(f"Unsupported learning reset scope: {scope}")
        conn.commit()
    if scope == "all":
        cleared_files = _clear_legacy_learning_files()
    return {
        "ok": True,
        "scope": scope,
        "message": "Learning memory reset",
        "feedback_deleted": deleted_events,
        "patterns_deleted": deleted_patterns,
        "deleted_feedback_events": deleted_events,
        "deleted_learned_patterns": deleted_patterns,
        "cleared_files": cleared_files,
    }


def _clear_legacy_learning_files() -> list[str]:
    cleared: list[str] = []
    try:
        import src.ai.memory_store as memory_store
        from src.config import FEEDBACK_FILE as product_feedback_file

        memory_store.ensure_memory_dir()
        for path in (memory_store.FEEDBACK_FILE, memory_store.EXAMPLES_FILE):
            path.write_text("", encoding="utf-8")
            cleared.append(str(path))
        memory_store.CATEGORY_RULES_FILE.write_text(
            json.dumps({"version": 1, "rules": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        cleared.append(str(memory_store.CATEGORY_RULES_FILE))
        product_feedback_file.parent.mkdir(parents=True, exist_ok=True)
        product_feedback_file.write_text("[]", encoding="utf-8")
        cleared.append(str(product_feedback_file))
    except Exception as exc:
        log("AI_LEARN", f"legacy_learning_file_reset_failed error={exc}", "WARN")
    return cleared


def feedback_summary_counts() -> dict[str, int]:
    try:
        with _connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM feedback_events").fetchone()[0]
            positive = conn.execute("SELECT COUNT(*) FROM feedback_events WHERE feedback_type='positive'").fetchone()[0]
            negative = conn.execute("SELECT COUNT(*) FROM feedback_events WHERE feedback_type='negative'").fetchone()[0]
            patterns = conn.execute("SELECT COUNT(*) FROM learned_patterns").fetchone()[0]
    except Exception:
        return {"sqlite_total": 0, "sqlite_positive": 0, "sqlite_negative": 0, "learned_patterns": 0}
    return {
        "sqlite_total": int(total),
        "sqlite_positive": int(positive),
        "sqlite_negative": int(negative),
        "learned_patterns": int(patterns),
    }


def _feedback_terms(
    product_title: str,
    product_constraints: dict[str, Any],
    reasons: list[str],
) -> list[str]:
    title = normalize_text(product_title)
    preferred: list[str] = []
    for key in ["gpu_model", "phone_model", "ram", "storage", "brand"]:
        value = product_constraints.get(key)
        if value:
            preferred.append(str(value))
    accessory_terms = [
        "tas laptop", "mouse", "keyboard", "cooling pad", "charger",
        "adaptor", "adapter", "casing", "softcase", "hardcase",
        "sleeve", "lcd", "baterai", "battery", "skin sticker",
    ]
    if "Cuma aksesoris" in reasons or "Bukan sesuai intent pencarian" in reasons or "Bukan produk utama" in reasons:
        preferred.extend(term for term in accessory_terms if term in title)
    preferred.extend(extract_learning_terms(product_title))
    return _dedupe_preserve_order(preferred)


def _primary_constraint_key(constraints: dict[str, Any]) -> str:
    for key in ["gpu_model", "phone_model", "ram", "storage", "category"]:
        value = constraints.get(key)
        if value:
            return f"{key}:{value}"
    return ""


def _non_empty_constraints(constraints: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in (constraints or {}).items() if value}


def _same_primary_constraint(current: dict[str, Any], stored: dict[str, Any]) -> bool:
    for key in ["gpu_model", "phone_model", "ram", "storage"]:
        if current.get(key) and current.get(key) == stored.get(key):
            return True
    return False


def _compact_feedback_event(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "query": row.get("query"),
        "query_intent": row.get("query_intent"),
        "product_title": row.get("product_title"),
        "feedback_type": row.get("feedback_type"),
        "reasons": _json_loads(row.get("reasons_json"), []),
        "note": row.get("note"),
        "query_constraints": _json_loads(row.get("query_constraints_json"), {}),
        "product_constraints": _json_loads(row.get("product_constraints_json"), {}),
    }


def _dedupe_preserve_order(values: Any) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = normalize_text(str(value))
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(text)
    return output


def _is_truly_invalid_product(product: dict[str, Any]) -> bool:
    title = str(product.get("title") or product.get("name") or "").strip()
    url = str(product.get("url") or product.get("product_url") or product.get("id") or "").strip()
    price = _as_int(product.get("price_value", product.get("price")), 0)
    return len(title) < 3 or (not url and price <= 0)


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, str):
            digits = re.sub(r"[^\d]", "", value)
            if digits:
                return int(digits)
        return int(float(str(value).replace(",", ".") or default))
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default
