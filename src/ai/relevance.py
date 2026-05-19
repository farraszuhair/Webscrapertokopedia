"""
Qwen-based relevance filtering.

Flow:
  deduped products -> optional budget filter -> batched compact JSON prompt
  -> Ollama /api/generate -> ranked candidates.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Iterator, List, Tuple

from src.ai.learning import get_recent_examples, get_recent_feedback
from src.ai.qwen_client import ask_qwen, call_ollama_generate, check_ollama_health, select_ollama_model
from src.utils.logger import log


RELEVANCE_THRESHOLD = float(os.getenv("AI_RELEVANCE_THRESHOLD", "0.55"))
FALLBACK_SCORE = 0.5
AI_BATCH_SIZE = max(1, int(os.getenv("AI_BATCH_SIZE", "25")))


@dataclass
class AiFilterResult:
    products: list[dict[str, Any]]
    qwen_status: str
    meta: dict[str, Any] = field(default_factory=dict)

    def __iter__(self) -> Iterator[Any]:
        # Backward compatible with: products, status = await filter_relevance(...)
        yield self.products
        yield self.qwen_status


def _query_terms(query: str) -> set[str]:
    return set(re.findall(r"\w+", query.lower()))


def _fallback_score(query: str, product: dict[str, Any]) -> dict[str, Any]:
    """
    Offline fallback when Qwen cannot run.

    This is intentionally conservative for accessory-looking titles. It keeps
    obvious main products and drops obvious accessories unless the query asks
    for that accessory.
    """
    title = str(product.get("title") or "").lower()
    title_words = set(re.findall(r"\w+", title))
    query_words = _query_terms(query)

    laptop_signals = {
        "laptop", "notebook", "rog", "legion", "nitro", "predator",
        "msi", "omen", "victus", "alienware", "tuf", "katana",
        "rtx", "gtx", "geforce", "radeon", "ryzen", "intel",
    }
    accessory_signals = {
        "mouse", "mice", "mousepad", "keyboard", "charger", "adaptor",
        "adapter", "cooling", "cooler", "stand", "headset", "earphone",
        "webcam", "sleeve", "tas", "bag", "ram", "ssd", "sticker",
        "stickers", "sparepart", "spare", "parts", "baterai", "battery",
    }
    accessory_query_terms = accessory_signals | {"aksesoris", "accessory", "accessories"}

    accessory_hits = accessory_signals & title_words
    laptop_hits = laptop_signals & title_words
    query_overlap = query_words & title_words
    query_asks_accessory = bool(query_words & accessory_query_terms)

    if accessory_hits and not query_asks_accessory:
        return {
            "relevant": False,
            "confidence": 0.15,
            "categories": ["accessory"],
            "reason": f"Fallback: accessory signals detected ({', '.join(sorted(accessory_hits))})",
            "source": "fallback",
        }

    if laptop_hits or query_overlap:
        confidence = min(0.9, 0.52 + len(laptop_hits) * 0.08 + len(query_overlap) * 0.05)
        return {
            "relevant": True,
            "confidence": confidence,
            "categories": ["gaming_laptop" if "gaming" in query_words else "main_product"],
            "reason": f"Fallback: matched signals {sorted(laptop_hits | query_overlap)}",
            "source": "fallback",
        }

    return {
        "relevant": True,
        "confidence": FALLBACK_SCORE,
        "categories": ["unknown"],
        "reason": "Fallback: no strong negative signal, kept by default",
        "source": "fallback",
    }


def _compact_product(index: int, product: dict[str, Any]) -> str:
    item = {
        "index": index,
        "title": str(product.get("title") or "")[:180],
        "price": product.get("price_raw") or product.get("price_text") or "",
        "rating": product.get("rating") or product.get("rating_text") or "",
        "sold_count": product.get("sold_count") or product.get("sold") or "",
        "shop": product.get("shop_name") or product.get("shop") or "",
        "has_image": bool(product.get("image_url") or product.get("image")),
        "has_url": bool(product.get("product_url") or product.get("url")),
    }
    return json.dumps(item, ensure_ascii=True, separators=(",", ":"))


def build_ai_batches(products: list[dict[str, Any]], batch_size: int = AI_BATCH_SIZE, max_prompt_chars: int = 12000):
    batches: list[list[tuple[int, dict[str, Any], str]]] = []
    current_batch: list[tuple[int, dict[str, Any], str]] = []
    current_chars = 0

    for index, product in enumerate(products):
        compact = _compact_product(index, product)
        if current_batch and (
            len(current_batch) >= batch_size
            or current_chars + len(compact) > max_prompt_chars
        ):
            batches.append(current_batch)
            current_batch = []
            current_chars = 0

        current_batch.append((index, product, compact))
        current_chars += len(compact)

    if current_batch:
        batches.append(current_batch)
    return batches


def _build_batch_prompt(query: str, batch_compacts, examples: list, feedback: list) -> str:
    few_shot = ""
    if examples:
        few_shot = "\nConfirmed feedback examples:\n"
        for ex in examples[-3:]:
            few_shot += (
                f'- "{ex.get("title", "")}" -> {ex.get("label", "unknown")}'
                f' | reason={ex.get("reason", "")}\n'
            )

    feedback_ctx = ""
    if feedback:
        feedback_ctx = "\nRecent user corrections:\n"
        for fb in feedback[-2:]:
            feedback_ctx += (
                f'- "{fb.get("product_title", "")}" was corrected to '
                f'{fb.get("corrected_label", fb.get("correction", ""))}'
                f' | reason={fb.get("custom_reason", fb.get("note", ""))}\n'
            )

    products_json = "[\n" + ",\n".join(compact for _, _, compact in batch_compacts) + "\n]"

    return f"""You are an e-commerce product relevance validator for Tokopedia.

User query: "{query}"

Evaluate only the compact product JSON below. Do not use raw HTML.
{few_shot}{feedback_ctx}
Relevance rules:
- Use semantic matching, not exact keyword matching only.
- For query "laptop gaming", accept ASUS ROG, Lenovo Legion, Acer Nitro, MSI Katana, HP Victus, ASUS TUF Gaming, and laptops with RTX, GTX, Radeon, Ryzen, or gaming specs.
- Reject mouse, keyboard, charger, laptop stand, cooling pad, RAM-only, SSD-only, stickers, spare parts, and unrelated accessories unless the query explicitly asks for that accessory.
- If the query asks for a main product, do not accept accessories as substitutes.

Products:
{products_json}

Return JSON only using exactly this schema:
{{
  "valid_indexes": [0, 1, 2],
  "rejected": [
    {{
      "index": 3,
      "reason": "not relevant"
    }}
  ],
  "notes": "optional short note"
}}"""


def _int_set(values: Any) -> set[int]:
    indexes: set[int] = set()
    if not isinstance(values, list):
        return indexes
    for value in values:
        try:
            indexes.add(int(value))
        except (TypeError, ValueError):
            continue
    return indexes


def _rejected_reason_map(values: Any) -> dict[int, str]:
    reasons: dict[int, str] = {}
    if not isinstance(values, list):
        return reasons
    for item in values:
        if not isinstance(item, dict):
            continue
        try:
            index = int(item.get("index"))
        except (TypeError, ValueError):
            continue
        reasons[index] = str(item.get("reason") or "rejected")
    return reasons


def _mark_product(product: dict[str, Any], decision: dict[str, Any]) -> None:
    product["relevance_score"] = float(decision.get("confidence", FALLBACK_SCORE))
    product["ai_decision"] = bool(decision.get("relevant", True))
    product["ai_reason"] = str(decision.get("reason", ""))
    product["ai_explanation"] = product["ai_reason"]
    product["ai_categories"] = decision.get("categories", [])
    product["ai_source"] = decision.get("source", "unknown")
    product["ai_label"] = "relevan" if product["ai_decision"] else "tidak_relevan"
    product["ai_confidence"] = product["relevance_score"]


def _apply_fallback_all(query: str, products: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    valid: list[dict[str, Any]] = []
    for product in products:
        decision = _fallback_score(query, product)
        decision["source"] = source
        _mark_product(product, decision)
        if decision["relevant"] and decision["confidence"] >= RELEVANCE_THRESHOLD:
            valid.append(product)
    return valid


def _keep_prefiltered_batch(
    batch: list[tuple[int, dict[str, Any], str]],
    reason: str,
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for _, product, _ in batch:
        _mark_product(product, {
            "relevant": True,
            "confidence": FALLBACK_SCORE,
            "categories": ["fallback"],
            "reason": reason,
            "source": "fallback_invalid_response",
        })
        kept.append(product)
    return kept


async def ai_filter_products(
    query: str,
    products: list[dict[str, Any]],
    use_ai: bool = True,
    search_id: str | None = None,
) -> AiFilterResult:
    if not products:
        warning = "AI skipped: products empty before AI"
        log("AI", warning, "WARN")
        return AiFilterResult([], "ok", {"warning": warning, "skipped_reason": "products_empty_before_ai"})

    if not use_ai:
        warning = "AI skipped: AI disabled by config"
        log("AI", warning, "WARN")
        result = _apply_fallback_all(query, products, "fallback_ai_disabled")
        return AiFilterResult(result, "disabled", {
            "warning": warning,
            "skipped_reason": "ai_disabled_by_config",
            "fallback_used": True,
            "accepted_count": len(result),
        })

    selection = await select_ollama_model()
    meta: dict[str, Any] = {
        "selected_model": selection.selected_model,
        "available_models": selection.available_models,
        "ollama_base_url": selection.base_url,
        "ollama_generate_url": selection.generate_url,
        "fallback_used": False,
        "warning": selection.warning,
        "skipped_reason": selection.reason,
    }
    if not selection.ok or not selection.selected_model:
        result = _apply_fallback_all(query, products, f"fallback_{selection.reason or 'ollama_unavailable'}")
        meta.update({"fallback_used": True, "accepted_count": len(result)})
        _save_qwen_filter_debug(search_id, query, products, result, "unavailable", 0, 0, [], meta)
        return AiFilterResult(result, "unavailable", meta)

    examples = get_recent_examples(query)
    feedback_items = get_recent_feedback(query)
    batches = build_ai_batches(products, batch_size=AI_BATCH_SIZE, max_prompt_chars=12000)
    log("AI", f"Qwen filter: products={len(products)} batches={len(batches)} batch_size={AI_BATCH_SIZE}", "INFO")

    from src.server.progress import update_progress

    valid: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    batches_ok = 0
    batches_failed = 0
    qwen_accepted = 0
    invalid_response_used = False

    for batch_idx, batch in enumerate(batches):
        batch_current = batch_idx + 1
        batch_total = len(batches)
        log("AI", f"batch={batch_current}/{batch_total}", "INFO")

        if search_id:
            percent = 70 + int(18 * ((batch_current - 1) / max(1, batch_total)))
            update_progress(
                search_id,
                stage="ai_filtering",
                percent=percent,
                message=f"AI filtering batch {batch_current}/{batch_total}",
                found=len(products),
            )

        prompt = _build_batch_prompt(query, batch, examples, feedback_items)
        generate = await call_ollama_generate(prompt, selection.selected_model, search_id)

        if not generate.ok or not isinstance(generate.data, dict):
            batches_failed += 1
            invalid_response_used = invalid_response_used or generate.error.startswith("invalid_json")
            reason = (
                "AI fallback used because response was invalid"
                if generate.error.startswith("invalid_json")
                else f"AI fallback used because generate failed: {generate.error}"
            )
            log("AI", reason, "WARN")
            fallback_products = _keep_prefiltered_batch(batch, reason)
            valid.extend(fallback_products)
            for idx, product, _ in batch:
                decisions.append({
                    "index": idx,
                    "title": product.get("title", "")[:80],
                    "decision": product.get("ai_label"),
                    "source": product.get("ai_source"),
                    "kept": True,
                    "reason": product.get("ai_reason"),
                })
            continue

        data = generate.data
        valid_indexes = _int_set(data.get("valid_indexes"))
        if "valid_indexes" not in data or not isinstance(data.get("valid_indexes"), list):
            batches_failed += 1
            invalid_response_used = True
            reason = "AI fallback used because response was invalid"
            log("AI", f"{reason}: missing valid_indexes", "WARN")
            fallback_products = _keep_prefiltered_batch(batch, reason)
            valid.extend(fallback_products)
            continue

        rejected_map = _rejected_reason_map(data.get("rejected"))
        notes = str(data.get("notes") or "")
        batches_ok += 1

        for idx, product, _ in batch:
            is_valid = idx in valid_indexes
            decision = {
                "relevant": is_valid,
                "confidence": 0.9 if is_valid else 0.1,
                "categories": ["relevant"] if is_valid else ["not_relevant"],
                "reason": notes or ("Qwen marked relevant" if is_valid else rejected_map.get(idx, "Qwen rejected")),
                "source": "qwen",
            }
            _mark_product(product, decision)
            kept = is_valid and product["relevance_score"] >= RELEVANCE_THRESHOLD
            if kept:
                valid.append(product)
                qwen_accepted += 1
            decisions.append({
                "index": idx,
                "title": product.get("title", "")[:80],
                "decision": decision,
                "kept": kept,
            })

        if search_id:
            progress = 70 + int(18 * (batch_current / max(1, batch_total)))
            update_progress(
                search_id,
                stage="ai_filtering",
                percent=progress,
                message=f"AI filtering batch {batch_current}/{batch_total} done",
                valid=len(valid),
            )

    if batches_ok and not batches_failed:
        qwen_status = "ok"
    elif batches_ok and batches_failed:
        qwen_status = "partial"
    else:
        qwen_status = "failed"

    warning = ""
    if invalid_response_used:
        warning = "AI fallback used because response was invalid"
    elif batches_failed:
        warning = "AI fallback used because generate failed"

    meta.update({
        "batch_count": len(batches),
        "batches_ok": batches_ok,
        "batches_failed": batches_failed,
        "qwen_accepted_count": qwen_accepted,
        "accepted_count": len(valid),
        "fallback_used": batches_failed > 0,
        "warning": warning or selection.warning,
    })

    _save_qwen_filter_debug(search_id, query, products, valid, qwen_status, batches_ok, batches_failed, decisions, meta)
    log("AI", f"accepted={len(valid)} qwen_accepted={qwen_accepted} status={qwen_status}", "OK")
    return AiFilterResult(valid, qwen_status, meta)


async def filter_relevance(
    query: str,
    products: List[dict[str, Any]],
    use_ai: bool = True,
    search_id: str | None = None,
) -> AiFilterResult:
    """Backward-compatible public entrypoint."""
    return await ai_filter_products(query, list(products or []), use_ai, search_id)


def _save_qwen_filter_debug(
    search_id: str | None,
    query: str,
    products: list,
    valid: list,
    qwen_status: str,
    ok_count: int,
    fail_count: int,
    decisions: list | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    if not search_id:
        return
    try:
        from src.utils.debug import save_json_debug

        save_json_debug(search_id, "qwen_filter_debug.json", {
            "query": query,
            "total_input": len(products),
            "total_kept": len(valid),
            "threshold": RELEVANCE_THRESHOLD,
            "qwen_status": qwen_status,
            "qwen_ok_count": ok_count,
            "qwen_fail_count": fail_count,
            "decisions": decisions or [],
            "meta": meta or {},
        })
    except Exception:
        pass
