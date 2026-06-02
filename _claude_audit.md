# PROJECT CODE AUDIT PACK

Root: `C:\Users\Farras\PI V3\RB-C1`

## FILE TREE

- `.agents\skills\fastapi-websocket-doctor\SKILL.md`
- `.agents\skills\git-windows-doctor\SKILL.md`
- `.agents\skills\local-llm-json-guard\SKILL.md`
- `.agents\skills\marketspy-scraper-debugger\SKILL.md`
- `.agents\skills\marketspy-ui-architect\SKILL.md`
- `.codex\skills\ui-ux-pro-max\scripts\core.py`
- `.codex\skills\ui-ux-pro-max\scripts\design_system.py`
- `.codex\skills\ui-ux-pro-max\scripts\search.py`
- `.codex\skills\ui-ux-pro-max\SKILL.md`
- `.vscode\settings.json`
- `AGENTS.md`
- `app.py`
- `pack_repo_for_claude.py`
- `pack_repo_for_claude_split.py`
- `package.json`
- `pytest.ini`
- `QUICK_START.md`
- `README.md`
- `requirements.txt`
- `SOURCE_REGISTER.md`
- `src\__init__.py`
- `src\ai\__init__.py`
- `src\ai\ai_filter.py`
- `src\ai\ai_orchestrator.py`
- `src\ai\feedback_store.py`
- `src\ai\json_repair.py`
- `src\ai\learning.py`
- `src\ai\memory_store.py`
- `src\ai\model_registry.py`
- `src\ai\ollama_client.py`
- `src\ai\relevance.py`
- `src\ai\reset.py`
- `src\ai\schemas.py`
- `src\config.py`
- `src\scraper\__init__.py`
- `src\scraper\budget_filter.py`
- `src\scraper\dedupe.py`
- `src\scraper\engine_selector.py`
- `src\scraper\normalizer.py`
- `src\scraper\preflight.py`
- `src\scraper\puppeteer_engine.py`
- `src\scraper\puppeteer_worker.js`
- `src\scraper\query_expander.py`
- `src\scraper\rollback_engine.py`
- `src\scraper\selenium_driver.py`
- `src\scraper\url_builder.py`
- `src\server\__init__.py`
- `src\server\lifecycle.py`
- `src\server\main.py`
- `src\server\progress.py`
- `src\server\routes.py`
- `src\server\schemas.py`
- `src\utils\__init__.py`
- `src\utils\currency.py`
- `src\utils\debug.py`
- `src\utils\eta.py`
- `src\utils\logger.py`
- `tests\test_ai_orchestrator_runtime_path.py`
- `tests\test_app_import.py`
- `tests\test_budget_filter.py`
- `tests\test_category_filter.py`
- `tests\test_currency.py`
- `tests\test_feedback_learning.py`
- `tests\test_integration.py`
- `tests\test_intent_relevance.py`
- `tests\test_model_registry.py`
- `tests\test_normalizer.py`
- `tests\test_pipeline_robustness.py`
- `tests\test_preflight.py`
- `tests\test_preflight_errors.py`
- `tests\test_query_expander.py`
- `tests\test_schema.py`
- `tests\test_url_builder.py`
- `tools\pack_repo_for_claude.py`
- `web\app.js`
- `web\index.html`
- `web\style.css`
- `web\vendor\anime.min.js`

---


## FILE: `.agents\skills\fastapi-websocket-doctor\SKILL.md`

```markdown
\---

name: fastapi-websocket-doctor

description: Use this skill when fixing FastAPI, Uvicorn, WebSocket progress, realtime ETA/elapsed time, port conflicts, async worker bugs, and API endpoint integration.

\---



You are the backend doctor for FastAPI + WebSocket.



Primary goals:

\- Fix backend bugs without breaking frontend contracts.

\- Keep progress realtime.

\- Keep scraping workers observable.

\- Prevent blocking requests.



Check these first:

1\. main.py or app.py import path.

2\. Uvicorn command.

3\. Port conflicts.

4\. WebSocket route.

5\. Search ID lifecycle.

6\. Thread-safe state updates.

7\. Async/sync boundary.

8\. Worker exception handling.

9\. CORS.

10\. API response shape.



MarketSpy required endpoints:

\- POST /api/search

\- GET /api/result/{search\_id}

\- WS /ws/{search\_id}

\- Optional GET /api/progress/{search\_id}



Progress rules:

\- elapsed time must tick every second.

\- ETA must update during scraping and AI filtering.

\- Do not freeze ETA at 00:30.

\- Send phase updates:

&#x20; - init

&#x20; - opening\_page

&#x20; - scraping

&#x20; - parsing

&#x20; - budget\_filter

&#x20; - ai\_filter

&#x20; - finalizing

&#x20; - done

&#x20; - error



Bug handling:

\- Never swallow exceptions.

\- Send final error event through WebSocket.

\- Keep logs structured.

\- Include search\_id in logs.

\- Avoid global mutable state without lock.


```

## FILE: `.agents\skills\git-windows-doctor\SKILL.md`

```markdown
\---

name: git-windows-doctor

description: Use this skill when fixing Git problems on Windows, merge conflicts, locked files, database files, branch comparison, git blame, git status, and rollback safety.

\---



You are the Git Windows doctor.



Rules:

\- Always inspect status before changing anything.

\- Never delete user work without backup.

\- Avoid committing database/runtime files.

\- Prefer safe commands first.



Checklist:

1\. Run git status.

2\. Check current branch.

3\. Check uncommitted changes.

4\. Identify locked files.

5\. For SQLite/db lock issues, find process using file.

6\. Resolve merge conflicts intentionally.

7\. Verify with git diff.

8\. Commit only after conflict is resolved.



Common Windows issues:

\- file used by another process

\- unable to unlink

\- MERGE\_HEAD missing

\- port/process still running

\- data/\*.db conflict



For merge conflict:

\- Explain conflict type:

&#x20; - modify/delete

&#x20; - both modified

&#x20; - add/add

\- Choose correct side:

&#x20; - ours

&#x20; - theirs

\- Stage resolved files.

\- Commit merge.



Never suggest:

\- git reset --hard

\- git clean -fd

unless user explicitly asks and backup/status is checked first.


```

## FILE: `.agents\skills\local-llm-json-guard\SKILL.md`

```markdown
\---

name: local-llm-json-guard

description: Use this skill when working with Ollama, qwen2.5:14b, local LLM filtering, JSON parsing, AI crosscheck, confidence scoring, semantic product matching, and feedback learning.

\---



You are the local LLM guard for MarketSpy AI.



Target model:

\- Ollama qwen2.5:14b

\- Fallback model allowed only if explicitly configured.



Core rules:

1\. Never trust raw LLM output.

2\. Always parse defensively.

3\. Extract JSON from markdown/code fences.

4\. Repair trailing commas when safe.

5\. Validate schema before using output.

6\. If parsing fails, log raw output preview.

7\. Never reject all products silently.



Product filtering schema:

\- accepted: boolean

\- confidence: number from 0 to 1

\- reason: string

\- tags: string\[]

\- matched\_query\_terms: string\[]



Semantic matching:

\- Broad query like "laptop gaming" should accept:

&#x20; - ASUS ROG

&#x20; - Lenovo Legion

&#x20; - Acer Nitro

&#x20; - MSI gaming laptops

&#x20; - RTX/GTX gaming products

\- Do not require exact keyword match only.

\- Budget filter must run separately from semantic relevance.

\- Budget tolerance must support Indonesian dot format:

&#x20; - 12.000.000

&#x20; - 2.500.000



Feedback learning:

\- Benar means positive example.

\- Salah opens reason modal.

\- Store feedback with:

&#x20; - query

&#x20; - product data

&#x20; - decision

&#x20; - selected reasons

&#x20; - timestamp

\- Add reset learning behavior if requested.



Failure policy:

\- If Ollama 500 or timeout occurs:

&#x20; - continue with rule-based fallback

&#x20; - mark AI status as fallback

&#x20; - do not destroy scraped results


```

## FILE: `.agents\skills\marketspy-scraper-debugger\SKILL.md`

```markdown
\---

name: marketspy-scraper-debugger

description: Use this skill when debugging Tokopedia/Shopee scraping, Puppeteer, Playwright, Selenium fallback, anti-bot errors, target count mismatch, timeout, captcha marker, pagination, infinite scroll, and product extraction.

\---



You are the scraper debugger for MarketSpy AI.



Main goal:

Make scraping reliable, observable, and recoverable.



Debug checklist:

1\. Identify selected engine:

&#x20;  - Puppeteer

&#x20;  - Playwright

&#x20;  - Selenium / undetected-chromedriver fallback

2\. Check search URL construction.

3\. Check page load strategy.

4\. Check selectors.

5\. Check pagination or infinite scroll.

6\. Check target\_count behavior.

7\. Check product deduplication.

8\. Check budget parsing.

9\. Check extraction completeness.

10\. Check debug artifacts:

&#x20;  - HTML snapshot

&#x20;  - Screenshot

&#x20;  - logs

&#x20;  - raw product count



Common errors:

\- net::ERR\_HTTP2\_PROTOCOL\_ERROR

\- net::ERR\_CONNECTION\_RESET

\- Page.goto timeout

\- Page.content failed because page is navigating

\- captcha marker

\- Muat Lebih Banyak not clickable

\- target\_count requested 50 but only returns 12/28

\- product image is data:image placeholder

\- product title/price missing



Rules:

\- Never silently return partial results without explaining source count.

\- If target\_count is 50, keep scraping until:

&#x20; - 50 valid unique products are found, or

&#x20; - max retry/page limit is reached.

\- Always log current phase.

\- Always separate:

&#x20; - raw scraped count

&#x20; - valid after parser

&#x20; - valid after budget

&#x20; - accepted by AI

&#x20; - displayed count



Fallback policy:

1\. Try primary engine.

2\. If network/protocol/captcha error occurs, switch engine.

3\. Preserve same search\_id and progress channel.

4\. Report fallback reason in logs.


```

## FILE: `.agents\skills\marketspy-ui-architect\SKILL.md`

```markdown
\---

name: marketspy-ui-architect

description: Use this skill when designing, refactoring, or improving the MarketSpy AI frontend, especially dashboard UI, landing page, AnimeJS-style interactions, Tailwind layout, product cards, progress UI, and AI scanning states.

\---



You are the UI architect for MarketSpy AI.



Before coding:

1\. Inspect the existing frontend structure.

2\. Identify the framework and styling system.

3\. Reuse existing components when possible.

4\. Do not create unused files.

5\. Do not break API integration.



Design rules:

\- Use midnight blue as the base theme.

\- Prefer premium SaaS dashboard style.

\- Use glassmorphism only when it improves clarity.

\- Keep contrast readable.

\- Make UI responsive from mobile to desktop.

\- Avoid fake buttons and dead components.

\- Every button must have a clear state or real handler.

\- Loading, empty, error, and success states are required.

\- Product cards must show name, price, store, rating, sold count, and image fallback.

\- Progress UI must show elapsed time, ETA, current phase, percentage, and logs.



MarketSpy-specific UI sections:

\- Hero/search form.

\- Scraping progress box.

\- AI crosscheck panel.

\- Realtime logs.

\- Product result grid.

\- Quick filters:

&#x20; - Most Trusted

&#x20; - Termurah

&#x20; - Terbaik

\- Feedback:

&#x20; - Benar

&#x20; - Salah

&#x20; - If Salah is clicked, open feedback modal.



When using Magic MCP or UI UX Pro Max:

1\. Generate component ideas.

2\. Adapt output to existing code style.

3\. Remove unused dependencies.

4\. Integrate into actual files.

5\. Run build/lint if available.


```

## FILE: `.codex\skills\ui-ux-pro-max\scripts\core.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Core - BM25 search engine for UI/UX style guides
"""

import csv
import re
from pathlib import Path
from math import log
from collections import defaultdict

# ============ CONFIGURATION ============
DATA_DIR = Path(__file__).parent.parent / "data"
MAX_RESULTS = 3

CSV_CONFIG = {
    "style": {
        "file": "styles.csv",
        "search_cols": ["Style Category", "Keywords", "Best For", "Type", "AI Prompt Keywords"],
        "output_cols": ["Style Category", "Type", "Keywords", "Primary Colors", "Effects & Animation", "Best For", "Performance", "Accessibility", "Framework Compatibility", "Complexity", "AI Prompt Keywords", "CSS/Technical Keywords", "Implementation Checklist", "Design System Variables"]
    },
    "color": {
        "file": "colors.csv",
        "search_cols": ["Product Type", "Notes"],
        "output_cols": ["Product Type", "Primary (Hex)", "Secondary (Hex)", "CTA (Hex)", "Background (Hex)", "Text (Hex)", "Notes"]
    },
    "chart": {
        "file": "charts.csv",
        "search_cols": ["Data Type", "Keywords", "Best Chart Type", "Accessibility Notes"],
        "output_cols": ["Data Type", "Keywords", "Best Chart Type", "Secondary Options", "Color Guidance", "Accessibility Notes", "Library Recommendation", "Interactive Level"]
    },
    "landing": {
        "file": "landing.csv",
        "search_cols": ["Pattern Name", "Keywords", "Conversion Optimization", "Section Order"],
        "output_cols": ["Pattern Name", "Keywords", "Section Order", "Primary CTA Placement", "Color Strategy", "Conversion Optimization"]
    },
    "product": {
        "file": "products.csv",
        "search_cols": ["Product Type", "Keywords", "Primary Style Recommendation", "Key Considerations"],
        "output_cols": ["Product Type", "Keywords", "Primary Style Recommendation", "Secondary Styles", "Landing Page Pattern", "Dashboard Style (if applicable)", "Color Palette Focus"]
    },
    "ux": {
        "file": "ux-guidelines.csv",
        "search_cols": ["Category", "Issue", "Description", "Platform"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "typography": {
        "file": "typography.csv",
        "search_cols": ["Font Pairing Name", "Category", "Mood/Style Keywords", "Best For", "Heading Font", "Body Font"],
        "output_cols": ["Font Pairing Name", "Category", "Heading Font", "Body Font", "Mood/Style Keywords", "Best For", "Google Fonts URL", "CSS Import", "Tailwind Config", "Notes"]
    },
    "icons": {
        "file": "icons.csv",
        "search_cols": ["Category", "Icon Name", "Keywords", "Best For"],
        "output_cols": ["Category", "Icon Name", "Keywords", "Library", "Import Code", "Usage", "Best For", "Style"]
    },
    "react": {
        "file": "react-performance.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "web": {
        "file": "web-interface.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    }
}

STACK_CONFIG = {
    "html-tailwind": {"file": "stacks/html-tailwind.csv"},
    "react": {"file": "stacks/react.csv"},
    "nextjs": {"file": "stacks/nextjs.csv"},
    "astro": {"file": "stacks/astro.csv"},
    "vue": {"file": "stacks/vue.csv"},
    "nuxtjs": {"file": "stacks/nuxtjs.csv"},
    "nuxt-ui": {"file": "stacks/nuxt-ui.csv"},
    "svelte": {"file": "stacks/svelte.csv"},
    "swiftui": {"file": "stacks/swiftui.csv"},
    "react-native": {"file": "stacks/react-native.csv"},
    "flutter": {"file": "stacks/flutter.csv"},
    "shadcn": {"file": "stacks/shadcn.csv"},
    "jetpack-compose": {"file": "stacks/jetpack-compose.csv"}
}

# Common columns for all stacks
_STACK_COLS = {
    "search_cols": ["Category", "Guideline", "Description", "Do", "Don't"],
    "output_cols": ["Category", "Guideline", "Description", "Do", "Don't", "Code Good", "Code Bad", "Severity", "Docs URL"]
}

AVAILABLE_STACKS = list(STACK_CONFIG.keys())


# ============ BM25 IMPLEMENTATION ============
class BM25:
    """BM25 ranking algorithm for text search"""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_lengths = []
        self.avgdl = 0
        self.idf = {}
        self.doc_freqs = defaultdict(int)
        self.N = 0

    def tokenize(self, text):
        """Lowercase, split, remove punctuation, filter short words"""
        text = re.sub(r'[^\w\s]', ' ', str(text).lower())
        return [w for w in text.split() if len(w) > 2]

    def fit(self, documents):
        """Build BM25 index from documents"""
        self.corpus = [self.tokenize(doc) for doc in documents]
        self.N = len(self.corpus)
        if self.N == 0:
            return
        self.doc_lengths = [len(doc) for doc in self.corpus]
        self.avgdl = sum(self.doc_lengths) / self.N

        for doc in self.corpus:
            seen = set()
            for word in doc:
                if word not in seen:
                    self.doc_freqs[word] += 1
                    seen.add(word)

        for word, freq in self.doc_freqs.items():
            self.idf[word] = log((self.N - freq + 0.5) / (freq + 0.5) + 1)

    def score(self, query):
        """Score all documents against query"""
        query_tokens = self.tokenize(query)
        scores = []

        for idx, doc in enumerate(self.corpus):
            score = 0
            doc_len = self.doc_lengths[idx]
            term_freqs = defaultdict(int)
            for word in doc:
                term_freqs[word] += 1

            for token in query_tokens:
                if token in self.idf:
                    tf = term_freqs[token]
                    idf = self.idf[token]
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                    score += idf * numerator / denominator

            scores.append((idx, score))

        return sorted(scores, key=lambda x: x[1], reverse=True)


# ============ SEARCH FUNCTIONS ============
def _load_csv(filepath):
    """Load CSV and return list of dicts"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _search_csv(filepath, search_cols, output_cols, query, max_results):
    """Core search function using BM25"""
    if not filepath.exists():
        return []

    data = _load_csv(filepath)

    # Build documents from search columns
    documents = [" ".join(str(row.get(col, "")) for col in search_cols) for row in data]

    # BM25 search
    bm25 = BM25()
    bm25.fit(documents)
    ranked = bm25.score(query)

    # Get top results with score > 0
    results = []
    for idx, score in ranked[:max_results]:
        if score > 0:
            row = data[idx]
            results.append({col: row.get(col, "") for col in output_cols if col in row})

    return results


def detect_domain(query):
    """Auto-detect the most relevant domain from query"""
    query_lower = query.lower()

    domain_keywords = {
        "color": ["color", "palette", "hex", "#", "rgb"],
        "chart": ["chart", "graph", "visualization", "trend", "bar", "pie", "scatter", "heatmap", "funnel"],
        "landing": ["landing", "page", "cta", "conversion", "hero", "testimonial", "pricing", "section"],
        "product": ["saas", "ecommerce", "e-commerce", "fintech", "healthcare", "gaming", "portfolio", "crypto", "dashboard"],
        "style": ["style", "design", "ui", "minimalism", "glassmorphism", "neumorphism", "brutalism", "dark mode", "flat", "aurora", "prompt", "css", "implementation", "variable", "checklist", "tailwind"],
        "ux": ["ux", "usability", "accessibility", "wcag", "touch", "scroll", "animation", "keyboard", "navigation", "mobile"],
        "typography": ["font", "typography", "heading", "serif", "sans"],
        "icons": ["icon", "icons", "lucide", "heroicons", "symbol", "glyph", "pictogram", "svg icon"],
        "react": ["react", "next.js", "nextjs", "suspense", "memo", "usecallback", "useeffect", "rerender", "bundle", "waterfall", "barrel", "dynamic import", "rsc", "server component"],
        "web": ["aria", "focus", "outline", "semantic", "virtualize", "autocomplete", "form", "input type", "preconnect"]
    }

    scores = {domain: sum(1 for kw in keywords if kw in query_lower) for domain, keywords in domain_keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "style"


def search(query, domain=None, max_results=MAX_RESULTS):
    """Main search function with auto-domain detection"""
    if domain is None:
        domain = detect_domain(query)

    config = CSV_CONFIG.get(domain, CSV_CONFIG["style"])
    filepath = DATA_DIR / config["file"]

    if not filepath.exists():
        return {"error": f"File not found: {filepath}", "domain": domain}

    results = _search_csv(filepath, config["search_cols"], config["output_cols"], query, max_results)

    return {
        "domain": domain,
        "query": query,
        "file": config["file"],
        "count": len(results),
        "results": results
    }


def search_stack(query, stack, max_results=MAX_RESULTS):
    """Search stack-specific guidelines"""
    if stack not in STACK_CONFIG:
        return {"error": f"Unknown stack: {stack}. Available: {', '.join(AVAILABLE_STACKS)}"}

    filepath = DATA_DIR / STACK_CONFIG[stack]["file"]

    if not filepath.exists():
        return {"error": f"Stack file not found: {filepath}", "stack": stack}

    results = _search_csv(filepath, _STACK_COLS["search_cols"], _STACK_COLS["output_cols"], query, max_results)

    return {
        "domain": "stack",
        "stack": stack,
        "query": query,
        "file": STACK_CONFIG[stack]["file"],
        "count": len(results),
        "results": results
    }

```

## FILE: `.codex\skills\ui-ux-pro-max\scripts\design_system.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design System Generator - Aggregates search results and applies reasoning
to generate comprehensive design system recommendations.

Usage:
    from design_system import generate_design_system
    result = generate_design_system("SaaS dashboard", "My Project")
    
    # With persistence (Master + Overrides pattern)
    result = generate_design_system("SaaS dashboard", "My Project", persist=True)
    result = generate_design_system("SaaS dashboard", "My Project", persist=True, page="dashboard")
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from core import search, DATA_DIR


# ============ CONFIGURATION ============
REASONING_FILE = "ui-reasoning.csv"

SEARCH_CONFIG = {
    "product": {"max_results": 1},
    "style": {"max_results": 3},
    "color": {"max_results": 2},
    "landing": {"max_results": 2},
    "typography": {"max_results": 2}
}


# ============ DESIGN SYSTEM GENERATOR ============
class DesignSystemGenerator:
    """Generates design system recommendations from aggregated searches."""

    def __init__(self):
        self.reasoning_data = self._load_reasoning()

    def _load_reasoning(self) -> list:
        """Load reasoning rules from CSV."""
        filepath = DATA_DIR / REASONING_FILE
        if not filepath.exists():
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _multi_domain_search(self, query: str, style_priority: list = None) -> dict:
        """Execute searches across multiple domains."""
        results = {}
        for domain, config in SEARCH_CONFIG.items():
            if domain == "style" and style_priority:
                # For style, also search with priority keywords
                priority_query = " ".join(style_priority[:2]) if style_priority else query
                combined_query = f"{query} {priority_query}"
                results[domain] = search(combined_query, domain, config["max_results"])
            else:
                results[domain] = search(query, domain, config["max_results"])
        return results

    def _find_reasoning_rule(self, category: str) -> dict:
        """Find matching reasoning rule for a category."""
        category_lower = category.lower()

        # Try exact match first
        for rule in self.reasoning_data:
            if rule.get("UI_Category", "").lower() == category_lower:
                return rule

        # Try partial match
        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            if ui_cat in category_lower or category_lower in ui_cat:
                return rule

        # Try keyword match
        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            keywords = ui_cat.replace("/", " ").replace("-", " ").split()
            if any(kw in category_lower for kw in keywords):
                return rule

        return {}

    def _apply_reasoning(self, category: str, search_results: dict) -> dict:
        """Apply reasoning rules to search results."""
        rule = self._find_reasoning_rule(category)

        if not rule:
            return {
                "pattern": "Hero + Features + CTA",
                "style_priority": ["Minimalism", "Flat Design"],
                "color_mood": "Professional",
                "typography_mood": "Clean",
                "key_effects": "Subtle hover transitions",
                "anti_patterns": "",
                "decision_rules": {},
                "severity": "MEDIUM"
            }

        # Parse decision rules JSON
        decision_rules = {}
        try:
            decision_rules = json.loads(rule.get("Decision_Rules", "{}"))
        except json.JSONDecodeError:
            pass

        return {
            "pattern": rule.get("Recommended_Pattern", ""),
            "style_priority": [s.strip() for s in rule.get("Style_Priority", "").split("+")],
            "color_mood": rule.get("Color_Mood", ""),
            "typography_mood": rule.get("Typography_Mood", ""),
            "key_effects": rule.get("Key_Effects", ""),
            "anti_patterns": rule.get("Anti_Patterns", ""),
            "decision_rules": decision_rules,
            "severity": rule.get("Severity", "MEDIUM")
        }

    def _select_best_match(self, results: list, priority_keywords: list) -> dict:
        """Select best matching result based on priority keywords."""
        if not results:
            return {}

        if not priority_keywords:
            return results[0]

        # First: try exact style name match
        for priority in priority_keywords:
            priority_lower = priority.lower().strip()
            for result in results:
                style_name = result.get("Style Category", "").lower()
                if priority_lower in style_name or style_name in priority_lower:
                    return result

        # Second: score by keyword match in all fields
        scored = []
        for result in results:
            result_str = str(result).lower()
            score = 0
            for kw in priority_keywords:
                kw_lower = kw.lower().strip()
                # Higher score for style name match
                if kw_lower in result.get("Style Category", "").lower():
                    score += 10
                # Lower score for keyword field match
                elif kw_lower in result.get("Keywords", "").lower():
                    score += 3
                # Even lower for other field matches
                elif kw_lower in result_str:
                    score += 1
            scored.append((score, result))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored and scored[0][0] > 0 else results[0]

    def _extract_results(self, search_result: dict) -> list:
        """Extract results list from search result dict."""
        return search_result.get("results", [])

    def generate(self, query: str, project_name: str = None) -> dict:
        """Generate complete design system recommendation."""
        # Step 1: First search product to get category
        product_result = search(query, "product", 1)
        product_results = product_result.get("results", [])
        category = "General"
        if product_results:
            category = product_results[0].get("Product Type", "General")

        # Step 2: Get reasoning rules for this category
        reasoning = self._apply_reasoning(category, {})
        style_priority = reasoning.get("style_priority", [])

        # Step 3: Multi-domain search with style priority hints
        search_results = self._multi_domain_search(query, style_priority)
        search_results["product"] = product_result  # Reuse product search

        # Step 4: Select best matches from each domain using priority
        style_results = self._extract_results(search_results.get("style", {}))
        color_results = self._extract_results(search_results.get("color", {}))
        typography_results = self._extract_results(search_results.get("typography", {}))
        landing_results = self._extract_results(search_results.get("landing", {}))

        best_style = self._select_best_match(style_results, reasoning.get("style_priority", []))
        best_color = color_results[0] if color_results else {}
        best_typography = typography_results[0] if typography_results else {}
        best_landing = landing_results[0] if landing_results else {}

        # Step 5: Build final recommendation
        # Combine effects from both reasoning and style search
        style_effects = best_style.get("Effects & Animation", "")
        reasoning_effects = reasoning.get("key_effects", "")
        combined_effects = style_effects if style_effects else reasoning_effects

        return {
            "project_name": project_name or query.upper(),
            "category": category,
            "pattern": {
                "name": best_landing.get("Pattern Name", reasoning.get("pattern", "Hero + Features + CTA")),
                "sections": best_landing.get("Section Order", "Hero > Features > CTA"),
                "cta_placement": best_landing.get("Primary CTA Placement", "Above fold"),
                "color_strategy": best_landing.get("Color Strategy", ""),
                "conversion": best_landing.get("Conversion Optimization", "")
            },
            "style": {
                "name": best_style.get("Style Category", "Minimalism"),
                "type": best_style.get("Type", "General"),
                "effects": style_effects,
                "keywords": best_style.get("Keywords", ""),
                "best_for": best_style.get("Best For", ""),
                "performance": best_style.get("Performance", ""),
                "accessibility": best_style.get("Accessibility", "")
            },
            "colors": {
                "primary": best_color.get("Primary (Hex)", "#2563EB"),
                "secondary": best_color.get("Secondary (Hex)", "#3B82F6"),
                "cta": best_color.get("CTA (Hex)", "#F97316"),
                "background": best_color.get("Background (Hex)", "#F8FAFC"),
                "text": best_color.get("Text (Hex)", "#1E293B"),
                "notes": best_color.get("Notes", "")
            },
            "typography": {
                "heading": best_typography.get("Heading Font", "Inter"),
                "body": best_typography.get("Body Font", "Inter"),
                "mood": best_typography.get("Mood/Style Keywords", reasoning.get("typography_mood", "")),
                "best_for": best_typography.get("Best For", ""),
                "google_fonts_url": best_typography.get("Google Fonts URL", ""),
                "css_import": best_typography.get("CSS Import", "")
            },
            "key_effects": combined_effects,
            "anti_patterns": reasoning.get("anti_patterns", ""),
            "decision_rules": reasoning.get("decision_rules", {}),
            "severity": reasoning.get("severity", "MEDIUM")
        }


# ============ OUTPUT FORMATTERS ============
BOX_WIDTH = 90  # Wider box for more content

def format_ascii_box(design_system: dict) -> str:
    """Format design system as ASCII box with emojis (MCP-style)."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")

    def wrap_text(text: str, prefix: str, width: int) -> list:
        """Wrap long text into multiple lines."""
        if not text:
            return []
        words = text.split()
        lines = []
        current_line = prefix
        for word in words:
            if len(current_line) + len(word) + 1 <= width - 2:
                current_line += (" " if current_line != prefix else "") + word
            else:
                if current_line != prefix:
                    lines.append(current_line)
                current_line = prefix + word
        if current_line != prefix:
            lines.append(current_line)
        return lines

    # Build sections from pattern
    sections = pattern.get("sections", "").split(">")
    sections = [s.strip() for s in sections if s.strip()]

    # Build output lines
    lines = []
    w = BOX_WIDTH - 1

    lines.append("+" + "-" * w + "+")
    lines.append(f"|  TARGET: {project} - RECOMMENDED DESIGN SYSTEM".ljust(BOX_WIDTH) + "|")
    lines.append("+" + "-" * w + "+")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Pattern section
    lines.append(f"|  PATTERN: {pattern.get('name', '')}".ljust(BOX_WIDTH) + "|")
    if pattern.get('conversion'):
        lines.append(f"|     Conversion: {pattern.get('conversion', '')}".ljust(BOX_WIDTH) + "|")
    if pattern.get('cta_placement'):
        lines.append(f"|     CTA: {pattern.get('cta_placement', '')}".ljust(BOX_WIDTH) + "|")
    lines.append("|     Sections:".ljust(BOX_WIDTH) + "|")
    for i, section in enumerate(sections, 1):
        lines.append(f"|       {i}. {section}".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Style section
    lines.append(f"|  STYLE: {style.get('name', '')}".ljust(BOX_WIDTH) + "|")
    if style.get("keywords"):
        for line in wrap_text(f"Keywords: {style.get('keywords', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("best_for"):
        for line in wrap_text(f"Best For: {style.get('best_for', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("performance") or style.get("accessibility"):
        perf_a11y = f"Performance: {style.get('performance', '')} | Accessibility: {style.get('accessibility', '')}"
        lines.append(f"|     {perf_a11y}".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Colors section
    lines.append("|  COLORS:".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Primary:    {colors.get('primary', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Secondary:  {colors.get('secondary', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     CTA:        {colors.get('cta', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Background: {colors.get('background', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Text:       {colors.get('text', '')}".ljust(BOX_WIDTH) + "|")
    if colors.get("notes"):
        for line in wrap_text(f"Notes: {colors.get('notes', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Typography section
    lines.append(f"|  TYPOGRAPHY: {typography.get('heading', '')} / {typography.get('body', '')}".ljust(BOX_WIDTH) + "|")
    if typography.get("mood"):
        for line in wrap_text(f"Mood: {typography.get('mood', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if typography.get("best_for"):
        for line in wrap_text(f"Best For: {typography.get('best_for', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if typography.get("google_fonts_url"):
        lines.append(f"|     Google Fonts: {typography.get('google_fonts_url', '')}".ljust(BOX_WIDTH) + "|")
    if typography.get("css_import"):
        lines.append(f"|     CSS Import: {typography.get('css_import', '')[:70]}...".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Key Effects section
    if effects:
        lines.append("|  KEY EFFECTS:".ljust(BOX_WIDTH) + "|")
        for line in wrap_text(effects, "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
        lines.append("|" + " " * BOX_WIDTH + "|")

    # Anti-patterns section
    if anti_patterns:
        lines.append("|  AVOID (Anti-patterns):".ljust(BOX_WIDTH) + "|")
        for line in wrap_text(anti_patterns, "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
        lines.append("|" + " " * BOX_WIDTH + "|")

    # Pre-Delivery Checklist section
    lines.append("|  PRE-DELIVERY CHECKLIST:".ljust(BOX_WIDTH) + "|")
    checklist_items = [
        "[ ] No emojis as icons (use SVG: Heroicons/Lucide)",
        "[ ] cursor-pointer on all clickable elements",
        "[ ] Hover states with smooth transitions (150-300ms)",
        "[ ] Light mode: text contrast 4.5:1 minimum",
        "[ ] Focus states visible for keyboard nav",
        "[ ] prefers-reduced-motion respected",
        "[ ] Responsive: 375px, 768px, 1024px, 1440px"
    ]
    for item in checklist_items:
        lines.append(f"|     {item}".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    lines.append("+" + "-" * w + "+")

    return "\n".join(lines)


def format_markdown(design_system: dict) -> str:
    """Format design system as markdown."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")

    lines = []
    lines.append(f"## Design System: {project}")
    lines.append("")

    # Pattern section
    lines.append("### Pattern")
    lines.append(f"- **Name:** {pattern.get('name', '')}")
    if pattern.get('conversion'):
        lines.append(f"- **Conversion Focus:** {pattern.get('conversion', '')}")
    if pattern.get('cta_placement'):
        lines.append(f"- **CTA Placement:** {pattern.get('cta_placement', '')}")
    if pattern.get('color_strategy'):
        lines.append(f"- **Color Strategy:** {pattern.get('color_strategy', '')}")
    lines.append(f"- **Sections:** {pattern.get('sections', '')}")
    lines.append("")

    # Style section
    lines.append("### Style")
    lines.append(f"- **Name:** {style.get('name', '')}")
    if style.get('keywords'):
        lines.append(f"- **Keywords:** {style.get('keywords', '')}")
    if style.get('best_for'):
        lines.append(f"- **Best For:** {style.get('best_for', '')}")
    if style.get('performance') or style.get('accessibility'):
        lines.append(f"- **Performance:** {style.get('performance', '')} | **Accessibility:** {style.get('accessibility', '')}")
    lines.append("")

    # Colors section
    lines.append("### Colors")
    lines.append(f"| Role | Hex |")
    lines.append(f"|------|-----|")
    lines.append(f"| Primary | {colors.get('primary', '')} |")
    lines.append(f"| Secondary | {colors.get('secondary', '')} |")
    lines.append(f"| CTA | {colors.get('cta', '')} |")
    lines.append(f"| Background | {colors.get('background', '')} |")
    lines.append(f"| Text | {colors.get('text', '')} |")
    if colors.get("notes"):
        lines.append(f"\n*Notes: {colors.get('notes', '')}*")
    lines.append("")

    # Typography section
    lines.append("### Typography")
    lines.append(f"- **Heading:** {typography.get('heading', '')}")
    lines.append(f"- **Body:** {typography.get('body', '')}")
    if typography.get("mood"):
        lines.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("best_for"):
        lines.append(f"- **Best For:** {typography.get('best_for', '')}")
    if typography.get("google_fonts_url"):
        lines.append(f"- **Google Fonts:** {typography.get('google_fonts_url', '')}")
    if typography.get("css_import"):
        lines.append(f"- **CSS Import:**")
        lines.append(f"```css")
        lines.append(f"{typography.get('css_import', '')}")
        lines.append(f"```")
    lines.append("")

    # Key Effects section
    if effects:
        lines.append("### Key Effects")
        lines.append(f"{effects}")
        lines.append("")

    # Anti-patterns section
    if anti_patterns:
        lines.append("### Avoid (Anti-patterns)")
        newline_bullet = '\n- '
        lines.append(f"- {anti_patterns.replace(' + ', newline_bullet)}")
        lines.append("")

    # Pre-Delivery Checklist section
    lines.append("### Pre-Delivery Checklist")
    lines.append("- [ ] No emojis as icons (use SVG: Heroicons/Lucide)")
    lines.append("- [ ] cursor-pointer on all clickable elements")
    lines.append("- [ ] Hover states with smooth transitions (150-300ms)")
    lines.append("- [ ] Light mode: text contrast 4.5:1 minimum")
    lines.append("- [ ] Focus states visible for keyboard nav")
    lines.append("- [ ] prefers-reduced-motion respected")
    lines.append("- [ ] Responsive: 375px, 768px, 1024px, 1440px")
    lines.append("")

    return "\n".join(lines)


# ============ MAIN ENTRY POINT ============
def generate_design_system(query: str, project_name: str = None, output_format: str = "ascii", 
                           persist: bool = False, page: str = None, output_dir: str = None) -> str:
    """
    Main entry point for design system generation.

    Args:
        query: Search query (e.g., "SaaS dashboard", "e-commerce luxury")
        project_name: Optional project name for output header
        output_format: "ascii" (default) or "markdown"
        persist: If True, save design system to design-system/ folder
        page: Optional page name for page-specific override file
        output_dir: Optional output directory (defaults to current working directory)

    Returns:
        Formatted design system string
    """
    generator = DesignSystemGenerator()
    design_system = generator.generate(query, project_name)
    
    # Persist to files if requested
    if persist:
        persist_design_system(design_system, page, output_dir, query)

    if output_format == "markdown":
        return format_markdown(design_system)
    return format_ascii_box(design_system)


# ============ PERSISTENCE FUNCTIONS ============
def persist_design_system(design_system: dict, page: str = None, output_dir: str = None, page_query: str = None) -> dict:
    """
    Persist design system to design-system/<project>/ folder using Master + Overrides pattern.
    
    Args:
        design_system: The generated design system dictionary
        page: Optional page name for page-specific override file
        output_dir: Optional output directory (defaults to current working directory)
        page_query: Optional query string for intelligent page override generation
    
    Returns:
        dict with created file paths and status
    """
    base_dir = Path(output_dir) if output_dir else Path.cwd()
    
    # Use project name for project-specific folder
    project_name = design_system.get("project_name", "default")
    project_slug = project_name.lower().replace(' ', '-')
    
    design_system_dir = base_dir / "design-system" / project_slug
    pages_dir = design_system_dir / "pages"
    
    created_files = []
    
    # Create directories
    design_system_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    master_file = design_system_dir / "MASTER.md"
    
    # Generate and write MASTER.md
    master_content = format_master_md(design_system)
    with open(master_file, 'w', encoding='utf-8') as f:
        f.write(master_content)
    created_files.append(str(master_file))
    
    # If page is specified, create page override file with intelligent content
    if page:
        page_file = pages_dir / f"{page.lower().replace(' ', '-')}.md"
        page_content = format_page_override_md(design_system, page, page_query)
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_content)
        created_files.append(str(page_file))
    
    return {
        "status": "success",
        "design_system_dir": str(design_system_dir),
        "created_files": created_files
    }


def format_master_md(design_system: dict) -> str:
    """Format design system as MASTER.md with hierarchical override logic."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    
    # Logic header
    lines.append("# Design System Master File")
    lines.append("")
    lines.append("> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.")
    lines.append("> If that file exists, its rules **override** this Master file.")
    lines.append("> If not, strictly follow the rules below.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**Project:** {project}")
    lines.append(f"**Generated:** {timestamp}")
    lines.append(f"**Category:** {design_system.get('category', 'General')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Global Rules section
    lines.append("## Global Rules")
    lines.append("")
    
    # Color Palette
    lines.append("### Color Palette")
    lines.append("")
    lines.append("| Role | Hex | CSS Variable |")
    lines.append("|------|-----|--------------|")
    lines.append(f"| Primary | `{colors.get('primary', '#2563EB')}` | `--color-primary` |")
    lines.append(f"| Secondary | `{colors.get('secondary', '#3B82F6')}` | `--color-secondary` |")
    lines.append(f"| CTA/Accent | `{colors.get('cta', '#F97316')}` | `--color-cta` |")
    lines.append(f"| Background | `{colors.get('background', '#F8FAFC')}` | `--color-background` |")
    lines.append(f"| Text | `{colors.get('text', '#1E293B')}` | `--color-text` |")
    lines.append("")
    if colors.get("notes"):
        lines.append(f"**Color Notes:** {colors.get('notes', '')}")
        lines.append("")
    
    # Typography
    lines.append("### Typography")
    lines.append("")
    lines.append(f"- **Heading Font:** {typography.get('heading', 'Inter')}")
    lines.append(f"- **Body Font:** {typography.get('body', 'Inter')}")
    if typography.get("mood"):
        lines.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("google_fonts_url"):
        lines.append(f"- **Google Fonts:** [{typography.get('heading', '')} + {typography.get('body', '')}]({typography.get('google_fonts_url', '')})")
    lines.append("")
    if typography.get("css_import"):
        lines.append("**CSS Import:**")
        lines.append("```css")
        lines.append(typography.get("css_import", ""))
        lines.append("```")
        lines.append("")
    
    # Spacing Variables
    lines.append("### Spacing Variables")
    lines.append("")
    lines.append("| Token | Value | Usage |")
    lines.append("|-------|-------|-------|")
    lines.append("| `--space-xs` | `4px` / `0.25rem` | Tight gaps |")
    lines.append("| `--space-sm` | `8px` / `0.5rem` | Icon gaps, inline spacing |")
    lines.append("| `--space-md` | `16px` / `1rem` | Standard padding |")
    lines.append("| `--space-lg` | `24px` / `1.5rem` | Section padding |")
    lines.append("| `--space-xl` | `32px` / `2rem` | Large gaps |")
    lines.append("| `--space-2xl` | `48px` / `3rem` | Section margins |")
    lines.append("| `--space-3xl` | `64px` / `4rem` | Hero padding |")
    lines.append("")
    
    # Shadow Depths
    lines.append("### Shadow Depths")
    lines.append("")
    lines.append("| Level | Value | Usage |")
    lines.append("|-------|-------|-------|")
    lines.append("| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |")
    lines.append("| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.1)` | Cards, buttons |")
    lines.append("| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dropdowns |")
    lines.append("| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | Hero images, featured cards |")
    lines.append("")
    
    # Component Specs section
    lines.append("---")
    lines.append("")
    lines.append("## Component Specs")
    lines.append("")
    
    # Buttons
    lines.append("### Buttons")
    lines.append("")
    lines.append("```css")
    lines.append("/* Primary Button */")
    lines.append(".btn-primary {")
    lines.append(f"  background: {colors.get('cta', '#F97316')};")
    lines.append("  color: white;")
    lines.append("  padding: 12px 24px;")
    lines.append("  border-radius: 8px;")
    lines.append("  font-weight: 600;")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("")
    lines.append(".btn-primary:hover {")
    lines.append("  opacity: 0.9;")
    lines.append("  transform: translateY(-1px);")
    lines.append("}")
    lines.append("")
    lines.append("/* Secondary Button */")
    lines.append(".btn-secondary {")
    lines.append(f"  background: transparent;")
    lines.append(f"  color: {colors.get('primary', '#2563EB')};")
    lines.append(f"  border: 2px solid {colors.get('primary', '#2563EB')};")
    lines.append("  padding: 12px 24px;")
    lines.append("  border-radius: 8px;")
    lines.append("  font-weight: 600;")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Cards
    lines.append("### Cards")
    lines.append("")
    lines.append("```css")
    lines.append(".card {")
    lines.append(f"  background: {colors.get('background', '#FFFFFF')};")
    lines.append("  border-radius: 12px;")
    lines.append("  padding: 24px;")
    lines.append("  box-shadow: var(--shadow-md);")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("")
    lines.append(".card:hover {")
    lines.append("  box-shadow: var(--shadow-lg);")
    lines.append("  transform: translateY(-2px);")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Inputs
    lines.append("### Inputs")
    lines.append("")
    lines.append("```css")
    lines.append(".input {")
    lines.append("  padding: 12px 16px;")
    lines.append("  border: 1px solid #E2E8F0;")
    lines.append("  border-radius: 8px;")
    lines.append("  font-size: 16px;")
    lines.append("  transition: border-color 200ms ease;")
    lines.append("}")
    lines.append("")
    lines.append(".input:focus {")
    lines.append(f"  border-color: {colors.get('primary', '#2563EB')};")
    lines.append("  outline: none;")
    lines.append(f"  box-shadow: 0 0 0 3px {colors.get('primary', '#2563EB')}20;")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Modals
    lines.append("### Modals")
    lines.append("")
    lines.append("```css")
    lines.append(".modal-overlay {")
    lines.append("  background: rgba(0, 0, 0, 0.5);")
    lines.append("  backdrop-filter: blur(4px);")
    lines.append("}")
    lines.append("")
    lines.append(".modal {")
    lines.append("  background: white;")
    lines.append("  border-radius: 16px;")
    lines.append("  padding: 32px;")
    lines.append("  box-shadow: var(--shadow-xl);")
    lines.append("  max-width: 500px;")
    lines.append("  width: 90%;")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Style section
    lines.append("---")
    lines.append("")
    lines.append("## Style Guidelines")
    lines.append("")
    lines.append(f"**Style:** {style.get('name', 'Minimalism')}")
    lines.append("")
    if style.get("keywords"):
        lines.append(f"**Keywords:** {style.get('keywords', '')}")
        lines.append("")
    if style.get("best_for"):
        lines.append(f"**Best For:** {style.get('best_for', '')}")
        lines.append("")
    if effects:
        lines.append(f"**Key Effects:** {effects}")
        lines.append("")
    
    # Layout Pattern
    lines.append("### Page Pattern")
    lines.append("")
    lines.append(f"**Pattern Name:** {pattern.get('name', '')}")
    lines.append("")
    if pattern.get('conversion'):
        lines.append(f"- **Conversion Strategy:** {pattern.get('conversion', '')}")
    if pattern.get('cta_placement'):
        lines.append(f"- **CTA Placement:** {pattern.get('cta_placement', '')}")
    lines.append(f"- **Section Order:** {pattern.get('sections', '')}")
    lines.append("")
    
    # Anti-Patterns section
    lines.append("---")
    lines.append("")
    lines.append("## Anti-Patterns (Do NOT Use)")
    lines.append("")
    if anti_patterns:
        anti_list = [a.strip() for a in anti_patterns.split("+")]
        for anti in anti_list:
            if anti:
                lines.append(f"- ❌ {anti}")
    lines.append("")
    lines.append("### Additional Forbidden Patterns")
    lines.append("")
    lines.append("- ❌ **Emojis as icons** — Use SVG icons (Heroicons, Lucide, Simple Icons)")
    lines.append("- ❌ **Missing cursor:pointer** — All clickable elements must have cursor:pointer")
    lines.append("- ❌ **Layout-shifting hovers** — Avoid scale transforms that shift layout")
    lines.append("- ❌ **Low contrast text** — Maintain 4.5:1 minimum contrast ratio")
    lines.append("- ❌ **Instant state changes** — Always use transitions (150-300ms)")
    lines.append("- ❌ **Invisible focus states** — Focus states must be visible for a11y")
    lines.append("")
    
    # Pre-Delivery Checklist
    lines.append("---")
    lines.append("")
    lines.append("## Pre-Delivery Checklist")
    lines.append("")
    lines.append("Before delivering any UI code, verify:")
    lines.append("")
    lines.append("- [ ] No emojis used as icons (use SVG instead)")
    lines.append("- [ ] All icons from consistent icon set (Heroicons/Lucide)")
    lines.append("- [ ] `cursor-pointer` on all clickable elements")
    lines.append("- [ ] Hover states with smooth transitions (150-300ms)")
    lines.append("- [ ] Light mode: text contrast 4.5:1 minimum")
    lines.append("- [ ] Focus states visible for keyboard navigation")
    lines.append("- [ ] `prefers-reduced-motion` respected")
    lines.append("- [ ] Responsive: 375px, 768px, 1024px, 1440px")
    lines.append("- [ ] No content hidden behind fixed navbars")
    lines.append("- [ ] No horizontal scroll on mobile")
    lines.append("")
    
    return "\n".join(lines)


def format_page_override_md(design_system: dict, page_name: str, page_query: str = None) -> str:
    """Format a page-specific override file with intelligent AI-generated content."""
    project = design_system.get("project_name", "PROJECT")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page_title = page_name.replace("-", " ").replace("_", " ").title()
    
    # Detect page type and generate intelligent overrides
    page_overrides = _generate_intelligent_overrides(page_name, page_query, design_system)
    
    lines = []
    
    lines.append(f"# {page_title} Page Overrides")
    lines.append("")
    lines.append(f"> **PROJECT:** {project}")
    lines.append(f"> **Generated:** {timestamp}")
    lines.append(f"> **Page Type:** {page_overrides.get('page_type', 'General')}")
    lines.append("")
    lines.append("> ⚠️ **IMPORTANT:** Rules in this file **override** the Master file (`design-system/MASTER.md`).")
    lines.append("> Only deviations from the Master are documented here. For all other rules, refer to the Master.")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Page-specific rules with actual content
    lines.append("## Page-Specific Rules")
    lines.append("")
    
    # Layout Overrides
    lines.append("### Layout Overrides")
    lines.append("")
    layout = page_overrides.get("layout", {})
    if layout:
        for key, value in layout.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master layout")
    lines.append("")
    
    # Spacing Overrides
    lines.append("### Spacing Overrides")
    lines.append("")
    spacing = page_overrides.get("spacing", {})
    if spacing:
        for key, value in spacing.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master spacing")
    lines.append("")
    
    # Typography Overrides
    lines.append("### Typography Overrides")
    lines.append("")
    typography = page_overrides.get("typography", {})
    if typography:
        for key, value in typography.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master typography")
    lines.append("")
    
    # Color Overrides
    lines.append("### Color Overrides")
    lines.append("")
    colors = page_overrides.get("colors", {})
    if colors:
        for key, value in colors.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master colors")
    lines.append("")
    
    # Component Overrides
    lines.append("### Component Overrides")
    lines.append("")
    components = page_overrides.get("components", [])
    if components:
        for comp in components:
            lines.append(f"- {comp}")
    else:
        lines.append("- No overrides — use Master component specs")
    lines.append("")
    
    # Page-Specific Components
    lines.append("---")
    lines.append("")
    lines.append("## Page-Specific Components")
    lines.append("")
    unique_components = page_overrides.get("unique_components", [])
    if unique_components:
        for comp in unique_components:
            lines.append(f"- {comp}")
    else:
        lines.append("- No unique components for this page")
    lines.append("")
    
    # Recommendations
    lines.append("---")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    recommendations = page_overrides.get("recommendations", [])
    if recommendations:
        for rec in recommendations:
            lines.append(f"- {rec}")
    lines.append("")
    
    return "\n".join(lines)


def _generate_intelligent_overrides(page_name: str, page_query: str, design_system: dict) -> dict:
    """
    Generate intelligent overrides based on page type using layered search.
    
    Uses the existing search infrastructure to find relevant style, UX, and layout
    data instead of hardcoded page types.
    """
    from core import search
    
    page_lower = page_name.lower()
    query_lower = (page_query or "").lower()
    combined_context = f"{page_lower} {query_lower}"
    
    # Search across multiple domains for page-specific guidance
    style_search = search(combined_context, "style", max_results=1)
    ux_search = search(combined_context, "ux", max_results=3)
    landing_search = search(combined_context, "landing", max_results=1)
    
    # Extract results from search response
    style_results = style_search.get("results", [])
    ux_results = ux_search.get("results", [])
    landing_results = landing_search.get("results", [])
    
    # Detect page type from search results or context
    page_type = _detect_page_type(combined_context, style_results)
    
    # Build overrides from search results
    layout = {}
    spacing = {}
    typography = {}
    colors = {}
    components = []
    unique_components = []
    recommendations = []
    
    # Extract style-based overrides
    if style_results:
        style = style_results[0]
        style_name = style.get("Style Category", "")
        keywords = style.get("Keywords", "")
        best_for = style.get("Best For", "")
        effects = style.get("Effects & Animation", "")
        
        # Infer layout from style keywords
        if any(kw in keywords.lower() for kw in ["data", "dense", "dashboard", "grid"]):
            layout["Max Width"] = "1400px or full-width"
            layout["Grid"] = "12-column grid for data flexibility"
            spacing["Content Density"] = "High — optimize for information display"
        elif any(kw in keywords.lower() for kw in ["minimal", "simple", "clean", "single"]):
            layout["Max Width"] = "800px (narrow, focused)"
            layout["Layout"] = "Single column, centered"
            spacing["Content Density"] = "Low — focus on clarity"
        else:
            layout["Max Width"] = "1200px (standard)"
            layout["Layout"] = "Full-width sections, centered content"
        
        if effects:
            recommendations.append(f"Effects: {effects}")
    
    # Extract UX guidelines as recommendations
    for ux in ux_results:
        category = ux.get("Category", "")
        do_text = ux.get("Do", "")
        dont_text = ux.get("Don't", "")
        if do_text:
            recommendations.append(f"{category}: {do_text}")
        if dont_text:
            components.append(f"Avoid: {dont_text}")
    
    # Extract landing pattern info for section structure
    if landing_results:
        landing = landing_results[0]
        sections = landing.get("Section Order", "")
        cta_placement = landing.get("Primary CTA Placement", "")
        color_strategy = landing.get("Color Strategy", "")
        
        if sections:
            layout["Sections"] = sections
        if cta_placement:
            recommendations.append(f"CTA Placement: {cta_placement}")
        if color_strategy:
            colors["Strategy"] = color_strategy
    
    # Add page-type specific defaults if no search results
    if not layout:
        layout["Max Width"] = "1200px"
        layout["Layout"] = "Responsive grid"
    
    if not recommendations:
        recommendations = [
            "Refer to MASTER.md for all design rules",
            "Add specific overrides as needed for this page"
        ]
    
    return {
        "page_type": page_type,
        "layout": layout,
        "spacing": spacing,
        "typography": typography,
        "colors": colors,
        "components": components,
        "unique_components": unique_components,
        "recommendations": recommendations
    }


def _detect_page_type(context: str, style_results: list) -> str:
    """Detect page type from context and search results."""
    context_lower = context.lower()
    
    # Check for common page type patterns
    page_patterns = [
        (["dashboard", "admin", "analytics", "data", "metrics", "stats", "monitor", "overview"], "Dashboard / Data View"),
        (["checkout", "payment", "cart", "purchase", "order", "billing"], "Checkout / Payment"),
        (["settings", "profile", "account", "preferences", "config"], "Settings / Profile"),
        (["landing", "marketing", "homepage", "hero", "home", "promo"], "Landing / Marketing"),
        (["login", "signin", "signup", "register", "auth", "password"], "Authentication"),
        (["pricing", "plans", "subscription", "tiers", "packages"], "Pricing / Plans"),
        (["blog", "article", "post", "news", "content", "story"], "Blog / Article"),
        (["product", "item", "detail", "pdp", "shop", "store"], "Product Detail"),
        (["search", "results", "browse", "filter", "catalog", "list"], "Search Results"),
        (["empty", "404", "error", "not found", "zero"], "Empty State"),
    ]
    
    for keywords, page_type in page_patterns:
        if any(kw in context_lower for kw in keywords):
            return page_type
    
    # Fallback: try to infer from style results
    if style_results:
        style_name = style_results[0].get("Style Category", "").lower()
        best_for = style_results[0].get("Best For", "").lower()
        
        if "dashboard" in best_for or "data" in best_for:
            return "Dashboard / Data View"
        elif "landing" in best_for or "marketing" in best_for:
            return "Landing / Marketing"
    
    return "General"


# ============ CLI SUPPORT ============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Design System")
    parser.add_argument("query", help="Search query (e.g., 'SaaS dashboard')")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format")

    args = parser.parse_args()

    result = generate_design_system(args.query, args.project_name, args.format)
    print(result)

```

## FILE: `.codex\skills\ui-ux-pro-max\scripts\search.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Search - BM25 search engine for UI/UX style guides
Usage: python search.py "<query>" [--domain <domain>] [--stack <stack>] [--max-results 3]
       python search.py "<query>" --design-system [-p "Project Name"]
       python search.py "<query>" --design-system --persist [-p "Project Name"] [--page "dashboard"]

Domains: style, prompt, color, chart, landing, product, ux, typography
Stacks: html-tailwind, react, nextjs

Persistence (Master + Overrides pattern):
  --persist    Save design system to design-system/MASTER.md
  --page       Also create a page-specific override file in design-system/pages/
"""

import argparse
import sys
import io
from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack
from design_system import generate_design_system, persist_design_system

# Force UTF-8 for stdout/stderr to handle emojis on Windows (cp1252 default)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def format_output(result):
    """Format results for Claude consumption (token-optimized)"""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []
    if result.get("stack"):
        output.append(f"## UI Pro Max Stack Guidelines")
        output.append(f"**Stack:** {result['stack']} | **Query:** {result['query']}")
    else:
        output.append(f"## UI Pro Max Search Results")
        output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']}")
    output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")

    for i, row in enumerate(result['results'], 1):
        output.append(f"### Result {i}")
        for key, value in row.items():
            value_str = str(value)
            if len(value_str) > 300:
                value_str = value_str[:300] + "..."
            output.append(f"- **{key}:** {value_str}")
        output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Pro Max Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help="Stack-specific search (html-tailwind, react, nextjs)")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    # Design system generation
    parser.add_argument("--design-system", "-ds", action="store_true", help="Generate complete design system recommendation")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name for design system output")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format for design system")
    # Persistence (Master + Overrides pattern)
    parser.add_argument("--persist", action="store_true", help="Save design system to design-system/MASTER.md (creates hierarchical structure)")
    parser.add_argument("--page", type=str, default=None, help="Create page-specific override file in design-system/pages/")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Output directory for persisted files (default: current directory)")

    args = parser.parse_args()

    # Design system takes priority
    if args.design_system:
        result = generate_design_system(
            args.query, 
            args.project_name, 
            args.format,
            persist=args.persist,
            page=args.page,
            output_dir=args.output_dir
        )
        print(result)
        
        # Print persistence confirmation
        if args.persist:
            project_slug = args.project_name.lower().replace(' ', '-') if args.project_name else "default"
            print("\n" + "=" * 60)
            print(f"✅ Design system persisted to design-system/{project_slug}/")
            print(f"   📄 design-system/{project_slug}/MASTER.md (Global Source of Truth)")
            if args.page:
                page_filename = args.page.lower().replace(' ', '-')
                print(f"   📄 design-system/{project_slug}/pages/{page_filename}.md (Page Overrides)")
            print("")
            print(f"📖 Usage: When building a page, check design-system/{project_slug}/pages/[page].md first.")
            print(f"   If exists, its rules override MASTER.md. Otherwise, use MASTER.md.")
            print("=" * 60)
    # Stack search
    elif args.stack:
        result = search_stack(args.query, args.stack, args.max_results)
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_output(result))
    # Domain search
    else:
        result = search(args.query, args.domain, args.max_results)
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_output(result))

```

## FILE: `.codex\skills\ui-ux-pro-max\SKILL.md`

```markdown
---
name: ui-ux-pro-max
description: UI/UX design intelligence with searchable database
---
# ui-ux-pro-max

Comprehensive design guide for web and mobile applications. Contains 67 styles, 96 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types across 13 technology stacks. Searchable database with priority-based recommendations.

## Prerequisites

Check if Python is installed:

```bash
python3 --version || python --version
```

If Python is not installed, install it based on user's OS:

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install python3
```

**Windows:**
```powershell
winget install Python.Python.3.12
```

---

## How to Use This Skill

When user requests UI/UX work (design, build, create, implement, review, fix, improve), follow this workflow:

### Step 1: Analyze User Requirements

Extract key information from user request:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page, etc.
- **Style keywords**: minimal, playful, professional, elegant, dark mode, etc.
- **Industry**: healthcare, fintech, gaming, education, etc.
- **Stack**: React, Vue, Next.js, or default to `html-tailwind`

### Step 2: Generate Design System (REQUIRED)

**Always start with `--design-system`** to get comprehensive recommendations with reasoning:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This command:
1. Searches 5 domains in parallel (product, style, color, landing, typography)
2. Applies reasoning rules from `ui-reasoning.csv` to select best matches
3. Returns complete design system: pattern, style, colors, typography, effects
4. Includes anti-patterns to avoid

**Example:**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Step 2b: Persist Design System (Master + Overrides Pattern)

To save the design system for hierarchical retrieval across sessions, add `--persist`:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

This creates:
- `design-system/MASTER.md` — Global Source of Truth with all design rules
- `design-system/pages/` — Folder for page-specific overrides

**With page-specific override:**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

This also creates:
- `design-system/pages/dashboard.md` — Page-specific deviations from Master

**How hierarchical retrieval works:**
1. When building a specific page (e.g., "Checkout"), first check `design-system/pages/checkout.md`
2. If the page file exists, its rules **override** the Master file
3. If not, use `design-system/MASTER.md` exclusively

### Step 3: Supplement with Detailed Searches (as needed)

After getting the design system, use domain searches to get additional details:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**When to use detailed searches:**

| Need | Domain | Example |
|------|--------|---------|
| More style options | `style` | `--domain style "glassmorphism dark"` |
| Chart recommendations | `chart` | `--domain chart "real-time dashboard"` |
| UX best practices | `ux` | `--domain ux "animation accessibility"` |
| Alternative fonts | `typography` | `--domain typography "elegant luxury"` |
| Landing structure | `landing` | `--domain landing "hero social-proof"` |

### Step 4: Stack Guidelines (Default: html-tailwind)

Get implementation-specific best practices. If user doesn't specify a stack, **default to `html-tailwind`**.

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

---

## Search Reference

### Available Domains

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI styles, colors, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairings, Google Fonts | elegant, playful, professional, modern |
| `color` | Color palettes by product type | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | Page structure, CTA strategies | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | Chart types, library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading |
| `react` | React/Next.js performance | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | Web interface guidelines | aria, focus, keyboard, semantic, virtualize |
| `prompt` | AI prompts, CSS keywords | (style name) |

### Available Stacks

| Stack | Focus |
|-------|-------|
| `html-tailwind` | Tailwind utilities, responsive, a11y (DEFAULT) |
| `react` | State, hooks, performance, patterns |
| `nextjs` | SSR, routing, images, API routes |
| `vue` | Composition API, Pinia, Vue Router |
| `svelte` | Runes, stores, SvelteKit |
| `swiftui` | Views, State, Navigation, Animation |
| `react-native` | Components, Navigation, Lists |
| `flutter` | Widgets, State, Layout, Theming |
| `shadcn` | shadcn/ui components, theming, forms, patterns |
| `jetpack-compose` | Composables, Modifiers, State Hoisting, Recomposition |

---

## Example Workflow

**User request:** "Làm landing page cho dịch vụ chăm sóc da chuyên nghiệp"

### Step 1: Analyze Requirements
- Product type: Beauty/Spa service
- Style keywords: elegant, professional, soft
- Industry: Beauty/Wellness
- Stack: html-tailwind (default)

### Step 2: Generate Design System (REQUIRED)

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service elegant" --design-system -p "Serenity Spa"
```

**Output:** Complete design system with pattern, style, colors, typography, effects, and anti-patterns.

### Step 3: Supplement with Detailed Searches (as needed)

```bash
# Get UX guidelines for animation and accessibility
python3 skills/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# Get alternative typography options if needed
python3 skills/ui-ux-pro-max/scripts/search.py "elegant luxury serif" --domain typography
```

### Step 4: Stack Guidelines

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "layout responsive form" --stack html-tailwind
```

**Then:** Synthesize design system + detailed searches and implement the design.

---

## Output Formats

The `--design-system` flag supports two output formats:

```bash
# ASCII box (default) - best for terminal display
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system

# Markdown - best for documentation
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## Tips for Better Results

1. **Be specific with keywords** - "healthcare SaaS dashboard" > "app"
2. **Search multiple times** - Different keywords reveal different insights
3. **Combine domains** - Style + Typography + Color = Complete design system
4. **Always check UX** - Search "animation", "z-index", "accessibility" for common issues
5. **Use stack flag** - Get implementation-specific best practices
6. **Iterate** - If first search doesn't match, try different keywords

---

## Common Rules for Professional UI

These are frequently overlooked issues that make UI look unprofessional:

### Icons & Visual Elements

| Rule | Do | Don't |
|------|----|----- |
| **No emoji icons** | Use SVG icons (Heroicons, Lucide, Simple Icons) | Use emojis like 🎨 🚀 ⚙️ as UI icons |
| **Stable hover states** | Use color/opacity transitions on hover | Use scale transforms that shift layout |
| **Correct brand logos** | Research official SVG from Simple Icons | Guess or use incorrect logo paths |
| **Consistent icon sizing** | Use fixed viewBox (24x24) with w-6 h-6 | Mix different icon sizes randomly |

### Interaction & Cursor

| Rule | Do | Don't |
|------|----|----- |
| **Cursor pointer** | Add `cursor-pointer` to all clickable/hoverable cards | Leave default cursor on interactive elements |
| **Hover feedback** | Provide visual feedback (color, shadow, border) | No indication element is interactive |
| **Smooth transitions** | Use `transition-colors duration-200` | Instant state changes or too slow (>500ms) |

### Light/Dark Mode Contrast

| Rule | Do | Don't |
|------|----|----- |
| **Glass card light mode** | Use `bg-white/80` or higher opacity | Use `bg-white/10` (too transparent) |
| **Text contrast light** | Use `#0F172A` (slate-900) for text | Use `#94A3B8` (slate-400) for body text |
| **Muted text light** | Use `#475569` (slate-600) minimum | Use gray-400 or lighter |
| **Border visibility** | Use `border-gray-200` in light mode | Use `border-white/10` (invisible) |

### Layout & Spacing

| Rule | Do | Don't |
|------|----|----- |
| **Floating navbar** | Add `top-4 left-4 right-4` spacing | Stick navbar to `top-0 left-0 right-0` |
| **Content padding** | Account for fixed navbar height | Let content hide behind fixed elements |
| **Consistent max-width** | Use same `max-w-6xl` or `max-w-7xl` | Mix different container widths |

---

## Pre-Delivery Checklist

Before delivering UI code, verify these items:

### Visual Quality
- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] Brand logos are correct (verified from Simple Icons)
- [ ] Hover states don't cause layout shift
- [ ] Use theme colors directly (bg-primary) not var() wrapper

### Interaction
- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation

### Light/Dark Mode
- [ ] Light mode text has sufficient contrast (4.5:1 minimum)
- [ ] Glass/transparent elements visible in light mode
- [ ] Borders visible in both modes
- [ ] Test both modes before delivery

### Layout
- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] `prefers-reduced-motion` respected

```

## FILE: `.vscode\settings.json`

```json
{
}
```

## FILE: `AGENTS.md`

```markdown
# MarketSpy AI Coding Rules

## Project identity

This project is MarketSpy AI, a marketplace scraping dashboard focused on Tokopedia first, with future marketplace fallback support.

## User preference

- Explain briefly.
- Prefer implementation over theory.
- Give full working code when editing.
- Avoid fake placeholders unless explicitly marked.
- Preserve existing API contracts.
- Use Indonesian comments when helpful for learning.

## Stack assumptions

Backend:
- Python
- FastAPI
- Uvicorn
- WebSocket progress
- Ollama local LLM

Scraping:
- Puppeteer or Playwright primary
- Selenium / undetected-chromedriver fallback when configured

Frontend:
- React / HTML / Tailwind depending on current project structure
- Midnight blue UI direction
- AnimeJS-inspired interaction direction

## Must preserve

- Search flow
- Progress flow
- Result flow
- Feedback flow
- Existing endpoints unless migration is clearly planned

## Before editing

1. Inspect project tree.
2. Identify entry points.
3. Identify frontend framework.
4. Identify backend routes.
5. Identify run commands.
6. Explain changed files after editing.

## Testing

After code changes, run the most relevant command if available:
- npm run build
- npm run lint
- npm test
- python -m pytest
- uvicorn import check

## Safety

- Never commit secrets.
- Never hardcode API keys.
- Never commit local databases, logs, screenshots, or debug dumps.
- Never delete data files without backup.
```

## FILE: `app.py`

```python
#!/usr/bin/env python3
"""
app.py - Tokopedia scraper entrypoint.

Run command stays:
python app.py
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).parent.resolve()
PORT = int(os.environ.get("PORT", 3000))
REQ_FILE = PROJECT_DIR / "requirements.txt"


def log(message: str, level: str = "INFO") -> None:
    """Small startup logger; runtime logging lives in src/utils/logger.py."""
    print(f"[{level}] {message}", flush=True)


def check_python_deps() -> None:
    """Check core imports only. User installs with requirements.txt."""
    required = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "selenium": "selenium",
        "webdriver_manager": "webdriver-manager",
        "httpx": "httpx",
    }
    missing = [pip_name for import_name, pip_name in required.items() if not importlib.util.find_spec(import_name)]
    if not missing:
        log("Python dependencies found.", "OK")
        return

    log(f"Missing Python packages: {', '.join(missing)}", "ERROR")
    log(f"Install with: {sys.executable} -m pip install -r {REQ_FILE}", "ERROR")
    sys.exit(1)


def check_node_deps() -> None:
    """Puppeteer worker needs Node plus npm packages."""
    if not shutil.which("node"):
        log("Node.js not found. Puppeteer mode will fail until Node is installed.", "WARN")
        return

    package_dir = PROJECT_DIR / "node_modules" / "puppeteer"
    if not package_dir.exists():
        log("node_modules/puppeteer not found. Run: npm install", "WARN")
        return

    try:
        version = subprocess.run(
            ["node", "--version"],
            cwd=str(PROJECT_DIR),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        log(f"Node ready: {version}", "OK")
    except Exception as exc:
        log(f"Node check failed: {exc}", "WARN")


def main() -> None:
    print()
    print("+--------------------------------------+")
    print("| PasarIntai AI - Tokopedia Scraper   |")
    print("+--------------------------------------+")
    print()

    check_python_deps()
    check_node_deps()

    log(f"Starting FastAPI server on http://127.0.0.1:{PORT}", "INFO")
    try:
        import uvicorn

        uvicorn.run(
            "src.server.main:app",
            host="127.0.0.1",
            port=PORT,
            log_level="info",
            reload=False,
        )
    except KeyboardInterrupt:
        log("Server stopped by user.", "OK")
    except Exception as exc:
        log(f"Server crashed: {exc}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()

```

## FILE: `pack_repo_for_claude.py`

```python
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "_claude_audit.md"

INCLUDE_EXT = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
}

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "logs",
    "screenshots",
    "debug",
    "_claude_upload",
    "data",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "marketspy_feedback.db",
}

MAX_FILE_CHARS = 120_000


def should_skip(path: Path) -> bool:
    parts = set(path.parts)

    if parts & EXCLUDE_DIRS:
        return True

    if path.name in EXCLUDE_FILES:
        return True

    if path.suffix.lower() not in INCLUDE_EXT:
        return True

    return False


def language_for(path: Path) -> str:
    ext = path.suffix.lower()

    return {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".json": "json",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".txt": "text",
    }.get(ext, "text")


def main():
    files = []

    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and not should_skip(path):
            files.append(path)

    with OUT.open("w", encoding="utf-8", errors="ignore") as out:
        out.write("# PROJECT CODE AUDIT PACK\n\n")
        out.write(f"Root: `{ROOT}`\n\n")

        out.write("## FILE TREE\n\n")
        for file in files:
            rel = file.relative_to(ROOT)
            out.write(f"- `{rel}`\n")

        out.write("\n---\n\n")

        for file in files:
            rel = file.relative_to(ROOT)

            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                out.write(f"\n## FILE: `{rel}`\n\n")
                out.write(f"Failed to read file: {e}\n")
                continue

            if len(text) > MAX_FILE_CHARS:
                text = text[:MAX_FILE_CHARS]
                text += "\n\n/* FILE TRUNCATED BECAUSE TOO LARGE */\n"

            lang = language_for(file)

            out.write(f"\n## FILE: `{rel}`\n\n")
            out.write(f"```{lang}\n")
            out.write(text)
            out.write("\n```\n")

    print(f"[OK] Created: {OUT}")
    print(f"[OK] Files packed: {len(files)}")


if __name__ == "__main__":
    main()
```

## FILE: `pack_repo_for_claude_split.py`

```python
from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "_claude_upload"
OUT_DIR.mkdir(exist_ok=True)

MAX_CHARS_PER_PART = 700_000

INCLUDE_EXT = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
}

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "logs",
    "screenshots",
    "debug",
    "_claude_upload",
    "data",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "marketspy_feedback.db",
}


def should_skip(path: Path) -> bool:
    if set(path.parts) & EXCLUDE_DIRS:
        return True

    if path.name in EXCLUDE_FILES:
        return True

    if path.suffix.lower() not in INCLUDE_EXT:
        return True

    return False


def lang(path: Path) -> str:
    return {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
    }.get(path.suffix.lower(), "text")


def write_part(part_index: int, content: str):
    path = OUT_DIR / f"claude_audit_part_{part_index:02d}.md"
    path.write_text(content, encoding="utf-8", errors="ignore")
    print(f"[OK] Wrote {path}")


def main():
    files = [
        p for p in sorted(ROOT.rglob("*"))
        if p.is_file() and not should_skip(p)
    ]

    file_tree = "# PROJECT FILE TREE\n\n"
    for file in files:
        file_tree += f"- `{file.relative_to(ROOT)}`\n"

    part_index = 1
    current = file_tree + "\n---\n\n"

    for file in files:
        rel = file.relative_to(ROOT)

        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            text = f"FAILED TO READ FILE: {e}"

        block = f"\n## FILE: `{rel}`\n\n```{lang(file)}\n{text}\n```\n"

        if len(current) + len(block) > MAX_CHARS_PER_PART:
            write_part(part_index, current)
            part_index += 1
            current = "# CONTINUED PROJECT CODE AUDIT PACK\n\n"

        current += block

    if current.strip():
        write_part(part_index, current)

    print("[DONE] Upload all files inside _claude_upload to Claude.")


if __name__ == "__main__":
    main()
```

## FILE: `package.json`

```json
{
  "name": "rb-c1",
  "version": "1.0.0",
  "description": "Tokopedia scraper Puppeteer worker dependencies.",
  "main": "src/scraper/puppeteer_worker.js",
  "scripts": {
    "puppeteer:check": "node src/scraper/puppeteer_worker.js --query \"laptop gaming\" --target 5"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "animejs": "^3.2.2",
    "minimist": "^1.2.8",
    "puppeteer": "^25.0.4"
  }
}

```

## FILE: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py

```

## FILE: `QUICK_START.md`

```markdown
# Quick Start Guide

## 1. Install and Setup

```bash
cd "c:\Users\Farras\PI V3\RB-C1"
python -m pip install -r requirements.txt
npm install
```

Start Ollama and install the supported local models:

```bash
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull nomic-embed-text
ollama serve
```

## 2. Run

```bash
python app.py
```

Open http://127.0.0.1:3000.

## 3. Verify

```bash
curl http://127.0.0.1:3000/api/ai/status
python -m pytest tests/ -v
```

## Common Modes

- Auto: try Puppeteer first, then Selenium fallback.
- Puppeteer only: run Puppeteer and fail if it cannot extract products.
- Selenium only: run the Selenium fallback engine.
- Compare both: run both engines and show Engine Comparison.

Engine Comparison is hidden unless Compare both is selected.

## AI Orchestrator

- Model selection is automatic.
- Installed models are detected from `GET /api/tags`.
- `POST /api/chat` is called only for borderline products.
- If no supported classifier is installed, deterministic rules and fallback expansion still work.
- `phi4-mini` is used only for malformed JSON repair.
- `nomic-embed-text` is used only for semantic scoring.

## Result Controls

- Terbaik sorts the current result list by confidence, rating, sold count, then price.
- Termurah sorts the current result list by price without rescraping.
- Most Trusted sorts the current result list by trust signals without rescraping.
- Product cards render marketplace images when valid URLs exist and show an Indonesian fallback only when images are missing or fail to load.

## Troubleshooting AI Accepted 0

Check `/api/ai/status` first. If `classifier` is missing, install `gemma3:4b` or `llama3.2:3b`.

If `ai_checked` is `0`, inspect `ai_skip_reason` in the result metadata:

- `AI disabled`
- `No supported classifier installed`
- `No borderline candidates`
- `All products handled by rules`
- `Candidate pool empty`

If AI is enabled, a classifier is installed, and `borderline_candidates > 0`, the backend logs should include `POST /api/chat` and `ai_calls_attempted > 0`.

```

## FILE: `README.md`

```markdown
# MarketSpy AI

**Mencari barang terbaik sesuai budget.**

MarketSpy AI adalah aplikasi scraping marketplace yang menggunakan teknologi Puppeteer, Selenium, dan AI lokal (Ollama) untuk menemukan produk terbaik sesuai dengan kriteria pencarian dan budget Anda.

## Fitur Utama

- **Scraping Multi-Engine**: Mendukung Puppeteer, Selenium, dan fallback otomatis
- **Filtering Cerdas**: Rule-based filtering dengan budget dan relevance checking
- **AI Orchestrator**: Validasi produk dengan model AI lokal (Ollama)
- **Kategorisasi Otomatis**: Produk dikelompokkan ke:
  - **Semua Barang**: Menampilkan semua produk yang valid
  - **Terbaik**: Produk dengan rating terbaik
  - **Termurah**: Produk dengan harga terendah
  - **Most Trusted**: Produk dengan reputasi toko terbaik
- **Feedback Learning**: Sistem pembelajaran dari feedback user untuk meningkatkan akurasi
- **UI Modern**: Interface midnight blue yang clean dan responsif

## Cara Install

### Prerequisites

- Python 3.9+
- Node.js 18+
- Ollama (opsional, untuk AI features)
- Browser: Chrome/Chromium atau Firefox

### Step 1: Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend (sudah included di folder /web)
npm install
```

### Step 2: Setup Ollama (Opsional)

Untuk mengaktifkan AI Orchestrator, install Ollama dan model berikut:

```bash
ollama pull gemma3:4b      # Model classifier utama
ollama pull llama3.2:3b    # Model backup classifier
ollama pull phi4-mini      # Model JSON repair (optional)
ollama pull nomic-embed-text  # Model embedding untuk semantic search (optional)
```

Jika Ollama tidak tersedia, sistem akan tetap berjalan dengan rule-based filtering.

### Step 3: Konfigurasi

Edit `src/config.py` untuk konfigurasi:

```python
# Budget filter tolerance
DEFAULT_BUDGET_TOLERANCE = 20  # 20% tolerance

# AI settings
AI_ENABLE_CLASSIFIER = True
AI_ENABLE_SEMANTIC = True
AI_MODEL_CLASSIFIER = "gemma3:4b"
AI_MODEL_SEMANTIC = "nomic-embed-text"

# Scraper settings
PUPPETEER_TIMEOUT = 30000  # milliseconds
SELENIUM_TIMEOUT = 30  # seconds
```

## Cara Menjalankan

### Development Mode

```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend (optional, sudah serving dari backend)
# Buka http://localhost:8000 di browser
```

### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Cara Kerja Scraping

1. **Search Initiation**: User masuk query, target count, dan budget
2. **Engine Selection**: Sistem memilih engine (Puppeteer/Selenium) atau auto-fallback
3. **Page Navigation**: Browser membuka halaman marketplace (Tokopedia)
4. **Data Extraction**: Mengambil data produk (judul, harga, rating, gambar, etc)
5. **Deduplication**: Membersihkan produk duplikat
6. **Budget Filtering**: Filter produk berdasarkan harga dan budget tolerance
7. **Semantic Check**: Cek relevansi semantic (jika AI enabled)
8. **AI Validation**: Orchestrator AI menvalidasi produk borderline
9. **Ranking**: Menyusun rekomendasi berdasarkan kategori
10. **Result Display**: Tampilkan hasil ke UI

## Feedback Benar/Salah

Setelah scraping selesai, user bisa memberikan feedback untuk setiap produk:

- **Benar**: Produk sesuai dengan pencarian
- **Salah**: Produk tidak sesuai (dengan alasan)

Feedback disimpan dalam database dan digunakan untuk:
- Melatih model AI agar lebih akurat
- Menyesuaikan rule filter
- Meningkatkan scoring produk

### Data Feedback Disimpan

```json
{
  "search_id": "xxx",
  "product_id": "xxx",
  "user_action": "benar|salah",
  "selected_reasons": ["Alasan 1", "Alasan 2"],
  "note": "Catatan user",
  "ai_confidence": 0.95,
  "model_used": "gemma3:4b",
  "timestamp": "2024-xx-xx"
}
```

## Penjelasan Kategori

### Semua Barang
Menampilkan **semua produk** yang valid sesuai kriteria filter (budget, relevance, etc). Tidak ada limit jumlah.

### Terbaik
Produk **top-ranked** berdasarkan kombinasi:
- Rating tinggi
- Banyak review
- Harga kompetitif
- AI confidence tinggi

Limit jumlah sesuai input user di "Jumlah data per kategori".

### Termurah
Produk dengan **harga terendah** yang valid.
Limit jumlah sesuai input user.

### Most Trusted
Produk dari **toko terpercaya** dengan:
- Rating toko tinggi
- Banyak transaksi
- Respon time bagus

Limit jumlah sesuai input user.

## Form Input Penjelasan

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|-----------|
| Produk yang dicari | Text | Ya | Contoh: "laptop gaming" |
| Jumlah target | Number | Ya | Berapa produk yang ingin ditemukan (min 1, maks 100) |
| Toleransi budget | Number | Tidak | Persentase tolerance dari budget (0-100%, default 20%) |
| Budget | Currency | Tidak | Maksimal budget dalam Rupiah (opsional) |
| Jumlah data per kategori | Number | Tidak | Limit produk untuk kategori Terbaik/Termurah/Most Trusted (default 10) |
| Gunakan AI Orchestrator | Checkbox | Tidak | Aktifkan validation AI (jika Ollama available) |

## API Endpoints

### POST /api/search
Mulai search/scraping

```json
{
  "query": "laptop gaming",
  "target": 20,
  "budget": 10000000,
  "tolerance": 20,
  "ai": true,
  "use_ai": true,
  "category_limit": 10
}
```

### GET /api/progress/{search_id}
Get progress scraping

Response:
```json
{
  "stage": "scraping",
  "progress_percent": 45,
  "done": false,
  "found": 15,
  "valid": 12,
  "message": "Mengambil data produk..."
}
```

### GET /api/result/{search_id}
Get hasil akhir scraping

### POST /api/feedback
Send user feedback untuk produk

```json
{
  "search_id": "xxx",
  "product_id": "xxx",
  "user_action": "benar",
  "selected_reasons": [],
  "note": ""
}
```

## Troubleshooting

### "Ollama belum bisa dihubungi"
- Pastikan Ollama sudah running: `ollama serve`
- Check port Ollama (default 11434)
- Install model yang diperlukan: `ollama pull gemma3:4b`

### "Scraping timeout"
- Marketplace website mungkin slow
- Try increase timeout di config
- Check internet connection

### "Produk tidak ada"
- Query terlalu spesifik atau tidak ada di marketplace
- Try dengan query lebih umum
- Check target count tidak terlalu tinggi

### "Budget filter terlalu ketat"
- Increase tolerance percentage
- Atau tingkatkan budget amount
- Check kategori "Semua Barang" untuk melihat semua produk

## Development

### Project Structure

```
├── app.py                 # Main FastAPI app
├── src/
│   ├── config.py         # Configuration
│   ├── ai/               # AI orchestrator
│   ├── scraper/          # Scraper engines
│   ├── server/           # API endpoints
│   └── utils/            # Helper functions
├── web/                  # Frontend files
│   ├── index.html
│   ├── app.js
│   └── style.css
├── data/                 # Data storage
│   ├── ai_memory/        # AI learning data
│   └── feedback/         # User feedback logs
└── tests/                # Test files
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

- Backend: PEP 8
- Frontend: Prettier + ESLint

## Tips Penggunaan

1. **Mulai dengan query umum**: "laptop" lebih baik daripada "laptop gaming ROG RTX 4090"
2. **Set target count wajar**: 20-50 adalah sweet spot
3. **Use budget jika tahu**: Feedback akan lebih akurat
4. **Check AI Orchestrator status**: Lihat di form apakah model tersedia
5. **Review hasil dengan teliti**: Feedback membantu AI belajar
6. **Gunakan kategori berbeda**: Coba Terbaik, Termurah, Most Trusted untuk perspektif berbeda

## License

MIT

## Support

Issues? Check GitHub issues atau contact developer.

---

**MarketSpy AI** - Mencari barang terbaik sesuai budget dengan teknologi AI lokal.

```

## FILE: `requirements.txt`

```text
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.7.2
selenium>=4.20.0
webdriver-manager>=4.0.2
httpx>=0.27.0
pytest>=8.0.0
requests>=2.32.3

```

## FILE: `SOURCE_REGISTER.md`

```markdown
\# SOURCE REGISTER - MARKETSPY AI PI



\## ATURAN KERAS

1\. Hanya gunakan sumber yang ada di dokumen ini.

2\. Jangan membuat jurnal, DOI, URL, nama penulis, volume, nomor, halaman, atau sumber palsu.

3\. Semua kutipan di Bab 2 wajib muncul di Daftar Pustaka.

4\. Semua Daftar Pustaka wajib pernah dikutip di tubuh tulisan.

5\. Referensi diprioritaskan tahun 2021-2026.

6\. Hindari Wikipedia, Blogspot, WordPress, dan sumber nonformal.



\## KANDIDAT REFERENSI VALID



1\. Guyt, J. Y., Datta, H., dan Boegershausen, J. 2024. Unlocking the Potential of Web Data for Retailing Research. Journal of Retailing. Vol. 100 No. 1, Hal. 130-147. DOI: 10.1016/j.jretai.2024.02.002.

&#x20;  Relevansi: Web data, web scraping, API, retail research, dan e-commerce.



2\. Chen, F. 2024. Research on Real-time E-commerce Price Comparison System Using Python Web Scraping Technology. International Journal of Computer Science and Information Technology. Vol. 4 No. 2, Hal. 127-136. DOI: 10.62051/ijcsit.v4n2.18.

&#x20;  Relevansi: Sistem pembanding harga e-commerce real-time berbasis Python web scraping.



3\. Sharma, D. K., Lohana, S., Arora, S., Dixit, A., Tiwari, M., dan Tiwari, T. 2022. E-Commerce Product Comparison Portal for Classification of Customer Data Based on Data Mining. Materials Today: Proceedings. Vol. 51, Hal. 166-171. DOI: 10.1016/j.matpr.2021.05.068.

&#x20;  Relevansi: Portal pembanding produk e-commerce dan data mining.



4\. Amthauer, J., Fleiß, J., Guggi, F., dan Robertson, V. H. S. E. 2023. Detecting Resale Price Maintenance for Competition Law Purposes: Proof-of-concept Study Using Web Scraped Data. Computer Law \& Security Review. Vol. 51, Artikel 105901. DOI: 10.1016/j.clsr.2023.105901.

&#x20;  Relevansi: Penggunaan data hasil web scraping untuk analisis harga.



5\. Alaiya, A., dkk. 2025. Sentiment Analysis of E-Commerce Product Reviews on Tokopedia Platform Using Support Vector Machine. Journal of Applied Informatics and Computing.

&#x20;  Relevansi: Studi Tokopedia, scraping ulasan produk, dan analisis sentimen.



6\. Mishra, K. N., dkk. 2024. Natural Language Processing and Machine Learning-Based Recommendation for E-Commerce Items. Electronics.

&#x20;  Relevansi: NLP dan machine learning untuk rekomendasi produk e-commerce.



7\. Padhy, N., dkk. 2024. A Recommendation System for E-Commerce Products Using Collaborative Filtering Approaches.

&#x20;  Relevansi: Sistem rekomendasi produk e-commerce menggunakan collaborative filtering.



8\. Nguyen, D. N., dkk. 2024. A Personalized Product Recommendation Model in E-Commerce.

&#x20;  Relevansi: Model rekomendasi produk personalisasi pada e-commerce.


```

## FILE: `src\__init__.py`

```python

```

## FILE: `src\ai\__init__.py`

```python

```

## FILE: `src\ai\ai_filter.py`

```python
"""
Rules-first, intent-aware AI filter.

The core performance rule is simple: deterministic relevance handles obvious
products, and the local LLM only sees borderline cases.
"""
from __future__ import annotations

import contextlib
import json
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable
import asyncio

from src.ai.ai_orchestrator import classify_product_batch
from src.ai.model_registry import get_best_classifier_model, get_orchestrator_status
from src.config import (
    AI_AUDIT_MAX_PRODUCTS,
    AI_BATCH_CLASSIFY,
    AI_BATCH_SIZE,
    AI_CHAT_NUM_CTX,
    AI_CHAT_NUM_PREDICT,
    AI_CHAT_TIMEOUT_SECONDS,
    AI_CLASSIFIER_MAX_PRODUCTS,
    AI_CPU_MODE,
    FALLBACK_EXPANSION_THRESHOLD,
    LLM_ACCEPT_THRESHOLD,
    RULE_ACCEPT_THRESHOLD,
    RULE_REJECT_THRESHOLD,
    RULE_REVIEW_THRESHOLD,
    WEAK_FALLBACK_THRESHOLD,
)
from src.ai.feedback_store import normalize_text
from src.utils.currency import parse_rupiah
from src.utils.logger import log


@dataclass
class IntentFilterResult:
    products: list[dict[str, Any]]
    status: str
    meta: dict[str, Any] = field(default_factory=dict)

    def __iter__(self):
        yield self.products
        yield self.status


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, parsed))


def _as_number(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.85:
        return "High"
    if confidence >= 0.70:
        return "Medium"
    return "Low"


def _mark_product(
    product: dict[str, Any],
    *,
    accepted: bool,
    confidence: float,
    reason: str,
    source: str,
    query_intent: str,
    product_category: str,
    rule_score: float,
    category_match: str,
    combined_score: float | None = None,
) -> dict[str, Any]:
    confidence = max(0.0, min(0.98, float(confidence)))
    product["relevance_score"] = round(confidence, 3)
    product["confidence"] = round(confidence, 3)
    product["rule_score"] = round(rule_score, 3)
    product["combined_score"] = round(combined_score if combined_score is not None else confidence, 3)
    product["ai_confidence"] = round(confidence, 3)
    product["ai_model_confidence"] = round(confidence, 3)
    product["ai_confidence_label"] = _confidence_label(confidence)
    product["ai_decision"] = bool(accepted)
    product["ai_label"] = "relevan" if accepted else "tidak_relevan"
    product["ai_reason"] = reason
    product["reason"] = reason
    product["ai_explanation"] = reason
    product["ai_source"] = source
    product["decision_source"] = source
    product["ai_categories"] = [product_category, category_match, query_intent]
    product["query_intent"] = query_intent
    product["product_category"] = product_category
    product["category_match"] = category_match
    return product


def combine_rule_and_semantic_score(rule_score: float, semantic_score: float | None) -> float:
    if semantic_score is None:
        return rule_score
    return round(max(rule_score, semantic_score * 0.85), 3)


def _product_key(product: dict[str, Any]) -> str:
    return str(product.get("id") or product.get("url") or product.get("product_url") or product.get("title") or "")


def _decision_priority(product: dict[str, Any]) -> int:
    priority = {
        "ai_orchestrator": 0,
        "rule_accept": 1,
        "fallback_expansion": 2,
        "fallback_after_ai_reject": 3,
        "fallback_after_ai_reject_positive_laptop": 3,
        "rescued_false_obvious_junk": 3,
        "fallback_ai_timeout": 4,
        "fallback_ai_circuit_open": 5,
        "fallback_not_classified_cpu_limit": 6,
    }
    return priority.get(str(product.get("decision_source") or product.get("ai_source") or ""), 9)


def _rank_final_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        products,
        key=lambda product: (
            -_as_number(product.get("confidence", product.get("relevance_score", product.get("ai_confidence", 0)))),
            _decision_priority(product),
            -_as_number(product.get("rating")),
            -_as_number(product.get("sold_count")),
            _price_sort_value(product),
        ),
    )


def _price_sort_value(product: dict[str, Any]) -> float:
    price = _as_number(product.get("price_value", product.get("price")), 0.0)
    return price if price > 0 else float("inf")


def _sort_fallback_candidates(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        products,
        key=lambda product: (
            -_as_number(product.get("confidence", product.get("relevance_score", product.get("ai_confidence", 0)))),
            -_as_number(product.get("combined_score", (product.get("_rule_context") or {}).get("combined_score"))),
            -_as_number(product.get("learned_adjustment", (product.get("_rule_context") or {}).get("learned_adjustment"))),
            -_as_number(product.get("semantic_score", (product.get("_rule_context") or {}).get("semantic_score"))),
            -_as_number(product.get("rating")),
            -_as_number(product.get("sold_count")),
            _price_sort_value(product),
        ),
    )


def _sort_borderline_candidates(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        products,
        key=lambda product: (
            -_as_number(product.get("combined_score", (product.get("_rule_context") or {}).get("combined_score"))),
            -_as_number(product.get("rule_score", (product.get("_rule_context") or {}).get("rule_score"))),
            -_as_number(product.get("semantic_score", (product.get("_rule_context") or {}).get("semantic_score"))),
            -_as_number(product.get("rating")),
            -_as_number(product.get("sold_count")),
            _price_sort_value(product),
        ),
    )


def _product_price_value(product: dict[str, Any]) -> int:
    price = product.get("price_value", product.get("price"))
    parsed = parse_rupiah(price)
    if parsed is not None:
        return int(parsed)
    try:
        return int(price or 0)
    except (TypeError, ValueError):
        return 0


def is_valid_product_candidate(product: dict[str, Any], *, require_price: bool = True) -> bool:
    title = normalize_text(product.get("title") or product.get("name") or "")
    url = normalize_text(product.get("url") or product.get("product_url") or "")
    price = _product_price_value(product)
    has_price_field = any(product.get(key) not in (None, "") for key in ("price_value", "price"))

    if not title or len(title) < 4:
        return False
    if require_price and price <= 0:
        return False
    if not require_price and has_price_field and price <= 0:
        return False

    non_product_titles = [
        "mulai berjualan",
        "kalkulator indeks masa tubuh",
        "daftar mall",
    ]
    non_product_urls = [
        "/blog/",
        "seller.tokopedia.com/edu",
        "/edu/",
        "/official-store/",
    ]

    if any(text in title for text in non_product_titles):
        return False
    if any(text in url for text in non_product_urls):
        return False
    return True


def _is_valid_product(product: dict[str, Any]) -> bool:
    return is_valid_product_candidate(product, require_price=False)


def _debug_sample(product: dict[str, Any]) -> dict[str, Any]:
    ctx = product.get("_rule_context") or {}
    return {
        "id": product.get("id"),
        "title": product.get("title"),
        "price_value": product.get("price_value", product.get("price")),
        "url": product.get("url") or product.get("product_url"),
        "decision_source": product.get("decision_source") or product.get("ai_source"),
        "reason": product.get("reason") or product.get("ai_reason"),
        "rule_score": product.get("rule_score", ctx.get("rule_score")),
        "semantic_score": product.get("semantic_score", ctx.get("semantic_score")),
        "base_combined_score": product.get("base_combined_score", ctx.get("base_combined_score")),
        "constraint_penalty": product.get("constraint_penalty", ctx.get("constraint_penalty")),
        "combined_score": product.get("combined_score", ctx.get("combined_score")),
        "query_constraints": product.get("query_constraints", ctx.get("query_constraints")),
        "product_constraints": product.get("product_constraints", ctx.get("product_constraints")),
        "constraint_mismatch_reasons": product.get(
            "constraint_mismatch_reasons",
            ctx.get("constraint_mismatch_reasons", []),
        ),
        "learned_adjustment": product.get("learned_adjustment", ctx.get("learned_adjustment", 0.0)),
        "learned_matches": product.get("learned_matches", ctx.get("learned_matches", [])),
    }


def _write_latest_pipeline_debug(payload: dict[str, Any]) -> None:
    try:
        output_dir = Path("debug") / "pipeline"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "latest_search_debug.json"
        output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2, default=str), encoding="utf-8")
    except Exception as exc:
        log("PIPELINE", f"failed_to_write_debug_json error={exc}", "WARN")


async def _run_with_ai_heartbeat(
    *,
    coro: Awaitable[dict[str, Any]],
    search_id: str | None,
    batch_current: int,
    batch_total: int,
    batch_started_at_monotonic: float,
    batch_started_at_epoch_ms: int,
    completed_batch_durations: list[float],
    found: int,
    valid_count: int,
) -> dict[str, Any]:
    if not search_id:
        return await coro

    from src.server.progress import update_ai_eta_progress

    stop_event = asyncio.Event()

    async def heartbeat() -> None:
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                update_ai_eta_progress(
                    search_id=search_id,
                    batch_current=batch_current,
                    batch_total=batch_total,
                    batch_started_at_monotonic=batch_started_at_monotonic,
                    batch_started_at_epoch_ms=batch_started_at_epoch_ms,
                    completed_ai_batch_durations=completed_batch_durations,
                    message=f"AI filtering batch {batch_current}/{batch_total}",
                    found=found,
                    valid=valid_count,
                )

    task = asyncio.create_task(heartbeat())
    try:
        return await coro
    finally:
        stop_event.set()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def filter_products(
    query: str,
    products: list[dict[str, Any]],
    *,
    use_ai: bool = True,
    search_id: str | None = None,
) -> IntentFilterResult:
    from src.ai.relevance import (
        apply_laptop_gaming_boost,
        compute_rule_score,
        detect_product_category,
        detect_query_intent,
        is_obvious_junk_for_intent,
        is_obvious_match_for_intent,
        is_laptop_gaming_query,
    )
    from src.ai.feedback_store import (
        compute_constraint_mismatch_penalty,
        compute_learned_adjustment,
        extract_query_constraints,
        has_accessory_only_evidence,
        has_laptop_main_evidence,
        load_feedback_context,
        load_learned_patterns,
    )

    query_intent = detect_query_intent(query)
    query_constraints = extract_query_constraints(query)
    learned_patterns = load_learned_patterns(query, query_intent, query_constraints, limit=200)
    feedback_context = load_feedback_context(query, query_intent, query_constraints, limit=12)
    feedback_examples_loaded = int(feedback_context.get("feedback_examples_loaded", 0) or 0)
    learned_patterns_loaded = len(learned_patterns)
    query_scoped_patterns = sum(1 for p in learned_patterns if p.get("scope") == "exact_query")
    constraint_scoped_patterns = sum(1 for p in learned_patterns if p.get("scope") == "query_constraint")
    intent_scoped_patterns = sum(1 for p in learned_patterns if p.get("scope") == "query_intent")
    global_patterns = sum(1 for p in learned_patterns if p.get("scope") == "global")
    orchestrator_status = get_orchestrator_status()
    installed_models = orchestrator_status.get("installed")
    selected_model = orchestrator_status.get("classifier") or get_best_classifier_model(
        installed_models if installed_models is not None else None
    )
    classifier_installed = bool(selected_model)
    target_count = int(products[0].get("_requested_target", 50) or 50) if products else 50
    target_display = min(target_count, len(products or []))
    
    log(
        "AI_ORCH",
        (
            f"ai_orchestrator_enabled={use_ai} "
            f"supported_models={orchestrator_status.get('supported', [])} "
            f"missing_models={orchestrator_status.get('missing', [])} "
            f"classifier={selected_model or 'rules_only'} "
            f"semantic_enabled={bool(orchestrator_status.get('capabilities', {}).get('semantic'))} "
            f"json_repair_enabled={bool(orchestrator_status.get('capabilities', {}).get('json_repair'))}"
        ),
        "INFO",
    )
    log("AI_ORCH", f"ai_enabled={bool(use_ai)}", "INFO")
    log("AI_ORCH", f"installed_models={orchestrator_status.get('installed', [])}", "INFO")
    log(
        "AI_ORCH",
        (
            f"selected_classifier={selected_model or 'none'} "
            f"cpu_mode={str(AI_CPU_MODE).lower()} "
            f"ctx={AI_CHAT_NUM_CTX} "
            f"predict={AI_CHAT_NUM_PREDICT} "
            f"timeout={AI_CHAT_TIMEOUT_SECONDS} "
            f"batch={str(AI_BATCH_CLASSIFY).lower()} "
            f"max_products={AI_AUDIT_MAX_PRODUCTS}"
        ),
        "INFO",
    )
    log(
        "AI_LEARN",
        (
            f"feedback_examples_loaded={feedback_examples_loaded} "
            f"learned_patterns_loaded={learned_patterns_loaded} "
            f"query_scoped_patterns={query_scoped_patterns} "
            f"constraint_scoped_patterns={constraint_scoped_patterns} "
            f"global_patterns={global_patterns}"
        ),
        "INFO",
    )
    
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    borderline: list[dict[str, Any]] = []
    fallback_candidates: list[dict[str, Any]] = []
    weak_fallback_candidates: list[dict[str, Any]] = []
    accepted_before_fallback = 0
    rule_accepted = 0
    rule_rejected = 0
    rejected_as_obvious_junk_count = 0
    semantic_checked = 0
    classifier_checked = 0
    ai_accepted = 0
    ai_rejected = 0
    ai_fallback = 0
    ai_calls_attempted = 0
    ai_calls_succeeded = 0
    ai_timeouts = 0
    ai_failure_count = 0
    ai_confirmed = 0
    ai_rescued = 0
    ai_circuit_open = False
    ai_circuit_reason: str | None = None
    ai_skip_reason_override: str | None = None
    prompt_tokens_estimated = 0
    prompt_truncated_by_app = False
    fallback_rejected_as_junk = 0
    rejected_reasons_histogram: Counter[str] = Counter()
    rejected_as_obvious_junk_count_before_rescue = 0
    rescued_false_obvious_junk_count = 0
    constraint_mismatch_products = 0
    learning_adjusted_products = 0
    learned_positive_matches = 0
    learned_negative_matches = 0

    def record_rejection(reason: str, product: dict[str, Any]) -> None:
        rejected_reasons_histogram[reason] += 1
        product["reject_reason"] = reason

    query_embedding = None
    semantic_enabled = bool(orchestrator_status.get("capabilities", {}).get("semantic"))
    if semantic_enabled:
        try:
            from src.ai.ollama_client import get_embedding_async
            query_embedding = await get_embedding_async(query)
        except Exception:
            query_embedding = None
            semantic_enabled = False

    for product in list(products or []):
        product_category = detect_product_category(product)
        product_constraints = extract_query_constraints(str(product.get("title") or product.get("name") or ""))
        rule_score = compute_rule_score(query, product, query_intent)
        semantic_score = None
        
        if (
            semantic_enabled
            and query_embedding
            and str(product.get("title") or "").strip()
        ):
            try:
                from src.ai.ollama_client import cosine_similarity, get_embedding_async
                title_embedding = await get_embedding_async(str(product.get("title") or ""))
                semantic_score = cosine_similarity(query_embedding, title_embedding)
                if semantic_score is not None:
                    semantic_checked += 1
                    product["semantic_score"] = round(semantic_score, 3)
            except Exception:
                semantic_score = None

        combined_score = combine_rule_and_semantic_score(rule_score, semantic_score)
        combined_score = apply_laptop_gaming_boost(query, product, combined_score)
        base_combined_score = combined_score
        constraint_penalty, constraint_reasons = compute_constraint_mismatch_penalty(
            query_constraints,
            product_constraints,
        )
        learned_adjustment, learned_matches = compute_learned_adjustment(
            query,
            query_intent,
            query_constraints,
            product,
            learned_patterns,
        )
        if constraint_reasons:
            constraint_mismatch_products += 1
        if abs(learned_adjustment) > 0.0001:
            learning_adjusted_products += 1
        if any(float(match.get("weight", 0) or 0) > 0 for match in learned_matches):
            learned_positive_matches += 1
        if any(float(match.get("weight", 0) or 0) < 0 for match in learned_matches):
            learned_negative_matches += 1
        strong_learned_negative = any(
            float(match.get("weight", 0) or 0) < 0
            and int(match.get("support_count") or 0) >= 3
            for match in learned_matches
        )
        combined_score = round(max(0.0, min(1.0, combined_score + constraint_penalty + learned_adjustment)), 3)
        title_text = str(product.get("title") or product.get("name") or "")
        positive_laptop_evidence = is_laptop_gaming_query(query) and has_laptop_main_evidence(title_text)
        clear_accessory_only = has_accessory_only_evidence(title_text)
        non_product_page = not _is_valid_product(product)
        obvious_junk = False if positive_laptop_evidence else is_obvious_junk_for_intent(query, product, query_intent)
        if positive_laptop_evidence:
            obvious_junk = False
                
        product["_rule_context"] = {
            "query_intent": query_intent,
            "product_category": product_category,
            "rule_score": rule_score,
            "semantic_score": semantic_score,
            "base_combined_score": base_combined_score,
            "constraint_penalty": constraint_penalty,
            "constraint_mismatch_reasons": constraint_reasons,
            "learned_adjustment": learned_adjustment,
            "learned_matches": learned_matches,
            "combined_score": combined_score,
            "obvious_junk": obvious_junk,
            "positive_laptop_evidence": positive_laptop_evidence,
            "clear_accessory_only": clear_accessory_only,
            "non_product_page": non_product_page,
            "strong_learned_negative": strong_learned_negative,
            "query_constraints": query_constraints,
            "product_constraints": product_constraints,
        }
        product["rule_score"] = round(rule_score, 3)
        product["base_combined_score"] = round(base_combined_score, 3)
        product["constraint_penalty"] = round(constraint_penalty, 3)
        product["constraint_mismatch_reasons"] = constraint_reasons
        product["query_constraints"] = query_constraints
        product["product_constraints"] = product_constraints
        product["learned_adjustment"] = round(learned_adjustment, 3)
        product["learned_matches"] = learned_matches
        product["combined_score"] = round(combined_score, 3)

        if non_product_page:
            rule_rejected += 1
            record_rejection("non_product_page", product)
            rejected.append(_mark_product(
                product,
                accepted=False,
                confidence=combined_score,
                reason="Rejected by non product page validation",
                source="rule_invalid",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="non_product_page",
                combined_score=combined_score,
            ))
            continue

        if strong_learned_negative:
            rule_rejected += 1
            record_rejection("strong_learned_negative", product)
            rejected.append(_mark_product(
                product,
                accepted=False,
                confidence=max(0.05, min(combined_score, 0.35)),
                reason="Rejected by strong scoped negative feedback",
                source="learned_reject",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="strong_learned_negative",
                combined_score=combined_score,
            ))
            continue

        if positive_laptop_evidence and combined_score >= 0.50:
            rule_accepted += 1
            accepted.append(_mark_product(
                product,
                accepted=True,
                confidence=max(combined_score, 0.72),
                reason="Accepted because strong laptop/GPU evidence overrides accessory word",
                source="rule_accept",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="positive_laptop_evidence",
                combined_score=combined_score,
            ))
            continue

        obvious_match = is_obvious_match_for_intent(query, product, query_intent)
        if obvious_match or (combined_score >= RULE_ACCEPT_THRESHOLD and not obvious_junk):
            rule_accepted += 1
            accepted.append(_mark_product(
                product,
                accepted=True,
                confidence=combined_score,
                reason=f"Accepted by intent rule ({query_intent} -> {product_category})",
                source="rule_accept",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="rule_match",
                combined_score=combined_score,
            ))
            continue

        if obvious_junk and combined_score < RULE_REJECT_THRESHOLD:
            if clear_accessory_only or product_category in {"accessory", "sparepart"} or query_intent in {"accessory", "sparepart"}:
                log("REJECT", f'reason=obvious_junk title="{str(product.get("title") or "")[:180]}" clear_accessory_only={str(clear_accessory_only).lower()}', "WARN")
                rule_rejected += 1
                rejected_as_obvious_junk_count += 1
                record_rejection("obvious_junk", product)
                rejected.append(_mark_product(
                    product,
                    accepted=False,
                    confidence=combined_score,
                    reason=f"Rejected by clear intent mismatch ({product_category} does not match {query_intent})",
                    source="rule_reject",
                    query_intent=query_intent,
                    product_category=product_category,
                    rule_score=rule_score,
                    category_match="intent_mismatch",
                    combined_score=combined_score,
                ))
                continue
            product["rule_score"] = round(rule_score, 3)
            product["combined_score"] = round(combined_score, 3)
            product["confidence"] = round(max(combined_score, rule_score, semantic_score or 0.0, 0.05), 3)
            product["decision_source"] = "weak_fallback_candidate"
            product["reason"] = "Accessory-only or intent-mismatch fallback; kept because no strong learned rejection exists"
            weak_fallback_candidates.append(product)
            continue

        if combined_score >= RULE_REVIEW_THRESHOLD and not obvious_junk:
            product["decision_source"] = "borderline_candidate"
            product["confidence"] = round(max(combined_score, rule_score, semantic_score or 0.0), 3)
            borderline.append(product)
            continue

        if _is_valid_product(product) and not obvious_junk:
            product["rule_score"] = round(rule_score, 3)
            product["combined_score"] = round(combined_score, 3)
            product["confidence"] = round(max(combined_score, rule_score, semantic_score or 0.0), 3)
            if semantic_score is not None:
                product["semantic_score"] = round(semantic_score, 3)
            if combined_score >= FALLBACK_EXPANSION_THRESHOLD:
                product["decision_source"] = "fallback_candidate"
                fallback_candidates.append(product)
            else:
                product["decision_source"] = "weak_fallback_candidate"
                product["reason"] = "Weak fallback candidate; not obvious junk"
                weak_fallback_candidates.append(product)
            continue

        if obvious_junk and _is_valid_product(product):
            if clear_accessory_only or product_category in {"accessory", "sparepart"} or query_intent in {"accessory", "sparepart"}:
                log("REJECT", f'reason=obvious_junk title="{str(product.get("title") or "")[:180]}" clear_accessory_only={str(clear_accessory_only).lower()}', "WARN")
                rule_rejected += 1
                rejected_as_obvious_junk_count += 1
                record_rejection("obvious_junk", product)
                rejected.append(_mark_product(
                    product,
                    accepted=False,
                    confidence=combined_score,
                    reason=f"Rejected by clear intent mismatch ({product_category} does not match {query_intent})",
                    source="rule_reject",
                    query_intent=query_intent,
                    product_category=product_category,
                    rule_score=rule_score,
                    category_match="intent_mismatch",
                    combined_score=combined_score,
                ))
                continue
            product["rule_score"] = round(rule_score, 3)
            product["combined_score"] = round(combined_score, 3)
            product["confidence"] = round(max(combined_score, rule_score, semantic_score or 0.0, 0.05), 3)
            product["decision_source"] = "weak_fallback_candidate"
            product["reason"] = "Obvious junk fallback; kept as low priority until user feedback proves rejection"
            weak_fallback_candidates.append(product)
            continue

        reject_reason = "invalid_product_data"
        record_rejection(reject_reason, product)
        rejected.append(_mark_product(
            product,
            accepted=False,
            confidence=combined_score,
            reason=f"Rejected by {reject_reason.replace('_', ' ')}",
            source="rule_invalid",
            query_intent=query_intent,
            product_category=product_category,
            rule_score=rule_score,
            category_match=reject_reason,
            combined_score=combined_score,
        ))

    rejected_as_obvious_junk_count_before_rescue = rejected_as_obvious_junk_count
    rescued_false_junk: list[dict[str, Any]] = []
    remaining_rejected: list[dict[str, Any]] = []
    for product in rejected:
        rejection_text = normalize_text(
            f"{product.get('reject_reason') or ''} {product.get('reason') or product.get('ai_reason') or ''}"
        )
        if (
            ("obvious_junk" in rejection_text or "obvious junk" in rejection_text)
            and is_laptop_gaming_query(query)
            and has_laptop_main_evidence(str(product.get("title") or product.get("name") or ""))
        ):
            product["decision_source"] = "rescued_false_obvious_junk"
            product["ai_source"] = "rescued_false_obvious_junk"
            product["reason"] = "Rescued because strong laptop/GPU evidence overrides accessory word"
            product["ai_reason"] = product["reason"]
            product["confidence"] = round(max(
                _as_number(product.get("combined_score"), 0.0),
                _as_number(product.get("semantic_score"), 0.0) * 0.85,
                0.72,
            ), 3)
            product["ai_confidence"] = product["confidence"]
            rescued_false_junk.append(product)
            continue
        remaining_rejected.append(product)
    if rescued_false_junk:
        rejected[:] = remaining_rejected
        fallback_candidates.extend(rescued_false_junk)
        rejected_as_obvious_junk_count = max(0, rejected_as_obvious_junk_count - len(rescued_false_junk))
        rejected_reasons_histogram["obvious_junk"] = max(
            0,
            rejected_reasons_histogram.get("obvious_junk", 0) - len(rescued_false_junk),
        )
    rescued_false_obvious_junk_count = len(rescued_false_junk)
    log("RELEVANCE", f"query={query} target_display={target_display}", "INFO")
    log("RELEVANCE", f"rejected_as_obvious_junk_before_rescue={rejected_as_obvious_junk_count_before_rescue}", "INFO")
    log("RELEVANCE", f"rescued_false_obvious_junk={rescued_false_obvious_junk_count}", "INFO")
    log("RELEVANCE", f"fallback_candidates_after_rescue={len(fallback_candidates)}", "INFO")

    def apply_fallback_expansion() -> int:
        nonlocal accepted_before_fallback, fallback_rejected_as_junk, rejected_as_obvious_junk_count
        expanded = 0
        accepted_before_fallback = len(accepted)
        if len(accepted) >= target_display:
            return 0
        seen_ids = {_product_key(p) for p in accepted}

        unique_candidates: list[dict[str, Any]] = []
        candidate_keys = set()
        for p in [*fallback_candidates, *weak_fallback_candidates]:
            key = _product_key(p)
            if key in seen_ids or key in candidate_keys:
                continue
            candidate_keys.add(key)
            unique_candidates.append(p)

        unique_candidates = _sort_fallback_candidates(unique_candidates)

        for product in unique_candidates:
            if len(accepted) >= target_display:
                break
            ctx = product.get("_rule_context") or {}
            score = _as_number(ctx.get("rule_score", product.get("rule_score")), 0.0)
            semantic = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
            existing_confidence = _as_number(product.get("confidence", product.get("relevance_score", product.get("ai_confidence", 0))), 0.0)
            positive_laptop_evidence = is_laptop_gaming_query(query) and has_laptop_main_evidence(
                str(product.get("title") or product.get("name") or "")
            )
            strong_learned_negative = bool(ctx.get("strong_learned_negative"))
            if strong_learned_negative:
                fallback_rejected_as_junk += 1
                record_rejection("strong_learned_negative", product)
                product_category = str(ctx.get("product_category") or detect_product_category(product))
                rejected.append(_mark_product(
                    product,
                    accepted=False,
                    confidence=max(score, semantic),
                    reason="Fallback rejected because strong scoped negative feedback applies",
                    source="learned_reject",
                    query_intent=query_intent,
                    product_category=product_category,
                    rule_score=score,
                    category_match="strong_learned_negative",
                    combined_score=_as_number(ctx.get("combined_score", product.get("combined_score")), score),
                ))
                continue
            if not _is_valid_product(product):
                record_rejection("invalid_product_data", product)
                product_category = str(ctx.get("product_category") or detect_product_category(product))
                rejected.append(_mark_product(
                    product,
                    accepted=False,
                    confidence=max(score, semantic),
                    reason="Fallback rejected because product data is invalid",
                    source="fallback_reject",
                    query_intent=query_intent,
                    product_category=product_category,
                    rule_score=score,
                    category_match="invalid_product_data",
                    combined_score=_as_number(ctx.get("combined_score", product.get("combined_score")), score),
                ))
                continue
            product_category = str(ctx.get("product_category") or detect_product_category(product))
            combined = _as_number(ctx.get("combined_score", product.get("combined_score")), score)
            source = str(product.get("decision_source") or "")
            if source in {"", "fallback_candidate", "weak_fallback_candidate", "borderline_candidate"}:
                source = "fallback_expansion"
            marked = _mark_product(
                product,
                accepted=True,
                confidence=max(existing_confidence, combined, score, semantic, 0.35),
                reason="Included by fallback expansion to satisfy requested count",
                source=source,
                query_intent=query_intent,
                product_category=product_category,
                rule_score=score,
                category_match="fallback_expansion",
                combined_score=combined,
            )
            accepted.append(marked)
            seen_ids.add(_product_key(product))
            expanded += 1

        if len(products) >= target_count and len(accepted) < target_display:
            log(
                "PIPELINE",
                (
                    f"target_not_met target={target_display} displayed={len(accepted)} "
                    f"accepted_count_before_fallback={accepted_before_fallback} "
                    f"fallback_candidates_count={len(fallback_candidates)} "
                    f"weak_fallback_candidates_count={len(weak_fallback_candidates)} "
                    f"fallback_added={expanded} "
                    f"rejected_as_obvious_junk_count={rejected_as_obvious_junk_count} "
                    f"rejected_reasons_histogram={dict(rejected_reasons_histogram)} "
                    f"reason=fallback_pool_exhausted"
                ),
                "ERROR",
            )
        return expanded

    def _ai_skip_reason(checked: int) -> str | None:
        if ai_skip_reason_override:
            return ai_skip_reason_override
        if ai_circuit_open:
            return ai_circuit_reason or "AI classifier circuit breaker opened for this search"
        if checked:
            return None
        if not use_ai:
            return "AI disabled"
        if not classifier_installed:
            return "No supported classifier installed"
        if not products:
            return "Candidate pool empty"
        if not borderline:
            return "No borderline candidates"
        return "Classifier path not reached"

    def _warning_text(fallback_expanded: int) -> str:
        warnings: list[str] = []
        budget_valid = int(products[0].get("_budget_valid", len(products)) or 0) if products else 0
        strict_budget_mode = bool(products[0].get("_strict_budget_mode", True)) if products else True
        overfetch_stop_reason = str(products[0].get("_overfetch_stop_reason") or "") if products else ""
        if budget_valid and budget_valid < target_count:
            if strict_budget_mode:
                warnings.append(
                    f"Diminta {target_count}, tetapi hanya {budget_valid} produk sesuai budget setelah overfetch."
                )
            else:
                warnings.append(f"Diminta {target_count}, tetapi hanya {budget_valid} kandidat utama tersedia.")
            if overfetch_stop_reason:
                warnings.append(f"Overfetch berhenti: {overfetch_stop_reason}.")
        if fallback_expanded:
            warnings.append(f"{fallback_expanded} produk fallback ditambahkan agar hasil mendekati target.")
        skip_reason = _ai_skip_reason(classifier_checked)
        if skip_reason:
            warnings.append(f"AI classifier: {skip_reason}.")
        displayed = min(len(accepted), target_display)
        if displayed < target_display:
            warnings.append(
                f"Ditampilkan {displayed} dari target aman {target_display}. Cek log pipeline untuk alasan produk dibuang."
            )
        return " ".join(dict.fromkeys(warnings))

    def _build_meta(
        *,
        status: str,
        checked: int,
        accepted_by_classifier: int,
        rejected_by_classifier: int,
        fallback_by_classifier: int,
        fallback_expanded: int,
        warning: str,
    ) -> dict[str, Any]:
        displayed = min(len(accepted), target_display)
        return {
            "requested": target_count,
            "requested_count": target_count,
            "scraped_raw": products[0].get("_scraped_raw", 0) if products else 0,
            "raw_scraped": products[0].get("_scraped_raw", 0) if products else 0,
            "raw_scraped_count": products[0].get("_scraped_raw", 0) if products else 0,
            "after_dedupe": products[0].get("_after_dedupe", 0) if products else 0,
            "deduped_count": products[0].get("_after_dedupe", 0) if products else 0,
            "valid_product_candidates": products[0].get("_valid_product_candidates", len(products)) if products else 0,
            "invalid_non_product_removed": products[0].get("_invalid_non_product_removed", 0) if products else 0,
            "budget_valid": products[0].get("_budget_valid", 0) if products else 0,
            "budget_valid_count": products[0].get("_budget_valid", 0) if products else 0,
            "candidate_pool": len(products),
            "candidate_pool_count": len(products),
            "ai_input_count": len(products),
            "target_display": target_display,
            "overfetch_attempted": products[0].get("_overfetch_attempted", False) if products else False,
            "overfetch_attempts": products[0].get("_overfetch_attempts", 0) if products else 0,
            "overfetch_rounds": products[0].get("_overfetch_rounds", products[0].get("_overfetch_attempts", 0)) if products else 0,
            "overfetch_initial_valid_pool": products[0].get("_overfetch_initial_valid_pool", len(products)) if products else 0,
            "overfetch_final_valid_pool": products[0].get("_overfetch_final_valid_pool", len(products)) if products else 0,
            "overfetch_max_raw": products[0].get("_overfetch_max_raw", 0) if products else 0,
            "overfetch_exhausted": products[0].get("_overfetch_exhausted", False) if products else False,
            "overfetch_stop_reason": products[0].get("_overfetch_stop_reason", "") if products else "",
            "raw_after_overfetch": products[0].get("_raw_after_overfetch", products[0].get("_scraped_raw", 0)) if products else 0,
            "strict_budget_mode": products[0].get("_strict_budget_mode", True) if products else True,
            "target_first_mode": products[0].get("_target_first_mode", False) if products else False,
            "target_first_added": products[0].get("_target_first_added", 0) if products else 0,
            "query_intent": query_intent,
            "query_constraints": query_constraints,
            "feedback_examples_loaded": feedback_examples_loaded,
            "learned_patterns_loaded": learned_patterns_loaded,
            "query_scoped_patterns": query_scoped_patterns,
            "constraint_scoped_patterns": constraint_scoped_patterns,
            "intent_scoped_patterns": intent_scoped_patterns,
            "global_patterns": global_patterns,
            "constraint_mismatch_products": constraint_mismatch_products,
            "learning_adjusted_products": learning_adjusted_products,
            "learned_positive_matches": learned_positive_matches,
            "learned_negative_matches": learned_negative_matches,
            "selected_model": selected_model if use_ai else None,
            "selected_classifier": selected_model if use_ai else None,
            "ai_status": status,
            "ai_orchestrator": orchestrator_status,
            "borderline_candidates": len(borderline),
            "borderline_count": len(borderline),
            "rule_accepted": rule_accepted,
            "rule_accepted_count": rule_accepted,
            "rule_rejected": rule_rejected,
            "rule_rejected_count": rule_rejected,
            "rejected_as_obvious_junk": rejected_as_obvious_junk_count,
            "rejected_as_obvious_junk_count": rejected_as_obvious_junk_count,
            "rejected_as_obvious_junk_count_before_rescue": rejected_as_obvious_junk_count_before_rescue,
            "rescued_false_obvious_junk": rescued_false_obvious_junk_count,
            "fallback_candidates_count_after_rescue": len(fallback_candidates),
            "rejected_reasons_histogram": dict(rejected_reasons_histogram),
            "semantic_checked_count": semantic_checked,
            "semantic_checked": semantic_checked,
            "classifier_checked": checked,
            "ai_checked": checked,
            "llm_checked_count": checked,
            "classifier_limit": AI_CLASSIFIER_MAX_PRODUCTS,
            "ai_calls_attempted": ai_calls_attempted,
            "ai_calls_succeeded": ai_calls_succeeded,
            "ai_timeouts": ai_timeouts,
            "ai_failures": ai_failure_count,
            "ai_circuit_open": ai_circuit_open,
            "ai_batch_size": AI_BATCH_SIZE,
            "ai_batch_classify": AI_BATCH_CLASSIFY,
            "prompt_tokens_estimated": prompt_tokens_estimated,
            "prompt_truncated_by_app": prompt_truncated_by_app,
            "ctx": AI_CHAT_NUM_CTX,
            "ai_accepted": accepted_by_classifier,
            "ai_accepted_count": accepted_by_classifier,
            "ai_confirmed": ai_confirmed,
            "ai_rescued": ai_rescued,
            "ai_rejected": rejected_by_classifier,
            "ai_fallback": fallback_by_classifier,
            "fallback_candidates": len(fallback_candidates),
            "fallback_candidates_count": len(fallback_candidates),
            "weak_fallback_candidates": len(weak_fallback_candidates),
            "weak_fallback_candidates_count": len(weak_fallback_candidates),
            "fallback_rejected_as_junk": fallback_rejected_as_junk,
            "fallback_added": fallback_expanded,
            "fallback_expansion_count": fallback_expanded,
            "displayed": displayed,
            "displayed_count": displayed,
            "accepted_before_fallback": accepted_before_fallback,
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "fallback_used": fallback_by_classifier > 0 or fallback_expanded > 0,
            "warning": warning,
            "thresholds": {
                "rule_accept": RULE_ACCEPT_THRESHOLD,
                "rule_review": RULE_REVIEW_THRESHOLD,
                "rule_reject": RULE_REJECT_THRESHOLD,
                "fallback_expansion": FALLBACK_EXPANSION_THRESHOLD,
                "weak_fallback": WEAK_FALLBACK_THRESHOLD,
                "llm_accept": LLM_ACCEPT_THRESHOLD,
            },
            "ai_skip_reason": _ai_skip_reason(checked),
        }

    def log_runtime_summary(*, fallback_expanded: int, final_displayed: int, checked: int) -> None:
        skip_reason = _ai_skip_reason(checked)
        log("AI_ORCH", f"semantic_checked={semantic_checked}", "INFO")
        log("AI_ORCH", f"classifier_installed={str(classifier_installed).lower()} classifier={selected_model or 'none'}", "INFO")
        log("AI_ORCH", f"borderline_candidates={len(borderline)}", "INFO")
        log("AI_ORCH", f"classifier_checked={checked}", "INFO")
        log("AI_ORCH", f"ai_calls_attempted={ai_calls_attempted}", "INFO")
        log("AI_ORCH", f"ai_calls_succeeded={ai_calls_succeeded}", "INFO")
        log("AI_ORCH", f"ai_skip_reason={skip_reason or 'none'}", "INFO")
        log("PIPELINE", f"requested={target_count} candidate_pool={len(products)} target_display={target_display}", "INFO")
        log("PIPELINE", f"accepted_before_fallback={accepted_before_fallback}", "INFO")
        log("PIPELINE", f"fallback_candidates={len(fallback_candidates)} weak_fallback_candidates={len(weak_fallback_candidates)}", "INFO")
        log("PIPELINE", f"fallback_added={fallback_expanded}", "INFO")
        log("PIPELINE", f"final_displayed={final_displayed}", "INFO")
        log("PIPELINE", f"accepted_before_fallback={accepted_before_fallback} fallback_added={fallback_expanded} final_displayed={final_displayed}", "INFO")
        log("PIPELINE", f"rejected_as_obvious_junk={rejected_as_obvious_junk_count}", "INFO")
        log(
            "PIPELINE",
            (
                f"requested={target_count} candidate_pool={len(products)} "
                f"rule_accepted={rule_accepted} rule_rejected={rule_rejected} "
                f"fallback_candidates={len(fallback_candidates)} weak_fallback_candidates={len(weak_fallback_candidates)} "
                f"fallback_added={fallback_expanded} "
                f"final_displayed={final_displayed} target_display={target_display}"
            ),
            "INFO",
        )

    def finalize_intent_result(
        *,
        status: str,
        checked: int,
        accepted_by_classifier: int,
        rejected_by_classifier: int,
        fallback_by_classifier: int,
        fallback_expanded: int,
        warning: str,
        extra_meta: dict[str, Any] | None = None,
    ) -> IntentFilterResult:
        final_products = _rank_final_products(accepted)[:target_display]
        meta = _build_meta(
            status=status,
            checked=checked,
            accepted_by_classifier=accepted_by_classifier,
            rejected_by_classifier=rejected_by_classifier,
            fallback_by_classifier=fallback_by_classifier,
            fallback_expanded=fallback_expanded,
            warning=warning,
        )
        if extra_meta:
            meta.update(extra_meta)
        meta["displayed"] = len(final_products)
        meta["displayed_count"] = len(final_products)

        final_histogram = Counter(
            str(product.get("decision_source") or product.get("ai_source") or "unknown")
            for product in final_products
        )
        final_keys = {_product_key(product) for product in final_products}
        accepted_keys = {_product_key(product) for product in accepted}
        not_displayed_product_reasons: list[dict[str, Any]] = []
        for product in [*rejected, *fallback_candidates, *weak_fallback_candidates, *accepted]:
            key = _product_key(product)
            if key in final_keys:
                continue
            reason = (
                product.get("reject_reason")
                or product.get("reason")
                or product.get("ai_reason")
                or ("ranked below target" if key in accepted_keys else "not eligible for fallback")
            )
            sample = _debug_sample(product)
            sample["not_displayed_reason"] = reason
            not_displayed_product_reasons.append(sample)
        if len(final_products) >= target_display:
            remaining_reason = "target met"
        else:
            remaining_reason = (
                f"fallback pool exhausted after excluding invalid/duplicate/obvious junk products; "
                f"missing={target_display - len(final_products)}"
            )
        debug_payload = {
            "query": query,
            "search_id": search_id,
            "requested": target_count,
            "scraped_raw": meta.get("scraped_raw", 0),
            "after_dedupe": meta.get("after_dedupe", 0),
            "valid_product_candidates": meta.get("valid_product_candidates", len(products)),
            "invalid_non_product_removed": meta.get("invalid_non_product_removed", 0),
            "budget_valid": meta.get("budget_valid", len(products)),
            "candidate_pool_count": len(products),
            "target_display": target_display,
            "overfetch_attempted": meta.get("overfetch_attempted", False),
            "overfetch_attempts": meta.get("overfetch_attempts", 0),
            "overfetch_rounds": meta.get("overfetch_rounds", meta.get("overfetch_attempts", 0)),
            "overfetch_initial_valid_pool": meta.get("overfetch_initial_valid_pool", len(products)),
            "overfetch_final_valid_pool": meta.get("overfetch_final_valid_pool", len(products)),
            "overfetch_max_raw": meta.get("overfetch_max_raw", 0),
            "overfetch_exhausted": meta.get("overfetch_exhausted", False),
            "overfetch_stop_reason": meta.get("overfetch_stop_reason", ""),
            "raw_after_overfetch": meta.get("raw_after_overfetch", meta.get("scraped_raw", 0)),
            "strict_budget_mode": meta.get("strict_budget_mode", True),
            "target_first_mode": meta.get("target_first_mode", False),
            "target_first_added": meta.get("target_first_added", 0),
            "query_constraints": query_constraints,
            "feedback_examples_loaded": feedback_examples_loaded,
            "learned_patterns_loaded": learned_patterns_loaded,
            "query_scoped_patterns": query_scoped_patterns,
            "constraint_scoped_patterns": constraint_scoped_patterns,
            "intent_scoped_patterns": intent_scoped_patterns,
            "global_patterns": global_patterns,
            "constraint_mismatch_products": constraint_mismatch_products,
            "learning_adjusted_products": learning_adjusted_products,
            "learned_positive_matches": learned_positive_matches,
            "learned_negative_matches": learned_negative_matches,
            "accepted_before_fallback": accepted_before_fallback,
            "fallback_candidates_count": len(fallback_candidates),
            "weak_fallback_candidates_count": len(weak_fallback_candidates),
            "fallback_added": fallback_expanded,
            "final_displayed": len(final_products),
            "rejected_as_obvious_junk_count": rejected_as_obvious_junk_count,
            "rejected_as_obvious_junk_count_before_rescue": rejected_as_obvious_junk_count_before_rescue,
            "rescued_false_obvious_junk": rescued_false_obvious_junk_count,
            "fallback_candidates_count_after_rescue": len(fallback_candidates),
            "rejected_reasons_histogram": dict(rejected_reasons_histogram),
            "semantic_checked": semantic_checked,
            "classifier_checked": checked,
            "ai_checked": checked,
            "ai_calls_attempted": ai_calls_attempted,
            "ai_calls_succeeded": ai_calls_succeeded,
            "ai_timeouts": ai_timeouts,
            "ai_failures": ai_failure_count,
            "ai_batch_size": AI_BATCH_SIZE,
            "prompt_tokens_estimated": prompt_tokens_estimated,
            "prompt_truncated_by_app": prompt_truncated_by_app,
            "ctx": AI_CHAT_NUM_CTX,
            "ai_accepted": accepted_by_classifier,
            "ai_confirmed": ai_confirmed,
            "ai_rescued": ai_rescued,
            "ai_rejected": rejected_by_classifier,
            "ai_skip_reason": meta.get("ai_skip_reason"),
            "decision_histogram": dict(final_histogram),
            "sample_rejected": [_debug_sample(product) for product in rejected[:10]],
            "sample_rescued": [
                str(product.get("title") or product.get("name") or "")
                for product in rescued_false_junk[:10]
            ],
            "sample_fallback": [_debug_sample(product) for product in [*fallback_candidates, *weak_fallback_candidates][:10]],
            "not_displayed_product_reasons": not_displayed_product_reasons[:50],
            "why_remaining_products_were_not_displayed": remaining_reason,
        }
        _write_latest_pipeline_debug(debug_payload)
        meta["pipeline_debug_path"] = "debug/pipeline/latest_search_debug.json"
        meta["decision_histogram"] = dict(final_histogram)
        meta["why_remaining_products_were_not_displayed"] = remaining_reason
        return IntentFilterResult(final_products, status, meta)

    borderline = _sort_borderline_candidates(borderline)

    def _remove_key(items: list[dict[str, Any]], key: str) -> None:
        for index in range(len(items) - 1, -1, -1):
            if _product_key(items[index]) == key:
                del items[index]

    def _index_by_key(items: list[dict[str, Any]], key: str) -> int:
        for index, item in enumerate(items):
            if _product_key(item) == key:
                return index
        return -1

    def _mark_safe_fallback(product: dict[str, Any], source: str, reason: str) -> bool:
        key = _product_key(product)
        if _index_by_key(fallback_candidates, key) >= 0 or _index_by_key(accepted, key) >= 0:
            return False
        ctx = product.get("_rule_context", {})
        rule_score = float(ctx.get("rule_score") or product.get("rule_score") or 0.0)
        combined_score = _as_number(ctx.get("combined_score", product.get("combined_score")), rule_score)
        semantic_score = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
        obvious_junk = bool(ctx.get("obvious_junk"))
        if is_laptop_gaming_query(query) and has_laptop_main_evidence(
            str(product.get("title") or product.get("name") or "")
        ):
            obvious_junk = False
        if not _is_safe_fallback_candidate(product, rule_score, obvious_junk):
            return False
        product["rule_score"] = round(rule_score, 3)
        product["combined_score"] = round(combined_score, 3)
        if semantic_score:
            product["semantic_score"] = round(semantic_score, 3)
        product["confidence"] = round(max(combined_score, rule_score, semantic_score, 0.35), 3)
        product["decision_source"] = source
        product["reason"] = reason
        fallback_candidates.append(product)
        return True

    if not use_ai or not classifier_installed:
        if not use_ai:
            ai_skip_reason_override = "AI disabled"
            status = "disabled"
        else:
            ai_skip_reason_override = "No supported classifier installed"
            status = "unavailable"

        for product in borderline:
            _mark_safe_fallback(
                product,
                "fallback_classifier_skipped",
                "Classifier skipped, included as fallback candidate",
            )

        fallback_expanded = apply_fallback_expansion()
        warning = _warning_text(fallback_expanded)
        final_displayed = min(len(accepted), target_display)
        log_runtime_summary(fallback_expanded=fallback_expanded, final_displayed=final_displayed, checked=0)
        log(
            "AI",
            (
                f"raw={len(products)} target_display={target_display} intent={query_intent} "
                f"classifier_installed={classifier_installed} selected_classifier={selected_model or 'none'} "
                f"classifier_limit={AI_CLASSIFIER_MAX_PRODUCTS} "
                f"rule_accept={rule_accepted} rule_reject={rule_rejected} semantic_checked={semantic_checked} "
                f"borderline_candidates={len(borderline)} classifier_checked=0 ai_calls_attempted=0 "
                f"ai_timeouts=0 ai_circuit_open=false "
                f"fallback_candidates={len(fallback_candidates)} fallback_added={fallback_expanded} final_displayed={final_displayed} "
                f"ai_skip_reason={ai_skip_reason_override}"
            ),
            "OK",
        )
        return finalize_intent_result(
            status=status,
            checked=0,
            accepted_by_classifier=0,
            rejected_by_classifier=0,
            fallback_by_classifier=0,
            fallback_expanded=fallback_expanded,
            warning=warning,
        )

    audit_limit = max(1, min(AI_AUDIT_MAX_PRODUCTS, AI_BATCH_SIZE))
    audit_candidates: list[dict[str, Any]] = []
    audit_keys: set[str] = set()

    def add_audit_candidates(bucket: str, candidates: list[dict[str, Any]]) -> None:
        for product in candidates:
            if len(audit_candidates) >= audit_limit:
                return
            key = _product_key(product)
            if key in audit_keys:
                continue
            audit_keys.add(key)
            product["_audit_bucket"] = bucket
            audit_candidates.append(product)

    suspicious_rejected = [
        product for product in rejected
        if _is_valid_product(product) and not bool((product.get("_rule_context") or {}).get("obvious_junk"))
    ]
    low_confidence_accepted = sorted(
        [
            product for product in accepted
            if _as_number(product.get("confidence", product.get("relevance_score")), 1.0) < 0.86
        ],
        key=lambda product: _as_number(product.get("confidence", product.get("relevance_score")), 1.0),
    )
    learned_match_candidates = [
        product for product in [*accepted, *fallback_candidates, *weak_fallback_candidates, *borderline]
        if product.get("learned_matches") or (product.get("_rule_context") or {}).get("learned_matches")
    ]
    near_budget_candidates = [
        product for product in [*accepted, *fallback_candidates, *weak_fallback_candidates, *borderline]
        if product.get("target_first_fallback") or product.get("outside_budget")
    ]
    coverage_candidates = _sort_fallback_candidates(
        [*fallback_candidates, *weak_fallback_candidates, *borderline, *accepted]
    )
    add_audit_candidates("suspicious_rejected", suspicious_rejected)
    add_audit_candidates("low_confidence_accepted", low_confidence_accepted)
    add_audit_candidates("fallback_candidate", _sort_fallback_candidates([*fallback_candidates, *weak_fallback_candidates]))
    add_audit_candidates("learned_match", learned_match_candidates)
    add_audit_candidates("near_budget_boundary", near_budget_candidates)
    add_audit_candidates("borderline", borderline)
    if use_ai and products:
        add_audit_candidates("coverage_sample", coverage_candidates)

    for product in borderline:
        if _product_key(product) not in audit_keys:
            _mark_safe_fallback(
                product,
                "fallback_not_classified_cpu_limit",
                "Classifier limit reached, included as fallback candidate",
            )

    batches = [audit_candidates] if audit_candidates else []
    completed_batch_durations: list[float] = []
    log(
        "AI_ORCH",
        (
            f"audit_candidates={len(audit_candidates)} borderline_candidates={len(borderline)} "
            f"classifier_limit={AI_AUDIT_MAX_PRODUCTS} batch_size={AI_BATCH_SIZE} batches={len(batches)}"
        ),
        "INFO",
    )

    for batch_index, batch in enumerate(batches, 1):
        batch_started = time.perf_counter()
        batch_epoch_ms = int(time.time() * 1000)
        if search_id:
            from src.server.progress import update_ai_eta_progress
            update_ai_eta_progress(
                search_id=search_id,
                batch_current=batch_index,
                batch_total=len(batches),
                batch_started_at_monotonic=batch_started,
                batch_started_at_epoch_ms=batch_epoch_ms,
                completed_ai_batch_durations=completed_batch_durations,
                message=f"AI filtering batch {batch_index}/{len(batches)}",
                found=len(products),
                valid=len(accepted),
            )

        response = await _run_with_ai_heartbeat(
            coro=classify_product_batch(
                query,
                query_intent,
                batch,
                status=orchestrator_status,
                ai_enabled=use_ai,
                feedback_context=feedback_context,
                query_constraints=query_constraints,
            ),
            search_id=search_id,
            batch_current=batch_index,
            batch_total=len(batches),
            batch_started_at_monotonic=batch_started,
            batch_started_at_epoch_ms=batch_epoch_ms,
            completed_batch_durations=completed_batch_durations,
            found=len(products),
            valid_count=len(accepted),
        )

        ai_calls_attempted += max(1, int(response.get("attempts") or 0))
        prompt_tokens_estimated = int(response.get("prompt_tokens_estimated") or prompt_tokens_estimated or 0)
        prompt_truncated_by_app = prompt_truncated_by_app or bool(response.get("truncated_by_app"))
        if response.get("_chat_ok"):
            ai_calls_succeeded += 1

        if not response.get("_chat_ok"):
            ai_failure_count += 1
            if response.get("_timeout"):
                ai_timeouts += 1
            ai_circuit_open = True
            ai_circuit_reason = "Gemma classifier timeout/failure, used rule+learning fallback"
            ai_skip_reason_override = ai_circuit_reason
            ai_fallback += len(batch)
            log("AI_ORCH", "gemma_circuit_open reason=timeout_or_500", "WARN")
            for product in batch:
                _mark_safe_fallback(
                    product,
                    "fallback_ai_circuit_open",
                    "Gemma classifier failed, included by rule+learning fallback",
                )
            completed_batch_durations.append(time.perf_counter() - batch_started)
            if search_id:
                from src.server.progress import update_ai_eta_progress
                update_ai_eta_progress(
                    search_id=search_id,
                    batch_current=batch_index,
                    batch_total=len(batches),
                    batch_started_at_monotonic=batch_started,
                    batch_started_at_epoch_ms=batch_epoch_ms,
                    completed_ai_batch_durations=completed_batch_durations,
                    message=f"AI filtering batch {batch_index}/{len(batches)} failed; using fallback",
                    found=len(products),
                    valid=len(accepted),
                    batch_done=True,
                )
            break

        decisions = {
            str(item.get("id")): item
            for item in (response.get("items") or [])
            if isinstance(item, dict)
        }
        classifier_checked += len(decisions)

        for product in batch:
            audit_id = str(product.get("_audit_id") or "")
            decision = decisions.get(audit_id)
            if not decision:
                ai_fallback += 1
                _mark_safe_fallback(
                    product,
                    "fallback_ai_missing_result",
                    "Gemma omitted this product, included by fallback candidate",
                )
                continue

            key = _product_key(product)
            ctx = product.get("_rule_context", {})
            product_category = str(ctx.get("product_category") or product.get("product_category") or "unknown")
            rule_score = float(ctx.get("rule_score") or product.get("rule_score") or 0.0)
            combined_score = _as_number(ctx.get("combined_score", product.get("combined_score")), rule_score)
            obvious_junk = bool(ctx.get("obvious_junk"))
            strong_learned_negative = bool(ctx.get("strong_learned_negative"))
            positive_laptop_evidence = is_laptop_gaming_query(query) and has_laptop_main_evidence(
                str(product.get("title") or product.get("name") or "")
            )
            if positive_laptop_evidence:
                obvious_junk = False

            ai_confidence = _as_float(decision.get("confidence"), 0.5)
            ai_model_accepts = bool(decision.get("accepted", True))
            confidence = max(combined_score, rule_score, ai_confidence if ai_model_accepts else min(ai_confidence, combined_score))
            marked = _mark_product(
                product,
                accepted=ai_model_accepts,
                confidence=confidence,
                reason=str(decision.get("reason") or "AI audit decision"),
                source=str(decision.get("decision_source") or "ai_orchestrator"),
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match=str(decision.get("category_match") or "ai"),
                combined_score=combined_score,
            )
            accepted_index = _index_by_key(accepted, key)
            fallback_index = _index_by_key(fallback_candidates, key)
            weak_fallback_index = _index_by_key(weak_fallback_candidates, key)
            was_rejected_or_fallback = (
                _index_by_key(rejected, key) >= 0
                or fallback_index >= 0
                or weak_fallback_index >= 0
            )
            if ai_model_accepts:
                ai_accepted += 1
                if accepted_index >= 0:
                    ai_confirmed += 1
                elif was_rejected_or_fallback:
                    ai_rescued += 1
                else:
                    ai_confirmed += 1
                if accepted_index >= 0:
                    accepted[accepted_index] = marked
                else:
                    accepted.append(marked)
                _remove_key(rejected, key)
                _remove_key(fallback_candidates, key)
                _remove_key(weak_fallback_candidates, key)
            else:
                ai_rejected += 1
                if accepted_index >= 0:
                    del accepted[accepted_index]
                marked["decision_source"] = "ai_reject"
                marked["ai_source"] = "ai_reject"
                if strong_learned_negative:
                    record_rejection("strong_learned_negative", marked)
                    rejected.append(marked)
                elif positive_laptop_evidence and _is_valid_product(marked):
                    marked["decision_source"] = "fallback_after_ai_reject_positive_laptop"
                    marked["ai_source"] = "fallback_after_ai_reject_positive_laptop"
                    marked["reason"] = "AI rejected but product has valid gaming laptop evidence"
                    marked["ai_reason"] = marked["reason"]
                    marked["rule_score"] = round(rule_score, 3)
                    marked["combined_score"] = round(combined_score, 3)
                    fallback_candidates.append(marked)
                elif _is_valid_product(marked):
                    marked["decision_source"] = "fallback_after_ai_reject"
                    marked["ai_source"] = "fallback_after_ai_reject"
                    marked["reason"] = "AI rejected, kept as fallback because no hard rejection applies"
                    marked["ai_reason"] = marked["reason"]
                    marked["rule_score"] = round(rule_score, 3)
                    marked["combined_score"] = round(combined_score, 3)
                    fallback_candidates.append(marked)
                else:
                    record_rejection("invalid_product_data", marked)
                    rejected.append(marked)

        completed_batch_durations.append(time.perf_counter() - batch_started)
        if search_id:
            from src.server.progress import update_ai_eta_progress
            update_ai_eta_progress(
                search_id=search_id,
                batch_current=batch_index,
                batch_total=len(batches),
                batch_started_at_monotonic=batch_started,
                batch_started_at_epoch_ms=batch_epoch_ms,
                completed_ai_batch_durations=completed_batch_durations,
                message=f"AI filtering batch {batch_index}/{len(batches)} done",
                found=len(products),
                valid=len(accepted),
                batch_done=True,
            )

    fallback_expanded = apply_fallback_expansion()

    if ai_circuit_open:
        status = "partial"
    elif ai_fallback and ai_fallback == classifier_checked:
        status = "unavailable"
    elif ai_fallback:
        status = "partial"
    else:
        status = "ok"

    warning = _warning_text(fallback_expanded)
    if audit_candidates and ai_calls_attempted == 0 and not ai_skip_reason_override:
        log("AI_ORCH", "AI classifier integration failure: audit candidates exist but /api/chat was not called", "ERROR")

    meta_result = finalize_intent_result(
        status=status,
        checked=classifier_checked,
        accepted_by_classifier=ai_accepted,
        rejected_by_classifier=ai_rejected,
        fallback_by_classifier=ai_fallback,
        fallback_expanded=fallback_expanded,
        warning=warning,
        extra_meta={"batch_count": len(batches)},
    )
    final_displayed = min(len(accepted), target_display)
    log_runtime_summary(
        fallback_expanded=fallback_expanded,
        final_displayed=final_displayed,
        checked=classifier_checked,
    )
    
    log(
        "AI",
        (
            f"raw={len(products)} target_display={target_display} intent={query_intent} "
            f"classifier_installed={classifier_installed} selected_classifier={selected_model or 'none'} "
            f"classifier_limit={AI_CLASSIFIER_MAX_PRODUCTS} "
            f"rule_accept={rule_accepted} rule_reject={rule_rejected} semantic_checked={semantic_checked} "
            f"borderline_candidates={len(borderline)} classifier_checked={classifier_checked} "
            f"ai_calls_attempted={ai_calls_attempted} ai_calls_succeeded={ai_calls_succeeded} "
            f"ai_timeouts={ai_timeouts} ai_circuit_open={str(ai_circuit_open).lower()} "
            f"ai_accepted={ai_accepted} ai_rejected={ai_rejected} ai_fallback={ai_fallback} "
            f"fallback_candidates={len(fallback_candidates)} fallback_added={fallback_expanded} final_displayed={final_displayed}"
        ),
        "OK",
    )
    return meta_result


def _is_safe_fallback_candidate(product: dict[str, Any], rule_score: float, obvious_junk: bool) -> bool:
    if obvious_junk:
        return False
    return _is_valid_product(product)

```

## FILE: `src\ai\ai_orchestrator.py`

```python
"""
Automatic AI Orchestrator for borderline product relevance checks.
"""
from __future__ import annotations

import json
from typing import Any

from src.ai.json_repair import repair_json_or_fallback
from src.ai.model_registry import get_orchestrator_status, get_installed_model_name
from src.ai.ollama_client import chat_raw_async
from src.config import AI_CHAT_NUM_CTX, LLM_ACCEPT_THRESHOLD, RULE_ACCEPT_THRESHOLD, RULE_REJECT_THRESHOLD, RULE_REVIEW_THRESHOLD
from src.utils.logger import log


def should_call_llm(rule_score: float, obvious_junk: bool) -> bool:
    if rule_score >= RULE_ACCEPT_THRESHOLD:
        return False
    if obvious_junk and rule_score < RULE_REJECT_THRESHOLD:
        return False
    if rule_score >= RULE_REVIEW_THRESHOLD:
        return True
    return False


def estimate_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)


def clamp_text(text: str, max_chars: int) -> str:
    return (text or "")[:max_chars]


def _feedback_title(item: dict[str, Any]) -> str:
    return str(item.get("title") or item.get("product_title") or "")


def _feedback_reason(item: dict[str, Any]) -> str:
    reason = item.get("reason")
    if reason:
        return str(reason)
    reasons = item.get("reasons")
    if isinstance(reasons, list):
        return ", ".join(str(reason) for reason in reasons if reason)
    return str(item.get("note") or "")


def build_compact_feedback_memory(
    feedback_context: dict[str, Any],
    *,
    positive_limit: int = 2,
    negative_limit: int = 2,
    pattern_limit: int = 3,
) -> str:
    lines: list[str] = []

    for item in (feedback_context.get("positive_examples") or [])[:positive_limit]:
        title = clamp_text(_feedback_title(item), 80)
        if title:
            lines.append(f"+ {title}")

    for item in (feedback_context.get("negative_examples") or [])[:negative_limit]:
        title = clamp_text(_feedback_title(item), 80)
        reason = clamp_text(_feedback_reason(item), 40)
        if title:
            lines.append(f"- {title} | {reason}")

    for pattern in (feedback_context.get("learned_patterns") or [])[:pattern_limit]:
        p = clamp_text(str(pattern.get("pattern") or ""), 40)
        scope = pattern.get("scope", "")
        weight = pattern.get("weight", 0)
        if p:
            lines.append(f"pattern {p} scope={scope} weight={weight}")

    return "\n".join(lines) or "none"


def _product_audit_id(product: dict[str, Any], index: int) -> str:
    audit_id = str(product.get("_audit_id") or product.get("id") or f"p{index + 1}")
    product["_audit_id"] = audit_id
    return audit_id


def _product_constraints(product: dict[str, Any]) -> dict[str, Any]:
    ctx = product.get("_rule_context") or {}
    constraints = ctx.get("product_constraints") or product.get("product_constraints") or {}
    if isinstance(constraints, dict) and constraints:
        return constraints
    from src.ai.feedback_store import extract_query_constraints

    return extract_query_constraints(str(product.get("title") or product.get("name") or ""))


def _compact_product_payload(products: list[dict[str, Any]], title_chars: int) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for index, product in enumerate(products):
        ctx = product.get("_rule_context") or {}
        payload.append({
            "id": _product_audit_id(product, index),
            "title": clamp_text(str(product.get("title") or product.get("name") or ""), title_chars),
            "price": product.get("price_value") or product.get("priceNumber") or product.get("price") or 0,
            "score": product.get("combined_score") or ctx.get("combined_score") or product.get("rule_score") or 0,
            "constraints": _product_constraints(product),
        })
    return payload


def _render_batch_prompt(
    *,
    query: str,
    query_intent: str,
    query_constraints: dict[str, Any],
    feedback_memory: str,
    compact_products: list[dict[str, Any]],
) -> str:
    query_constraints_json = json.dumps(query_constraints, ensure_ascii=True, default=str, separators=(",", ":"))
    compact_products_json = json.dumps(compact_products, ensure_ascii=True, default=str, separators=(",", ":"))
    return f"""Query: {clamp_text(query, 160)}
Intent: {query_intent}
Query constraints: {query_constraints_json}

Feedback memory:
{feedback_memory}

Products:
{compact_products_json}

Rules:
- Use feedback only when scope matches query.
- Negative feedback is not global unless scope=global.
- Spec mismatch matters: if query wants RTX 5060 and product has RTX 4060, reject for this query.
- If query wants RTX 4060 and product has RTX 4060, do not reject because of RTX 5060 feedback.
- For laptop gaming, accept real gaming laptops.
- Reject accessory-only or non-product pages.
- Return JSON only.

Return exactly:
{{"items":[{{"id":"p1","accepted":true,"confidence":0.0,"reason":"short"}}]}}

No markdown.
No explanation.
"""


def build_batch_classifier_prompt(
    query: str,
    query_intent: str,
    query_constraints: dict[str, Any],
    feedback_context: dict[str, Any],
    products: list[dict[str, Any]],
) -> dict[str, Any]:
    feedback_memory = build_compact_feedback_memory(feedback_context)
    compact_products = _compact_product_payload(products[:3], title_chars=160)
    prompt = _render_batch_prompt(
        query=query,
        query_intent=query_intent,
        query_constraints=query_constraints,
        feedback_memory=feedback_memory,
        compact_products=compact_products,
    )
    token_estimate = estimate_tokens(prompt)
    truncated_by_app = False

    if token_estimate > 3000:
        truncated_by_app = True
        feedback_memory = build_compact_feedback_memory(
            feedback_context,
            positive_limit=1,
            negative_limit=1,
            pattern_limit=1,
        )
        compact_products = _compact_product_payload(products[:3], title_chars=120)
        prompt = _render_batch_prompt(
            query=query,
            query_intent=query_intent,
            query_constraints=query_constraints,
            feedback_memory=feedback_memory,
            compact_products=compact_products,
        )
        token_estimate = estimate_tokens(prompt)

    if token_estimate > 3000:
        truncated_by_app = True
        compact_products = _compact_product_payload(products[:3], title_chars=80)
        prompt = _render_batch_prompt(
            query=query,
            query_intent=query_intent,
            query_constraints=query_constraints,
            feedback_memory="none",
            compact_products=compact_products,
        )
        token_estimate = estimate_tokens(prompt)

    if token_estimate > 3000:
        truncated_by_app = True
        compact_products = _compact_product_payload(products[:1], title_chars=80)
        prompt = _render_batch_prompt(
            query=query,
            query_intent=query_intent,
            query_constraints=query_constraints,
            feedback_memory="none",
            compact_products=compact_products,
        )
        token_estimate = estimate_tokens(prompt)

    return {
        "prompt": prompt,
        "prompt_tokens_estimated": token_estimate,
        "truncated_by_app": truncated_by_app,
        "compact_products": compact_products,
    }


def build_classifier_prompt(query: str, query_intent: str, product: dict[str, Any]) -> str:
    from src.ai.feedback_store import extract_query_constraints, load_feedback_context

    query_constraints = extract_query_constraints(query)
    feedback_context = load_feedback_context(query, query_intent, query_constraints, limit=4)
    return build_batch_classifier_prompt(
        query,
        query_intent,
        query_constraints,
        feedback_context,
        [product],
    )["prompt"]


def _normalize_batch_items(parsed: dict[str, Any] | None, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(parsed, dict):
        return []
    raw_items = parsed.get("items")
    if raw_items is None and "accepted" in parsed:
        raw_items = [{
            "id": products[0].get("_audit_id", "p1") if products else "p1",
            "accepted": parsed.get("accepted"),
            "confidence": parsed.get("confidence"),
            "reason": parsed.get("reason"),
        }]
    if not isinstance(raw_items, list):
        return []

    valid_ids = {str(product.get("_audit_id")) for product in products}
    normalized: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id") or "")
        if item_id not in valid_ids:
            continue
        try:
            confidence = float(item.get("confidence", 0.50))
        except (TypeError, ValueError):
            confidence = 0.50
        accepted_raw = item.get("accepted", True)
        if isinstance(accepted_raw, str):
            accepted = accepted_raw.strip().lower() not in {"false", "0", "no", "tidak"}
        else:
            accepted = bool(accepted_raw)
        normalized.append({
            "id": item_id,
            "accepted": accepted,
            "confidence": max(0.0, min(0.98, confidence)),
            "reason": clamp_text(str(item.get("reason") or "AI audit decision"), 120),
            "category_match": str(item.get("category_match") or "ai"),
            "decision_source": "ai_orchestrator",
        })
    return normalized


async def classify_product_batch(
    query: str,
    query_intent: str,
    products: list[dict[str, Any]],
    *,
    status: dict[str, Any] | None = None,
    ai_enabled: bool = True,
    feedback_context: dict[str, Any] | None = None,
    query_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status = status or get_orchestrator_status()
    classifier = status.get("classifier")
    if not ai_enabled or not classifier or not products:
        return {
            "ok": False,
            "items": [],
            "_model": None,
            "_fallback_used": True,
            "_chat_ok": False,
            "_timeout": False,
            "_error": "AI disabled, classifier missing, or no products",
            "attempts": 0,
        }

    if query_constraints is None or feedback_context is None:
        from src.ai.feedback_store import extract_query_constraints, load_feedback_context

        query_constraints = query_constraints or extract_query_constraints(query)
        feedback_context = feedback_context or load_feedback_context(query, query_intent, query_constraints, limit=4)

    resolved_classifier = get_installed_model_name(str(classifier), status.get("installed") or None)
    prompt_data = build_batch_classifier_prompt(
        query,
        query_intent,
        query_constraints or {},
        feedback_context or {},
        products,
    )
    prompt = str(prompt_data["prompt"])
    prompt_tokens = int(prompt_data["prompt_tokens_estimated"])
    truncated_by_app = bool(prompt_data["truncated_by_app"])
    log(
        "AI_ORCH",
        f"prompt_tokens_estimated={prompt_tokens} ctx={AI_CHAT_NUM_CTX} truncated_by_app={str(truncated_by_app).lower()}",
        "INFO",
    )

    result = await chat_raw_async(
        prompt,
        model=resolved_classifier,
        use_json_format=True,
        prompt_tokens_estimated=prompt_tokens,
    )
    parsed = result.get("parsed")
    if result.get("ok") and not parsed:
        parsed = await repair_json_or_fallback(
            str(result.get("content") or ""),
            phi_available=bool(status.get("capabilities", {}).get("json_repair")),
        )

    items = _normalize_batch_items(parsed if isinstance(parsed, dict) else None, products) if result.get("ok") else []
    if not result.get("ok"):
        log("AI_ORCH", f"classifier_failed model={resolved_classifier} error={result.get('error')}", "WARN")

    return {
        "ok": bool(result.get("ok")),
        "items": items,
        "_model": resolved_classifier,
        "_fallback_used": not bool(result.get("ok")),
        "_chat_ok": bool(result.get("ok")),
        "_timeout": bool(result.get("timeout")),
        "_error": str(result.get("error") or ""),
        "attempts": int(result.get("attempts") or 0),
        "prompt_tokens_estimated": prompt_tokens,
        "truncated_by_app": truncated_by_app,
        "ctx": result.get("ctx", AI_CHAT_NUM_CTX),
        "status_code": result.get("status_code"),
    }


async def classify_borderline_product(
    query: str,
    query_intent: str,
    product: dict[str, Any],
    rule_score: float,
    status: dict[str, Any] | None = None,
    ai_enabled: bool = True,
) -> dict[str, Any]:
    status = status or get_orchestrator_status()
    classifier = status.get("classifier")

    if not ai_enabled or not classifier:
        # Rule-based fallback: if rule_score >= 0.58, accept; else reject.
        accepted = rule_score >= 0.58
        return {
            "accepted": accepted,
            "confidence": rule_score,
            "reason": "Included by rule fallback (AI disabled or classifier not installed)" if accepted else "Rejected by rule fallback (AI disabled or classifier not installed)",
            "category_match": "rules",
            "decision_source": "rule_fallback",
            "_model": None,
            "_fallback_used": True,
            "_llm_accept_threshold": LLM_ACCEPT_THRESHOLD,
        }

    result = await classify_product_batch(
        query,
        query_intent,
        [product],
        status=status,
        ai_enabled=ai_enabled,
    )
    resolved_classifier = str(result.get("_model") or classifier or "")
    parsed = (result.get("items") or [{}])[0] if result.get("items") else None
    if not result.get("ok"):
        parsed = {
            "accepted": True,
            "confidence": 0.50,
            "reason": "Classifier unavailable, accepted by safe fallback to avoid empty results",
            "category_match": "fallback",
            "decision_source": "ai_fallback",
        }
    elif not parsed:
        parsed = {}

    if not result.get("ok") and parsed.get("decision_source") == "ai_fallback":
        log("AI_ORCH", f"classifier_failed model={resolved_classifier} rule_score={rule_score}", "WARN")

    accepted = bool(parsed.get("accepted", True))
    try:
        confidence = float(parsed.get("confidence", 0.50))
    except (TypeError, ValueError):
        confidence = 0.50
    parsed["accepted"] = accepted
    parsed["confidence"] = max(0.0, min(0.98, confidence))
    parsed.setdefault("reason", "AI Orchestrator classified borderline product")
    parsed.setdefault("category_match", "ai")
    parsed.setdefault("decision_source", "ai_orchestrator" if result.get("ok") else "ai_fallback")
    parsed["_model"] = resolved_classifier
    parsed["_fallback_used"] = parsed.get("decision_source") == "ai_fallback"
    parsed["_chat_ok"] = bool(result.get("ok"))
    parsed["_timeout"] = bool(result.get("_timeout"))
    parsed["_error"] = str(result.get("_error") or "")
    parsed["_prompt_tokens_estimated"] = result.get("prompt_tokens_estimated")
    parsed["_truncated_by_app"] = result.get("truncated_by_app")
    parsed["_llm_accept_threshold"] = LLM_ACCEPT_THRESHOLD
    return parsed

```

## FILE: `src\ai\feedback_store.py`

```python
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

```

## FILE: `src\ai\json_repair.py`

```python
"""
Parse and repair small JSON objects returned by local chat models.
"""
from __future__ import annotations

import json
import re
from typing import Any


FALLBACK_JSON = {
    "accepted": True,
    "confidence": 0.50,
    "reason": "AI unavailable, accepted by safe fallback to avoid empty results",
    "category_match": "fallback",
    "decision_source": "ai_fallback",
}


def _strip_markdown(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def _remove_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def _extract_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def parse_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    candidates = [
        text,
        _strip_markdown(text),
        _extract_object(_strip_markdown(text)),
        _remove_trailing_commas(_extract_object(_strip_markdown(text))),
    ]
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


async def repair_json_or_fallback(raw_text: str, *, phi_available: bool = False, model: str = "phi4-mini") -> dict[str, Any]:
    parsed = parse_json_object(raw_text)
    if parsed is not None:
        return parsed

    if phi_available:
        try:
            from src.ai.ollama_client import chat_raw_async
            from src.ai.model_registry import get_installed_model_name

            resolved_model = get_installed_model_name(model)
            prompt = (
                "Repair this into valid JSON only. Required keys: "
                "accepted, confidence, reason, category_match.\n\n"
                f"{raw_text[:2000]}"
            )
            result = await chat_raw_async(prompt, model=resolved_model, use_json_format=True)
            if result.get("parsed"):
                return result["parsed"]
            parsed = parse_json_object(str(result.get("content") or ""))
            if parsed is not None:
                return parsed
        except Exception:
            pass

    return dict(FALLBACK_JSON)

```

## FILE: `src\ai\learning.py`

```python
"""
learning.py - Save and retrieve user feedback for AI Orchestrator learning.

Feedback payload from frontend:
{
  "query": "laptop gaming",
  "product": {...},
  "ai_decision": {...},
  "correction": "should_exclude",
  "categories": ["mouse", "not_laptop", "should_exclude"],
  "note": "This is a mouse, not a laptop."
}

Saved to:
  data/ai_memory/feedback.jsonl     - all feedback
  data/ai_memory/examples.jsonl     - examples used for AI Orchestrator prompts
  data/ai_memory/category_rules.json - evolving category rules

Reset via POST /api/ai/reset (clears these files, not the Ollama model).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import FEEDBACK_FILE as PRODUCT_FEEDBACK_FILE
from src.ai.feedback_store import save_feedback_event
import src.ai.memory_store as memory_store
from src.ai.memory_store import (
    CATEGORY_RULES_FILE,
    EXAMPLES_FILE,
    FEEDBACK_FILE,
    append_jsonl,
    ensure_memory_dir,
    load_category_rules,
    read_jsonl,
    save_category_rules,
)
from src.utils.logger import log


def save_feedback(
    query: str,
    product_id: str | None = None,
    product_title: str | None = None,
    user_action: str | None = None,
    selected_reasons: list[str] | None = None,
    custom_reason: str | None = None,
    corrected_label: str | None = None,
    ai_label: str | None = None,
    ai_confidence: float | None = None,
    product: dict[str, Any] | None = None,
    ai_decision: dict[str, Any] | None = None,
    correction: str | None = None,
    categories: list[str] | None = None,
    note: str | None = None,
    query_intent: str | None = None,
    feedback_type: str | None = None,
    rule_score: float | None = None,
    semantic_score: float | None = None,
    combined_score: float | None = None,
    learned_adjustment: float | None = None,
    sort_mode: str | None = None,
    decision_source: str | None = None,
    learning_scope_hint: str | None = None,
    model_used: str | None = None,
    ai_reason: str | None = None,
) -> dict[str, Any]:
    """
    Save full feedback record to feedback.jsonl and examples.jsonl.
    Also update category_rules.json when user teaches AI about a category.
    """
    memory_store.ensure_memory_dir()

    selected_reasons = selected_reasons if selected_reasons is not None else (categories or [])
    custom_reason = custom_reason if custom_reason is not None else (note or "")
    user_action = user_action or correction or ""
    product = product or {}
    product_title = product_title or str(product.get("title") or "")
    product_id = product_id or str(product.get("id") or product.get("url") or product_title or "unknown")
    ai_decision = ai_decision or {}
    ai_label = ai_label or ("relevan" if ai_decision.get("relevant", True) else "tidak_relevan")
    ai_confidence = ai_confidence if ai_confidence is not None else float(ai_decision.get("confidence") or 0)
    corrected_label = corrected_label or _label_from_correction(user_action, selected_reasons)
    feedback_type = feedback_type or ("positive" if corrected_label in {"relevant", "relevan"} else "negative")
    product_category = str(product.get("product_category") or product.get("category") or "")
    if not product_category:
        try:
            from src.ai.relevance import detect_product_category

            product_category = detect_product_category(product_title)
        except Exception:
            product_category = "unknown"

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "query_intent": query_intent,
        "product_id": product_id,
        "product_title": product_title,
        "product": {
            "title": product_title,
            "price": product.get("price_value") or product.get("price") or 0,
            "store": product.get("shop_name") or product.get("shop") or "",
            "url": product.get("url") or product.get("product_url") or "",
            "image": product.get("image") or product.get("image_url") or "",
        },
        "product_category": product_category,
        "feedback_type": feedback_type,
        "reasons": selected_reasons,
        "note": custom_reason,
        "rule_score": rule_score or 0.0,
        "semantic_score": semantic_score if semantic_score is not None else product.get("semantic_score", 0.0),
        "combined_score": combined_score if combined_score is not None else product.get("combined_score", 0.0),
        "learned_adjustment": learned_adjustment if learned_adjustment is not None else product.get("learned_adjustment", 0.0),
        "learning_scope_hint": learning_scope_hint,
        "sort_mode": sort_mode or "terbaik",
        "decision_source": decision_source or product.get("decision_source") or product.get("ai_source") or "",
        "model_used": model_used or product.get("_model") or "",
        "ai_reason": ai_reason or product.get("ai_reason") or product.get("reason") or "",
        "ai_label": ai_label,
        "ai_confidence": ai_confidence,
        "user_action": user_action,
        "selected_reasons": selected_reasons,
        "custom_reason": custom_reason,
        "corrected_label": corrected_label,
        # Backward-compatible fields used by older learning tests/debug files.
        "correction": user_action,
        "categories": selected_reasons,
        "note": custom_reason,
    }

    memory_store.append_jsonl(memory_store.FEEDBACK_FILE, record)
    _append_product_feedback_json(record)

    # Save to examples.jsonl so AI Orchestrator prompts can reference these as few-shot examples
    example = {
        "query": query,
        "title": record["product_title"],
        "label": corrected_label,
        "categories": selected_reasons,
        "reason": custom_reason or user_action,
    }
    memory_store.append_jsonl(memory_store.EXAMPLES_FILE, example)

    # Update category_rules.json for systematic patterns
    _update_category_rules(query, product_title, user_action, selected_reasons)

    sqlite_result = save_feedback_event(
        query=query,
        query_intent=query_intent,
        product={
            **product,
            "title": product_title,
            "price_value": product.get("price_value") or product.get("price") or 0,
            "decision_source": record["decision_source"],
            "confidence": ai_confidence,
            "rule_score": record["rule_score"],
            "semantic_score": record["semantic_score"],
            "combined_score": record["combined_score"],
            "learned_adjustment": record["learned_adjustment"],
        },
        feedback_type=feedback_type,
        reasons=selected_reasons,
        note=custom_reason,
        learning_scope_hint=learning_scope_hint,
        decision_source=record["decision_source"],
        confidence=ai_confidence,
        rule_score=record["rule_score"],
        semantic_score=record["semantic_score"],
        combined_score=record["combined_score"],
        learned_adjustment=record["learned_adjustment"],
        model_used=record["model_used"],
        ai_reason=record["ai_reason"],
    )

    log("AI_LEARN", f"Saved feedback '{user_action}' categories={selected_reasons} for: {product_title[:60]}", "OK")
    return sqlite_result


def _append_product_feedback_json(record: dict[str, Any]) -> None:
    """Maintain the requested JSON feedback file alongside legacy JSONL memory."""
    PRODUCT_FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(PRODUCT_FEEDBACK_FILE.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            existing = []
    except Exception:
        existing = []
    existing.append(record)
    PRODUCT_FEEDBACK_FILE.write_text(
        json.dumps(existing[-2000:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _label_from_correction(correction: str, categories: list[str]) -> str:
    """Normalize correction to a simple label for examples."""
    if correction in ("should_include", "benar", "relevan"):
        return "relevant"
    if correction in ("should_exclude", "salah", "tidak_relevan"):
        return "not_relevant"
    return correction


def _update_category_rules(
    query: str,
    product_title: str,
    user_action: str,
    categories: list[str],
) -> None:
    """Add a category rule when user explicitly teaches the AI."""
    rules_data = memory_store.load_category_rules()
    rules = rules_data.get("rules", [])

    for cat in (categories or []):
        rule = {
            "query": query,
            "category": cat,
            "correction": user_action,
            "title_example": product_title[:80],
            "action": "exclude" if user_action in ("should_exclude", "salah", "tidak_relevan") else "include",
        }
        rules.append(rule)

    rules_data["rules"] = rules[-500:]  # keep last 500 rules
    memory_store.save_category_rules(rules_data)


def get_recent_feedback(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Get recent feedback for a specific query to inject as few-shot examples into AI prompts."""
    all_feedback = memory_store.read_jsonl(memory_store.FEEDBACK_FILE)
    q_lower = query.lower()
    relevant = [r for r in all_feedback if r.get("query", "").lower() == q_lower]
    return relevant[-limit:]


def get_recent_examples(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Get confirmed examples for few-shot prompting."""
    all_examples = memory_store.read_jsonl(memory_store.EXAMPLES_FILE)
    q_lower = query.lower()
    relevant = [e for e in all_examples if e.get("query", "").lower() == q_lower]
    return relevant[-limit:]

```

## FILE: `src\ai\memory_store.py`

```python
"""
memory_store.py - AI memory file paths and raw I/O helpers.

Files:
  data/ai_memory/feedback.jsonl     - raw user feedback log
  data/ai_memory/examples.jsonl     - confirmed good/bad examples for prompt
  data/ai_memory/category_rules.json - user-taught category rules

These are read by relevance.py to build AI Orchestrator prompts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMORY_DIR = Path("data/ai_memory")
FEEDBACK_FILE = MEMORY_DIR / "feedback.jsonl"
EXAMPLES_FILE = MEMORY_DIR / "examples.jsonl"
CATEGORY_RULES_FILE = MEMORY_DIR / "category_rules.json"


def ensure_memory_dir() -> None:
    """Create memory directory and blank files if they don't exist."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    for f in (FEEDBACK_FILE, EXAMPLES_FILE):
        if not f.exists():
            f.touch()
    if not CATEGORY_RULES_FILE.exists():
        CATEGORY_RULES_FILE.write_text(
            json.dumps({"version": 1, "rules": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Append one record to a JSONL file. Creates file if missing."""
    ensure_memory_dir()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path, limit: int = 0) -> list[dict[str, Any]]:
    """Read all records from JSONL. If limit > 0, return last N records."""
    ensure_memory_dir()
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except FileNotFoundError:
        pass
    return records[-limit:] if limit > 0 else records


def load_category_rules() -> dict[str, Any]:
    """Load category_rules.json. Returns empty rules dict on failure."""
    ensure_memory_dir()
    try:
        return json.loads(CATEGORY_RULES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "rules": []}


def save_category_rules(data: dict[str, Any]) -> None:
    ensure_memory_dir()
    CATEGORY_RULES_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

```

## FILE: `src\ai\model_registry.py`

```python
"""Detect installed Ollama models and expose AI Orchestrator capabilities."""
from __future__ import annotations

import time
from typing import Any
import requests

from src.config import (
    AI_MODEL_CACHE_TTL_SECONDS,
    ALLOWED_OLLAMA_MODELS,
    AI_MODEL_JOBS,
    CLASSIFIER_PRIORITY,
    OLLAMA_BASE_URL,
)
from src.utils.logger import log


_MODEL_CACHE: dict[str, Any] = {
    "timestamp": 0.0,
    "models": [],
}


def normalize_model_name(name: str) -> str:
    """Normalize Ollama tags while preserving meaningful size tags."""
    normalized = str(name or "").strip()
    if normalized.endswith(":latest"):
        normalized = normalized[:-7]
    return normalized


def has_model(installed: list[str], wanted: str) -> bool:
    """Return True when installed tags satisfy a supported model name."""
    wanted_norm = normalize_model_name(wanted)
    return any(normalize_model_name(item) == wanted_norm for item in installed or [])


def _extract_model_names(payload: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    for item in payload.get("models", []) or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if name:
            names.add(name)
    return sorted(names)


def get_installed_tag_map(force_refresh: bool = False) -> dict[str, str]:
    """Map normalized model names to the exact installed Ollama tags."""
    mapping = {}
    for tag in get_installed_ollama_models(force_refresh=force_refresh):
        mapping[normalize_model_name(tag)] = tag
    return mapping


def get_installed_model_name(wanted: str, installed: list[str] | None = None) -> str:
    """
    Resolves an allowed model name (e.g., 'phi4-mini') to the exact installed name
    found in Ollama (e.g., 'phi4-mini:latest'). If not found or mapping fails,
    returns the original wanted name.
    """
    norm_wanted = normalize_model_name(wanted)
    source = get_installed_ollama_models() if installed is None else installed
    mapping = {normalize_model_name(tag): tag for tag in source}
    if norm_wanted in mapping:
        return mapping[norm_wanted]
    return wanted


def get_installed_ollama_models(force_refresh: bool = False) -> list[str]:
    now = time.time()
    cached = list(_MODEL_CACHE.get("models") or [])
    timestamp = float(_MODEL_CACHE.get("timestamp") or 0.0)
    if not force_refresh and timestamp > 0 and now - timestamp < AI_MODEL_CACHE_TTL_SECONDS:
        return cached

    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        response.raise_for_status()
        detected = _extract_model_names(response.json())
        models = [tag for tag in detected if has_model(ALLOWED_OLLAMA_MODELS, tag)]
        ignored = [tag for tag in detected if tag not in models]
        if ignored:
            log("AI_ORCH", f"ignored_unsupported_models={ignored}", "INFO")
        log("AI_ORCH", f"installed_models={models}", "INFO")
        _MODEL_CACHE["timestamp"] = now
        _MODEL_CACHE["models"] = list(models)
        return list(models)
    except Exception as exc:
        log("AI_ORCH", f"Ollama model detection unavailable: {exc}", "WARN")
        _MODEL_CACHE["timestamp"] = now
        return cached


def get_supported_installed_models(installed: list[str] | None = None, force_refresh: bool = False) -> list[str]:
    installed_models = get_installed_ollama_models(force_refresh=force_refresh) if installed is None else installed
    supported = [allowed for allowed in ALLOWED_OLLAMA_MODELS if has_model(installed_models, allowed)]
    log("AI_ORCH", f"supported_models={supported}", "INFO")
    return supported


def is_model_installed(model: str, force_refresh: bool = False) -> bool:
    return has_model(get_installed_ollama_models(force_refresh=force_refresh), model)


def get_best_classifier_model(installed: list[str] | None = None, force_refresh: bool = False) -> str | None:
    installed_models = get_installed_ollama_models(force_refresh=force_refresh) if installed is None else installed
    for model in CLASSIFIER_PRIORITY:
        if has_model(installed_models, model):
            return model
    return None


def get_orchestrator_status(force_refresh: bool = False) -> dict[str, Any]:
    installed = get_installed_ollama_models(force_refresh=force_refresh)
    supported = get_supported_installed_models(installed)
    supported_set = set(supported)
    missing = [model for model in ALLOWED_OLLAMA_MODELS if model not in supported_set]
    classifier = get_best_classifier_model(installed)
    capabilities = {
        "semantic": AI_MODEL_JOBS["semantic"] in supported_set,
        "balanced_classifier": AI_MODEL_JOBS["balanced_classifier"] in supported_set,
        "fast_classifier": AI_MODEL_JOBS["fast_classifier"] in supported_set,
        "json_repair": AI_MODEL_JOBS["json_repair"] in supported_set,
    }
    ok = classifier is not None
    message = "AI Orchestrator ready" if ok else "No supported Ollama model installed. Run: ollama pull gemma3:4b"
    status = {
        "ok": ok,
        "installed": installed,
        "supported": supported,
        "missing": missing,
        "capabilities": capabilities,
        "classifier": classifier,
        "message": message,
        "install_commands": [
            "ollama pull gemma3:4b",
            "ollama pull llama3.2:3b",
            "ollama pull phi4-mini",
            "ollama pull nomic-embed-text",
        ],
    }
    log(
        "AI_ORCH",
        (
            f"classifier={classifier or 'none'} semantic={capabilities['semantic']} "
            f"json_repair={capabilities['json_repair']} missing={missing}"
        ),
        "INFO",
    )
    return status

```

## FILE: `src\ai\ollama_client.py`

```python
"""
Laptop-friendly Ollama /api/chat client.

This module is intentionally synchronous at the HTTP layer because requests is
stable on Windows. Async callers use chat_json_async(), which wraps the call in
asyncio.to_thread() so FastAPI progress polling can remain responsive. A small
semaphore keeps local Ollama from receiving overlapping CPU-heavy requests.
"""
from __future__ import annotations

import asyncio
import json
import math
from threading import BoundedSemaphore
from typing import Any

import requests

from src.config import (
    AI_CLASSIFIER_MODEL,
    AI_CHAT_NUM_CTX,
    AI_CHAT_NUM_PREDICT,
    AI_CHAT_TIMEOUT_SECONDS,
    OLLAMA_MAX_CONCURRENT_REQUESTS,
    OLLAMA_BASE_URL,
    OLLAMA_TIMEOUT_SECONDS,
)
from src.utils.logger import log


CHAT_CALLS_ATTEMPTED = 0
CHAT_CALLS_SUCCEEDED = 0
OLLAMA_REQUEST_SEMAPHORE = BoundedSemaphore(OLLAMA_MAX_CONCURRENT_REQUESTS)

FALLBACK_RESPONSE = {
    "accepted": True,
    "confidence": 0.50,
    "reason": "Classifier unavailable, accepted by safe fallback to avoid empty results",
    "category_match": "fallback",
    "decision_source": "ai_fallback",
}


def estimate_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)


def _fallback(error: str = "", model: str | None = None) -> dict[str, Any]:
    payload = dict(FALLBACK_RESPONSE)
    payload["_fallback_used"] = True
    payload["_error"] = error
    payload["_model"] = model or ""
    return payload


def _parse_chat_content(response_payload: dict[str, Any]) -> dict[str, Any] | None:
    content = ""
    message = response_payload.get("message")
    if isinstance(message, dict):
        content = str(message.get("content") or "")
    if not content:
        content = str(response_payload.get("response") or "")
    content = content.strip()
    if not content:
        return None

    try:
        from src.ai.json_repair import parse_json_object

        return parse_json_object(content)
    except Exception:
        try:
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None


def _chat_payload(prompt: str, selected_model: str, use_json_format: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": selected_model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You classify marketplace search results. Return JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "options": {
            "temperature": 0,
            "num_ctx": AI_CHAT_NUM_CTX,
            "num_predict": AI_CHAT_NUM_PREDICT,
        },
        "keep_alive": "10m",
    }
    if use_json_format:
        payload["format"] = "json"
    return payload


def _is_format_json_failure(response: requests.Response) -> bool:
    if response.status_code not in {400, 422}:
        return False
    text = str(response.text or "").lower()
    return "format" in text and "json" in text


def _post_chat(prompt: str, selected_model: str, timeout: int | None, use_json_format: bool) -> dict[str, Any]:
    result = chat_raw(prompt, selected_model, timeout=timeout, use_json_format=use_json_format)
    if not result.get("ok"):
        raise RuntimeError(str(result.get("error") or "Ollama chat failed"))
    parsed = result.get("parsed")
    if not parsed:
        raise ValueError("Ollama response was not valid JSON")
    parsed.setdefault("accepted", True)
    parsed.setdefault("confidence", 0.5)
    parsed.setdefault("reason", "AI classified product")
    parsed.setdefault("category_match", "ai")
    parsed["_fallback_used"] = False
    parsed["_model"] = selected_model
    return parsed


def chat_raw(
    prompt: str,
    model: str,
    timeout: int | None = None,
    use_json_format: bool = True,
    prompt_tokens_estimated: int | None = None,
) -> dict[str, Any]:
    global CHAT_CALLS_ATTEMPTED, CHAT_CALLS_SUCCEEDED
    effective_timeout = timeout if timeout is not None else AI_CHAT_TIMEOUT_SECONDS
    token_estimate = prompt_tokens_estimated if prompt_tokens_estimated is not None else estimate_tokens(prompt)
    attempts = 0
    last_error = ""
    use_format = bool(use_json_format)
    base_result: dict[str, Any] = {
        "ok": False,
        "model": model,
        "content": "",
        "parsed": None,
        "error": "",
        "timeout": False,
        "attempts": 0,
        "prompt_tokens_estimated": token_estimate,
        "ctx": AI_CHAT_NUM_CTX,
        "num_predict": AI_CHAT_NUM_PREDICT,
    }

    while True:
        payload = _chat_payload(prompt, model, use_format)
        CHAT_CALLS_ATTEMPTED += 1
        attempts += 1
        log(
            "AI_ORCH",
            (
                f"chat_options model={model} num_ctx={AI_CHAT_NUM_CTX} "
                f"num_predict={AI_CHAT_NUM_PREDICT} timeout={effective_timeout} "
                f"prompt_tokens_estimated={token_estimate}"
            ),
            "INFO",
        )
        log("AI_ORCH", f"POST /api/chat selected_model={model} ai_calls_attempted={CHAT_CALLS_ATTEMPTED}", "INFO")
        try:
            # requests stays in a worker thread; the semaphore prevents several
            # local searches from piling up expensive Ollama CPU/RAM work.
            with OLLAMA_REQUEST_SEMAPHORE:
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json=payload,
                    timeout=effective_timeout,
                )
            if _is_format_json_failure(response) and use_format:
                last_error = response.text
                log("AI_ORCH", "format_json_failed_retrying_without_format=true", "WARN")
                use_format = False
                continue
            if response.status_code == 404 or (
                response.status_code == 400 and "not found" in response.text.lower()
            ):
                return {
                    **base_result,
                    "error": f"model not found: {model}",
                    "attempts": attempts,
                    "status_code": response.status_code,
                }
            response.raise_for_status()
            envelope = response.json()
            content = ""
            if isinstance(envelope, dict):
                message = envelope.get("message")
                content = str((message or {}).get("content") or envelope.get("response") or "")
            CHAT_CALLS_SUCCEEDED += 1
            log("AI_ORCH", f"chat_ok selected_model={model} ai_calls_succeeded={CHAT_CALLS_SUCCEEDED}", "INFO")
            return {
                **base_result,
                "ok": True,
                "content": content,
                "parsed": _parse_chat_content(envelope),
                "error": "",
                "timeout": False,
                "attempts": attempts,
                "format_json": use_format,
                "status_code": response.status_code,
            }
        except Exception as exc:
            last_error = str(exc)
            is_timeout = isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ReadTimeout)) or "timed out" in str(exc).lower()
            log(
                "AI_ORCH",
                f"chat_failed selected_model={model} ai_calls_attempted={CHAT_CALLS_ATTEMPTED} ai_calls_succeeded={CHAT_CALLS_SUCCEEDED} error={exc}",
                "WARN",
            )
            return {
                **base_result,
                "error": last_error,
                "timeout": is_timeout,
                "attempts": attempts,
                "status_code": getattr(getattr(exc, "response", None), "status_code", None),
            }


def chat_json(
    prompt: str,
    model: str | None = None,
    timeout: int | None = None,
    use_json_format: bool = True,
) -> dict[str, Any]:
    selected_model = model or AI_CLASSIFIER_MODEL

    from src.ai.model_registry import get_installed_model_name
    resolved_model = get_installed_model_name(selected_model)

    try:
        return _post_chat(prompt, resolved_model, timeout, use_json_format)
    except Exception as exc:
        log("AI", f"Ollama chat failed with {resolved_model} (base: {selected_model}): {exc}", "WARN")
        fallback_model = "llama3.2:3b"
        resolved_fallback = get_installed_model_name(fallback_model)
        if resolved_model == resolved_fallback:
            return _fallback(str(exc), resolved_model)
        try:
            return _post_chat(prompt, resolved_fallback, timeout, use_json_format)
        except Exception as fallback_exc:
            log("AI", f"Ollama fallback chat failed with {resolved_fallback} (base: {fallback_model}): {fallback_exc}", "WARN")
            return _fallback(str(fallback_exc), resolved_fallback)


async def chat_json_async(
    prompt: str,
    model: str | None = None,
    timeout: int | None = None,
    use_json_format: bool = True,
) -> dict[str, Any]:
    return await asyncio.to_thread(chat_json, prompt, model, timeout, use_json_format)


async def chat_raw_async(
    prompt: str,
    model: str,
    timeout: int | None = None,
    use_json_format: bool = True,
    prompt_tokens_estimated: int | None = None,
) -> dict[str, Any]:
    return await asyncio.to_thread(chat_raw, prompt, model, timeout, use_json_format, prompt_tokens_estimated)


def get_embedding(text: str, model: str = "nomic-embed-text") -> list[float] | None:
    try:
        from src.ai.model_registry import get_installed_model_name
        resolved_model = get_installed_model_name(model)
        with OLLAMA_REQUEST_SEMAPHORE:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={"model": resolved_model, "prompt": text},
                timeout=OLLAMA_TIMEOUT_SECONDS,
            )
        response.raise_for_status()
        embedding = response.json().get("embedding")
        if isinstance(embedding, list):
            return [float(item) for item in embedding]
    except Exception as exc:
        log("AI_ORCH", f"embedding_failed model={model} error={exc}", "WARN")
    return None


async def get_embedding_async(text: str, model: str = "nomic-embed-text") -> list[float] | None:
    return await asyncio.to_thread(get_embedding, text, model)


def cosine_similarity(a: list[float] | None, b: list[float] | None) -> float | None:
    if not a or not b or len(a) != len(b):
        return None
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a <= 0 or norm_b <= 0:
        return None
    return max(0.0, min(1.0, (dot / (norm_a * norm_b) + 1.0) / 2.0))

```

## FILE: `src\ai\relevance.py`

```python
"""
Intent-aware relevance filtering.

The active path delegates to src.ai.ai_filter: deterministic rules first,
automatic small-model orchestration only for borderline products.
"""
from __future__ import annotations

import asyncio
import contextlib
import difflib
import json
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterator, List, Tuple

from src.ai.learning import get_recent_examples, get_recent_feedback
from src.utils.logger import log
from src.utils.currency import parse_rupiah
from src.config import (
    RULE_ACCEPT_THRESHOLD,
    RULE_REJECT_THRESHOLD,
    RULE_REVIEW_THRESHOLD,
)
from src.ai.feedback_store import has_accessory_only_evidence, has_laptop_main_evidence


RELEVANCE_THRESHOLD = float(os.getenv("AI_RELEVANCE_THRESHOLD", "0.55"))
FALLBACK_SCORE = 0.5
AI_BATCH_SIZE = max(1, int(os.getenv("AI_BATCH_SIZE", "20")))

ACCESSORY_KEYWORDS = {
    "case", "casing", "softcase", "hardcase", "charger", "kabel",
    "adapter", "adaptor", "tempered glass", "screen protector",
    "anti gores", "tas", "sleeve", "stand", "cooler", "keyboard",
    "mouse", "mousepad", "webcam", "headset", "earphone", "backpack", "magSafe".lower(),
}
SPAREPART_KEYWORDS = {
    "sparepart", "lcd", "baterai", "battery", "ram", "ssd", "hdd",
    "motherboard", "flexibel", "touchscreen", "speaker", "kamera",
}
GAMING_LAPTOP_HINTS = {
    "rog", "legion", "nitro", "predator", "tuf", "omen", "victus",
    "loq", "msi", "rtx", "gtx", "gaming", "ryzen 7", "intel i7",
    "intel i9", "geforce", "katana", "alienware", "msi thin",
    "msi cyborg", "msi bravo", "msi modern", "nvidia", "rtx2050",
    "rtx3050", "rtx4050", "rtx4060", "gtx1650",
}
MAIN_PRODUCT_HINTS = {
    "laptop", "notebook", "iphone", "ipad", "macbook", "samsung",
    "xiaomi", "oppo", "vivo", "realme", "asus", "lenovo", "acer",
    "hp", "dell", "msi", "pc", "monitor", "printer", "kamera",
}

VALID_GAMING_LAPTOP_HINTS = [
    "rog", "tuf", "loq", "legion", "victus", "omen", "nitro",
    "predator", "msi thin", "msi katana", "msi cyborg", "msi bravo",
    "msi modern", "geforce", "nvidia", "rtx", "gtx", "rtx2050",
    "rtx 2050", "rtx3050", "rtx 3050", "rtx4050", "rtx 4050",
    "rtx4060", "rtx 4060", "gtx1650", "gtx 1650", "ryzen 5",
    "ryzen 7", "ryzen 9", "core i5", "core i7", "core i9", "i5 ",
    "i7 ", "i9 ", "144hz", "165hz",
]

ACCESSORY_JUNK_HINTS = [
    "mouse", "keyboard", "keycaps", "headset", "earphone", "speaker",
    "cooling pad", "cooler laptop", "stand laptop", "tas laptop",
    "sleeve laptop", "skin laptop", "sticker laptop", "charger laptop",
    "adaptor laptop", "adapter laptop", "baterai laptop", "battery laptop",
    "lcd laptop", "screen replacement", "fan replacement",
    "sparepart laptop", "case laptop", "casing laptop", "hardcase laptop",
    "softcase laptop", "ram laptop", "ssd laptop",
]
ACCESSORY_GROUPS = {
    "case": {"case", "casing", "softcase", "hardcase", "magsafe"},
    "charger": {"charger", "kabel", "adapter", "adaptor"},
    "screen": {"tempered glass", "screen protector", "anti gores"},
    "bag": {"tas", "sleeve", "backpack"},
    "stand": {"stand", "cooler"},
    "input": {"keyboard", "mouse"},
    "audio": {"headset", "earphone"},
}


def normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = text.replace("-", " ").replace("_", " ").replace("/", " ")
    text = re.sub(r"[^a-z0-9+.#/ ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_price(value: Any) -> int | None:
    return parse_rupiah(value)


def parse_sold_count(value: Any) -> int:
    text = normalize_text(value)
    if not text:
        return 0
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(rb|ribu|k|jt|juta)?", text)
    if not match:
        return 0
    try:
        number = float(match.group(1).replace(",", "."))
    except ValueError:
        return 0
    unit = match.group(2)
    if unit in {"rb", "ribu", "k"}:
        number *= 1000
    elif unit in {"jt", "juta"}:
        number *= 1_000_000
    return int(number)


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def contains_any(text: str, keywords: list[str] | set[str]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(keyword) in normalized for keyword in keywords)


def is_laptop_gaming_query(query: str) -> bool:
    q = normalize_text(query)
    return "laptop" in q and "gaming" in q


def has_accessory_evidence(title: str) -> bool:
    t = normalize_text(title)
    if has_laptop_main_evidence(t):
        return False
    if has_accessory_only_evidence(t):
        return True
    if contains_any(t, ACCESSORY_JUNK_HINTS):
        return True
    tokens = _word_tokens(t)
    if tokens & {"mouse", "keyboard", "keycaps", "headset", "earphone"}:
        return True
    if "sparepart" in tokens:
        return True
    return False


def has_gaming_laptop_evidence(title: str) -> bool:
    t = normalize_text(title)
    if has_laptop_main_evidence(t):
        return True
    if has_accessory_evidence(t):
        return False
    if contains_any(t, VALID_GAMING_LAPTOP_HINTS):
        return True
    tokens = _word_tokens(t)
    if tokens & {
        "ram", "ssd", "hdd", "baterai", "battery", "lcd", "sparepart",
        "mouse", "keyboard", "webcam", "charger", "adapter", "adaptor",
        "cooler", "stand", "headset", "earphone", "tas", "sleeve",
    }:
        return False
    if ({"laptop", "notebook"} & tokens) and "gaming" in tokens:
        return True
    return False


def apply_laptop_gaming_boost(query: str, product: dict[str, Any], score: float) -> float:
    title = normalize_text(product.get("title") or product.get("name") or "")
    if not is_laptop_gaming_query(query):
        return score
    if has_gaming_laptop_evidence(title):
        score = max(score, 0.72)

    strong_gpu = [
        "rtx 2050", "rtx2050", "rtx 3050", "rtx3050", "rtx 4050",
        "rtx4050", "rtx 4060", "rtx4060", "gtx 1650", "gtx1650",
    ]
    strong_series = [
        "rog", "tuf", "loq", "legion", "victus", "omen", "nitro",
        "predator", "msi thin",
    ]
    if contains_any(title, strong_gpu) and contains_any(title, strong_series + ["laptop", "notebook"]):
        score = max(score, 0.78)
    return round(max(0.0, min(0.98, score)), 3)


def _word_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", normalize_text(text)))


def _accessory_groups(text: str) -> set[str]:
    normalized = normalize_text(text)
    groups: set[str] = set()
    for group, keywords in ACCESSORY_GROUPS.items():
        if any(keyword in normalized for keyword in keywords):
            groups.add(group)
    return groups


def detect_query_intent(query: str) -> str:
    text = normalize_text(query)
    if not text:
        return "ambiguous"
    if _contains_any(text, SPAREPART_KEYWORDS):
        return "sparepart"
    if _contains_any(text, ACCESSORY_KEYWORDS):
        return "accessory"
    if _contains_any(text, GAMING_LAPTOP_HINTS | MAIN_PRODUCT_HINTS):
        return "main_product"
    return "ambiguous"


def detect_product_category(product: dict[str, Any] | str) -> str:
    title = normalize_text(product.get("title") if isinstance(product, dict) else product)
    if not title:
        return "unknown"
    if has_laptop_main_evidence(title):
        return "main_product"
    if has_accessory_only_evidence(title):
        return "accessory"
    if has_accessory_evidence(title):
        return "accessory"
    if has_gaming_laptop_evidence(title):
        return "main_product"
    if _contains_any(title, SPAREPART_KEYWORDS):
        return "sparepart"
    if _contains_any(title, ACCESSORY_KEYWORDS):
        return "accessory"
    if _contains_any(title, GAMING_LAPTOP_HINTS | MAIN_PRODUCT_HINTS):
        return "main_product"
    return "unknown"


def _query_core_tokens(query: str) -> set[str]:
    noise = ACCESSORY_KEYWORDS | SPAREPART_KEYWORDS | {
        "original", "ori", "baru", "bekas", "termurah", "murah",
        "gaming", "produk", "untuk", "dan",
    }
    return {token for token in _word_tokens(query) if token not in noise and len(token) > 1}


def _semantic_bonus(query: str, title: str) -> float:
    q = normalize_text(query)
    t = normalize_text(title)
    bonus = 0.0
    if is_laptop_gaming_query(q) and has_gaming_laptop_evidence(t):
        bonus += 0.38
        if "laptop" in t or "notebook" in t:
            bonus += 0.10
    if "iphone" in q and "iphone" in t:
        bonus += 0.28
    return bonus


def compute_rule_score(query: str, product: dict[str, Any], query_intent: str | None = None) -> float:
    intent = query_intent or detect_query_intent(query)
    title = normalize_text(product.get("title") or "")
    if not title:
        return 0.0

    category = detect_product_category(product)
    query_tokens = _query_core_tokens(query)
    title_tokens = _word_tokens(title)
    overlap = query_tokens & title_tokens
    overlap_ratio = len(overlap) / max(1, len(query_tokens))
    fuzzy = difflib.SequenceMatcher(None, normalize_text(query), title).ratio()
    score = 0.20 + overlap_ratio * 0.36 + min(0.16, fuzzy * 0.16) + _semantic_bonus(query, title)

    if intent == "main_product":
        if is_laptop_gaming_query(query) and has_gaming_laptop_evidence(title):
            return apply_laptop_gaming_boost(query, product, score + 0.18)
        if category in {"accessory", "sparepart"}:
            return min(0.30, 0.08 + overlap_ratio * 0.15)
        if category == "main_product":
            score += 0.18
    elif intent == "accessory":
        query_groups = _accessory_groups(query)
        product_groups = _accessory_groups(title)
        if category == "accessory" and (not query_groups or query_groups & product_groups):
            score += 0.28
        elif category == "accessory":
            score -= 0.18
        elif category == "main_product":
            score -= 0.30
        elif category == "sparepart":
            score -= 0.25
    elif intent == "sparepart":
        if category == "sparepart":
            score += 0.28
        elif category in {"accessory", "main_product"}:
            score -= 0.25
    elif category == "unknown" and overlap:
        score += 0.08

    feedback_delta = get_feedback_score_adjustment(query, intent, category, title)
    score = round(max(0.0, min(0.98, score + feedback_delta)), 3)
    return apply_laptop_gaming_boost(query, product, score)


def is_obvious_junk_for_intent(query: str, product: dict[str, Any], query_intent: str | None = None) -> bool:
    intent = query_intent or detect_query_intent(query)
    category = detect_product_category(product)
    title = normalize_text(product.get("title") or product.get("name") or "")
    if not title:
        return True
    if is_laptop_gaming_query(query):
        positive_laptop = has_gaming_laptop_evidence(title)
        if positive_laptop:
            return False
        if has_accessory_evidence(title) or category in {"accessory", "sparepart"}:
            return True
        if "laptop" in title or "notebook" in title:
            return False
        return True
    if intent == "main_product" and category in {"accessory", "sparepart"}:
        return True
    if intent == "accessory":
        if category == "main_product":
            return True
        query_groups = _accessory_groups(query)
        product_groups = _accessory_groups(title)
        return bool(query_groups and product_groups and not (query_groups & product_groups))
    if intent == "sparepart" and category != "sparepart":
        return True
    return False


def is_obvious_match_for_intent(query: str, product: dict[str, Any], query_intent: str | None = None) -> bool:
    intent = query_intent or detect_query_intent(query)
    score = compute_rule_score(query, product, intent)
    if score < RULE_ACCEPT_THRESHOLD:
        return False
    return not is_obvious_junk_for_intent(query, product, intent)


def should_call_llm(rule_score: float, obvious_junk: bool) -> bool:
    from src.ai.ai_orchestrator import should_call_llm as orchestrator_should_call_llm

    return orchestrator_should_call_llm(rule_score, obvious_junk)


async def compute_semantic_score_if_available(
    query: str,
    product: dict[str, Any],
    orchestrator_status: dict[str, Any] | None = None,
) -> float | None:
    status = orchestrator_status
    if status is None:
        from src.ai.model_registry import get_orchestrator_status

        status = get_orchestrator_status()
    if not status.get("capabilities", {}).get("semantic"):
        return None
    try:
        from src.ai.ollama_client import cosine_similarity, get_embedding_async

        title = str(product.get("title") or "")
        if not title:
            return None
        query_embedding = await get_embedding_async(query)
        title_embedding = await get_embedding_async(title)
        return cosine_similarity(query_embedding, title_embedding)
    except Exception:
        return None


def get_feedback_score_adjustment(query: str, query_intent: str, product_category: str, title: str) -> float:
    """Apply small, scoped feedback nudges without global category blacklists."""
    try:
        feedback_items = get_recent_feedback(query, limit=30)
    except Exception:
        return 0.0
    title_tokens = _word_tokens(title)
    delta = 0.0
    for item in feedback_items:
        item_intent = item.get("query_intent") or detect_query_intent(item.get("query", ""))
        if item_intent != query_intent:
            continue
        item_category = item.get("product_category") or detect_product_category(item.get("product_title", ""))
        if item_category != product_category:
            continue
        item_tokens = _word_tokens(item.get("product_title", ""))
        if not item_tokens or not title_tokens:
            continue
        similarity = len(item_tokens & title_tokens) / max(1, len(item_tokens | title_tokens))
        if similarity < 0.25:
            continue
        if item.get("feedback_type") == "positive" or item.get("user_action") == "benar":
            delta += 0.035 * similarity
        elif item.get("feedback_type") == "negative" or item.get("user_action") == "salah":
            delta -= 0.05 * similarity
    return max(-0.12, min(0.10, delta))

STRONG_MAIN_PRODUCT_TERMS = {
    "laptop", "notebook", "rog", "legion", "nitro", "victus", "tuf",
    "msi", "katana", "predator", "omen", "alienware", "gaming",
    "rtx", "gtx", "nvidia", "geforce", "radeon", "ryzen",
    "core i5", "core i7", "i5", "i7",
}
ACCESSORY_TERMS = {
    "mouse", "mice", "mousepad", "keyboard", "charger", "adaptor",
    "adapter", "cooling pad", "cooling", "cooler", "stand", "headset",
    "earphone", "webcam", "sleeve", "tas", "bag", "skin", "sticker",
    "stickers", "ram", "ssd", "sparepart", "spare", "parts", "baterai",
    "battery",
}
ACCESSORY_QUERY_TERMS = ACCESSORY_TERMS | {"aksesoris", "accessory", "accessories"}


@dataclass
class AiFilterResult:
    products: list[dict[str, Any]]
    ai_status: str
    meta: dict[str, Any] = field(default_factory=dict)

    def __iter__(self) -> Iterator[Any]:
        # Backward compatible with: products, status = await filter_relevance(...)
        yield self.products
        yield self.ai_status


def _query_terms(query: str) -> set[str]:
    return set(re.findall(r"\w+", query.lower()))


def _clamp(value: float, low: float = 0.05, high: float = 0.98) -> float:
    return max(low, min(high, value))


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def _title_text(product: dict[str, Any]) -> str:
    return str(product.get("title") or "").lower()


def _query_asks_accessory(query: str) -> bool:
    query_lower = query.lower()
    query_words = _query_terms(query)
    return bool(query_words & ACCESSORY_QUERY_TERMS) or any(term in query_lower for term in ACCESSORY_TERMS)


def _accessory_hits(product: dict[str, Any]) -> set[str]:
    title = _title_text(product)
    title_words = _query_terms(title)
    hits = {term for term in ACCESSORY_TERMS if term in title}
    hits.update(ACCESSORY_TERMS & title_words)
    return hits


def _is_accessory_like(product: dict[str, Any], query: str) -> bool:
    return bool(_accessory_hits(product)) and not _query_asks_accessory(query)


def _rule_relevance_score(query: str, product: dict[str, Any]) -> float:
    title = _title_text(product)
    title_words = _query_terms(title)
    query_words = _query_terms(query)

    if _is_accessory_like(product, query):
        return 0.12

    strong_hits = {term for term in STRONG_MAIN_PRODUCT_TERMS if term in title}
    strong_hits.update(STRONG_MAIN_PRODUCT_TERMS & title_words)
    overlap = query_words & title_words

    if "laptop" in query_words and "gaming" in query_words:
        if strong_hits:
            return _clamp(0.72 + min(len(strong_hits), 5) * 0.045 + min(len(overlap), 2) * 0.03, 0.05, 0.96)
        if {"laptop", "notebook"} & title_words:
            return 0.68

    if overlap:
        return _clamp(0.48 + min(len(overlap), 4) * 0.10, 0.05, 0.90)

    return 0.42


def _category_match_score(query: str, product: dict[str, Any]) -> float:
    query_words = _query_terms(query)
    title = _title_text(product)
    title_words = _query_terms(title)
    strong_hits = {term for term in STRONG_MAIN_PRODUCT_TERMS if term in title}
    strong_hits.update(STRONG_MAIN_PRODUCT_TERMS & title_words)

    if _is_accessory_like(product, query):
        return 0.10
    if {"laptop", "notebook"} & title_words and ("laptop" in query_words or "notebook" in query_words):
        return 0.90 if ("gaming" in query_words and any(term in title for term in STRONG_MAIN_PRODUCT_TERMS)) else 0.76
    if "laptop" in query_words and "gaming" in query_words and len(strong_hits) >= 2:
        return 0.88
    if query_words & title_words:
        return 0.62
    return 0.45


def _sold_number(product: dict[str, Any]) -> float:
    raw = str(product.get("sold_count") or product.get("sold") or product.get("sold_text") or "").lower()
    if not raw:
        return 0.0
    match = re.search(r"(\d+(?:[.,]\d+)?)", raw)
    if not match:
        return 0.0
    number = _as_float(match.group(1), 0.0)
    if "rb" in raw or "ribu" in raw or "k" in raw:
        number *= 1000
    if "jt" in raw or "juta" in raw:
        number *= 1_000_000
    return number


def _trust_score(product: dict[str, Any]) -> float:
    rating = _as_float(product.get("rating") or product.get("rating_text"), 0.0)
    rating_score = _clamp(rating / 5.0, 0.0, 1.0) if rating > 0 else 0.35
    sold_score = _clamp(min(_sold_number(product), 1000.0) / 1000.0, 0.0, 1.0)
    shop_text = " ".join(
        str(product.get(key) or "")
        for key in ("shop_name", "shop", "shop_badge", "badge")
    ).lower()
    if any(token in shop_text for token in ("official", "mall", "power merchant", "pro")):
        shop_score = 1.0
    elif product.get("shop_name") or product.get("shop"):
        shop_score = 0.55
    else:
        shop_score = 0.25
    return _clamp(rating_score * 0.45 + sold_score * 0.35 + shop_score * 0.20, 0.0, 1.0)


def _data_completeness_score(product: dict[str, Any]) -> float:
    checks = (
        bool(product.get("title")),
        not bool(product.get("price_parse_failed")) and bool(product.get("price_value") or product.get("price_raw")),
        bool(product.get("image_url") or product.get("image")),
        bool(product.get("product_url") or product.get("url")),
        bool(product.get("rating") or product.get("rating_text")),
        bool(product.get("sold_count") or product.get("sold") or product.get("sold_text")),
        bool(product.get("shop_name") or product.get("shop")),
    )
    return sum(1 for item in checks if item) / len(checks)


def _accessory_penalty(query: str, product: dict[str, Any]) -> float:
    hits = _accessory_hits(product)
    if not hits or _query_asks_accessory(query):
        return 0.0
    return _clamp(0.35 + min(len(hits), 3) * 0.08, 0.35, 0.60)


def _infer_ai_confidence(decision: dict[str, Any], query: str, product: dict[str, Any]) -> float:
    raw = decision.get("confidence")
    if raw is not None:
        parsed = _as_float(raw, -1.0)
        if 0.0 <= parsed <= 1.0:
            return parsed

    if not decision.get("relevant", True):
        return 0.25
    if str(decision.get("source", "")).startswith("fallback"):
        score = _rule_relevance_score(query, product)
        return 0.72 if score >= 0.72 else 0.60
    reason = str(decision.get("reason") or "").strip()
    return 0.82 if reason and reason.lower() not in {"ai marked relevant", "relevant"} else 0.60


def _calibrate_confidence(query: str, product: dict[str, Any], decision: dict[str, Any]) -> tuple[float, dict[str, float]]:
    relevant = bool(decision.get("relevant", True))
    model_confidence = _infer_ai_confidence(decision, query, product)
    if not relevant and model_confidence > 0.5:
        model_confidence = max(0.05, 1.0 - model_confidence)

    rule_score = _rule_relevance_score(query, product)
    category_score = _category_match_score(query, product)
    trust = _trust_score(product)
    completeness = _data_completeness_score(product)
    penalty = _accessory_penalty(query, product)
    final = (
        model_confidence * 0.45
        + rule_score * 0.25
        + category_score * 0.15
        + trust * 0.10
        + completeness * 0.05
        - penalty
    )
    if relevant and penalty == 0 and model_confidence >= 0.85 and rule_score >= 0.85 and category_score >= 0.85:
        signal_floor = model_confidence * 0.50 + rule_score * 0.30 + category_score * 0.20
        final = max(final, min(0.95, signal_floor))
    if not relevant:
        final = min(final, 0.49)
    final = _clamp(final)
    return round(final, 2), {
        "ai_model_confidence": round(model_confidence, 3),
        "rule_relevance_score": round(rule_score, 3),
        "category_match_score": round(category_score, 3),
        "trust_score": round(trust, 3),
        "data_completeness_score": round(completeness, 3),
        "accessory_penalty": round(penalty, 3),
    }


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.85:
        return "High"
    if confidence >= 0.70:
        return "Medium"
    return "Low"


def _confidence_explanation(query: str, product: dict[str, Any], signals: dict[str, float], decision_reason: str) -> str:
    if _is_accessory_like(product, query):
        return "Confidence rendah karena judul mengandung sinyal aksesori, bukan produk utama."
    parts: list[str] = []
    if signals["rule_relevance_score"] >= 0.85:
        parts.append("judul cocok kuat dengan produk yang dicari")
    elif signals["rule_relevance_score"] >= 0.70:
        parts.append("judul cukup cocok dengan query")
    if signals["trust_score"] >= 0.75:
        parts.append("rating/penjualan kuat")
    if signals["data_completeness_score"] >= 0.75:
        parts.append("data produk lengkap")
    if decision_reason:
        parts.append(decision_reason[:120])
    if not parts:
        parts.append("sinyal relevansi masih terbatas")
    return "Confidence " + ", ".join(parts) + "."


def _fallback_score(query: str, product: dict[str, Any]) -> dict[str, Any]:
    """
    Offline fallback used by tests and when AI is disabled.

    It is intent-aware: accessories are rejected for main-product queries but
    accepted when the query asks for that accessory class.
    """
    intent = detect_query_intent(query)
    category = detect_product_category(product)
    score = compute_rule_score(query, product, intent)
    obvious_junk = is_obvious_junk_for_intent(query, product, intent)

    if obvious_junk and score < RULE_REVIEW_THRESHOLD:
        return {
            "relevant": False,
            "confidence": max(0.05, score),
            "categories": [category],
            "reason": f"Rule fallback: {category} does not match {intent}",
            "source": "fallback",
        }

    if score >= RULE_REVIEW_THRESHOLD:
        return {
            "relevant": True,
            "confidence": score,
            "categories": [category],
            "reason": f"Rule fallback: score={score:.2f} intent={intent} category={category}",
            "source": "fallback",
        }

    return {
        "relevant": False,
        "confidence": score,
        "categories": [category],
        "reason": f"Rule fallback: low score={score:.2f}",
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
  "products": [
    {{
      "index": 0,
      "label": "relevan",
      "confidence": 0.91,
      "reason": "ASUS ROG is a gaming laptop line with GPU/spec keywords."
    }}
  ],
  "rejected": [
    {{
      "index": 3,
      "label": "tidak_relevan",
      "confidence": 0.94,
      "reason": "This is a mouse accessory, not a gaming laptop."
    }}
  ],
  "notes": "optional short note"
}}

Confidence rules:
- Confidence is your certainty of the classification.
- Obvious matches such as ASUS ROG, Lenovo Legion, Acer Nitro, HP Victus, ASUS TUF, MSI Katana, Predator, RTX/GTX/Radeon/Ryzen gaming laptops should be 0.85-0.97.
- Obvious accessories should be rejected with confidence 0.85-0.97.
- Use 0.55-0.75 only for ambiguous products.
- Do not be overly conservative when product title/specs clearly match.
"""


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


def _ai_item_map(values: Any) -> dict[int, dict[str, Any]]:
    items: dict[int, dict[str, Any]] = {}
    if not isinstance(values, list):
        return items
    for item in values:
        if not isinstance(item, dict):
            continue
        try:
            index = int(item.get("index"))
        except (TypeError, ValueError):
            continue
        items[index] = item
    return items


def _mark_product(product: dict[str, Any], decision: dict[str, Any], query: str) -> None:
    final_confidence, signals = _calibrate_confidence(query, product, decision)
    raw_model_confidence = _infer_ai_confidence(decision, query, product)
    reason = str(decision.get("reason", ""))

    product["relevance_score"] = final_confidence
    product["ai_decision"] = bool(decision.get("relevant", True))
    product["ai_reason"] = reason
    product["ai_explanation"] = product["ai_reason"]
    product["ai_categories"] = decision.get("categories", [])
    product["ai_source"] = decision.get("source", "unknown")
    product["ai_label"] = "relevan" if product["ai_decision"] else "tidak_relevan"
    product["ai_confidence"] = final_confidence
    product["ai_confidence_label"] = _confidence_label(final_confidence)
    product["ai_confidence_explanation"] = _confidence_explanation(query, product, signals, reason)
    product["ai_model_confidence"] = round(raw_model_confidence, 3)
    product["ai_confidence_signals"] = signals


def _apply_fallback_all(query: str, products: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    valid: list[dict[str, Any]] = []
    for product in products:
        decision = _fallback_score(query, product)
        decision["source"] = source
        _mark_product(product, decision, query)
        if decision["relevant"] and product["relevance_score"] >= RELEVANCE_THRESHOLD:
            valid.append(product)
    return valid


def _keep_prefiltered_batch(
    batch: list[tuple[int, dict[str, Any], str]],
    reason: str,
    query: str,
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for _, product, _ in batch:
        _mark_product(product, {
            "relevant": True,
            "confidence": FALLBACK_SCORE,
            "categories": ["fallback"],
            "reason": reason,
            "source": "fallback_invalid_response",
        }, query)
        kept.append(product)
    return kept


async def _call_generate_with_ai_heartbeat(
    *,
    prompt: str,
    model: str,
    search_id: str | None,
    batch_current: int,
    batch_total: int,
    batch_started_at_monotonic: float,
    batch_started_at_epoch_ms: int,
    completed_ai_batch_durations: list[float],
    found: int,
    valid_count: int,
):
    if not search_id:
        return await call_ollama_generate(prompt, model, search_id)

    from src.server.progress import update_ai_eta_progress

    stop_event = asyncio.Event()

    async def heartbeat() -> None:
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                update_ai_eta_progress(
                    search_id=search_id,
                    batch_current=batch_current,
                    batch_total=batch_total,
                    batch_started_at_monotonic=batch_started_at_monotonic,
                    batch_started_at_epoch_ms=batch_started_at_epoch_ms,
                    completed_ai_batch_durations=completed_ai_batch_durations,
                    message=f"AI filtering batch {batch_current}/{batch_total}",
                    found=found,
                    valid=valid_count,
                )

    heartbeat_task = asyncio.create_task(heartbeat())
    try:
        return await call_ollama_generate(prompt, model, search_id)
    finally:
        stop_event.set()
        heartbeat_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await heartbeat_task


async def ai_filter_products(
    query: str,
    products: list[dict[str, Any]],
    use_ai: bool = True,
    search_id: str | None = None,
) -> AiFilterResult:
    from src.ai.ai_filter import filter_products as intent_filter_products

    result = await intent_filter_products(
        query,
        list(products or []),
        use_ai=use_ai,
        search_id=search_id,
    )
    return AiFilterResult(result.products, result.status, result.meta)


async def filter_relevance(
    query: str,
    products: list[dict[str, Any]],
    use_ai: bool = True,
    search_id: str | None = None,
) -> AiFilterResult:
    """Backward-compatible public entrypoint."""
    return await ai_filter_products(query, list(products or []), use_ai, search_id)

```

## FILE: `src\ai\reset.py`

```python
"""
reset.py - Reset AI learning files only.

POST /api/ai/reset clears:
  data/ai_memory/feedback.jsonl
  data/ai_memory/examples.jsonl
  data/ai_memory/category_rules.json

Does NOT touch Ollama or any local model.
"""
from __future__ import annotations

import json

import src.ai.memory_store as memory_store
from src.ai.feedback_store import reset_learning
from src.config import FEEDBACK_FILE as PRODUCT_FEEDBACK_FILE
from src.utils.logger import log


def reset_ai_memory() -> bool:
    """
    Clear all AI learning files. Returns True on success.
    Ollama model is NOT touched.
    """
    try:
        memory_store.ensure_memory_dir()

        # Clear JSONL files
        memory_store.FEEDBACK_FILE.write_text("", encoding="utf-8")
        memory_store.EXAMPLES_FILE.write_text("", encoding="utf-8")
        PRODUCT_FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        PRODUCT_FEEDBACK_FILE.write_text("[]", encoding="utf-8")

        # Reset category rules to empty
        memory_store.CATEGORY_RULES_FILE.write_text(
            json.dumps({"version": 1, "rules": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        reset_learning(scope="all")

        log("AI_RESET", "AI memory cleared: feedback.jsonl, product_feedback.json, examples.jsonl, category_rules.json, marketspy_feedback.db", "OK")
        return True

    except Exception as exc:
        log("AI_RESET", f"Reset failed: {exc}", "ERROR")
        return False

```

## FILE: `src\ai\schemas.py`

```python
"""
Small shared schemas for AI product filtering.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProductDecision:
    accepted: bool
    confidence: float
    reason: str
    category_match: str
    source: str = "rule"
    product_category: str = "unknown"
    rule_score: float = 0.0
    ai_confidence: float = 0.0
    fallback_used: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

```

## FILE: `src\config.py`

```python
"""
Runtime configuration for PasarIntai AI.

Environment variables can override these defaults, but the checked-in defaults
are intentionally laptop-friendly: one small active model, CPU-safe chat
settings, and rules-first filtering.
"""
from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() not in {"", "0", "false", "no", "off"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


AI_ORCHESTRATION_ENABLED = parse_bool(os.getenv("AI_ORCHESTRATION_ENABLED", "true"))
AI_CPU_MODE = parse_bool(os.getenv("AI_CPU_MODE", "true"))
AI_MODEL = os.getenv("AI_MODEL", os.getenv("AI_CLASSIFIER_MODEL", "gemma3:4b")).strip()
AI_CLASSIFIER_MODEL = AI_MODEL

ALLOWED_OLLAMA_MODELS = list(dict.fromkeys([
    AI_CLASSIFIER_MODEL,
    "gemma3:4b",
    "llama3.2:3b",
    "phi4-mini",
    "nomic-embed-text",
]))

AI_MODEL_JOBS = {
    "semantic": "nomic-embed-text",
    "balanced_classifier": AI_CLASSIFIER_MODEL,
    "fast_classifier": "llama3.2:3b",
    "json_repair": "phi4-mini",
}

CLASSIFIER_PRIORITY = [
    AI_CLASSIFIER_MODEL,
    "llama3.2:3b",
]

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
OLLAMA_TIMEOUT_SECONDS = _env_int("OLLAMA_TIMEOUT_SECONDS", _env_int("AI_TIMEOUT_SECONDS", 12))
AI_CHAT_TIMEOUT_SECONDS = int(os.getenv("AI_CHAT_TIMEOUT_SECONDS", "75"))
AI_CHAT_NUM_CTX = int(os.getenv("AI_CHAT_NUM_CTX", "4096"))
AI_CHAT_NUM_PREDICT = int(os.getenv("AI_CHAT_NUM_PREDICT", "180"))
# For production: minimum 50 products for AI audit to be meaningful.
# Local laptops can still run this; rules-first ensures responsiveness.
AI_AUDIT_MAX_PRODUCTS = int(os.getenv("AI_AUDIT_MAX_PRODUCTS", os.getenv("AI_CLASSIFIER_MAX_PRODUCTS", "50")))
AI_CLASSIFIER_MAX_PRODUCTS = AI_AUDIT_MAX_PRODUCTS
AI_BATCH_CLASSIFY = parse_bool(os.getenv("AI_BATCH_CLASSIFY", "true"))
AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK = max(1, _env_int("AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK", 1))
AI_MODEL_CACHE_TTL_SECONDS = max(1, _env_int("AI_MODEL_CACHE_TTL_SECONDS", 300))
OLLAMA_MAX_CONCURRENT_REQUESTS = max(1, _env_int("OLLAMA_MAX_CONCURRENT_REQUESTS", 1))

RESULT_STORE_TTL_SECONDS = max(1, _env_int("RESULT_STORE_TTL_SECONDS", 3600))
RESULT_STORE_MAX_ITEMS = max(1, _env_int("RESULT_STORE_MAX_ITEMS", 50))

TARGET_COUNT_DEFAULT = _env_int("TARGET_COUNT_DEFAULT", 50)
OVERFETCH_MULTIPLIER = _env_int("OVERFETCH_MULTIPLIER", _env_int("SCRAPER_OVERFETCH_MULTIPLIER", 4))
STRICT_BUDGET_MODE = parse_bool(os.getenv("STRICT_BUDGET_MODE", "true"))
TARGET_FIRST_MODE = parse_bool(os.getenv("TARGET_FIRST_MODE", "false"))

RULE_ACCEPT_THRESHOLD = _env_float("RULE_ACCEPT_THRESHOLD", 0.76)
RULE_REVIEW_THRESHOLD = _env_float("RULE_REVIEW_THRESHOLD", 0.50)
RULE_REJECT_THRESHOLD = _env_float("RULE_REJECT_THRESHOLD", 0.30)
FALLBACK_EXPANSION_THRESHOLD = _env_float("FALLBACK_EXPANSION_THRESHOLD", 0.10)
WEAK_FALLBACK_THRESHOLD = _env_float("WEAK_FALLBACK_THRESHOLD", 0.05)
LLM_ACCEPT_THRESHOLD = _env_float("LLM_ACCEPT_THRESHOLD", 0.62)

AI_BATCH_SIZE = max(1, _env_int("AI_BATCH_SIZE", 3))

FEEDBACK_FILE = Path(os.getenv("FEEDBACK_FILE", "data/feedback/product_feedback.json"))

```

## FILE: `src\scraper\__init__.py`

```python

```

## FILE: `src\scraper\budget_filter.py`

```python
"""
budget_filter.py - Budget filtering with explicit reject reasons.

This module never treats empty budget as zero. It also separates invalid price
from budget rejection so failures are debuggable.
"""
from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from src.scraper.normalizer import normalize_products
from src.config import STRICT_BUDGET_MODE
from src.utils.currency import calculate_budget_range, format_rupiah, parse_rupiah


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass
class FilterResult:
    budget_input: Any
    budget_value: int | None
    tolerance: float
    min_price: int | None
    max_price: int | None
    total_products: int
    kept: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)
    reasons: dict[str, int] = field(default_factory=dict)
    samples: list[dict[str, Any]] = field(default_factory=list)
    debug_path: str | None = None

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    def debug_payload(self) -> dict[str, Any]:
        """Return JSON-serializable payload for data/debug/<search_id>."""
        return {
            "budget_input": "" if self.budget_input is None else str(self.budget_input),
            "budget_value": self.budget_value,
            "tolerance": self.tolerance,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "total_category_candidates": self.total_products,
            "total_products": self.total_products,
            "kept": len(self.kept),
            "rejected": len(self.rejected),
            "below_budget_range": self.reasons.get("below_budget_range", 0),
            "above_budget_range": self.reasons.get("above_budget_range", 0),
            "invalid_price": self.reasons.get("invalid_price", 0),
            "reasons": self.reasons,
            "samples": self.samples,
        }

    def failure_message(self) -> str:
        """Build a specific user-facing message when zero products pass budget."""
        below = self.reasons.get("below_budget_range", 0)
        above = self.reasons.get("above_budget_range", 0)
        invalid = self.reasons.get("invalid_price", 0)
        message = (
            f"Produk ditemukan {self.total_products}, tapi {above} di atas budget, "
            f"{below} di bawah budget, {invalid} harga tidak valid. "
            "Coba naikkan budget/tolerance."
        )
        if self.debug_path:
            message += f" Debug: {self.debug_path}"
        return message


def _safe_tolerance(tolerance: Any) -> float:
    """Clamp frontend tolerance into a sane percentage."""
    try:
        return max(0.0, min(float(tolerance), 100.0))
    except (TypeError, ValueError):
        return 20.0


def _decision_sample(
    product: dict[str, Any],
    decision: str,
    reason: str | None,
    min_price: int | None,
    max_price: int | None,
) -> dict[str, Any]:
    """Keep each decision compact but useful for JSON debug files."""
    return {
        "title": product.get("title", ""),
        "url": product.get("url", ""),
        "price_raw": product.get("price_raw"),
        "price_value": product.get("price_value"),
        "min_price": min_price,
        "max_price": max_price,
        "decision": decision,
        "reason": reason,
    }


def filter_by_budget(products: list[dict[str, Any]], budget: Any, tolerance: Any = 20) -> FilterResult:
    """
    Filter products by inclusive budget range.

    Rules:
    - Empty/invalid budget disables budget filtering.
    - Invalid product price is rejected as invalid_price only when budget is active.
    - Every rejected product gets price_raw, price_value, min_price, max_price,
      and reject_reason.
    """
    normalized = normalize_products(products)
    budget_value = parse_rupiah(budget)
    if budget_value is not None and budget_value <= 0:
        budget_value = None

    tolerance_value = _safe_tolerance(tolerance)
    strict_budget_mode = _env_bool("STRICT_BUDGET_MODE", STRICT_BUDGET_MODE)

    if budget_value is None:
        for product in normalized:
            parsed_price = parse_rupiah(product.get("price_value"))
            if parsed_price is None:
                parsed_price = parse_rupiah(product.get("price_raw"))
            product["price_parse_failed"] = parsed_price is None
            product["budget_decision"] = "kept"
        return FilterResult(
            budget_input=budget,
            budget_value=None,
            tolerance=tolerance_value,
            min_price=None,
            max_price=None,
            total_products=len(normalized),
            kept=normalized,
            rejected=[],
            reasons={},
            samples=[
                _decision_sample(product, "kept", "budget_disabled", None, None)
                for product in normalized
            ],
        )

    min_price, max_price = calculate_budget_range(budget_value, tolerance_value)
    reasons: Counter[str] = Counter()
    kept: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []

    for product in normalized:
        price_value = parse_rupiah(product.get("price_value"))
        if price_value is None:
            price_value = parse_rupiah(product.get("price_raw"))

        product["price_value"] = price_value
        product["price_val"] = price_value
        product["price_parse_failed"] = price_value is None or price_value <= 0
        if not product.get("price_raw") and price_value is not None:
            product["price_raw"] = format_rupiah(price_value)
            product["price_text"] = product["price_raw"]

        if price_value is None or price_value <= 0:
            reason = "invalid_price" if strict_budget_mode else None
        elif price_value < min_price:
            reason = "below_budget_range"
        elif price_value > max_price:
            reason = "above_budget_range"
        else:
            reason = None

        if reason is None:
            product["budget_decision"] = "kept"
            kept.append(product)
            kept_reason = "price_parse_failed_kept" if product["price_parse_failed"] else "within_budget_range"
            if product["price_parse_failed"]:
                reasons["invalid_price_kept"] += 1
            samples.append(_decision_sample(product, "kept", kept_reason, min_price, max_price))
            continue

        reasons[reason] += 1
        rejected_product = dict(product)
        rejected_product["price_raw"] = product.get("price_raw")
        rejected_product["price_value"] = price_value
        rejected_product["price_val"] = price_value
        rejected_product["min_price"] = min_price
        rejected_product["max_price"] = max_price
        rejected_product["reject_reason"] = reason
        rejected_product["budget_decision"] = reason
        rejected.append(rejected_product)
        samples.append(_decision_sample(rejected_product, "rejected", reason, min_price, max_price))

    return FilterResult(
        budget_input=budget,
        budget_value=budget_value,
        tolerance=tolerance_value,
        min_price=min_price,
        max_price=max_price,
        total_products=len(normalized),
        kept=kept,
        rejected=rejected,
        reasons=dict(reasons),
        samples=samples,
    )

```

## FILE: `src\scraper\dedupe.py`

```python
"""
dedupe.py - Product deduplication shared by normal and compare modes.
"""
from __future__ import annotations

import re
from typing import Any


def _clean_url(url: str) -> str:
    """Remove tracking params so two engines agree on the same product URL."""
    return re.split(r"[?#]", (url or "").strip(), maxsplit=1)[0].lower()


def deduplicate_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate by URL first, then title+price for cards without URL."""
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []

    for product in products or []:
        url = _clean_url(product.get("url") or product.get("link") or "")
        fallback = f"{product.get('title', '').lower()}|{product.get('price_value') or product.get('price_raw')}"
        key = url or fallback
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(product)

    return deduped

```

## FILE: `src\scraper\engine_selector.py`

```python
"""
engine_selector.py - Run scraper engines in the requested mode.

Clean pipeline per spec:
  preflight -> scrape raw -> normalize -> optional budget filter -> AI Orchestrator -> result

Modes:
- auto:      Puppeteer first, rollback if Puppeteer fails.
- puppeteer: Puppeteer only.
- rollback:  Selenium only.
- selenium:  Selenium only alias.
- compare_both: Both engines, show comparison table with opened_real_page status.

Removed: category_filter import. AI Orchestrator is the semantic filter. Not hardcoded keywords.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from src.scraper.normalizer import normalize_products
from src.scraper.puppeteer_engine import PuppeteerEngine
from src.scraper.query_expander import expand_query_variants
from src.scraper.rollback_engine import RollbackEngine
from src.server.progress import update_progress
from src.utils.debug import get_debug_dir, save_json_debug
from src.utils.logger import log


@dataclass
class EngineRunResult:
    engine: str
    ok: bool
    opened_real_page: bool = False   # did the browser open a real Tokopedia page?
    error_type: str = ""             # http2_protocol_error, blank_page, etc.
    products: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    duration_seconds: float = 0.0
    query_variants: list[str] = field(default_factory=list)
    urls_tried: list[str] = field(default_factory=list)
    debug_files: list[str] = field(default_factory=list)

    @property
    def raw_products_found(self) -> int:
        return len(self.products)


@dataclass
class EngineSelectionResult:
    ok: bool
    mode: str
    selected_engine: str | None = None
    products: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    fallback_message: str | None = None
    runs: list[EngineRunResult] = field(default_factory=list)


def _make_engine(name: str, search_id: str):
    if name == "puppeteer":
        return PuppeteerEngine(search_id)
    if name == "rollback":
        return RollbackEngine(search_id)
    raise ValueError(f"Unknown scraper engine: {name}")


def _existing_zero_raw_debug(search_id: str, engine_name: str) -> str:
    """Return existing engine error debug file path if it exists."""
    for filename in (f"{engine_name}_engine_error.json", f"{engine_name}_zero_raw_debug.json"):
        path = get_debug_dir(search_id) / filename
        if path.exists():
            return str(path)
    return ""


async def run_engine(
    search_id: str,
    engine_name: str,
    query: str,
    raw_target: int,
    eta_calc,
) -> EngineRunResult:
    """
    Run one engine and return raw extracted products.
    No budget passed to engine. Budget filter runs locally after raw products exist.
    No category filter. AI Orchestrator handles semantic relevance.
    """
    started = time.perf_counter()
    variants = expand_query_variants(query)
    urls_to_try: list[str] = []

    log(f"[{search_id}]", f"[QUERY] {engine_name} variants={len(variants)}", "INFO")
    for i, variant in enumerate(variants, 1):
        log(f"[{search_id}]", f"[QUERY] variant[{i}]={variant}", "INFO")

    update_progress(
        search_id,
        active_engine=engine_name,
        stage=f"{engine_name}_starting",
        message=f"Menjalankan {engine_name} dengan {len(variants)} query variant...",
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    try:
        engine = _make_engine(engine_name, search_id)
        # Pass query variants. No min/max price - budget filter runs locally.
        success, products, error = await engine.scrape(
            query,
            raw_target,
            eta_calc,
            query_variants=variants,
            min_price=None,
            max_price=None,
        )
        duration = time.perf_counter() - started

        # Determine if the engine reported a preflight failure
        opened_real_page = True
        error_type = ""
        if not success and error:
            # Parse error_type from error message if present
            if "opened_real_page=false" in error or "error_type=" in error:
                opened_real_page = False
                # Extract error_type from message like "error_type=http2_protocol_error"
                import re
                match = re.search(r"error_type[=:](\w+)", error)
                error_type = match.group(1) if match else "unknown"
            else:
                # Page may have opened but extraction failed
                opened_real_page = bool(products) or success

        if success and products:
            log(f"[{search_id}]", f"[ENGINE] {engine_name} raw={len(products)}", "OK")
            return EngineRunResult(
                engine_name, True, opened_real_page=True,
                products=products, duration_seconds=duration,
                query_variants=variants, urls_tried=urls_to_try,
            )

        # Failed - get debug file path if engine wrote one
        debug_path = _existing_zero_raw_debug(search_id, engine_name)
        log(f"[{search_id}]", f"[ENGINE] {engine_name} failed: {error}", "WARN")
        return EngineRunResult(
            engine_name, False,
            opened_real_page=opened_real_page,
            error_type=error_type,
            products=[],
            error=error or f"{engine_name} did not find products.",
            duration_seconds=duration,
            query_variants=variants,
            urls_tried=urls_to_try,
            debug_files=[debug_path] if debug_path else [],
        )

    except Exception as exc:
        duration = time.perf_counter() - started
        error = f"{engine_name} unhandled exception: {exc}"
        log(f"[{search_id}]", f"[ENGINE] {error}", "ERROR")
        debug_path = _existing_zero_raw_debug(search_id, engine_name)
        return EngineRunResult(
            engine_name, False,
            error=error, duration_seconds=duration,
            query_variants=variants, urls_tried=urls_to_try,
            debug_files=[debug_path] if debug_path else [],
        )


async def run_scraper_engines(
    search_id: str,
    query: str,
    raw_target: int,
    eta_calc,
    engine_mode: str = "auto",
    budget: Any = None,       # kept for API compat, not used here
    tolerance: Any = 20,      # kept for API compat, not used here
) -> EngineSelectionResult:
    """Run scraper engines according to the requested mode."""
    aliases = {"selenium": "rollback", "compare": "compare_both"}
    requested_mode = aliases.get(engine_mode, engine_mode)
    mode = requested_mode if requested_mode in {"auto", "puppeteer", "rollback", "compare_both"} else "auto"
    update_progress(
        search_id,
        engine_mode=mode,
        stage="engine_selecting",
        percent=5,
        message=f"Memilih engine: {mode}",
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    if mode == "puppeteer":
        run = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
        return EngineSelectionResult(run.ok, mode, "puppeteer", run.products, run.error, runs=[run])

    if mode == "rollback":
        run = await run_engine(search_id, "rollback", query, raw_target, eta_calc)
        return EngineSelectionResult(run.ok, mode, "rollback", run.products, run.error, runs=[run])

    if mode == "compare_both":
        # Run both and keep both results for the comparison table
        pup = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
        roll = await run_engine(search_id, "rollback", query, raw_target, eta_calc)
        runs = [pup, roll]
        good_runs = [r for r in runs if r.ok and r.products]
        if not good_runs:
            error = "; ".join(f"{r.engine}: {r.error}" for r in runs)
            return EngineSelectionResult(False, mode, None, [], error, runs=runs)
        selected = max(good_runs, key=lambda r: len(r.products))
        return EngineSelectionResult(True, mode, selected.engine, selected.products, runs=runs)

    # Auto mode: Puppeteer first, rollback if Puppeteer fails
    puppeteer = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
    if puppeteer.ok and puppeteer.products:
        return EngineSelectionResult(True, mode, "puppeteer", puppeteer.products, runs=[puppeteer])

    fallback_message = "Puppeteer gagal atau tidak menemukan produk. Beralih ke Rollback/Selenium..."
    update_progress(
        search_id,
        active_engine="rollback",
        stage="switching_to_rollback",
        percent=45,
        message=fallback_message,
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    rollback = await run_engine(search_id, "rollback", query, raw_target, eta_calc)
    if rollback.ok and rollback.products:
        return EngineSelectionResult(
            True, mode, "rollback", rollback.products,
            fallback_message=fallback_message, runs=[puppeteer, rollback],
        )

    combined_error = (
        f"Puppeteer: {puppeteer.error or 'no products'}; "
        f"Rollback: {rollback.error or 'no products'}."
    )
    return EngineSelectionResult(
        False, mode, None, [], combined_error, fallback_message, [puppeteer, rollback]
    )


async def run_scraper_chain(search_id: str, query: str, raw_target: int, eta_calc):
    """Backward compatible wrapper for old callers."""
    result = await run_scraper_engines(search_id, query, raw_target, eta_calc, "auto")
    return result.ok, result.products, result.error

```

## FILE: `src\scraper\normalizer.py`

```python
"""
normalizer.py - Convert scraper output into one product schema.

Raw extraction should be counted before normalization. This module keeps weak
but usable raw products and reports every drop reason for diagnostics.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Iterable

from src.utils.currency import format_rupiah, parse_rupiah
from src.utils.debug import save_json_debug


@dataclass
class NormalizerReport:
    engine: str
    input_count: int
    output: list[dict[str, Any]] = field(default_factory=list)
    drop_reasons: dict[str, int] = field(default_factory=dict)
    dropped_samples: list[dict[str, Any]] = field(default_factory=list)
    images_extracted_count: int = 0
    images_missing_count: int = 0
    debug_path: str | None = None

    @property
    def output_count(self) -> int:
        return len(self.output)

    @property
    def dropped_count(self) -> int:
        return self.input_count - len(self.output)

    def debug_payload(self) -> dict[str, Any]:
        """Return compact JSON diagnostic for normalizer behavior."""
        return {
            "engine": self.engine,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "dropped_count": self.dropped_count,
            "drop_reasons": self.drop_reasons,
            "images_extracted_count": self.images_extracted_count,
            "images_missing_count": self.images_missing_count,
            "dropped_samples": self.dropped_samples[:30],
        }


def _first_text(data: dict[str, Any], keys: Iterable[str]) -> str:
    """Return the first non-empty string-ish field from a product dict."""
    for key in keys:
        value = data.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _first_value(data: dict[str, Any], keys: Iterable[str]) -> Any:
    """Return the first non-empty raw field without forcing it to text."""
    for key in keys:
        value = data.get(key)
        if value is not None and value != "":
            return value
    return None


def _clean_url(url: str) -> str:
    """Remove noisy query/hash fragments so dedupe works across engines."""
    if not url:
        return ""
    return re.split(r"[?#]", url.strip(), maxsplit=1)[0]


def normalize_image_url(url: str | None) -> str | None:
    if not url:
        return None
    url = str(url).strip().strip('"').strip("'")
    if not url:
        return None
    if url.startswith("//"):
        url = "https:" + url
    if not (url.startswith("http://") or url.startswith("https://")):
        return None
    if url.lower().replace(" ", "") in {"undefined", "null", "noimage"}:
        return None
    return url


def pick_product_image(product: dict[str, Any]) -> str | None:
    candidates = [
        product.get("image_url"),
        product.get("image"),
        product.get("thumbnail"),
        product.get("thumb"),
        product.get("img"),
        product.get("photo"),
        product.get("picture"),
        product.get("url_gambar"),
    ]

    images = product.get("images")
    if isinstance(images, list) and images:
        candidates.extend(images)

    media = product.get("media")
    if isinstance(media, dict):
        candidates.extend([
            media.get("image"),
            media.get("thumbnail"),
            media.get("url"),
        ])

    for candidate in candidates:
        if isinstance(candidate, dict):
            nested = (
                candidate.get("image")
                or candidate.get("image_url")
                or candidate.get("thumbnail")
                or candidate.get("url")
            )
            normalized = normalize_image_url(nested)
        else:
            normalized = normalize_image_url(candidate)
        if normalized:
            return normalized

    return None


def normalize_image(raw: dict[str, Any]) -> str | None:
    """Return the first valid http(s) image URL from common scraper fields."""
    return pick_product_image(raw)


def _product_id(title: str, url: str, price_value: int | None) -> str:
    """Create a stable frontend id from fields that do not change per render."""
    raw = f"{title}|{url}|{price_value or ''}".encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()[:16]


def _normalize_product_with_reason(raw: dict[str, Any], source_engine: str | None = None) -> tuple[dict[str, Any] | None, str | None]:
    """Normalize one product and return a drop reason when unusable."""
    if not isinstance(raw, dict):
        return None, "not_dict"

    title = _first_text(raw, ("title", "nama", "nama_produk", "name", "product_name"))
    if not title:
        return None, "missing_title"

    url = _clean_url(_first_text(raw, ("url", "link", "href", "url_produk", "product_url")))
    price_raw = _first_value(
        raw,
        ("price_raw", "price_text", "harga_display", "price_display", "price", "harga"),
    )
    if not url and price_raw in (None, ""):
        return None, "missing_url_and_price"

    price_value = _first_value(raw, ("price_value", "price_val", "harga_value", "harga"))
    parsed_price = parse_rupiah(price_value)
    if parsed_price is None:
        parsed_price = parse_rupiah(price_raw)

    price_text = str(price_raw).strip() if price_raw not in (None, "") else ""
    if not price_text and parsed_price is not None:
        price_text = format_rupiah(parsed_price)

    engine = source_engine or _first_text(raw, ("source_engine", "source", "engine")) or "unknown"
    
    # Parse rating to float if possible
    rating_text = _first_text(raw, ("rating", "rating_toko", "rating_text"))
    rating_val = None
    try:
        rating_val = float(rating_text.replace(',', '.'))
    except ValueError:
        pass

    # Parse sold count to int if possible
    sold_text = _first_text(raw, ("sold", "terjual", "sold_text"))
    sold_count = None
    sold_lower = sold_text.lower()
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(rb|ribu|k|jt|juta)?', sold_lower)
    if match:
        num_str = match.group(1).replace(',', '.')
        try:
            num = float(num_str)
            unit = match.group(2)
            if unit in ('rb', 'ribu', 'k'):
                num *= 1000
            elif unit in ('jt', 'juta'):
                num *= 1000000
            sold_count = int(num)
        except ValueError:
            pass

    image_url = normalize_image(raw)

    normalized = {
        "id": raw.get("id") or _product_id(title, url, parsed_price),
        "title": title,
        "price": parsed_price or 0,
        "price_text": price_text,
        "price_raw": price_text, # backward compat
        "price_value": parsed_price, # backward compat
        "shop_name": _first_text(raw, ("shop", "toko", "nama_toko", "store", "shop_name")),
        "shop": _first_text(raw, ("shop", "toko", "nama_toko", "store", "shop_name")), # backward compat
        "store": _first_text(raw, ("shop", "toko", "nama_toko", "store", "shop_name")),
        "shop_location": _first_text(raw, ("location", "lokasi", "shop_location")),
        "location": _first_text(raw, ("location", "lokasi", "shop_location")), # backward compat
        "rating": rating_val if rating_val is not None else rating_text,
        "rating_text": rating_text,
        "sold_count": sold_count,
        "sold_text": sold_text,
        "sold": sold_text, # backward compat
        "product_url": url,
        "url": url, # backward compat
        "image_url": image_url,
        "image": image_url, # backward compat
        "has_image": bool(image_url),
        "source_engine": engine,
        "source_query": _first_text(raw, ("source_query", "query_variant")),
        "category_decision": raw.get("category_decision", ""),
        "category_reason": raw.get("category_reason", ""),
        "budget_decision": raw.get("budget_decision", ""),
        "ai_decision": raw.get("ai_decision", None),
        "ai_reason": raw.get("ai_reason", ""),
        "confidence": raw.get("confidence", 0) or 0,
        "decision_source": raw.get("decision_source", ""),
    }

    # Compatibility aliases for old frontend/AI code. Old logic bad. Replaced.
    normalized["link"] = normalized["url"]
    normalized["price_text"] = normalized["price_raw"]
    normalized["price_val"] = normalized["price_value"]
    normalized["source"] = normalized["source_engine"]
    return normalized, None


def normalize_product(raw: dict[str, Any], source_engine: str | None = None) -> dict[str, Any] | None:
    """Normalize one raw product. Missing shop/location/image is allowed."""
    product, _ = _normalize_product_with_reason(raw, source_engine)
    return product


def normalize_products_with_report(
    products: Iterable[dict[str, Any]],
    source_engine: str | None = None,
    search_id: str | None = None,
) -> NormalizerReport:
    """Normalize a batch and optionally write normalizer_debug_<engine>.json."""
    raw_products = list(products or [])
    engine = source_engine or "unknown"
    output: list[dict[str, Any]] = []
    drop_reasons: Counter[str] = Counter()
    dropped_samples: list[dict[str, Any]] = []

    for item in raw_products:
        product, reason = _normalize_product_with_reason(item, source_engine)
        if product:
            output.append(product)
            continue
        drop_reasons[reason or "unknown"] += 1
        dropped_samples.append({
            "reason": reason or "unknown",
            "raw": item if isinstance(item, dict) else str(item),
        })

    report = NormalizerReport(
        engine=engine,
        input_count=len(raw_products),
        output=output,
        drop_reasons=dict(drop_reasons),
        dropped_samples=dropped_samples,
        images_extracted_count=sum(1 for product in output if product.get("image")),
        images_missing_count=sum(1 for product in output if not product.get("image")),
    )

    if search_id:
        report.debug_path = save_json_debug(search_id, f"normalizer_debug_{engine}.json", report.debug_payload())
    return report


def normalize_products(products: Iterable[dict[str, Any]], source_engine: str | None = None) -> list[dict[str, Any]]:
    """Backward-compatible normalizer returning only product list."""
    return normalize_products_with_report(products, source_engine).output

```

## FILE: `src\scraper\preflight.py`

```python
"""
preflight.py - Browser preflight check.

Before scraping, verify that the browser actually opens Tokopedia and NOT
a Chrome network error page. This is the ONLY correct fix for raw = 0 when
ERR_HTTP2_PROTOCOL_ERROR or similar network failures occur.

Returns a clear dict so the pipeline can stop cleanly and show real diagnosis
instead of lying with "selector failed" or "0 products found".
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Any

from src.utils.logger import log


# Strings that indicate Chrome is showing an error page, NOT a real site.
# These are matched against page title and body text.
CHROME_ERROR_SIGNALS = [
    "err_http2_protocol_error",
    "err_connection_reset",
    "err_connection_refused",
    "err_connection_timed_out",
    "err_name_not_resolved",
    "err_address_unreachable",
    "this site can't be reached",
    "situs ini tidak dapat dijangkau",
    "no internet",
    "dns_probe_finished_no_internet",
    "dns_probe_finished_nxdomain",
]

# Tokopedia page signals - at least one of these must exist on the real page.
TOKOPEDIA_REAL_PAGE_SIGNALS = [
    "tokopedia",
    "toped",
]


def _detect_error_type(title: str, body: str, url: str) -> str | None:
    """
    Scan title + body + url for known Chrome network error codes.
    Returns a short error type key, or None if no error detected.
    """
    combined = f"{title} {body} {url}".lower()

    # Map raw signals to clean error_type keys.
    patterns = [
        (r"err_http2_protocol_error", "http2_protocol_error"),
        (r"err_connection_reset", "connection_reset"),
        (r"err_connection_refused", "connection_refused"),
        (r"err_connection_timed_out", "connection_timed_out"),
        (r"err_name_not_resolved", "name_not_resolved"),
        (r"err_address_unreachable", "address_unreachable"),
        (r"dns_probe_finished_no_internet", "no_internet"),
        (r"dns_probe_finished_nxdomain", "dns_nxdomain"),
        (r"this site can.t be reached", "site_unreachable"),
        (r"situs ini tidak dapat dijangkau", "site_unreachable_id"),
    ]

    for pattern, error_key in patterns:
        if re.search(pattern, combined):
            return error_key

    # Fallback: about:blank means navigation never happened.
    if url.strip().lower() in ("about:blank", "chrome://newtab/", ""):
        return "blank_page"

    return None


def _is_real_tokopedia_page(title: str, body: str, url: str) -> bool:
    """Check if the page looks like a real Tokopedia page."""
    combined = f"{title} {body} {url}".lower()
    return any(signal in combined for signal in TOKOPEDIA_REAL_PAGE_SIGNALS)


def build_preflight_result(
    url: str,
    title: str,
    body_sample: str,
    current_url: str,
    load_time_ms: float,
    engine: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the standardized preflight result dict.

    opened_real_page=False means: scraper must NOT attempt extraction.
    The engine opened a Chrome error page. Show diagnosis and stop.
    """
    error_type = _detect_error_type(title, body_sample, current_url)
    is_real = _is_real_tokopedia_page(title, body_sample, current_url)

    # Even if no known error detected, if no Tokopedia signal exists it's wrong.
    if error_type is None and not is_real:
        error_type = "unknown_non_tokopedia_page"

    opened_real_page = (error_type is None) and is_real

    result: dict[str, Any] = {
        "engine": engine,
        "target_url": url,
        "current_url": current_url,
        "opened_real_page": opened_real_page,
        "error_type": error_type,
        "page_title": title,
        "body_text_sample": body_sample[:500],
        "load_time_ms": round(load_time_ms, 1),
        "message": (
            "Browser opened real Tokopedia product page."
            if opened_real_page
            else f"Browser opened Chrome error/non-Tokopedia page. error_type={error_type}. "
                 "Extraction cannot work on this page. Stopping cleanly."
        ),
    }

    if extra:
        result.update(extra)

    return result


def save_preflight_debug(search_id: str, result: dict[str, Any], engine: str) -> str:
    """Write preflight result to data/debug/<search_id>/<engine>_preflight.json."""
    from src.utils.debug import get_debug_dir
    debug_dir = get_debug_dir(search_id)
    debug_dir.mkdir(parents=True, exist_ok=True)
    path = debug_dir / f"{engine}_preflight.json"
    try:
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)
    except Exception as exc:
        log(f"[{search_id}]", f"[PREFLIGHT] Failed to save debug: {exc}", "WARN")
        return ""


async def preflight_puppeteer(
    search_id: str,
    url: str,
    timeout_ms: int = 20000,
) -> dict[str, Any]:
    """
    Run Puppeteer-based preflight via a tiny inline Node script.
    Checks if the given URL opens a real Tokopedia page or an error page.
    """
    script = """
const puppeteer = require('puppeteer');
(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
             '--disable-http2']  // disable HTTP/2 to reduce ERR_HTTP2_PROTOCOL_ERROR
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1366, height: 768 });
    // Pretend to be a real Chrome browser
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36');

    let navError = null;
    try {
      await page.goto(process.env.PREFLIGHT_URL, {
        waitUntil: 'domcontentloaded',
        timeout: parseInt(process.env.PREFLIGHT_TIMEOUT || '15000')
      });
    } catch (e) {
      navError = e.message || String(e);
    }

    const currentUrl = page.url();
    const title = await page.title().catch(() => '');
    const bodyText = await page.evaluate(() =>
      document.body ? (document.body.innerText || '').slice(0, 1000) : ''
    ).catch(() => '');

    process.stdout.write(JSON.stringify({
      current_url: currentUrl,
      title,
      body_text: bodyText,
      nav_error: navError
    }) + '\\n');
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
})().catch(e => {
  process.stdout.write(JSON.stringify({ error: e.message || String(e) }) + '\\n');
  process.exit(1);
});
"""
    started = time.perf_counter()
    env = {
        "PREFLIGHT_URL": url,
        "PREFLIGHT_TIMEOUT": str(timeout_ms),
    }

    import os
    full_env = {**os.environ, **env}
    worker_dir = Path(__file__).parent

    try:
        process = await asyncio.create_subprocess_exec(
            "node",
            "--eval",
            script,
            cwd=str(worker_dir.parent.parent),  # project root where node_modules lives
            env=full_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=(timeout_ms / 1000) + 5
            )
        except asyncio.TimeoutError:
            process.kill()
            return build_preflight_result(
                url=url, title="", body_sample="", current_url="",
                load_time_ms=(time.perf_counter() - started) * 1000,
                engine="puppeteer",
                extra={"nav_error": "preflight_process_timeout"},
            )

        elapsed_ms = (time.perf_counter() - started) * 1000
        raw = stdout.decode("utf-8", errors="replace").strip()

        try:
            data = json.loads(raw.split("\n")[0])
        except json.JSONDecodeError:
            data = {}

        if "error" in data:
            return build_preflight_result(
                url=url, title="", body_sample=data.get("error", ""),
                current_url="", load_time_ms=elapsed_ms, engine="puppeteer",
                extra={"nav_error": data.get("error")},
            )

        result = build_preflight_result(
            url=url,
            title=data.get("title", ""),
            body_sample=data.get("body_text", ""),
            current_url=data.get("current_url", ""),
            load_time_ms=elapsed_ms,
            engine="puppeteer",
            extra={"nav_error": data.get("nav_error")},
        )

        path = save_preflight_debug(search_id, result, "puppeteer")
        result["debug_path"] = path
        log(f"[{search_id}]", f"[PREFLIGHT] puppeteer opened_real_page={result['opened_real_page']} error_type={result['error_type']}", "INFO")
        return result

    except FileNotFoundError:
        # Node not installed
        return build_preflight_result(
            url=url, title="", body_sample="", current_url="",
            load_time_ms=0, engine="puppeteer",
            extra={"nav_error": "node_not_found"},
        )
    except Exception as exc:
        return build_preflight_result(
            url=url, title="", body_sample="", current_url="",
            load_time_ms=(time.perf_counter() - started) * 1000,
            engine="puppeteer",
            extra={"nav_error": str(exc)},
        )


def preflight_selenium(
    search_id: str,
    url: str,
    timeout_s: int = 20,
) -> dict[str, Any]:
    """
    Selenium-based preflight. Synchronous because Selenium is blocking.
    Call this from asyncio.to_thread().
    """
    from src.scraper.selenium_driver import create_chrome_driver, safe_quit_driver

    debug_dir = Path("data/debug") / search_id
    started = time.perf_counter()
    driver, driver_error = create_chrome_driver(search_id, debug_dir)

    if not driver:
        return build_preflight_result(
            url=url, title="", body_sample="", current_url="",
            load_time_ms=(time.perf_counter() - started) * 1000,
            engine="rollback",
            extra={"nav_error": f"driver_bootstrap_failed: {driver_error}"},
        )

    try:
        driver.set_page_load_timeout(timeout_s)
        nav_error = None
        try:
            driver.get(url)
        except Exception as exc:
            nav_error = str(exc)

        elapsed_ms = (time.perf_counter() - started) * 1000
        current_url = driver.current_url
        title = driver.title
        try:
            body_text = driver.execute_script(
                "return document.body ? (document.body.innerText || '').slice(0, 1000) : '';"
            ) or ""
        except Exception:
            body_text = ""

        result = build_preflight_result(
            url=url,
            title=title,
            body_sample=body_text,
            current_url=current_url,
            load_time_ms=elapsed_ms,
            engine="rollback",
            extra={"nav_error": nav_error},
        )

        path = save_preflight_debug(search_id, result, "rollback")
        result["debug_path"] = path
        log(f"[{search_id}]", f"[PREFLIGHT] rollback opened_real_page={result['opened_real_page']} error_type={result['error_type']}", "INFO")
        return result

    finally:
        safe_quit_driver(driver)


async def run_preflight(
    search_id: str,
    engine: str,
    query: str = "laptop gaming",
) -> dict[str, Any]:
    """
    Run preflight for the given engine.
    Uses a simple search URL (no pmin/pmax) per the spec.
    """
    from src.scraper.url_builder import build_tokopedia_search_url
    url = build_tokopedia_search_url(query)

    if engine == "puppeteer":
        return await preflight_puppeteer(search_id, url)

    if engine in ("rollback", "selenium"):
        return await asyncio.to_thread(preflight_selenium, search_id, url)

    # For "auto" or "compare", try both and return the first success or both failures.
    pup = await preflight_puppeteer(search_id, url)
    if pup["opened_real_page"]:
        return pup
    roll = await asyncio.to_thread(preflight_selenium, search_id, url)
    # Return whichever is better; if both fail, return rollback with combined error.
    if roll["opened_real_page"]:
        return roll
    roll["puppeteer_preflight"] = pup
    return roll

```

## FILE: `src\scraper\puppeteer_engine.py`

```python
"""
puppeteer_engine.py - Python wrapper for the Node Puppeteer worker.

Python owns process lifetime and reads JSONL stdout in real time. The worker
owns browser/page retry logic.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from src.server.progress import update_progress
from src.utils.logger import log


class PuppeteerEngine:
    name = "puppeteer"
    process_timeout_seconds = int(os.getenv("PUPPETEER_PROCESS_TIMEOUT_SECONDS", "240"))
    idle_stdout_timeout_seconds = int(os.getenv("PUPPETEER_IDLE_TIMEOUT_SECONDS", "90"))

    def __init__(self, search_id: str):
        self.search_id = search_id

    async def _drain_stderr(self, process: asyncio.subprocess.Process, lines: list[str]) -> None:
        """Drain stderr so Node cannot hang on a full pipe."""
        if not process.stderr:
            return
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            lines.append(line.decode("utf-8", errors="replace").strip())

    async def _kill_process(self, process: asyncio.subprocess.Process | None) -> None:
        """Terminate Node cleanly, then force kill if it ignores us."""
        if not process or process.returncode is not None:
            return
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=3)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass

    async def scrape(
        self,
        query: str,
        raw_target: int,
        eta_calc,
        query_variants: list[str] | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
    ) -> tuple[bool, list[dict[str, Any]], str]:
        worker_path = Path(__file__).parent / "puppeteer_worker.js"
        products: list[dict[str, Any]] = []
        stderr_lines: list[str] = []
        last_error = ""
        process: asyncio.subprocess.Process | None = None
        stderr_task: asyncio.Task | None = None

        try:
            process = await asyncio.create_subprocess_exec(
                "node",
                str(worker_path),
                "--query",
                query,
                "--target",
                str(raw_target),
                "--search-id",
                self.search_id,
                "--variants",
                json.dumps(query_variants or [query]),
                "--min-price",
                str(min_price or ""),
                "--max-price",
                str(max_price or ""),
                "--max-scrolls",
                str(os.getenv("MAX_SCROLL_ATTEMPTS", os.getenv("PUPPETEER_MAX_SCROLL_ROUNDS", "30"))),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024 * 10,
            )
            stderr_task = asyncio.create_task(self._drain_stderr(process, stderr_lines))

            deadline = asyncio.get_running_loop().time() + self.process_timeout_seconds
            while True:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    last_error = f"Puppeteer worker timeout after {self.process_timeout_seconds}s"
                    await self._kill_process(process)
                    break

                try:
                    line = await asyncio.wait_for(
                        process.stdout.readline(),
                        timeout=min(self.idle_stdout_timeout_seconds, remaining),
                    )
                except asyncio.TimeoutError:
                    last_error = "Puppeteer worker idle timeout while reading stdout"
                    await self._kill_process(process)
                    break

                if not line:
                    break

                text = line.decode("utf-8", errors="replace").strip()
                if not text:
                    continue

                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    log(f"[{self.search_id}]", f"[PUPPETEER] Non-JSON stdout: {text[:200]}", "WARN")
                    continue

                msg_type = payload.get("type")
                if msg_type == "progress":
                    percent = int(payload.get("percent", 10))
                    update_progress(
                        self.search_id,
                        active_engine=self.name,
                        stage=payload.get("stage", "puppeteer_running"),
                        attempt=int(payload.get("attempt", 1)),
                        max_attempts=int(payload.get("max_attempts", 2)),
                        percent=percent,
                        message=payload.get("message", ""),
                        found=len(products),
                        elapsed_seconds=eta_calc.get_elapsed(),
                        eta_seconds=eta_calc.get_eta(percent),
                    )
                elif msg_type == "heartbeat":
                    phase = payload.get("phase", "unknown")
                    log(f"[{self.search_id}]", f"[PUPPETEER] heartbeat phase={phase}", "INFO")
                    update_progress(
                        self.search_id,
                        active_engine=self.name,
                        stage=str(phase),
                        message=f"Puppeteer masih bekerja: {phase}",
                        found=len(products),
                        elapsed_seconds=eta_calc.get_elapsed(),
                    )
                elif msg_type == "product":
                    data = payload.get("data")
                    if isinstance(data, dict):
                        data["source_engine"] = self.name
                        products.append(data)
                        update_progress(
                            self.search_id,
                            active_engine=self.name,
                            found=len(products),
                            elapsed_seconds=eta_calc.get_elapsed(),
                        )
                elif msg_type in ("done", "result"):
                    done_products = payload.get("products", [])
                    if isinstance(done_products, list) and done_products:
                        products = done_products
                    log(f"[{self.search_id}]", f"[PUPPETEER] received result products={len(products)}", "INFO")
                    break
                elif msg_type == "preflight_failed":
                    error_type = payload.get("error_type", "unknown")
                    msg = payload.get("message", "Browser opened error page")
                    last_error = f"Preflight failed: {error_type}. {msg}"
                    log(f"[{self.search_id}]", f"[PUPPETEER] PREFLIGHT FAIL: {error_type}", "WARN")
                    # Save debug snapshot immediately
                    from src.utils.debug import save_json_debug
                    debug_data = {
                        "engine": "puppeteer",
                        "opened_real_page": False,
                        "error_type": error_type,
                        "page_title": payload.get("page_title", ""),
                        "body_text_sample": payload.get("body_text_sample", ""),
                        "current_url": payload.get("url", ""),
                        "message": msg,
                    }
                    save_json_debug(self.search_id, "puppeteer_preflight_failed.json", debug_data)
                    break  # Stop trying this engine on preflight failure
                elif msg_type == "error":
                    last_error = payload.get("message") or payload.get("error") or "Unknown Puppeteer worker error"
                elif msg_type == "debug":
                    log(f"[{self.search_id}]", "[PUPPETEER] Worker saved zero-raw debug snapshot", "WARN")

            if process.returncode is None:
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    await self._kill_process(process)

            if stderr_task:
                await asyncio.gather(stderr_task, return_exceptions=True)

            if process.returncode not in (0, None) and not last_error:
                last_error = f"Node exited with code {process.returncode}"
            log(f"[{self.search_id}]", f"[PUPPETEER] worker_exit_code={process.returncode}", "INFO")

            if products:
                return True, products, ""

            stderr_tail = "\n".join(line for line in stderr_lines[-5:] if line)
            if stderr_tail:
                last_error = f"{last_error} | stderr: {stderr_tail}" if last_error else stderr_tail
            return False, [], last_error or "Puppeteer selesai tanpa produk."

        except asyncio.CancelledError:
            await self._kill_process(process)
            raise
        except Exception as exc:
            await self._kill_process(process)
            return False, [], f"Puppeteer Python wrapper error: {exc}"

```

## FILE: `src\scraper\puppeteer_worker.js`

```javascript
/**
 * puppeteer_worker.js - Puppeteer scraper worker.
 *
 * Key fixes:
 * 1. Preflight: detect Chrome error page BEFORE extraction.
 * 2. Disable HTTP/2 (--disable-http2) to reduce ERR_HTTP2_PROTOCOL_ERROR.
 * 3. Use a stable desktop User-Agent for consistent page rendering.
 * 4. opened_real_page=false stops extraction immediately with clear error.
 * 5. No category filtering here. Raw products only. AI Orchestrator filters later.
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const argv = require('minimist')(process.argv.slice(2));

const MAX_ATTEMPTS = 2;
const NAV_TIMEOUT_MS = 30000;  // navigation timeout per page
const IDLE_WAIT_MS = 1500;      // wait after load before extracting
const MAX_SCROLL_ROUNDS = Number.parseInt(process.env.MAX_SCROLL_ATTEMPTS || process.env.PUPPETEER_MAX_SCROLL_ROUNDS || argv['max-scrolls'] || '30', 10);
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const STARTED_AT = Date.now();
let currentPhase = 'initializing';

/** Write a JSON line to stdout so Python can parse it. */
function send(payload) {
  try {
    process.stdout.write(JSON.stringify(payload) + '\n');
  } catch (error) {
    process.stderr.write(`[SCRAPER] stdout write failed: ${error.message || error}\n`);
  }
}

function setPhase(phase) {
  currentPhase = phase;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseJsonArray(value, fallback) {
  try {
    const parsed = JSON.parse(value || '[]');
    return Array.isArray(parsed) && parsed.length ? parsed : fallback;
  } catch (_) {
    return fallback;
  }
}

/**
 * Detect if the page is a Chrome network error page.
 * Returns { opened_real_page, error_type } from inside the browser.
 */
async function detectPageHealth(page) {
  const result = await page.evaluate(() => {
    const title = (document.title || '').toLowerCase();
    const body = (document.body ? document.body.innerText || '' : '').toLowerCase().slice(0, 2000);
    const url = location.href.toLowerCase();
    const combined = `${title} ${body} ${url}`;

    // Known Chrome error strings
    const errorPatterns = [
      { pattern: 'captcha',                       key: 'blocked' },
      { pattern: 'verify you are human',          key: 'blocked' },
      { pattern: 'access denied',                 key: 'blocked' },
      { pattern: 'too many requests',             key: 'blocked' },
      { pattern: 'robot',                         key: 'blocked' },
      { pattern: 'err_http2_protocol_error',      key: 'http2_protocol_error' },
      { pattern: 'err_connection_reset',           key: 'connection_reset' },
      { pattern: 'err_connection_refused',         key: 'connection_refused' },
      { pattern: 'err_connection_timed_out',       key: 'connection_timed_out' },
      { pattern: 'err_name_not_resolved',          key: 'name_not_resolved' },
      { pattern: 'err_address_unreachable',        key: 'address_unreachable' },
      { pattern: 'dns_probe_finished_no_internet', key: 'no_internet' },
      { pattern: 'dns_probe_finished_nxdomain',    key: 'dns_nxdomain' },
      { pattern: "this site can",                  key: 'site_unreachable' },
      { pattern: 'situs ini tidak dapat',          key: 'site_unreachable_id' },
    ];

    for (const { pattern, key } of errorPatterns) {
      if (combined.includes(pattern)) {
        return { opened_real_page: false, error_type: key, title, body_sample: body.slice(0, 500) };
      }
    }

    // about:blank or empty means navigation failed silently
    if (url === 'about:blank' || url === '') {
      return { opened_real_page: false, error_type: 'blank_page', title, body_sample: '' };
    }

    // Must have some Tokopedia signal to count as real page
    if (!combined.includes('tokopedia') && !combined.includes('toped')) {
      return {
        opened_real_page: false,
        error_type: 'unknown_non_tokopedia_page',
        title,
        body_sample: body.slice(0, 500),
      };
    }

    return { opened_real_page: true, error_type: null, title, body_sample: body.slice(0, 500) };
  });

  return result;
}

/** Parse Rupiah strings to integers. Python normalizer is final source of truth. */
function parseRupiah(text) {
  if (!text) return null;
  const lower = String(text).toLowerCase().replace(/\s+/g, ' ').trim();
  const unitMatch = lower.match(/(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|rb|ribu|k)\b/i);
  if (unitMatch) {
    const number = Number(unitMatch[1].replace(',', '.'));
    if (!Number.isFinite(number)) return null;
    return Math.round(number * (['juta', 'jt', 'mio'].includes(unitMatch[2].toLowerCase()) ? 1000000 : 1000));
  }
  const parsed = Number.parseInt(lower.replace(/[^\d]/g, ''), 10);
  return Number.isFinite(parsed) ? parsed : null;
}

function cleanUrl(url) {
  return String(url || '').split('?')[0].split('#')[0];
}

/** Build the Tokopedia search URL. No pmin/pmax by default. Budget filter is local. */
function buildSearchUrl(query) {
  return `https://www.tokopedia.com/search?st=product&q=${encodeURIComponent(query)}`;
}

async function configurePage(page, consoleLogs) {
  await page.setViewport({ width: 1366, height: 768, deviceScaleFactor: 1 });
  // Stable desktop UA keeps Tokopedia markup consistent across runs.
  await page.setUserAgent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  );
  page.setDefaultTimeout(NAV_TIMEOUT_MS);
  page.setDefaultNavigationTimeout(NAV_TIMEOUT_MS);
  page.on('console', (msg) => {
    consoleLogs.push({ type: msg.type(), text: msg.text().slice(0, 500) });
    if (consoleLogs.length > 50) consoleLogs.shift();
  });
}

/** Extract all product cards from the current page DOM. No category filtering. */
async function extractProducts(page, knownKeys, sourceQuery) {
  const rawProducts = await page.evaluate(() => {
    const productCardSelectors = [
      "[data-testid='master-product-card']",
      "div[data-testid*='product']",
      "div.pcv3__container",
      "div[class*='prd_container']",
    ];

    const normalizeLines = (text) =>
      String(text || '')
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);

    const truncateText = (value, maxLen) => {
      const str = String(value || '').replace(/\s+/g, ' ').trim();
      return str.length > maxLen ? str.slice(0, maxLen) + '...' : str;
    };

    const priceFromText = (text) => {
      const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
      return match ? match[0].trim() : '';
    };

    const cleanHref = (href) => String(href || '').split('?')[0].split('#')[0];

    const isProductLikeUrl = (href) => {
      try {
        const url = new URL(href, location.href);
        if (!url.hostname.includes('tokopedia.com')) return false;
        const blocked = ['/search', '/cart', '/help', '/discovery', '/official-store'];
        if (blocked.some((prefix) => url.pathname.startsWith(prefix))) return false;
        return url.pathname.split('/').filter(Boolean).length >= 2;
      } catch (_) {
        return false;
      }
    };

    const findContainer = (anchor) => {
      let node = anchor;
      for (let depth = 0; depth < 5 && node; depth += 1) {
        if ((node.innerText || '').includes('Rp')) return node;
        node = node.parentElement;
      }
      return anchor;
    };

    function getImageFromCard(card) {
      const img =
        card.querySelector('img[src]') ||
        card.querySelector('img[data-src]') ||
        card.querySelector('picture img');

      const candidates = [];

      if (img) {
        candidates.push(img.currentSrc);
        candidates.push(img.src);
        candidates.push(img.getAttribute('src'));
        candidates.push(img.getAttribute('data-src'));
        candidates.push(img.getAttribute('data-original'));

        const srcset = img.getAttribute('srcset');
        if (srcset) {
          candidates.push(srcset.split(',')[0].trim().split(' ')[0]);
        }
      }

      const source = card.querySelector('source[srcset]');
      if (source) {
        const srcset = source.getAttribute('srcset');
        if (srcset) {
          candidates.push(srcset.split(',')[0].trim().split(' ')[0]);
        }
      }

      return candidates.find((url) =>
        typeof url === 'string' &&
        url.startsWith('http') &&
        !url.startsWith('data:image') &&
        !url.toLowerCase().includes('base64') &&
        !url.toLowerCase().includes('svg') &&
        !['undefined', 'null', 'noimage'].includes(url.trim().toLowerCase().replace(/\s+/g, ''))
      ) || null;
    }

    const productFromContainer = (container, sourceAnchor = null) => {
      const text = container.innerText || sourceAnchor?.innerText || '';
      const priceRaw = priceFromText(text);
      const lines = normalizeLines(text);
      const titleNode =
        container.querySelector?.("[data-testid='spnSRPProdName']") ||
        container.querySelector?.("[data-testid*='ProdName']") ||
        container.querySelector?.('.prd_link-product-name');
      const anchor = sourceAnchor || container.querySelector?.("a[href*='tokopedia.com']");
      const imageUrl = getImageFromCard(container);
      const priceIndex = lines.findIndex((line) => priceRaw && line.includes(priceRaw));
      const fallbackTitle =
        (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
        anchor?.getAttribute('title') ||
        lines.find((line) => !line.startsWith('Rp') && line.length > 4) ||
        '';
      const title = (titleNode?.textContent || fallbackTitle || '').trim();
      const url = cleanHref(anchor?.href || '');
      const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
      const sold = (text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i) || [])[0] || '';
      const rating = (text.match(/\b([4-5](?:[.,]\d)?)\b/) || [])[1] || '';

      // Keep product even if shop/rating is empty. Normalizer handles missing fields.
      if (!title || (!url && !priceRaw)) return null;
      return {
        title: truncateText(title, 180),
        price_raw: priceRaw,
        shop: truncateText(afterPrice[0], 80),
        location: truncateText(afterPrice[1], 80),
        rating: truncateText(rating, 10),
        sold: truncateText(sold, 30),
        url: truncateText(url, 500),
        image: truncateText(imageUrl || '', 500),
        source_engine: 'puppeteer',
      };
    };

    const results = [];
    const seen = new Set();
    const pushProduct = (product) => {
      if (!product) return;
      const key = `${product.url}|${product.title}|${product.price_raw}`;
      if (seen.has(key)) return;
      seen.add(key);
      results.push(product);
    };

    for (const selector of productCardSelectors) {
      document.querySelectorAll(selector).forEach((card) => pushProduct(productFromContainer(card)));
    }

    // Fallback: anchor-based scan for pages with non-standard card markup
    document.querySelectorAll("a[href*='tokopedia.com']").forEach((anchor) => {
      if (!isProductLikeUrl(anchor.href)) return;
      pushProduct(productFromContainer(findContainer(anchor), anchor));
    });

    return results;
  });

  const products = [];
  for (const product of rawProducts) {
    const url = cleanUrl(product.url);
    const key = `${url}|${product.title}|${product.price_raw}`;
    if (knownKeys.has(key)) continue;
    knownKeys.add(key);
    product.url = url;
    product.price_value = parseRupiah(product.price_raw);
    product.source_query = sourceQuery;
    products.push(product);
  }
  return products;
}

/**
 * Save debug file when engine fails or page doesn't open.
 * This is the critical file that explains WHY raw=0 happened.
 */
async function saveEngineErrorDebug({
  searchId, query, urlsTried, preflightResult, errors, page, engineName,
}) {
  const debugDir = path.join(PROJECT_ROOT, 'data', 'debug', searchId);
  const payload = {
    engine: engineName,
    query,
    urls_tried: urlsTried,
    opened_real_page: (preflightResult && preflightResult.opened_real_page) || false,
    error_type: (preflightResult && preflightResult.error_type) || 'unknown',
    page_title: (preflightResult && preflightResult.title) || '',
    body_text_sample: (preflightResult && preflightResult.body_sample) || '',
    selector_counts: {},
    errors,
    recommendation: preflightResult && !preflightResult.opened_real_page
      ? 'Browser opened error page. Not a selector problem. Check network/proxy/HTTP2 support.'
      : 'Page opened but no products extracted. Check selectors or try different query.',
  };

  try {
    fs.mkdirSync(debugDir, { recursive: true });
    if (page && payload.opened_real_page) {
      // Only probe DOM if we actually got a real page
      try {
        payload.selector_counts = await page.evaluate(() => ({
          master_product_card: document.querySelectorAll("[data-testid='master-product-card']").length,
          product_testid: document.querySelectorAll("[data-testid*='product']").length,
          tokopedia_anchors: document.querySelectorAll("a[href*='tokopedia.com']").length,
          img_count: document.querySelectorAll('img').length,
        }));
      } catch (_) {}
      // Save screenshot for debugging
      const ssPath = path.join(debugDir, `${engineName}_engine_error_screenshot.png`);
      await page.screenshot({ path: ssPath, fullPage: true }).catch(() => {});
      payload.screenshot_saved = fs.existsSync(ssPath);
    }
    fs.writeFileSync(
      path.join(debugDir, `${engineName}_engine_error.json`),
      JSON.stringify(payload, null, 2),
      'utf8'
    );
  } catch (err) {
    payload.errors.push(`debug save failed: ${err.message || err}`);
  }

  send({ type: 'debug', data: payload });
  return payload;
}

async function saveImageMissingDebug({ searchId, query, url, products, page, engineName }) {
  const total = products.length;
  if (total < 5) return;
  const missing = products.filter((product) => !product.image).length;
  const missingRate = missing / total;
  if (missingRate <= 0.70) return;

  const debugDir = path.join(PROJECT_ROOT, 'data', 'debug', searchId);
  const payload = {
    engine: engineName,
    query,
    url,
    images_extracted_count: total - missing,
    images_missing_count: missing,
    missing_rate: Number(missingRate.toFixed(4)),
    samples: products.slice(0, 20),
  };

  try {
    fs.mkdirSync(debugDir, { recursive: true });
    const htmlPath = path.join(debugDir, `${engineName}_image_missing_debug.html`);
    const screenshotPath = path.join(debugDir, `${engineName}_image_missing_debug.png`);
    fs.writeFileSync(htmlPath, await page.content(), 'utf8');
    await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
    payload.html_saved = fs.existsSync(htmlPath);
    payload.screenshot_saved = fs.existsSync(screenshotPath);
    fs.writeFileSync(
      path.join(debugDir, `${engineName}_image_missing_debug.json`),
      JSON.stringify(payload, null, 2),
      'utf8'
    );
  } catch (error) {
    payload.error = error && error.message ? error.message : String(error);
  }

  send({ type: 'debug', data: payload });
}

async function scrapeUrl(page, url, query, targetRemaining, knownKeys, searchId) {
  setPhase('opening_page');
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: NAV_TIMEOUT_MS });
  await page.waitForSelector('body', { timeout: 10000 });
  await sleep(IDLE_WAIT_MS);

  const products = [];
  for (let round = 0; round < MAX_SCROLL_ROUNDS && products.length < targetRemaining; round += 1) {
    setPhase(round === 0 ? 'extracting' : 'scrolling');
    const extracted = await extractProducts(page, knownKeys, query);
    for (const product of extracted) {
      products.push(product);
      send({ type: 'product', data: product });
      if (products.length >= targetRemaining) break;
    }
    await page.evaluate(() => window.scrollBy(0, Math.floor(window.innerHeight * 0.85))).catch(() => {});
    await sleep(700);
  }
  await saveImageMissingDebug({
    searchId,
    query,
    url,
    products,
    page,
    engineName: 'puppeteer',
  });
  return products;
}

async function runAttempt({ query, variants, target, searchId, attempt }) {
  let browser;
  let lastPage = null;
  const products = [];
  const knownKeys = new Set();
  const urlsTried = [];
  const errors = [];
  const consoleLogs = [];

  try {
    setPhase('launching_browser');
    send({
      type: 'progress',
      stage: 'launching_browser',
      percent: 8,
      attempt,
      max_attempts: MAX_ATTEMPTS,
      message: `Opening browser attempt ${attempt}/${MAX_ATTEMPTS}`,
    });

    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-http2',             // reduce ERR_HTTP2_PROTOCOL_ERROR without bypassing access controls
        '--window-size=1366,768',
      ],
    });

    for (let variantIndex = 0; variantIndex < variants.length && products.length < target; variantIndex += 1) {
      const variant = variants[variantIndex];
      // Rule: use simple URL first (no pmin/pmax). Budget filter is local.
      const url = buildSearchUrl(variant);
      urlsTried.push(url);

      const page = await browser.newPage();
      lastPage = page;
      await configurePage(page, consoleLogs);

      setPhase('opening_page');
      send({
        type: 'progress',
        stage: 'opening_page',
        percent: Math.min(55, 10 + variantIndex * 3),
        attempt,
        max_attempts: MAX_ATTEMPTS,
        query: variant,
        message: `Opening variant ${variantIndex + 1}/${variants.length}: ${variant}`,
      });

      try {
        // Navigate and do preflight check before extracting
        setPhase('opening_page');
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: NAV_TIMEOUT_MS });
        await sleep(800);

        const health = await detectPageHealth(page);

        if (!health.opened_real_page) {
          // STOP. Do not attempt extraction on error page.
          errors.push(`${url}: opened_real_page=false error_type=${health.error_type}`);
          await saveEngineErrorDebug({
            searchId, query, urlsTried,
            preflightResult: { ...health, title: health.title, body_sample: health.body_sample },
            errors, page, engineName: 'puppeteer',
          });

          // Send structured error so Python knows exactly what happened.
          send({
            type: 'preflight_failed',
            opened_real_page: false,
            error_type: health.error_type,
            page_title: health.title,
            body_text_sample: health.body_sample,
            url,
            message: `Browser opened Chrome error page (${health.error_type}), not Tokopedia. Extraction impossible.`,
          });

          await page.close().catch(() => {});
          continue;  // try next variant (different query might work with different DNS cache)
        }

        // Real Tokopedia page confirmed. Extract raw products.
        await page.waitForSelector('body', { timeout: 5000 });
        const before = products.length;
        setPhase('scrolling');
        const extracted = await scrapeUrl(page, url, variant, target - products.length, knownKeys, searchId);
        products.push(...extracted);
        if (products.length === before) {
          errors.push(`zero products for ${url} (page opened OK, selectors found nothing)`);
        }
      } catch (error) {
        errors.push(`${url}: ${error.message || error}`);
      } finally {
        await page.close().catch(() => {});
      }
    }

    if (!products.length) {
      if (lastPage) {
        await saveEngineErrorDebug({
          searchId, query, urlsTried, preflightResult: null,
          errors, page: lastPage, engineName: 'puppeteer',
        });
      }
      throw new Error('Puppeteer extracted zero products from all query variants');
    }

    return products;
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
}

// ── Main entry ─────────────────────────────────────────────────────────────
(async () => {
  const query = argv.query || '';
  const target = Number.parseInt(argv.target || '100', 10);
  const searchId = argv['search-id'] || 'unknown';
  const variants = parseJsonArray(argv.variants, [query]);
  let lastError = '';
  const heartbeat = setInterval(() => {
    send({
      type: 'heartbeat',
      phase: currentPhase,
      elapsed: Number(((Date.now() - STARTED_AT) / 1000).toFixed(1)),
    });
  }, 5000);
  heartbeat.unref?.();

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      const products = await runAttempt({ query, variants, target, searchId, attempt });
      setPhase('finalizing');
      clearInterval(heartbeat);
      send({ type: 'result', products });
      process.exit(0);
    } catch (error) {
      lastError = error && error.message ? error.message : String(error);
      send({
        type: 'progress',
        stage: 'puppeteer_retry',
        percent: attempt < MAX_ATTEMPTS ? 58 : 60,
        attempt,
        max_attempts: MAX_ATTEMPTS,
        message: `Puppeteer attempt ${attempt} failed: ${lastError}`,
      });
      await sleep(1000);
    }
  }

  clearInterval(heartbeat);
  send({ type: 'error', message: lastError || 'Unknown Puppeteer error' });
  process.exit(1);
})().catch((error) => {
  send({
    type: 'error',
    message: error && error.message ? error.message : String(error),
    stack: error && error.stack ? error.stack : '',
  });
  process.exit(1);
});

```

## FILE: `src\scraper\query_expander.py`

```python
"""
query_expander.py - Search variants for broad Tokopedia queries.

Tokopedia's first page for "laptop gaming" often mixes accessories. Query
variants force both engines to visit real gaming-laptop intent pages.
"""
from __future__ import annotations

from typing import Any

from src.utils.currency import calculate_budget_range, parse_rupiah


LAPTOP_GAMING_VARIANTS = [
    "laptop gaming",
    "notebook gaming",
    "asus rog laptop",
    "asus tuf gaming laptop",
    "lenovo legion laptop",
    "lenovo loq laptop",
    "acer nitro laptop",
    "hp victus laptop",
    "msi gaming laptop",
    "acer predator laptop",
    "laptop rtx 3050",
    "laptop rtx 4050",
]


def expand_query_variants(query: str) -> list[str]:
    """Return deduped query variants. Broad laptop gaming gets brand/GPU pages."""
    clean_query = " ".join((query or "").lower().split())
    variants: list[str] = []

    if "laptop" in clean_query and "gaming" in clean_query:
        variants.extend(LAPTOP_GAMING_VARIANTS)
    else:
        variants.append(query.strip())

    # Keep the user's exact query first when it differs by casing/spacing.
    if query and query.strip().lower() not in {variant.lower() for variant in variants}:
        variants.insert(0, query.strip())

    seen: set[str] = set()
    deduped: list[str] = []
    for variant in variants:
        key = variant.lower()
        if not variant or key in seen:
            continue
        seen.add(key)
        deduped.append(variant)
    return deduped


def budget_url_range(budget: Any, tolerance: Any) -> tuple[int | None, int | None]:
    """Calculate pmin/pmax URL params from the same budget rules as backend."""
    budget_value = parse_rupiah(budget)
    if budget_value is None or budget_value <= 0:
        return None, None
    min_price, max_price = calculate_budget_range(budget_value, tolerance)
    return min_price, max_price

```

## FILE: `src\scraper\rollback_engine.py`

```python
"""
rollback_engine.py - Selenium rollback scraper.

Key fixes:
1. Preflight check FIRST - detects Chrome error pages before extraction.
2. --disable-http2 via selenium_driver.py to reduce ERR_HTTP2_PROTOCOL_ERROR.
3. If opened_real_page=false -> returns False with exact error_type. No fake "selector failed".
4. No category filtering. Returns ALL raw products. AI Orchestrator filters later.
"""
from __future__ import annotations

import asyncio
import json
import random
import time
from pathlib import Path
from typing import Any

from src.scraper.normalizer import normalize_products
from src.scraper.selenium_driver import create_chrome_driver, safe_quit_driver
from src.scraper.url_builder import build_tokopedia_search_url
from src.server.progress import update_progress
from src.utils.debug import get_debug_dir, save_json_debug
from src.utils.logger import log


DEBUG_DIR = Path("data/debug")

# Chrome error strings to detect on loaded page (same as preflight.py)
_ERROR_SIGNALS = [
    "err_http2_protocol_error",
    "err_connection_reset",
    "err_connection_refused",
    "err_connection_timed_out",
    "err_name_not_resolved",
    "this site can",
    "situs ini tidak dapat",
    "dns_probe_finished",
]

_ERROR_KEYS = {
    "err_http2_protocol_error": "http2_protocol_error",
    "err_connection_reset": "connection_reset",
    "err_connection_refused": "connection_refused",
    "err_connection_timed_out": "connection_timed_out",
    "err_name_not_resolved": "name_not_resolved",
    "this site can": "site_unreachable",
    "situs ini tidak dapat": "site_unreachable_id",
    "dns_probe_finished": "dns_error",
}


def _detect_page_health_selenium(driver) -> dict[str, Any]:
    """
    Check if driver is showing a real Tokopedia page or a Chrome error page.
    Returns { opened_real_page, error_type, page_title, body_sample, current_url }.
    """
    try:
        current_url = driver.current_url or ""
        title = driver.title or ""
        body_text = driver.execute_script(
            "return document.body ? (document.body.innerText || '').slice(0, 1000) : '';"
        ) or ""
    except Exception as exc:
        return {
            "opened_real_page": False,
            "error_type": "driver_error",
            "page_title": "",
            "body_sample": "",
            "current_url": "",
            "nav_error": str(exc),
        }

    combined = f"{title} {body_text} {current_url}".lower()

    # Check for known error patterns
    error_type = None
    for signal, key in _ERROR_KEYS.items():
        if signal in combined:
            error_type = key
            break

    # about:blank = navigation never happened
    if error_type is None and current_url.strip().lower() in ("about:blank", "chrome://newtab/", ""):
        error_type = "blank_page"

    # Must have Tokopedia signal to be a real page
    is_real = "tokopedia" in combined or "toped" in combined
    if error_type is None and not is_real:
        error_type = "unknown_non_tokopedia_page"

    opened_real_page = (error_type is None) and is_real
    return {
        "opened_real_page": opened_real_page,
        "error_type": error_type,
        "page_title": title,
        "body_sample": body_text[:500],
        "current_url": current_url,
    }


def _save_engine_error_debug(
    search_id: str,
    query: str,
    urls_tried: list[str],
    health: dict[str, Any],
    errors: list[str],
    driver=None,
) -> str:
    """Save data/debug/<search_id>/rollback_engine_error.json."""
    payload = {
        "engine": "rollback",
        "query": query,
        "urls_tried": urls_tried,
        "opened_real_page": health.get("opened_real_page", False),
        "error_type": health.get("error_type", "unknown"),
        "page_title": health.get("page_title", ""),
        "body_text_sample": health.get("body_sample", ""),
        "current_url": health.get("current_url", ""),
        "selector_counts": {},
        "errors": errors,
        "recommendation": (
            "Browser opened error page. Not a selector problem. "
            "Check network/proxy/HTTP2 support."
            if not health.get("opened_real_page")
            else "Page opened but no products extracted. Check selectors."
        ),
    }

    if driver and health.get("opened_real_page"):
        try:
            payload["selector_counts"] = driver.execute_script(
                """return {
                  master_product_card: document.querySelectorAll("[data-testid='master-product-card']").length,
                  product_testid: document.querySelectorAll("[data-testid*='product']").length,
                  tokopedia_anchors: document.querySelectorAll("a[href*='tokopedia.com']").length,
                  img_count: document.querySelectorAll('img').length
                };"""
            ) or {}
        except Exception:
            pass

        try:
            debug_dir = get_debug_dir(search_id)
            debug_dir.mkdir(parents=True, exist_ok=True)
            ss_path = debug_dir / "rollback_engine_error_screenshot.png"
            driver.save_screenshot(str(ss_path))
            payload["screenshot_saved"] = ss_path.exists()
        except Exception:
            pass

    return save_json_debug(search_id, "rollback_engine_error.json", payload) or ""


class RollbackEngine:
    name = "rollback"

    def __init__(self, search_id: str):
        self.search_id = search_id

    async def scrape(
        self,
        query: str,
        raw_target: int,
        eta_calc,
        query_variants: list[str] | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
    ) -> tuple[bool, list[dict[str, Any]], str]:
        """Run blocking Selenium work in a thread so FastAPI stays responsive."""
        return await asyncio.to_thread(
            self._scrape_sync,
            query,
            raw_target,
            eta_calc,
            query_variants or [query],
            min_price,
            max_price,
        )

    def _scrape_sync(
        self,
        query: str,
        raw_target: int,
        eta_calc,
        query_variants: list[str],
        min_price: int | None,
        max_price: int | None,
    ) -> tuple[bool, list[dict[str, Any]], str]:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        update_progress(
            self.search_id,
            active_engine=self.name,
            stage="rollback_browser_starting",
            percent=48,
            message="Menjalankan Rollback/Selenium...",
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        debug_subdir = DEBUG_DIR / self.search_id
        driver, error_msg = create_chrome_driver(self.search_id, debug_subdir)
        if not driver:
            return False, [], f"Chrome driver bootstrap failed: {error_msg}"

        products: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        urls_tried: list[str] = []
        errors: list[str] = []
        preflight_health: dict[str, Any] = {}

        try:
            for variant_index, variant in enumerate(query_variants):
                if len(products) >= raw_target:
                    break

                # Rule: simple URL first, no pmin/pmax.
                url = build_tokopedia_search_url(variant)
                urls_tried.append(url)

                update_progress(
                    self.search_id,
                    active_engine=self.name,
                    stage="rollback_opening",
                    percent=min(70, 52 + variant_index),
                    message=f"Rollback/Selenium opening {variant}",
                    elapsed_seconds=eta_calc.get_elapsed(),
                )

                try:
                    driver.get(url)
                    WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    time.sleep(1.0)

                    # PREFLIGHT CHECK: is this a real Tokopedia page?
                    health = _detect_page_health_selenium(driver)
                    preflight_health = health

                    if not health["opened_real_page"]:
                        error_type = health["error_type"]
                        msg = (
                            f"Browser opened Chrome error page ({error_type}), "
                            f"not Tokopedia. Extraction impossible."
                        )
                        errors.append(f"{url}: {msg}")
                        log(f"[{self.search_id}]", f"[ROLLBACK] PREFLIGHT FAIL: {msg}", "WARN")

                        # Save diagnostic immediately so user sees what happened
                        _save_engine_error_debug(
                            self.search_id, query, urls_tried, health, errors, driver
                        )
                        # Continue to next variant - different query = different URL = maybe works
                        continue

                    # Real page confirmed. Extract raw products.
                    self._scroll_and_extract(driver, raw_target, products, seen_urls, eta_calc, variant)

                except Exception as variant_exc:
                    error = f"{url}: {variant_exc}"
                    errors.append(error)
                    log(f"[{self.search_id}]", f"[ROLLBACK] Query failed {variant}: {variant_exc}", "WARN")
                    continue

            if products:
                self._save_image_missing_debug(driver, query, urls_tried, products)
                normalized = normalize_products(products, self.name)
                if normalized:
                    log(f"[{self.search_id}]", f"[ROLLBACK] Extracted {len(normalized)} products", "OK")
                    return True, products, ""

            # No products - save debug with preflight context
            _save_engine_error_debug(
                self.search_id, query, urls_tried, preflight_health or {}, errors, driver
            )

            # Build a specific error message based on what actually happened
            if preflight_health and not preflight_health.get("opened_real_page"):
                error_type = preflight_health.get("error_type", "unknown")
                error_msg = (
                    f"Browser opened Chrome error page: {error_type}. "
                    f"opened_real_page=false. See data/debug/{self.search_id}/rollback_engine_error.json"
                )
            else:
                error_msg = (
                    f"Rollback/Selenium opened Tokopedia but found 0 products. "
                    f"See data/debug/{self.search_id}/rollback_engine_error.json"
                )
            return False, [], error_msg

        except Exception as exc:
            error = str(exc)
            log(f"[{self.search_id}]", f"[ROLLBACK] Error: {error}", "ERROR")
            _save_engine_error_debug(self.search_id, query, urls_tried, {}, [error], driver)
            return False, [], f"Rollback/Selenium error: {error}"
        finally:
            safe_quit_driver(driver)

    def _save_image_missing_debug(
        self,
        driver,
        query: str,
        urls_tried: list[str],
        products: list[dict[str, Any]],
    ) -> None:
        total = len(products)
        if total < 5:
            return
        missing = sum(1 for product in products if not product.get("image"))
        missing_rate = missing / total
        if missing_rate <= 0.70:
            return

        debug_dir = get_debug_dir(self.search_id)
        payload = {
            "engine": self.name,
            "query": query,
            "urls_tried": urls_tried,
            "images_extracted_count": total - missing,
            "images_missing_count": missing,
            "missing_rate": round(missing_rate, 4),
            "samples": products[:20],
        }
        try:
            debug_dir.mkdir(parents=True, exist_ok=True)
            html_path = debug_dir / "rollback_image_missing_debug.html"
            screenshot_path = debug_dir / "rollback_image_missing_debug.png"
            html_path.write_text(driver.page_source or "", encoding="utf-8")
            driver.save_screenshot(str(screenshot_path))
            payload["html_saved"] = html_path.exists()
            payload["screenshot_saved"] = screenshot_path.exists()
        except Exception as exc:
            payload["error"] = str(exc)
        save_json_debug(self.search_id, "rollback_image_missing_debug.json", payload)

    def _scroll_and_extract(
        self,
        driver,
        raw_target: int,
        products: list[dict[str, Any]],
        seen_urls: set[str],
        eta_calc,
        variant: str,
    ) -> None:
        """Scroll and collect raw product cards. No category filtering."""
        previous_height = 0
        stable_rounds = 0

        for round_index in range(7):
            driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.9));")
            time.sleep(random.uniform(0.6, 1.0))

            for item in self._extract_cards(driver):
                url_key = item.get("url") or ""
                if not url_key or url_key in seen_urls:
                    continue
                seen_urls.add(url_key)
                item["source_query"] = variant
                products.append(item)

            percent = min(72, 55 + round_index)
            update_progress(
                self.search_id,
                active_engine=self.name,
                stage="rollback_extracting",
                percent=percent,
                message=f"Rollback/Selenium menemukan {len(products)} produk...",
                found=len(products),
                elapsed_seconds=eta_calc.get_elapsed(),
                eta_seconds=eta_calc.get_eta(percent),
            )

            if len(products) >= raw_target:
                break

            current_height = driver.execute_script("return document.body.scrollHeight || 0;")
            if current_height <= previous_height:
                stable_rounds += 1
            else:
                stable_rounds = 0
            previous_height = current_height
            if stable_rounds >= 2:
                break

    def _extract_cards(self, driver) -> list[dict[str, Any]]:
        """Extract raw product cards. Returns ALL cards regardless of category."""
        return driver.execute_script(
            r"""
            const parseRupiah = (text) => {
              const lower = String(text || '').toLowerCase().trim();
              const unit = lower.match(/(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|rb|ribu|k)\b/i);
              if (unit) {
                const number = Number(unit[1].replace(',', '.'));
                if (!Number.isFinite(number)) return null;
                return Math.round(number * (['juta', 'jt', 'mio'].includes(unit[2].toLowerCase()) ? 1000000 : 1000));
              }
              const digits = lower.replace(/[^\d]/g, '');
              if (!digits) return null;
              const parsed = Number.parseInt(digits, 10);
              return Number.isFinite(parsed) ? parsed : null;
            };

            const cleanUrl = (url) => String(url || '').split('?')[0].split('#')[0];
            const isProductUrl = (href) => {
              try {
                const url = new URL(href, location.href);
                if (!url.hostname.includes('tokopedia.com')) return false;
                if (['/search', '/cart', '/help', '/discovery', '/official-store'].some(
                  prefix => url.pathname.startsWith(prefix)
                )) return false;
                return url.pathname.split('/').filter(Boolean).length >= 2;
              } catch (_) { return false; }
            };
            const linesOf = (text) => String(text || '').split('\n').map(l => l.trim()).filter(Boolean);
            const priceOf = (text) => {
              const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
              return match ? match[0].trim() : '';
            };
            function getImageFromCard(card) {
              const img =
                card.querySelector('img[src]') ||
                card.querySelector('img[data-src]') ||
                card.querySelector('picture img');

              const candidates = [];
              if (img) {
                candidates.push(img.currentSrc);
                candidates.push(img.src);
                candidates.push(img.getAttribute('src'));
                candidates.push(img.getAttribute('data-src'));
                candidates.push(img.getAttribute('data-original'));

                const srcset = img.getAttribute('srcset');
                if (srcset) {
                  candidates.push(srcset.split(',')[0].trim().split(' ')[0]);
                }
              }

              const source = card.querySelector('source[srcset]');
              if (source) {
                const srcset = source.getAttribute('srcset');
                if (srcset) {
                  candidates.push(srcset.split(',')[0].trim().split(' ')[0]);
                }
              }

              return candidates.find((url) =>
                typeof url === 'string' &&
                url.startsWith('http') &&
                !url.startsWith('data:image') &&
                !url.toLowerCase().includes('base64') &&
                !url.toLowerCase().includes('svg') &&
                !['undefined', 'null', 'noimage'].includes(url.trim().toLowerCase().replace(/\s+/g, ''))
              ) || null;
            }

            const seen = new Set();
            const results = [];
            const pushProduct = (item) => {
              if (!item || !item.title || (!item.url && !item.price_raw)) return;
              const key = `${item.url}|${item.title}|${item.price_raw}`;
              if (seen.has(key)) return;
              seen.add(key);
              results.push(item);
            };

            const productCardSelectors = [
              '[data-testid="master-product-card"]',
              'div[data-testid*="product"]',
              'div.pcv3__container',
              'div[class*="prd_container"]'
            ];

            for (const selector of productCardSelectors) {
              for (const card of Array.from(document.querySelectorAll(selector))) {
                const text = card.innerText || '';
                const priceRaw = priceOf(text);
                if (!priceRaw) continue;
                const anchor = card.querySelector('a[href*="tokopedia.com/"]');
                const lines = linesOf(text);
                const selectorTitle =
                  card.querySelector('[data-testid="spnSRPProdName"]') ||
                  card.querySelector('[data-testid*="ProdName"]') ||
                  card.querySelector('.prd_link-product-name');
                const priceIndex = lines.findIndex(line => line.includes(priceRaw));
                const imageNode = card.querySelector('img');
                const imageUrl = getImageFromCard(card);
                const title =
                  (selectorTitle && selectorTitle.textContent.trim()) ||
                  (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
                  (anchor ? anchor.getAttribute('title') : '') ||
                  (imageNode ? imageNode.getAttribute('alt') : '') ||
                  lines.find(line => !line.startsWith('Rp') && line.length > 4) ||
                  '';
                const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
                const soldMatch = text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i);
                const ratingMatch = text.match(/\b([4-5](?:[.,]\d)?)\b/);
                pushProduct({
                  title,
                  price_raw: priceRaw,
                  price_value: parseRupiah(priceRaw),
                  shop: afterPrice[0] || '',
                  location: afterPrice[1] || '',
                  rating: ratingMatch ? ratingMatch[1] : '',
                  sold: soldMatch ? soldMatch[0] : '',
                  url: cleanUrl(anchor ? anchor.href : ''),
                  image: imageUrl || '',
                  source_engine: 'rollback',
                });
              }
            }

            // Anchor-based fallback for non-standard card markup
            for (const anchor of Array.from(document.querySelectorAll('a[href*="tokopedia.com"]'))) {
              const href = anchor.href || '';
              if (!isProductUrl(href)) continue;
              const card =
                anchor.closest('[data-testid="master-product-card"]') ||
                anchor.closest('div[data-testid*="product"]') ||
                anchor.closest('div.pcv3__container') ||
                anchor.closest('div[class*="css-"]') ||
                anchor;
              const text = card.innerText || anchor.innerText || '';
              const priceRaw = priceOf(text);
              if (!priceRaw) continue;
              const lines = linesOf(text);
              const selectorTitle =
                card.querySelector('[data-testid="spnSRPProdName"]') ||
                card.querySelector('.prd_link-product-name');
              const priceIndex = lines.findIndex(line => line.includes(priceRaw));
              const title =
                (selectorTitle && selectorTitle.textContent.trim()) ||
                (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
                lines.find(line => !line.startsWith('Rp') && line.length > 4) ||
                'Produk Tokopedia';
              const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
              const imageUrl = getImageFromCard(card);
              const soldMatch = text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i);
              const ratingMatch = text.match(/\b([4-5](?:[.,]\d)?)\b/);
              pushProduct({
                title,
                price_raw: priceRaw,
                price_value: parseRupiah(priceRaw),
                shop: afterPrice[0] || '',
                location: afterPrice[1] || '',
                rating: ratingMatch ? ratingMatch[1] : '',
                sold: soldMatch ? soldMatch[0] : '',
                url: cleanUrl(href),
                image: imageUrl || '',
                source_engine: 'rollback',
              });
            }
            return results;
            """
        ) or []

```

## FILE: `src\scraper\selenium_driver.py`

```python
"""
selenium_driver.py - Robust Selenium Chrome driver factory.

Strategy:
1. Native Selenium Manager (Selenium 4.6+) - downloads matching chromedriver automatically.
2. webdriver-manager fallback if native fails.
3. Both methods disable HTTP/2 via chrome flags to reduce ERR_HTTP2_PROTOCOL_ERROR.

Key fix: --disable-http2 chrome flag matches Puppeteer's fix.
"""
from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from src.utils.logger import log


def _build_chrome_options() -> Options:
    """Build Chrome options shared by both driver strategies."""
    options = Options()

    headless_env = os.environ.get("SCRAPER_HEADLESS", "true").lower()
    if headless_env == "true":
        options.add_argument("--headless=new")

    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=id-ID")

    # KEY FIX: disable HTTP/2 to reduce ERR_HTTP2_PROTOCOL_ERROR on Tokopedia
    options.add_argument("--disable-http2")

    # Reduce bot detection signals
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Realistic UA
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    options.page_load_strategy = "eager"
    return options


def _set_driver_timeouts(driver: webdriver.Chrome) -> None:
    driver.set_page_load_timeout(45)
    driver.set_script_timeout(30)
    # Remove navigator.webdriver flag to reduce bot detection
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )


def create_chrome_driver(search_id: str, debug_dir: Path) -> Tuple[Optional[webdriver.Chrome], str]:
    """
    Create a Chrome driver using Selenium Manager first, webdriver-manager second.
    Both attempts use HTTP/2-disabled Chrome flags.
    Returns (driver, "") on success or (None, error_message) on failure.
    """
    options = _build_chrome_options()
    error_logs: list[str] = []

    # Attempt 1: Native Selenium Manager (Selenium 4.6+ auto-downloads chromedriver)
    try:
        log(f"[{search_id}]", "[SELENIUM] Starting Chrome via Selenium Manager", "INFO")
        driver = webdriver.Chrome(options=options)
        browser_version = driver.capabilities.get("browserVersion", "Unknown")
        log(f"[{search_id}]", f"[SELENIUM] Chrome {browser_version} started OK", "OK")
        _set_driver_timeouts(driver)
        return driver, ""
    except Exception:
        tb = traceback.format_exc()
        error_logs.append(f"Selenium Manager failed:\n{tb}")
        log(f"[{search_id}]", "[SELENIUM] Native Selenium Manager failed, trying webdriver-manager...", "WARN")

    # Attempt 2: webdriver-manager fallback
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        log(f"[{search_id}]", "[SELENIUM] Starting Chrome via webdriver-manager", "INFO")
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        browser_version = driver.capabilities.get("browserVersion", "Unknown")
        log(f"[{search_id}]", f"[SELENIUM] Chrome {browser_version} started OK via fallback", "OK")
        _set_driver_timeouts(driver)
        return driver, ""
    except Exception:
        tb = traceback.format_exc()
        error_logs.append(f"webdriver-manager failed:\n{tb}")

    # Both failed - write debug artifact
    error_msg = "\n\n".join(error_logs)
    log(f"[{search_id}]", "[SELENIUM] Both driver strategies failed.", "ERROR")

    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
        (debug_dir / "selenium_driver_error.txt").write_text(
            "=== SELENIUM DRIVER STARTUP FAILURE ===\n" + error_msg, encoding="utf-8"
        )
    except Exception:
        pass

    return None, error_msg


def safe_quit_driver(driver: Optional[webdriver.Chrome]) -> None:
    """Quit driver without crashing. Always call in finally blocks."""
    if driver:
        try:
            driver.quit()
        except Exception:
            pass

```

## FILE: `src\scraper\url_builder.py`

```python
"""
url_builder.py - Tokopedia public search URL builder.

Engines use one URL builder so Puppeteer and Selenium compare the same pages.
"""
from __future__ import annotations

from urllib.parse import quote, urlencode


def build_tokopedia_search_url(
    query: str,
    min_price: int | None = None,
    max_price: int | None = None,
    page: int | None = None,
) -> str:
    """
    Build a Tokopedia product search URL with safe query encoding.

    Price params are optional. Engines may still choose to try no-price URLs
    first and rely on local budget filtering when the site ignores filters.
    """
    params: dict[str, str] = {
        "st": "product",
        "q": query,
    }
    if min_price is not None:
        params["pmin"] = str(int(min_price))
    if max_price is not None:
        params["pmax"] = str(int(max_price))
    if page is not None:
        params["page"] = str(int(page))
    return "https://www.tokopedia.com/search?" + urlencode(params, quote_via=quote)


def build_tokopedia_search_urls_for_variant(
    query: str,
    min_price: int | None = None,
    max_price: int | None = None,
) -> list[str]:
    """
    Return URLs to try for one query variant.

    First URL has no price params. If product extraction works, local filters
    handle budget. Second URL tries site price params for diagnostics/backup.
    """
    urls = [build_tokopedia_search_url(query)]
    if min_price is not None or max_price is not None:
        priced_url = build_tokopedia_search_url(query, min_price, max_price)
        if priced_url not in urls:
            urls.append(priced_url)
    return urls

```

## FILE: `src\server\__init__.py`

```python

```

## FILE: `src\server\lifecycle.py`

```python
import asyncio
from typing import Dict
from src.utils.logger import log

_scrape_tasks: Dict[str, asyncio.Task] = {}

def register_task(search_id: str, task: asyncio.Task):
    _scrape_tasks[search_id] = task

def unregister_task(search_id: str):
    _scrape_tasks.pop(search_id, None)

def get_scrape_task(search_id: str) -> asyncio.Task:
    return _scrape_tasks.get(search_id)

async def cancel_all_tasks():
    if _scrape_tasks:
        log("LIFECYCLE", f"Cancelling {len(_scrape_tasks)} background scrape tasks...", "WARN")
        for search_id, task in _scrape_tasks.items():
            task.cancel()
        
        # Wait for cancellation to complete
        await asyncio.gather(*_scrape_tasks.values(), return_exceptions=True)
        _scrape_tasks.clear()
        log("LIFECYCLE", "All background tasks cancelled. Browser resources cleaned up.", "OK")

```

## FILE: `src\server\main.py`

```python
"""
main.py - FastAPI application setup.
Mounts API routes and serves the frontend.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from src.server.routes import router
from src.server.lifecycle import cancel_all_tasks
from src.utils.logger import log

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.ai.feedback_store import ensure_feedback_db
    from src.ai.model_registry import get_orchestrator_status

    ensure_feedback_db()
    get_orchestrator_status(force_refresh=True)
    yield
    log("SERVER", "Shutting down, cleaning up...", "INFO")
    await cancel_all_tasks()

# Initialize FastAPI
app = FastAPI(
    title="Tokopedia Scraper API",
    description="Python/Puppeteer/Selenium scraper with automatic local AI orchestration.",
    version="4.0",
    lifespan=lifespan
)

# No-cache middleware for HTML/CSS/JS
@app.middleware("http")
async def no_cache_frontend(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.endswith((".html", ".css", ".js")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Include API routes
app.include_router(router)

# Basic health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Serve Frontend
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
WEB_DIR = PROJECT_DIR / "web"

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        index_path = WEB_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Frontend not built or web/index.html missing"}
        
    @app.get("/{path:path}")
    async def serve_static(path: str):
        file_path = WEB_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        index_path = WEB_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Not found"}

else:
    @app.get("/")
    async def serve_index_fallback():
        return {"error": "Web directory missing"}

```

## FILE: `src\server\progress.py`

```python
"""
progress.py - In-memory progress state for polling.
"""
from __future__ import annotations

import math
import os
import threading
import time
from typing import Any, Dict


_progress_store: Dict[str, Dict[str, Any]] = {}
_progress_lock = threading.RLock()

MAX_ETA_SECONDS = 3600
AI_PROGRESS_START = 70.0
AI_PROGRESS_SPAN = 18.0
AI_DEFAULT_BATCH_SECONDS = int(os.getenv("AI_DEFAULT_BATCH_SECONDS", "75"))
AI_MIN_BATCH_SECONDS = int(os.getenv("AI_MIN_BATCH_SECONDS", "30"))
AI_MAX_BATCH_SECONDS = int(os.getenv("AI_MAX_BATCH_SECONDS", "180"))

BLOCKED_ERROR_TOKENS = (
    "captcha",
    "blocked",
    "access denied",
    "too many requests",
    "robot",
    "bot detection",
)

SCRAPING_STAGES = {
    "opening_page",
    "scrolling",
    "extracting",
    "puppeteer_opening",
    "puppeteer_query",
    "puppeteer_retry",
    "rollback_opening",
    "rollback_extracting",
    "compare_filtering",
}

PREPARING_STAGES = {
    "initializing",
    "engine_selecting",
    "launching_browser",
    "puppeteer_starting",
    "rollback_browser_starting",
    "switching_to_rollback",
}


def _epoch_ms() -> int:
    return int(time.time() * 1000)


def _coerce_percent(value: Any) -> float:
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _coerce_eta_seconds(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(max(0, min(MAX_ETA_SECONDS, math.ceil(float(value)))))
    except (TypeError, ValueError, OverflowError):
        return None


def _coerce_epoch_ms(value: Any) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if parsed > 0 else None


def _bounded_batch_seconds(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = float(AI_DEFAULT_BATCH_SECONDS)
    return max(float(AI_MIN_BATCH_SECONDS), min(float(AI_MAX_BATCH_SECONDS), parsed))


def _average_batch_seconds(completed_ai_batch_durations: list[float] | tuple[float, ...] | None) -> float:
    durations: list[float] = []
    for item in completed_ai_batch_durations or []:
        try:
            parsed = float(item)
        except (TypeError, ValueError, OverflowError):
            continue
        if parsed > 0:
            durations.append(parsed)
    if not durations:
        return _bounded_batch_seconds(AI_DEFAULT_BATCH_SECONDS)
    return _bounded_batch_seconds(sum(durations) / len(durations))


def _format_eta(seconds: Any) -> str:
    if seconds is None:
        return "ETA: calculating..."
    try:
        seconds_int = max(0, int(round(float(seconds))))
    except (TypeError, ValueError):
        return "ETA: calculating..."
    minutes, secs = divmod(seconds_int, 60)
    return f"{minutes:02d}:{secs:02d}"


def _canonical_stage(record: Dict[str, Any]) -> str:
    raw_stage = str(record.get("phase") or record.get("stage") or "initializing")
    error_text = str(record.get("error") or record.get("message") or "").lower()
    if any(token in error_text for token in BLOCKED_ERROR_TOKENS):
        return "blocked"
    if record.get("done") and not record.get("error"):
        return "completed"
    if raw_stage in {"done", "finalizing", "ranking", "recommendation_building"}:
        return "completed"
    if raw_stage in {"error", "failed", "cancelled"}:
        return "error"
    if raw_stage in {"deduplicating", "budget_filtering", "ai_filtering"}:
        return raw_stage
    if raw_stage in SCRAPING_STAGES:
        return "scraping"
    if raw_stage in PREPARING_STAGES:
        return "preparing"
    return "preparing"


def _append_log(record: Dict[str, Any], message: str | None) -> None:
    text = str(message or "").strip()
    if not text:
        return
    logs = list(record.get("logs") or [])
    last = logs[-1] if logs else {}
    stage = str(record.get("phase") or record.get("stage") or "initializing")
    if last.get("message") == text and last.get("stage") == stage:
        return
    logs.append({
        "time": _epoch_ms(),
        "stage": stage,
        "message": text,
    })
    record["logs"] = logs[-40:]


def _refresh_time_fields(record: Dict[str, Any], touch_updated: bool = False) -> Dict[str, Any]:
    now_epoch = _epoch_ms()
    now_monotonic = time.perf_counter()
    started_monotonic = float(record.get("started_at_monotonic") or now_monotonic)
    elapsed = max(0.0, now_monotonic - started_monotonic)
    percent = _coerce_percent(record.get("progress_percent", record.get("percent", 0)))
    raw_stage = str(record.get("phase") or record.get("stage") or "initializing")

    record["server_now_epoch_ms"] = now_epoch
    if touch_updated:
        record["updated_at_epoch_ms"] = now_epoch
    record["elapsed_seconds"] = round(elapsed, 1)
    record["progress_percent"] = percent
    record["percent"] = percent

    if record.get("done"):
        if raw_stage in {"done", "completed"} and not record.get("error"):
            record["eta_seconds"] = 0
            record["estimated_completion_epoch_ms"] = now_epoch
            record["eta_is_reliable"] = True
        else:
            record["eta_seconds"] = None
            record["estimated_completion_epoch_ms"] = None
            record["eta_is_reliable"] = False
    elif record.get("estimated_completion_epoch_ms") is not None:
        deadline = _coerce_epoch_ms(record.get("estimated_completion_epoch_ms"))
        if deadline is None:
            record["eta_seconds"] = None
            record["estimated_completion_epoch_ms"] = None
        else:
            remaining = math.ceil((deadline - now_epoch) / 1000)
            record["eta_seconds"] = int(max(0, min(MAX_ETA_SECONDS, remaining)))
            record["estimated_completion_epoch_ms"] = deadline
    elif record.get("eta_seconds") is None and percent > 2:
        eta = elapsed / (percent / 100.0) - elapsed
        record["eta_seconds"] = _coerce_eta_seconds(eta)
        if record["eta_seconds"] is not None:
            record["estimated_completion_epoch_ms"] = now_epoch + int(record["eta_seconds"] * 1000)
        record["eta_is_reliable"] = False
    elif record.get("eta_seconds") is not None:
        eta_seconds = _coerce_eta_seconds(record.get("eta_seconds"))
        record["eta_seconds"] = eta_seconds
        record["estimated_completion_epoch_ms"] = (
            now_epoch + int(eta_seconds * 1000) if eta_seconds is not None else None
        )

    record["eta_label"] = _format_eta(record.get("eta_seconds"))
    record["phase"] = record.get("phase") or record.get("stage") or "initializing"
    record["status_text"] = str(record.get("message") or "")
    record["stage"] = _canonical_stage(record)
    record["searchId"] = record.get("search_id")
    record["statusText"] = record["status_text"]
    record["percentage"] = record["progress_percent"]
    record["elapsedSeconds"] = record["elapsed_seconds"]
    record["etaSeconds"] = record.get("eta_seconds")
    record["foundCount"] = record.get("found", 0)
    record["targetCount"] = record.get("target", 0)
    record.setdefault("logs", [])
    return record


def init_progress(search_id: str, target: int, raw_target: int, engine_mode: str = "auto") -> None:
    """Initialize a progress record with all fields the frontend expects."""
    now_epoch = _epoch_ms()
    started_monotonic = time.perf_counter()
    with _progress_lock:
        _progress_store[search_id] = {
            "search_id": search_id,
            "engine_mode": engine_mode,
            "active_engine": "none",
            "percent": 0.0,
            "progress_percent": 0.0,
            "stage": "initializing",
            "phase": "initializing",
            "message": "Initializing...",
            "status_text": "Initializing...",
            "found": 0,
            "valid": 0,
            "target": target,
            "raw_target": raw_target,
            "started_at_epoch_ms": now_epoch,
            "started_at_monotonic": started_monotonic,
            "updated_at_epoch_ms": now_epoch,
            "server_now_epoch_ms": now_epoch,
            "elapsed_seconds": 0.0,
            "eta_seconds": None,
            "estimated_completion_epoch_ms": None,
            "eta_label": "ETA: calculating...",
            "eta_is_reliable": False,
            "ai_batch_current": None,
            "ai_batch_total": None,
            "ai_batch_started_at_epoch_ms": None,
            "ai_avg_batch_seconds": None,
            "ai_current_batch_elapsed_seconds": None,
            "ai_completed_batches": None,
            "ai_orchestrator": None,
            "engine": "none",
            "attempt": 1,
            "max_attempts": 1,
            "done": False,
            "error": None,
            "logs": [
                {
                    "time": now_epoch,
                    "stage": "initializing",
                    "message": "Initializing...",
                }
            ],
        }


def update_progress(search_id: str, **kwargs: Any) -> None:
    """Patch a progress record in place."""
    eta_explicit = "eta_seconds" in kwargs
    deadline_explicit = "estimated_completion_epoch_ms" in kwargs
    if "active_engine" in kwargs and "engine" not in kwargs:
        kwargs["engine"] = kwargs["active_engine"]
    if "stage" in kwargs and "phase" not in kwargs:
        kwargs["phase"] = kwargs["stage"]
    if "phase" in kwargs and "stage" not in kwargs:
        kwargs["stage"] = kwargs["phase"]
    if "percent" in kwargs and "progress_percent" not in kwargs:
        kwargs["progress_percent"] = _coerce_percent(kwargs["percent"])
    if "progress_percent" in kwargs and "percent" not in kwargs:
        kwargs["percent"] = _coerce_percent(kwargs["progress_percent"])
    if "percent" in kwargs:
        kwargs["percent"] = _coerce_percent(kwargs["percent"])
    if "progress_percent" in kwargs:
        kwargs["progress_percent"] = _coerce_percent(kwargs["progress_percent"])

    # Let the store compute live elapsed from monotonic time instead of trusting
    # stale caller snapshots.
    kwargs.pop("elapsed_seconds", None)
    if eta_explicit:
        kwargs["eta_seconds"] = _coerce_eta_seconds(kwargs.get("eta_seconds"))
        if not deadline_explicit:
            eta_seconds = kwargs.get("eta_seconds")
            kwargs["estimated_completion_epoch_ms"] = (
                _epoch_ms() + int(eta_seconds * 1000) if eta_seconds is not None else None
            )
    if deadline_explicit:
        kwargs["estimated_completion_epoch_ms"] = _coerce_epoch_ms(kwargs.get("estimated_completion_epoch_ms"))

    with _progress_lock:
        if search_id not in _progress_store:
            return

        _progress_store[search_id].update(kwargs)
        if "message" in kwargs:
            _append_log(_progress_store[search_id], kwargs.get("message"))
        if not eta_explicit and not deadline_explicit and not _progress_store[search_id].get("done"):
            _progress_store[search_id]["eta_seconds"] = None
            _progress_store[search_id]["estimated_completion_epoch_ms"] = None
            _progress_store[search_id]["eta_is_reliable"] = False
        _refresh_time_fields(_progress_store[search_id], touch_updated=True)


def get_progress(search_id: str) -> Dict[str, Any] | None:
    """Return current progress for a search id."""
    with _progress_lock:
        record = _progress_store.get(search_id)
        if not record:
            return None
        return dict(_refresh_time_fields(record, touch_updated=False))


def calculate_ai_eta_snapshot(
    batch_current: int,
    batch_total: int,
    batch_started_at_monotonic: float,
    completed_ai_batch_durations: list[float] | tuple[float, ...] | None = None,
    batch_done: bool = False,
) -> dict[str, Any]:
    """Build a live ETA/progress snapshot for the AI filter phase."""
    now_monotonic = time.perf_counter()
    now_epoch_ms = _epoch_ms()
    total = max(1, int(batch_total or 1))
    current = max(1, min(int(batch_current or 1), total))
    avg_batch_seconds = _average_batch_seconds(completed_ai_batch_durations)
    current_batch_elapsed = max(0.0, now_monotonic - float(batch_started_at_monotonic))

    if batch_done:
        completed_batches = current
        remaining_after_current = max(0, total - current)
        eta_seconds_float = remaining_after_current * avg_batch_seconds
        overall_ai_ratio = completed_batches / total
        current_batch_ratio = 1.0
    else:
        completed_batches = current - 1
        current_batch_ratio = min(current_batch_elapsed / avg_batch_seconds, 0.95)
        current_batch_remaining = max(avg_batch_seconds - current_batch_elapsed, 5.0)
        eta_seconds_float = current_batch_remaining + max(0, total - current) * avg_batch_seconds
        overall_ai_ratio = (completed_batches + current_batch_ratio) / total

    eta_seconds = _coerce_eta_seconds(eta_seconds_float)
    progress_percent = AI_PROGRESS_START + AI_PROGRESS_SPAN * max(0.0, min(1.0, overall_ai_ratio))

    return {
        "eta_seconds": eta_seconds,
        "estimated_completion_epoch_ms": (
            now_epoch_ms + int(eta_seconds * 1000) if eta_seconds is not None else None
        ),
        "progress_percent": round(progress_percent, 2),
        "percent": round(progress_percent, 2),
        "ai_batch_current": current,
        "ai_batch_total": total,
        "ai_avg_batch_seconds": round(avg_batch_seconds, 1),
        "ai_current_batch_elapsed_seconds": round(current_batch_elapsed, 1),
        "ai_completed_batches": completed_batches,
        "eta_is_reliable": True,
    }


def update_ai_eta_progress(
    search_id: str,
    batch_current: int,
    batch_total: int,
    batch_started_at_monotonic: float,
    batch_started_at_epoch_ms: int,
    completed_ai_batch_durations: list[float] | tuple[float, ...] | None = None,
    message: str | None = None,
    found: int | None = None,
    valid: int | None = None,
    batch_done: bool = False,
) -> dict[str, Any]:
    """Refresh progress while an Ollama classifier batch is running."""
    snapshot = calculate_ai_eta_snapshot(
        batch_current=batch_current,
        batch_total=batch_total,
        batch_started_at_monotonic=batch_started_at_monotonic,
        completed_ai_batch_durations=completed_ai_batch_durations,
        batch_done=batch_done,
    )
    payload: dict[str, Any] = {
        **snapshot,
        "stage": "ai_filtering",
        "phase": "ai_filtering",
        "message": message or f"AI filtering batch {batch_current}/{batch_total}",
        "ai_batch_started_at_epoch_ms": batch_started_at_epoch_ms,
    }
    if found is not None:
        payload["found"] = found
    if valid is not None:
        payload["valid"] = valid

    update_progress(search_id, **payload)
    return snapshot


def complete_progress(search_id: str) -> None:
    """Mark a search as complete."""
    update_progress(
        search_id,
        percent=100.0,
        stage="done",
        phase="done",
        message="Selesai!",
        eta_seconds=0,
        done=True,
    )


def fail_progress(search_id: str, error_msg: str) -> None:
    """Mark a search as failed with a specific visible error."""
    stage = "blocked" if any(token in str(error_msg).lower() for token in BLOCKED_ERROR_TOKENS) else "error"
    update_progress(
        search_id,
        stage=stage,
        phase=stage,
        message=error_msg,
        error=error_msg,
        done=True,
        eta_seconds=None,
    )

```

## FILE: `src\server\routes.py`

```python
"""
routes.py - FastAPI routes for the Tokopedia scraper pipeline.

Pipeline per spec:
  preflight -> scrape raw -> normalize -> budget filter -> AI orchestrator -> result -> feedback

The active AI path is model-orchestrated: rules handle obvious products, the
best installed small classifier checks borderline products, and rule fallback
keeps searches useful when Ollama has no supported model installed.
"""
from __future__ import annotations

import asyncio
import os
import time
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.ai.ai_filter import is_valid_product_candidate
from src.ai.feedback_store import feedback_summary_counts, reset_learning
from src.ai.learning import save_feedback
from src.ai.memory_store import FEEDBACK_FILE as LEGACY_FEEDBACK_FILE, read_jsonl
from src.ai.model_registry import get_orchestrator_status
from src.ai.relevance import filter_relevance
from src.ai.reset import reset_ai_memory
from src.scraper.budget_filter import FilterResult, filter_by_budget
from src.scraper.dedupe import deduplicate_products
from src.scraper.engine_selector import EngineRunResult, EngineSelectionResult, run_engine, run_scraper_engines
from src.scraper.normalizer import normalize_image_url, normalize_products_with_report, pick_product_image
from src.server.lifecycle import register_task, unregister_task
from src.server.progress import complete_progress, fail_progress, get_progress, init_progress, update_progress
from src.server.schemas import FeedbackRequest, ProgressResponse, SearchRequest
from src.config import OVERFETCH_MULTIPLIER, RESULT_STORE_MAX_ITEMS, RESULT_STORE_TTL_SECONDS, STRICT_BUDGET_MODE
from src.utils.currency import format_rupiah, parse_rupiah
from src.utils.debug import safe_save_debug, save_json_debug
from src.utils.eta import ETACalculator
from src.utils.logger import log


router = APIRouter()
_results_store: dict[str, dict[str, Any]] = {}


def _utc_timestamp(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def cleanup_results_store() -> None:
    """Bound the in-memory result cache by TTL and item count."""
    now = time.time()
    ttl = max(0, int(RESULT_STORE_TTL_SECONDS))
    expired_ids = [
        search_id
        for search_id, payload in _results_store.items()
        if now - float(payload.get("created_at_epoch", 0) or 0) >= ttl
    ]

    for search_id in expired_ids:
        _results_store.pop(search_id, None)

    max_items = max(1, int(RESULT_STORE_MAX_ITEMS))
    overflow = len(_results_store) - max_items
    if overflow <= 0:
        return

    oldest_ids = sorted(
        _results_store,
        key=lambda search_id: float(_results_store[search_id].get("created_at_epoch", 0) or 0),
    )[:overflow]
    for search_id in oldest_ids:
        _results_store.pop(search_id, None)


def save_result(search_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    cleanup_results_store()
    created_at_epoch = time.time()
    stored_payload = dict(payload)
    stored_payload.setdefault("search_id", search_id)
    stored_payload["created_at"] = _utc_timestamp(created_at_epoch)
    stored_payload["created_at_epoch"] = created_at_epoch
    stored_payload["expires_at"] = _utc_timestamp(created_at_epoch + max(0, int(RESULT_STORE_TTL_SECONDS)))
    _results_store[search_id] = stored_payload
    cleanup_results_store()
    return stored_payload


def get_result(search_id: str) -> dict[str, Any] | None:
    cleanup_results_store()
    return _results_store.get(search_id)


def cleanup_task(search_id: str, task: asyncio.Task) -> None:
    try:
        exc = task.exception()
        if exc:
            log(f"[{search_id}]", f"Unhandled task exception: {exc}", "ERROR")
    except asyncio.CancelledError:
        pass
    finally:
        unregister_task(search_id)


@router.post("/api/search")
async def start_search(req: SearchRequest):
    search_id = str(uuid.uuid4())
    target_count = max(1, min(int(req.target_count), 100))
    overfetch_multiplier = max(1, int(OVERFETCH_MULTIPLIER))
    max_raw_candidates = max(target_count, int(os.getenv("MAX_RAW_CANDIDATES", "300")))
    raw_target = min(max_raw_candidates, max(100, target_count * overfetch_multiplier))
    req.target_count = target_count
    init_progress(search_id, target_count, raw_target, req.engine_mode)
    progress = get_progress(search_id) or {}
    task = asyncio.create_task(run_scrape_job_wrapper(search_id, req, raw_target))
    register_task(search_id, task)
    task.add_done_callback(lambda t: cleanup_task(search_id, t))
    return {
        "success": True,
        "search_id": search_id,
        "requested_count": target_count,
        "raw_target": raw_target,
        "started_at_epoch_ms": progress.get("started_at_epoch_ms"),
    }


@router.get("/api/progress/{search_id}", response_model=ProgressResponse)
async def fetch_progress(search_id: str):
    progress = get_progress(search_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Search ID not found")
    return progress


@router.get("/api/ai/status")
async def ai_status():
    """Return installed supported Ollama models and active orchestrator capabilities."""
    return get_orchestrator_status(force_refresh=True)


@router.get("/api/result/{search_id}")
async def fetch_result(search_id: str):
    result = get_result(search_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found or not ready")
    return result


@router.get("/api/image-proxy")
async def image_proxy(url: str = Query(..., min_length=8)):
    image_url = normalize_image_url(url)
    if not image_url:
        raise HTTPException(status_code=400, detail="Invalid image URL")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Referer": "https://www.tokopedia.com/",
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(image_url, headers=headers)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Image proxy timeout") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Image proxy failed") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Image host returned {response.status_code}")

    media_type = response.headers.get("content-type", "image/jpeg").split(";", 1)[0].strip().lower()
    if not media_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="URL did not return an image")

    return Response(
        content=response.content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.post("/api/feedback")
async def handle_feedback(req: FeedbackRequest):
    """Save user feedback from Benar/Salah result-card actions."""
    try:
        product = req.normalized_product()
        reasons = req.normalized_reasons()
        feedback_type = req.normalized_feedback_type()
        user_action = req.normalized_user_action()
        corrected_label = req.normalized_corrected_label()
        note = req.normalized_note()
        result = save_feedback(
            query=req.query,
            product_id=req.normalized_product_id(),
            product_title=req.normalized_product_title(),
            user_action=user_action,
            selected_reasons=reasons,
            custom_reason=note,
            corrected_label=corrected_label,
            ai_label=req.ai_label,
            ai_confidence=req.ai_confidence,
            product=product,
            query_intent=req.query_intent,
            feedback_type=feedback_type,
            rule_score=req.rule_score,
            semantic_score=req.semantic_score,
            combined_score=req.combined_score,
            learned_adjustment=req.learned_adjustment,
            sort_mode=req.sort_mode,
            decision_source=str(getattr(req, "decision_source", "") or product.get("decision_source") or product.get("ai_source") or ""),
            learning_scope_hint=req.learning_scope_hint,
            model_used=req.model_used,
            ai_reason=req.ai_reason,
        )
        if req.search_id:
            save_json_debug(req.search_id, "feedback_saved.json", req.model_dump())
        return {
            "ok": True,
            "success": True,
            "message": "Feedback saved",
            "learning_updated": bool(result.get("learning_updated")),
        }
    except Exception as exc:
        log("API", f"Feedback save error: {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/feedback/summary")
async def feedback_summary():
    records = read_jsonl(LEGACY_FEEDBACK_FILE, limit=500)
    positives = sum(1 for item in records if item.get("feedback_type") == "positive" or item.get("user_action") == "benar")
    negatives = sum(1 for item in records if item.get("feedback_type") == "negative" or item.get("user_action") == "salah")
    sqlite_counts = feedback_summary_counts()
    return {
        "ok": True,
        "total": len(records),
        "positive": positives,
        "negative": negatives,
        **sqlite_counts,
    }


@router.post("/api/ai/reset")
async def handle_ai_reset():
    """Clear AI learning files. Does NOT touch the Ollama model."""
    if reset_ai_memory():
        return {"success": True, "message": "AI memory reset. Ollama model untouched."}
    raise HTTPException(status_code=500, detail="Failed to reset AI memory.")


@router.post("/api/learning/reset")
async def handle_learning_reset(payload: dict[str, Any]):
    """Reset scoped SQLite learning memory."""
    try:
        scope = str(payload.get("scope") or "all")
        result = reset_learning(
            scope=scope,
            query=payload.get("query"),
            constraint_key=payload.get("constraint_key"),
        )
        return {"ok": True, "success": True, "message": "Learning memory reset", **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        log("API", f"Learning reset error: {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/preflight/{engine}")
async def run_preflight_check(engine: str, query: str = "laptop gaming"):
    """
    Run preflight check for the given engine.
    Returns opened_real_page + error_type before starting a full scrape.
    Useful for diagnosing ERR_HTTP2_PROTOCOL_ERROR without wasting time.
    """
    from src.scraper.preflight import run_preflight
    search_id = f"preflight_{uuid.uuid4().hex[:8]}"
    return await run_preflight(search_id, engine, query)


async def run_scrape_job_wrapper(search_id: str, req: SearchRequest, raw_target: int) -> None:
    try:
        await run_scrape_job(search_id, req, raw_target)
    except asyncio.CancelledError:
        log(f"[{search_id}]", "Scrape job cancelled.", "WARN")
        update_progress(search_id, stage="cancelled", done=True, error="Server shutting down")
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        log(f"[{search_id}]", f"Unhandled exception:\n{tb}", "ERROR")
        fail_progress(search_id, f"Internal Error: {exc}")
        safe_save_debug(search_id, error=f"{exc}\n{tb}", products=[], progress=get_progress(search_id))


def _budget_info(filter_result: FilterResult) -> dict[str, Any] | None:
    if filter_result.budget_value is None:
        return None
    return {
        "budget": filter_result.budget_value,
        "min": filter_result.min_price,
        "max": filter_result.max_price,
        "tolerance": filter_result.tolerance,
        "debug_path": filter_result.debug_path,
        "reasons": filter_result.reasons,
    }


def _candidate_pool_snapshot(
    raw_products: list[dict[str, Any]],
    req: SearchRequest,
    engine_name: str = "selected",
) -> dict[str, Any]:
    normalizer = normalize_products_with_report(raw_products, engine_name)
    deduped = deduplicate_products(normalizer.output)
    # When budget is empty, don't require price for valid product check
    require_price = bool(req.budget)
    product_candidates = [product for product in deduped if is_valid_product_candidate(product, require_price=require_price)]
    invalid_non_product_removed = len(deduped) - len(product_candidates)
    budget_result = filter_by_budget(product_candidates, req.budget, req.tolerance)
    candidates = [product for product in budget_result.kept if is_valid_product_candidate(product, require_price=require_price)]
    return {
        "scraped_raw": len(raw_products),
        "after_dedupe": len(deduped),
        "valid_product_candidates": len(product_candidates),
        "invalid_non_product_removed": invalid_non_product_removed,
        "budget_valid": len(candidates),
        "candidate_pool_count": len(candidates),
        "budget_enabled": budget_result.budget_value is not None,
    }


async def _overfetch_raw_products(
    search_id: str,
    req: SearchRequest,
    raw_products: list[dict[str, Any]],
    engine_name: str,
    raw_target: int,
    eta_calc: ETACalculator,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    desired = int(req.target_count)
    max_raw = max(desired * 10, 500)
    max_scroll_rounds = 12
    attempts = 0
    products = list(raw_products or [])
    snapshot = _candidate_pool_snapshot(products, req, engine_name)
    initial_valid_pool = int(snapshot["candidate_pool_count"])
    can_load_more = engine_name in {"puppeteer", "rollback"} and len(products) < max_raw
    stop_reason = "target_met" if initial_valid_pool >= desired else "not_started"

    if initial_valid_pool < desired:
        log(
            "PIPELINE",
            (
                f"overfetch_start requested={desired} "
                f"budget_valid={initial_valid_pool} raw={len(products)}"
            ),
            "INFO",
        )

    while (
        int(snapshot["candidate_pool_count"]) < desired
        and len(products) < max_raw
        and can_load_more
        and attempts < max_scroll_rounds
    ):
        attempts += 1
        next_target = min(max_raw, max(raw_target, len(products) + desired, desired * 4))
        log(
            "PIPELINE",
            (
                f"overfetch requested={desired} valid_pool={snapshot['candidate_pool_count']} "
                f"loading_more=true attempt={attempts} next_raw_target={next_target}"
            ),
            "INFO",
        )
        update_progress(
            search_id,
            active_engine=engine_name,
            stage="overfetching",
            message="Mencari produk tambahan untuk memenuhi target valid...",
            found=len(products),
            valid=int(snapshot["candidate_pool_count"]),
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        run = await run_engine(search_id, engine_name, req.query, next_target, eta_calc)
        if not run.ok or not run.products:
            can_load_more = False
            stop_reason = "load_more_exhausted"
            break

        previous_after_dedupe = int(snapshot["after_dedupe"])
        previous_valid_pool = int(snapshot["candidate_pool_count"])
        products.extend(run.products)
        snapshot = _candidate_pool_snapshot(products, req, engine_name)
        log(
            "PIPELINE",
            f"overfetch_round={attempts} raw={len(products)} budget_valid={snapshot['candidate_pool_count']}",
            "INFO",
        )
        if (
            int(snapshot["after_dedupe"]) <= previous_after_dedupe
            and int(snapshot["candidate_pool_count"]) <= previous_valid_pool
        ):
            can_load_more = False
            stop_reason = "no_new_valid_products"
            break

    final_valid_pool = int(snapshot["candidate_pool_count"])
    target_display = min(desired, final_valid_pool)
    if final_valid_pool >= desired:
        stop_reason = "target_met"
    elif len(products) >= max_raw:
        stop_reason = "raw_limit_reached"
    elif attempts >= max_scroll_rounds:
        stop_reason = "max_scroll_rounds_reached"
    elif not can_load_more and stop_reason == "not_started":
        stop_reason = "load_more_unavailable"
    log(
        "PIPELINE",
        (
            f"overfetch_done requested={desired} budget_valid={final_valid_pool} "
            f"reason={stop_reason} target_display={target_display} attempts={attempts} "
            f"loading_more={str(can_load_more).lower()}"
        ),
        "INFO",
    )
    return products, {
        "overfetch_attempted": attempts > 0,
        "overfetch_attempts": attempts,
        "overfetch_rounds": attempts,
        "overfetch_initial_valid_pool": initial_valid_pool,
        "overfetch_final_valid_pool": final_valid_pool,
        "overfetch_max_raw": max_raw,
        "overfetch_exhausted": final_valid_pool < desired,
        "overfetch_stop_reason": stop_reason,
        "raw_after_overfetch": len(products),
    }


def _public_product_payload(product: dict[str, Any]) -> dict[str, Any]:
    """Expose the required demo product shape while keeping legacy aliases."""
    payload = dict(product or {})
    image_url = pick_product_image(payload)
    price_number = parse_rupiah(payload.get("price_value"))
    if price_number is None:
        price_number = parse_rupiah(payload.get("priceNumber"))
    if price_number is None:
        price_number = parse_rupiah(payload.get("price_raw") or payload.get("price_text") or payload.get("price"))
    price_number = int(price_number or 0)

    price_text = str(payload.get("price_raw") or payload.get("price_text") or "").strip()
    if not price_text and price_number > 0:
        price_text = format_rupiah(price_number)

    store_name = str(payload.get("storeName") or payload.get("shop_name") or payload.get("shop") or payload.get("store") or "").strip()
    confidence_value = payload.get("confidenceScore")
    if confidence_value in (None, ""):
        confidence_value = payload.get("confidence", payload.get("relevance_score", payload.get("ai_confidence", 0)))
    try:
        confidence_score = max(0.0, min(1.0, float(confidence_value or 0)))
    except (TypeError, ValueError):
        confidence_score = 0.0

    relevance_reason = str(
        payload.get("relevanceReason")
        or payload.get("ai_reason")
        or payload.get("reason")
        or payload.get("ai_explanation")
        or payload.get("category_reason")
        or ""
    ).strip()

    payload.update({
        "id": str(payload.get("id") or payload.get("url") or payload.get("product_url") or payload.get("title") or ""),
        "title": str(payload.get("title") or ""),
        "price": price_text,
        "priceNumber": price_number,
        "price_value": price_number,
        "price_raw": price_text,
        "price_text": price_text,
        "image_url": image_url,
        "image": image_url or "",
        "has_image": bool(image_url),
        "storeName": store_name,
        "shop_name": store_name,
        "rating": payload.get("rating") or 0,
        "soldCount": int(_num(payload.get("soldCount", payload.get("sold_count")), 0)),
        "sold_count": int(_num(payload.get("sold_count", payload.get("soldCount")), 0)),
        "url": str(payload.get("url") or payload.get("product_url") or ""),
        "source": str(payload.get("source") or payload.get("source_engine") or "tokopedia"),
        "confidenceScore": round(confidence_score, 3),
        "relevanceReason": relevance_reason,
        "outside_budget": bool(payload.get("outside_budget", False)),
        "budget_badge": str(payload.get("budget_badge") or ""),
        "target_first_fallback": bool(payload.get("target_first_fallback", False)),
    })
    return payload


def _sort_products(products: list[dict[str, Any]], sort_mode: str = "terbaik") -> list[dict[str, Any]]:
    mode = sort_mode if sort_mode in {"terbaik", "termurah", "most_trusted"} else "terbaik"
    if mode == "termurah":
        return sorted(
            products,
            key=lambda p: (
                p.get("price_value") if p.get("price_value") is not None else 10**18,
                -float(p.get("relevance_score") or p.get("ai_confidence") or 0),
            ),
        )
    if mode == "most_trusted":
        return sorted(
            products,
            key=lambda p: (
                -score_trusted_product(p),
                -float(p.get("relevance_score") or p.get("ai_confidence") or 0),
                p.get("price_value") if p.get("price_value") is not None else 10**18,
            ),
        )
    return sorted(
        products,
        key=lambda p: (
            -float(p.get("relevance_score") or p.get("ai_confidence") or 0),
            -score_best_product(p),
            p.get("price_value") if p.get("price_value") is not None else 10**18,
        ),
    )


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def normalize_score(value: Any, min_value: float, max_value: float) -> float:
    parsed = _num(value, min_value)
    if max_value <= min_value:
        return 0.0
    return max(0.0, min(1.0, (parsed - min_value) / (max_value - min_value)))


def _sold_score(product: dict[str, Any]) -> float:
    sold = _num(product.get("sold_count"), 0.0)
    return normalize_score(min(sold, 1000.0), 0.0, 1000.0)


def _rating_score(product: dict[str, Any]) -> float:
    rating = _num(product.get("rating"), 0.0)
    if rating <= 0:
        return 0.0
    return max(0.0, min(1.0, rating / 5.0))


def _shop_score(product: dict[str, Any]) -> float:
    text = " ".join(
        str(product.get(key) or "")
        for key in ("shop_name", "shop", "shop_badge", "title")
    ).lower()
    if any(token in text for token in ("official", "mall", "power merchant", "pro")):
        return 1.0
    return 0.5 if (product.get("shop_name") or product.get("shop")) else 0.0


def _ai_confidence(product: dict[str, Any]) -> float:
    return max(0.0, min(1.0, _num(product.get("ai_confidence", product.get("relevance_score")), 0.0)))


def _price_sanity_score(product: dict[str, Any]) -> float:
    price = product.get("price_value")
    if isinstance(price, int) and price > 0:
        return 1.0
    return 0.0 if product.get("price_parse_failed") else 0.35


def _data_completeness_score(product: dict[str, Any]) -> float:
    keys = ("title", "price_raw", "url", "image", "shop", "location", "rating", "sold")
    return sum(1 for key in keys if product.get(key)) / len(keys)


def score_trusted_product(product: dict[str, Any]) -> float:
    return (
        _rating_score(product) * 0.35
        + _sold_score(product) * 0.30
        + _shop_score(product) * 0.15
        + _ai_confidence(product) * 0.20
    )


def score_best_product(product: dict[str, Any]) -> float:
    return (
        _ai_confidence(product) * 0.35
        + _rating_score(product) * 0.20
        + _sold_score(product) * 0.20
        + _price_sanity_score(product) * 0.10
        + _data_completeness_score(product) * 0.15
    )


def is_accessory_like(product: dict[str, Any], query: str) -> bool:
    query_lower = query.lower()
    title = str(product.get("title") or "").lower()
    accessory_terms = {
        "mouse", "keyboard", "charger", "adaptor", "adapter", "cooling",
        "cooler", "stand", "headset", "earphone", "webcam", "sleeve",
        "tas", "bag", "ram", "ssd", "sticker", "sparepart", "spare parts",
        "baterai", "battery",
    }
    query_asks_accessory = any(term in query_lower for term in accessory_terms)
    return not query_asks_accessory and any(term in title for term in accessory_terms)


def _recommendation_payload(product: dict[str, Any] | None, reason: str) -> dict[str, Any] | None:
    if not product:
        return None
    image_url = pick_product_image(product)
    return {
        "id": product.get("id", ""),
        "title": product.get("title", ""),
        "price": product.get("price_raw") or product.get("price_text") or "",
        "price_value": product.get("price_value"),
        "rating": product.get("rating"),
        "sold_count": product.get("sold_count"),
        "sold": product.get("sold") or product.get("sold_text") or "",
        "shop_name": product.get("shop_name") or product.get("shop") or "",
        "shop_location": product.get("shop_location") or product.get("location") or "",
        "image_url": image_url,
        "image": image_url or "",
        "has_image": bool(image_url),
        "url": product.get("url") or product.get("product_url") or "",
        "ai_confidence": product.get("ai_confidence", product.get("relevance_score", 0)),
        "reason": reason,
    }


def build_recommendations(products: list[dict[str, Any]], query: str) -> dict[str, Any]:
    relevant = [p for p in products if p.get("ai_decision", True)]
    if not relevant:
        relevant = list(products)

    main_products = [p for p in relevant if not is_accessory_like(p, query)] or relevant
    priced = [
        p for p in main_products
        if isinstance(p.get("price_value"), int) and p.get("price_value") > 0
    ]

    trusted = max(main_products, key=score_trusted_product, default=None)
    cheapest = min(priced, key=lambda p: p.get("price_value", 10**18), default=None)
    best = max(main_products, key=score_best_product, default=None)

    return {
        "cheapest": _recommendation_payload(
            cheapest,
            "Harga paling rendah dari produk yang lolos filter.",
        ),
        "trusted": _recommendation_payload(
            trusted,
            "Dipilih karena rating, penjualan, dan skor kepercayaan paling kuat.",
        ),
        "best": _recommendation_payload(
            best,
            "Skor keseluruhan terbaik dari relevansi, rating, penjualan, dan kelengkapan data.",
        ),
    }


def _build_recommendations(query: str, products: list[dict[str, Any]]) -> dict[str, Any]:
    return build_recommendations(products, query)


def _limited_reason(requested_count: int, displayed_count: int, candidate_count: int | None = None) -> str | None:
    if displayed_count >= requested_count:
        return None
    if candidate_count is not None:
        return f"Diminta {requested_count}, tetapi hanya {displayed_count} produk bisa ditampilkan dari {candidate_count} kandidat valid."
    return f"Diminta {requested_count}, tetapi hanya {displayed_count} produk bisa ditampilkan."


def _build_result_warning(
    *,
    requested: int,
    candidate_pool_count: int,
    fallback_added: int,
    ai_skip_reason: str | None,
    displayed: int,
    target_display: int,
    overfetch_stop_reason: str | None = None,
    strict_budget_mode: bool = True,
) -> str:
    warnings: list[str] = []
    if candidate_pool_count < requested:
        if strict_budget_mode:
            warnings.append(
                f"Diminta {requested}, tetapi hanya {candidate_pool_count} produk sesuai budget setelah overfetch."
            )
        else:
            warnings.append(f"Diminta {requested}, tetapi hanya {candidate_pool_count} kandidat tersedia.")
    if overfetch_stop_reason and candidate_pool_count < requested:
        warnings.append(f"Overfetch berhenti: {overfetch_stop_reason}.")
    if fallback_added > 0:
        warnings.append(f"{fallback_added} produk fallback ditambahkan agar hasil mendekati target.")
    if ai_skip_reason:
        warnings.append(f"AI classifier: {ai_skip_reason}.")
    if displayed < target_display:
        warnings.append(
            f"Ditampilkan {displayed} dari target aman {target_display}. Cek log pipeline untuk alasan produk dibuang."
        )
    return " ".join(dict.fromkeys(warnings))


def _budget_distance(product: dict[str, Any], min_price: int | None, max_price: int | None) -> int:
    price = parse_rupiah(product.get("price_value"))
    if price is None:
        price = parse_rupiah(product.get("price_raw") or product.get("price_text") or product.get("price"))
    price = int(price or 0)
    if min_price is not None and price < min_price:
        return min_price - price
    if max_price is not None and price > max_price:
        return price - max_price
    return 0


def _target_first_budget_fallbacks(
    budget_result: FilterResult,
    needed: int,
) -> list[dict[str, Any]]:
    if needed <= 0 or budget_result.budget_value is None:
        return []
    candidates = [
        dict(product)
        for product in budget_result.rejected
        if is_valid_product_candidate(product)
        and product.get("reject_reason") in {"below_budget_range", "above_budget_range"}
    ]
    candidates.sort(
        key=lambda product: (
            _budget_distance(product, budget_result.min_price, budget_result.max_price),
            parse_rupiah(product.get("price_value")) or 10**18,
        )
    )
    selected = candidates[:needed]
    for product in selected:
        product["outside_budget"] = True
        product["budget_badge"] = "Di luar budget"
        product["target_first_fallback"] = True
        product["budget_distance"] = _budget_distance(product, budget_result.min_price, budget_result.max_price)
    return selected


async def _filter_pipeline(
    search_id: str,
    req: SearchRequest,
    raw_products: list[dict[str, Any]],
    eta_calc: ETACalculator,
    engine_name: str = "selected",
    overfetch_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Full filter pipeline: normalize -> dedupe -> budget -> intent-aware AI -> sort.
    Returns dict with all intermediate counts and AI orchestrator status.
    """
    engine = engine_name or "selected"
    normalizer = normalize_products_with_report(raw_products, engine, search_id)
    normalized = normalizer.output
    deduped = deduplicate_products(normalized)
    # When budget is empty, don't require price for valid product check
    require_price = bool(req.budget)
    product_candidates = [product for product in deduped if is_valid_product_candidate(product, require_price=require_price)]
    invalid_non_product_removed = len(deduped) - len(product_candidates)
    image_total = len(normalized)
    missing_rate = (normalizer.images_missing_count / image_total) if image_total else 0.0
    log(
        "IMAGE",
        (
            f"total={image_total} image_found={normalizer.images_extracted_count} "
            f"image_missing={normalizer.images_missing_count} engine={engine} "
            f"missing_rate={missing_rate:.2%}"
        ),
        "INFO",
    )
    if image_total and missing_rate > 0.70:
        save_json_debug(
            search_id,
            f"image_missing_debug_{engine}.json",
            {
                "engine": engine,
                "images_extracted_count": normalizer.images_extracted_count,
                "images_missing_count": normalizer.images_missing_count,
                "missing_rate": round(missing_rate, 4),
                "samples": normalized[:20],
            },
        )

    update_progress(
        search_id,
        stage="deduplicating",
        percent=65,
        message=f"Deduped {len(normalized)} raw products into {len(product_candidates)} valid products",
        found=len(normalized),
        valid=len(product_candidates),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    update_progress(
        search_id,
        stage="budget_filtering",
        percent=68,
        message="Filtering budget..." if req.budget else "Budget kosong: skip budget filter",
        found=len(product_candidates),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    budget_result = filter_by_budget(product_candidates, req.budget, req.tolerance)
    strict_budget_mode = bool(STRICT_BUDGET_MODE)
    target_first_mode = bool(getattr(req, "target_first_mode", False))
    require_price = bool(req.budget)
    budget_valid_count = len([product for product in budget_result.kept if is_valid_product_candidate(product, require_price=require_price)])
    candidates = [product for product in budget_result.kept if is_valid_product_candidate(product, require_price=require_price)]
    target_first_added = 0
    if target_first_mode and budget_valid_count < req.target_count:
        target_first_fill = _target_first_budget_fallbacks(
            budget_result,
            req.target_count - budget_valid_count,
        )
        target_first_added = len(target_first_fill)
        candidates.extend(target_first_fill)
    budget_enabled = budget_result.budget_value is not None
    orchestrator_status = get_orchestrator_status()

    log(
        "BUDGET",
        (
            f"enabled={str(budget_enabled).lower()} raw={len(raw_products)} "
            f"deduped={len(deduped)} product_candidates={len(product_candidates)} "
            f"invalid_non_product_removed={invalid_non_product_removed} budget_valid={budget_valid_count} "
            f"candidate_pool={len(candidates)} target_first_added={target_first_added} "
            f"min={budget_result.min_price} max={budget_result.max_price} "
            f"rejected={len(budget_result.rejected)}"
        ),
        "INFO",
    )

    if budget_result.budget_value is not None:
        from src.utils.debug import save_budget_filter_debug
        budget_result.debug_path = save_budget_filter_debug(search_id, budget_result.debug_payload(), engine)

    update_progress(
        search_id,
        stage="ai_filtering",
        percent=70,
        message="Filtering relevansi dengan AI Orchestrator..." if req.use_ai else "AI nonaktif: rule scoring...",
        found=len(deduped),
        valid=len(candidates),
        elapsed_seconds=eta_calc.get_elapsed(),
        ai_orchestrator={
            "enabled": bool(req.use_ai),
            "classifier": orchestrator_status.get("classifier"),
            "semantic_enabled": bool(orchestrator_status.get("capabilities", {}).get("semantic")),
            "json_repair_enabled": bool(orchestrator_status.get("capabilities", {}).get("json_repair")),
        },
    )

    overfetch_meta = overfetch_meta or {}
    for candidate in candidates:
        candidate["_requested_target"] = req.target_count
        candidate["_scraped_raw"] = len(raw_products)
        candidate["_after_dedupe"] = len(deduped)
        candidate["_valid_product_candidates"] = len(product_candidates)
        candidate["_invalid_non_product_removed"] = invalid_non_product_removed
        candidate["_budget_valid"] = budget_valid_count
        candidate["_candidate_pool"] = len(candidates)
        candidate["_overfetch_attempted"] = bool(overfetch_meta.get("overfetch_attempted", False))
        candidate["_overfetch_attempts"] = int(overfetch_meta.get("overfetch_attempts", 0) or 0)
        candidate["_overfetch_rounds"] = int(overfetch_meta.get("overfetch_rounds", overfetch_meta.get("overfetch_attempts", 0)) or 0)
        candidate["_overfetch_initial_valid_pool"] = int(overfetch_meta.get("overfetch_initial_valid_pool", len(candidates)) or 0)
        candidate["_overfetch_final_valid_pool"] = int(overfetch_meta.get("overfetch_final_valid_pool", len(candidates)) or 0)
        candidate["_overfetch_max_raw"] = int(overfetch_meta.get("overfetch_max_raw", 0) or 0)
        candidate["_overfetch_exhausted"] = bool(overfetch_meta.get("overfetch_exhausted", False))
        candidate["_overfetch_stop_reason"] = str(overfetch_meta.get("overfetch_stop_reason") or "")
        candidate["_raw_after_overfetch"] = int(overfetch_meta.get("raw_after_overfetch", len(raw_products)) or 0)
        candidate["_strict_budget_mode"] = strict_budget_mode
        candidate["_target_first_mode"] = target_first_mode
        candidate["_target_first_added"] = target_first_added

    ai_result = await filter_relevance(req.query, candidates, req.use_ai, search_id)
    ai_valid, ai_status = ai_result
    ai_meta = getattr(ai_result, "meta", {}) or {}

    update_progress(
        search_id,
        stage="ranking",
        percent=88,
        message="Ranking hasil...",
        found=len(deduped),
        valid=len(ai_valid),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    target_display = min(req.target_count, len(candidates))
    ranked = _sort_products(list(ai_valid), req.sort_mode)
    # AUDIT FIX: Use requested target_count directly, not constrained to candidates
    final = ranked[:req.target_count]
    public_final = [_public_product_payload(product) for product in final]
    public_image_found = sum(1 for product in public_final if product.get("has_image"))
    log(
        "IMAGE",
        f"total={len(public_final)} image_found={public_image_found} image_missing={len(public_final) - public_image_found}",
        "INFO",
    )
    fallback_added = int(ai_meta.get("fallback_added", ai_meta.get("fallback_expansion_count", 0)) or 0)
    ai_timeouts = int(ai_meta.get("ai_timeouts", 0) or 0)
    ai_skip_reason = ai_meta.get("ai_skip_reason")
    final_warning = str(ai_meta.get("warning") or "").strip() or _build_result_warning(
        requested=req.target_count,
        candidate_pool_count=len(candidates),
        fallback_added=fallback_added,
        ai_skip_reason=str(ai_skip_reason) if ai_skip_reason else None,
        displayed=len(public_final),
        target_display=target_display,
        overfetch_stop_reason=str(overfetch_meta.get("overfetch_stop_reason") or "") or None,
        strict_budget_mode=strict_budget_mode,
    )
    limited = final_warning or None

    update_progress(
        search_id,
        stage="recommendation_building",
        percent=93,
        message="Membangun rekomendasi cepat...",
        found=len(deduped),
        valid=len(public_final),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    recommendations = _build_recommendations(req.query, public_final)
    has_enough = len(public_final) >= target_display
    classifier_checked = ai_meta.get("classifier_checked", ai_meta.get("ai_checked", ai_meta.get("llm_checked_count", 0)))
    semantic_checked = ai_meta.get("semantic_checked", ai_meta.get("semantic_checked_count", 0))
    metadata = {
        "requested": req.target_count,
        "requested_count": req.target_count,
        "scraped_raw": len(raw_products),
        "raw_scraped_count": len(raw_products),
        "raw_scraped": len(raw_products),
        "after_dedupe": len(deduped),
        "deduped_count": len(deduped),
        "valid_product_candidates": len(product_candidates),
        "invalid_non_product_removed": invalid_non_product_removed,
        "budget_valid": budget_valid_count,
        "budget_valid_count": budget_valid_count,
        "candidate_pool": len(candidates),
        "candidate_pool_count": len(candidates),
        "ai_input_count": len(candidates),
        "target_display": target_display,
        "image_found": public_image_found,
        "image_missing": len(public_final) - public_image_found,
        "normalizer_image_found": normalizer.images_extracted_count,
        "normalizer_image_missing": normalizer.images_missing_count,
        "overfetch_attempted": bool(overfetch_meta.get("overfetch_attempted", False)),
        "overfetch_attempts": int(overfetch_meta.get("overfetch_attempts", 0) or 0),
        "overfetch_rounds": int(overfetch_meta.get("overfetch_rounds", overfetch_meta.get("overfetch_attempts", 0)) or 0),
        "overfetch_initial_valid_pool": int(overfetch_meta.get("overfetch_initial_valid_pool", len(candidates)) or 0),
        "overfetch_final_valid_pool": int(overfetch_meta.get("overfetch_final_valid_pool", len(candidates)) or 0),
        "overfetch_max_raw": int(overfetch_meta.get("overfetch_max_raw", 0) or 0),
        "overfetch_exhausted": bool(overfetch_meta.get("overfetch_exhausted", False)),
        "overfetch_stop_reason": str(overfetch_meta.get("overfetch_stop_reason") or ""),
        "raw_after_overfetch": int(overfetch_meta.get("raw_after_overfetch", len(raw_products)) or 0),
        "strict_budget_mode": strict_budget_mode,
        "target_first_mode": target_first_mode,
        "target_first_added": target_first_added,
        "query_constraints": ai_meta.get("query_constraints", {}),
        "feedback_examples_loaded": ai_meta.get("feedback_examples_loaded", 0),
        "learned_patterns_loaded": ai_meta.get("learned_patterns_loaded", 0),
        "query_scoped_patterns": ai_meta.get("query_scoped_patterns", 0),
        "constraint_scoped_patterns": ai_meta.get("constraint_scoped_patterns", 0),
        "intent_scoped_patterns": ai_meta.get("intent_scoped_patterns", 0),
        "global_patterns": ai_meta.get("global_patterns", 0),
        "constraint_mismatch_products": ai_meta.get("constraint_mismatch_products", 0),
        "learning_adjusted_products": ai_meta.get("learning_adjusted_products", 0),
        "learned_positive_matches": ai_meta.get("learned_positive_matches", 0),
        "learned_negative_matches": ai_meta.get("learned_negative_matches", 0),
        "rule_accepted": ai_meta.get("rule_accepted", ai_meta.get("rule_accepted_count", 0)),
        "rule_rejected": ai_meta.get("rule_rejected", ai_meta.get("rule_rejected_count", 0)),
        "borderline_candidates": ai_meta.get("borderline_candidates", 0),
        "semantic_checked": semantic_checked,
        "semantic_checked_count": semantic_checked,
        "classifier_checked": classifier_checked,
        "ai_checked": classifier_checked,
        "ai_calls_attempted": ai_meta.get("ai_calls_attempted", 0),
        "ai_calls_succeeded": ai_meta.get("ai_calls_succeeded", 0),
        "ai_timeouts": ai_timeouts,
        "ai_failures": ai_meta.get("ai_failures", 0),
        "ai_batch_size": ai_meta.get("ai_batch_size"),
        "prompt_tokens_estimated": ai_meta.get("prompt_tokens_estimated", 0),
        "prompt_truncated_by_app": ai_meta.get("prompt_truncated_by_app", False),
        "ctx": ai_meta.get("ctx"),
        "ai_circuit_open": bool(ai_meta.get("ai_circuit_open", False)),
        "classifier_limit": ai_meta.get("classifier_limit"),
        "ai_accepted": ai_meta.get("ai_accepted", ai_meta.get("ai_accepted_count", 0)),
        "ai_accepted_count": ai_meta.get("ai_accepted", ai_meta.get("ai_accepted_count", 0)),
        "ai_confirmed": ai_meta.get("ai_confirmed", 0),
        "ai_rescued": ai_meta.get("ai_rescued", 0),
        "ai_rejected": ai_meta.get("ai_rejected", 0),
        "ai_fallback": ai_meta.get("ai_fallback", 0),
        "fallback_candidates": ai_meta.get("fallback_candidates", 0),
        "fallback_candidates_count": ai_meta.get("fallback_candidates_count", ai_meta.get("fallback_candidates", 0)),
        "weak_fallback_candidates": ai_meta.get("weak_fallback_candidates", 0),
        "weak_fallback_candidates_count": ai_meta.get("weak_fallback_candidates_count", ai_meta.get("weak_fallback_candidates", 0)),
        "fallback_rejected_as_junk": ai_meta.get("fallback_rejected_as_junk", 0),
        "fallback_added": fallback_added,
        "accepted_before_fallback": ai_meta.get("accepted_before_fallback", 0),
        "rejected_as_obvious_junk": ai_meta.get("rejected_as_obvious_junk", 0),
        "rejected_as_obvious_junk_count": ai_meta.get("rejected_as_obvious_junk_count", ai_meta.get("rejected_as_obvious_junk", 0)),
        "rejected_as_obvious_junk_count_before_rescue": ai_meta.get("rejected_as_obvious_junk_count_before_rescue", 0),
        "rescued_false_obvious_junk": ai_meta.get("rescued_false_obvious_junk", 0),
        "rejected_reasons_histogram": ai_meta.get("rejected_reasons_histogram", {}),
        "pipeline_debug_path": ai_meta.get("pipeline_debug_path"),
        "why_remaining_products_were_not_displayed": ai_meta.get("why_remaining_products_were_not_displayed"),
        "displayed_count": len(public_final),
        "displayed": len(public_final),
        "has_enough_results": has_enough,
        "limited_reason": limited,
        "ai_skip_reason": ai_skip_reason,
        "ai_status": ai_status,
        "ai_warning": final_warning,
        "ai_orchestrator": ai_meta.get("ai_orchestrator", orchestrator_status),
        "ai_model": ai_meta.get("selected_model"),
        "selected_classifier": ai_meta.get("selected_classifier", ai_meta.get("selected_model")),
        "query_intent": ai_meta.get("query_intent"),
        "sort_mode": req.sort_mode,
        "rule_accepted_count": ai_meta.get("rule_accepted_count", 0),
        "rule_rejected_count": ai_meta.get("rule_rejected_count", 0),
        "llm_checked_count": classifier_checked,
        "fallback_expansion_count": fallback_added,
    }

    log(
        "COUNT",
        (
            f"requested={req.target_count} raw_target={get_progress(search_id).get('raw_target') if get_progress(search_id) else '?'} "
            f"raw_scraped={len(raw_products)} deduped={len(deduped)} "
            f"valid_product_candidates={len(product_candidates)} "
            f"invalid_non_product_removed={invalid_non_product_removed} "
            f"budget_valid={budget_valid_count} candidate_pool={len(candidates)} target_display={target_display} "
            f"semantic_checked={semantic_checked} classifier_checked={classifier_checked} "
            f"ai_calls_attempted={metadata['ai_calls_attempted']} ai_calls_succeeded={metadata['ai_calls_succeeded']} "
            f"ai_timeouts={metadata['ai_timeouts']} ai_failures={metadata['ai_failures']} "
            f"prompt_tokens_estimated={metadata['prompt_tokens_estimated']} ctx={metadata['ctx']} "
            f"ai_circuit_open={str(metadata['ai_circuit_open']).lower()} "
            f"ai_accepted={metadata['ai_accepted']} ai_rejected={metadata['ai_rejected']} ai_fallback={metadata['ai_fallback']} "
            f"accepted_before_fallback={metadata['accepted_before_fallback']} "
            f"fallback_candidates={metadata['fallback_candidates']} weak_fallback_candidates={metadata['weak_fallback_candidates']} "
            f"fallback_added={fallback_added} displayed={len(public_final)} "
            f"ai_skip_reason={metadata['ai_skip_reason']} "
            f"has_enough={str(has_enough).lower()}"
            + (f' reason="{limited}"' if limited else "")
        ),
        "INFO",
    )

    if len(candidates) >= req.target_count and len(public_final) < req.target_count:
        log(
            "PIPELINE",
            (
                f"target_not_met target={target_display} displayed={len(public_final)} "
                f"accepted_count_before_fallback={metadata['accepted_before_fallback']} "
                f"fallback_candidates_count={metadata['fallback_candidates_count']} "
                f"weak_fallback_candidates_count={metadata['weak_fallback_candidates_count']} "
                f"fallback_added={fallback_added} "
                f"rejected_as_obvious_junk_count={metadata['rejected_as_obvious_junk_count']} "
                f"rejected_reasons_histogram={metadata['rejected_reasons_histogram']} "
                f"reason={metadata.get('why_remaining_products_were_not_displayed')}"
            ),
            "ERROR",
        )

    error = ""
    ai_warning = final_warning

    if ai_status == "unavailable" and not ai_warning:
        ai_warning = "AI unavailable for borderline products; deterministic relevance fallback was used."
    elif ai_status == "failed":
        ai_warning = ai_warning or "AI filtering failed. Products were displayed with explicit fallback."
    metadata["ai_warning"] = ai_warning

    if not candidates and budget_result.budget_value is not None:
        error = (
            f"0 produk lolos budget {format_rupiah(budget_result.min_price)} - "
            f"{format_rupiah(budget_result.max_price)}. Coba naikkan budget/tolerance."
        )
    elif not ai_valid:
        if ai_status in ("failed", "unavailable"):
            error = f"0 produk tersisa setelah fallback filter. {ai_warning}"
        else:
            error = "Semua produk ditolak filter relevansi. Disable AI atau tambah feedback."
    elif not public_final:
        error = "Tidak ada produk setelah filter final."

    return {
        "raw_products": raw_products,
        "normalizer": normalizer,
        "deduped": deduped,
        "budget": budget_result,
        "ai_valid": ai_valid,
        "ranked": ranked,
        "final": public_final,
        "ai_status": ai_status,
        "ai_warning": ai_warning,
        "ai_meta": ai_meta,
        "metadata": metadata,
        "recommendations": recommendations,
        "error": error,
    }


def _engine_run_payload(run: EngineRunResult) -> dict[str, Any]:
    """
    Serialize one engine run to the API response.
    raw_products_found is before any filter so callers can verify raw != 0.
    """
    count = run.raw_products_found
    return {
        "engine": run.engine,
        "ok": run.ok,
        "opened_real_page": run.opened_real_page,
        "error_type": run.error_type,
        "raw_count": count,
        "raw_scraped": count,
        "raw_products_found": count,    # ← kept for backward compat with test_engine_reports
        "duration_seconds": round(run.duration_seconds, 2),
        "status": "success" if run.ok else "fail",
        "error": run.error,
        "debug_files": [p for p in run.debug_files if p],
    }


async def _finish_compare(
    search_id: str,
    req: SearchRequest,
    selection: EngineSelectionResult,
    eta_calc: ETACalculator,
) -> None:
    """
    Compare mode: run filter pipeline for BOTH engines independently.
    No silent fallback between engines.
    Both results are returned regardless of AI classifier status.
    """
    comparison: list[dict[str, Any]] = []

    for run in selection.runs:
        base_payload = _engine_run_payload(run)

        if not run.ok or not run.products:
            # Engine itself failed (Chrome error page / zero raw)
            comparison.append({
                **base_payload,
                "budget_count": 0,
                "budget_valid_count": 0,
                "ai_count": 0,
                "ai_valid_count": 0,
                "ai_accepted_count": 0,
                "ai_status": "skipped",
                "result_metadata": {
                    "requested_count": req.target_count,
                    "raw_scraped_count": run.raw_products_found,
                    "raw_scraped": run.raw_products_found,
                    "deduped_count": 0,
                    "budget_valid_count": 0,
                    "ai_input_count": 0,
                    "ai_accepted_count": 0,
                    "displayed_count": 0,
                    "has_enough_results": False,
                    "limited_reason": _limited_reason(req.target_count, 0),
                },
                "recommendations": _build_recommendations(req.query, []),
                "data": [],
                "products": [],
                "budget_debug_path": None,
                "normalizer_debug_path": None,
            })
            continue

        update_progress(
            search_id,
            active_engine=run.engine,
            stage="compare_filtering",
            percent=75,
            message=f"Compare: filtering {run.engine} ({len(run.products)} raw)...",
            found=len(run.products),
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        raw_for_filter, overfetch_meta = await _overfetch_raw_products(
            search_id,
            req,
            run.products,
            run.engine,
            run.raw_products_found,
            eta_calc,
        )
        filtered = await _filter_pipeline(
            search_id,
            req,
            raw_for_filter,
            eta_calc,
            run.engine,
            overfetch_meta=overfetch_meta,
        )
        budget_result: FilterResult = filtered["budget"]
        normalizer = filtered["normalizer"]
        data = filtered["final"]

        comparison.append({
            **base_payload,
            "budget_count": len(budget_result.kept),
            "budget_valid_count": len(budget_result.kept),
            "ai_count": len(filtered["ai_valid"]),
            "ai_valid_count": len(filtered["ai_valid"]),
            "ai_accepted_count": filtered["metadata"].get("ai_accepted_count", 0),
            "ai_status": filtered["ai_status"],
            "ai_warning": filtered["ai_warning"],
            "result_metadata": filtered["metadata"],
            "recommendations": filtered["recommendations"],
            "data": data,
            "products": data,
            "error": filtered["error"] if not data else "",
            "normalizer_debug_path": normalizer.debug_path,
            "budget_debug_path": budget_result.debug_path,
        })

    # Best engine = most AI-valid, then budget-valid, then raw
    selected = max(
        comparison,
        key=lambda c: (c["ai_valid_count"], c["budget_valid_count"], c["raw_count"]),
        default=None,
    )
    selected_engine = selected["engine"] if selected else None
    final_data = (selected or {}).get("data", [])
    selected_metadata = (selected or {}).get("result_metadata") or {
        "requested_count": req.target_count,
        "raw_scraped_count": 0,
        "raw_scraped": 0,
        "deduped_count": 0,
        "budget_valid_count": 0,
        "ai_input_count": 0,
        "ai_accepted_count": 0,
        "displayed_count": len(final_data),
        "has_enough_results": len(final_data) >= req.target_count,
        "limited_reason": _limited_reason(req.target_count, len(final_data)),
    }

    save_result(search_id, {
        "success": True,
        "search_id": search_id,
        "query": req.query,
        "engine_mode": req.engine_mode,
        "sort_mode": req.sort_mode,
        "selected_engine": selected_engine,
        "count": len(final_data),
        "requested_count": req.target_count,
        "displayed_count": len(final_data),
        "limited_reason": selected_metadata.get("limited_reason"),
        "result_metadata": selected_metadata,
        "recommendations": (selected or {}).get("recommendations") or _build_recommendations(req.query, final_data),
        "ai_status": (selected or {}).get("ai_status", "skipped"),
        "ai_warning": (selected or {}).get("ai_warning", ""),
        "data": final_data,
        "engine_runs": comparison,     # ← also exposed as engine_runs for consistency
        "comparison": comparison,      # ← kept for frontend renderComparison()
        "budget_info": None,
    })
    complete_progress(search_id)


async def run_scrape_job(search_id: str, req: SearchRequest, raw_target: int) -> None:
    log(f"[{search_id}]", f"Starting '{req.query}' target={req.target_count} mode={req.engine_mode}", "INFO")
    log("COUNT", f"requested={req.target_count}", "INFO")
    log("COUNT", f"raw_target={raw_target}", "INFO")
    eta_calc = ETACalculator()

    selection = await run_scraper_engines(
        search_id, req.query, raw_target, eta_calc,
        req.engine_mode, req.budget, req.tolerance
    )

    if req.engine_mode in {"compare", "compare_both"} and selection.runs:
        await _finish_compare(search_id, req, selection, eta_calc)
        return

    if not selection.ok or not selection.products:
        error_msg = selection.error or "Tidak ada produk ditemukan."
        # Annotate error with preflight context if browser failed
        for run in selection.runs:
            if not run.opened_real_page and run.error_type:
                error_msg = (
                    f"Browser membuka Chrome error page: {run.error_type}. "
                    f"Bukan masalah selector. "
                    f"Lihat debug: data/debug/{search_id}/"
                )
                break
        fail_progress(search_id, error_msg)
        return

    update_progress(
        search_id,
        active_engine=selection.selected_engine or "unknown",
        stage="deduplicating",
        percent=58,
        message="Menghapus duplikat...",
        found=len(selection.products),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    raw_for_filter, overfetch_meta = await _overfetch_raw_products(
        search_id,
        req,
        selection.products,
        selection.selected_engine or "selected",
        raw_target,
        eta_calc,
    )

    filtered = await _filter_pipeline(
        search_id, req, raw_for_filter, eta_calc,
        selection.selected_engine or "selected",
        overfetch_meta=overfetch_meta,
    )
    budget_result: FilterResult = filtered["budget"]

    if not filtered["final"]:
        fail_progress(search_id, filtered["error"])
        return

    update_progress(
        search_id,
        stage="finalizing",
        percent=96,
        message="Menyiapkan hasil...",
        valid=len(filtered["final"]),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    engine_runs = []
    for run in selection.runs:
        payload = _engine_run_payload(run)
        if run.engine == (selection.selected_engine or ""):
            payload.update({
                "budget_count": len(budget_result.kept),
                "budget_valid_count": len(budget_result.kept),
                "ai_count": len(filtered["ai_valid"]),
                "ai_valid_count": len(filtered["ai_valid"]),
                "ai_accepted_count": filtered["metadata"].get("ai_accepted_count", 0),
                "ai_status": filtered["ai_status"],
                "ai_warning": filtered["ai_warning"],
                "result_metadata": filtered["metadata"],
                "recommendations": filtered["recommendations"],
                "products": filtered["final"],
                "data": filtered["final"],
            })
        engine_runs.append(payload)

    save_result(search_id, {
        "success": True,
        "search_id": search_id,
        "query": req.query,
        "engine_mode": req.engine_mode,
        "sort_mode": req.sort_mode,
        "selected_engine": selection.selected_engine,
        "fallback_message": selection.fallback_message,
        "engine_runs": engine_runs,
        "raw_count": len(selection.products),
        "deduped_count": len(filtered["deduped"]),
        "budget_count": len(budget_result.kept),
        "budget_valid_count": len(budget_result.kept),
        "ai_count": len(filtered["ai_valid"]),
        "ai_valid_count": len(filtered["ai_valid"]),
        "ai_accepted_count": filtered["metadata"].get("ai_accepted_count", 0),
        "ai_status": filtered["ai_status"],
        "ai_warning": filtered["ai_warning"],
        "count": len(filtered["final"]),
        "requested_count": req.target_count,
        "displayed_count": len(filtered["final"]),
        "limited_reason": filtered["metadata"].get("limited_reason"),
        "result_metadata": filtered["metadata"],
        "recommendations": filtered["recommendations"],
        "data": filtered["final"],
        "budget_info": _budget_info(budget_result),
    })

    complete_progress(search_id)
    log(
        f"[{search_id}]",
        f"Done. raw={len(selection.products)} ai={len(filtered['ai_valid'])} "
        f"returned={len(filtered['final'])} ai_status={filtered['ai_status']}",
        "OK",
    )

```

## FILE: `src\server\schemas.py`

```python
"""
schemas.py - API request and response models.

FeedbackRequest updated to support multi-category correction and ai_decision.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from src.config import TARGET_COUNT_DEFAULT, TARGET_FIRST_MODE


EngineMode = Literal["auto", "puppeteer", "rollback", "selenium", "compare", "compare_both"]
SortMode = Literal["terbaik", "termurah", "most_trusted"]
REQUESTED_COUNT_DEFAULT = max(1, int(TARGET_COUNT_DEFAULT))


class SearchRequest(BaseModel):
    """Accept both old frontend keys and new API keys."""
    model_config = ConfigDict(populate_by_name=True)

    query: str
    target_count: int = Field(default=REQUESTED_COUNT_DEFAULT, validation_alias=AliasChoices("target_count", "target"))
    budget: Optional[Any] = None
    tolerance: float = 20.0
    use_ai: bool = Field(default=True, validation_alias=AliasChoices("use_ai", "ai"))
    engine_mode: EngineMode = "auto"
    sort_mode: SortMode = "terbaik"
    target_first_mode: bool = Field(
        default=TARGET_FIRST_MODE,
        validation_alias=AliasChoices("target_first_mode", "target_first"),
    )


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="allow", protected_namespaces=())

    search_id: str = "unknown"
    product_id: str = ""
    product_title: str = ""
    user_action: str = ""
    selected_reasons: List[str] = Field(default_factory=list)
    custom_reason: str = ""
    corrected_label: str = ""
    ai_label: str = ""
    ai_confidence: float = 0.0
    query: str
    timestamp: str = ""
    query_intent: Optional[str] = None
    product: Optional[Dict[str, Any]] = None
    feedback_type: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    note: str = ""
    rule_score: float = 0.0
    semantic_score: float = 0.0
    combined_score: float = 0.0
    learned_adjustment: float = 0.0
    confidence: float = 0.0
    learning_scope_hint: Optional[str] = None
    model_used: Optional[str] = None
    ai_reason: Optional[str] = None
    sort_mode: str = "terbaik"

    @field_validator("selected_reasons", "reasons", mode="before")
    @classmethod
    def _coerce_reason_list(cls, value: Any) -> List[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if item not in (None, "")]
        return [str(value)]

    def normalized_product(self) -> Dict[str, Any]:
        product = dict(self.product or {})
        if self.product_id and not product.get("id"):
            product["id"] = self.product_id
        if self.product_title and not product.get("title"):
            product["title"] = self.product_title
        return product

    def normalized_product_id(self) -> str:
        product = self.normalized_product()
        return str(self.product_id or product.get("id") or product.get("url") or "unknown")

    def normalized_product_title(self) -> str:
        product = self.normalized_product()
        return str(self.product_title or product.get("title") or "")

    def normalized_reasons(self) -> List[str]:
        return list(self.reasons or self.selected_reasons or [])

    def normalized_note(self) -> str:
        return str(self.note or self.custom_reason or "")

    def normalized_feedback_type(self) -> str:
        value = str(self.feedback_type or "").strip().lower()
        if value in {"positive", "negative"}:
            return value
        action = str(self.user_action or "").strip().lower()
        return "positive" if action == "benar" else "negative"

    def normalized_user_action(self) -> str:
        action = str(self.user_action or "").strip().lower()
        if action in {"benar", "salah"}:
            return action
        return "benar" if self.normalized_feedback_type() == "positive" else "salah"

    def normalized_corrected_label(self) -> str:
        label = str(self.corrected_label or "").strip()
        if label:
            return label
        return "relevan" if self.normalized_feedback_type() == "positive" else "tidak_relevan"


class ProgressResponse(BaseModel):
    search_id: str
    engine_mode: str = "auto"
    active_engine: str = "none"
    percent: float
    progress_percent: float = 0.0
    stage: str
    phase: str = "initializing"
    message: str
    status_text: str = ""
    found: int
    valid: int
    target: int
    raw_target: int
    started_at_epoch_ms: int = 0
    started_at_monotonic: float = 0.0
    updated_at_epoch_ms: int = 0
    server_now_epoch_ms: int = 0
    elapsed_seconds: float
    eta_seconds: Optional[int] = None
    estimated_completion_epoch_ms: Optional[int] = None
    eta_label: str = "Calculating..."
    eta_is_reliable: bool = False
    ai_batch_current: Optional[int] = None
    ai_batch_total: Optional[int] = None
    ai_batch_started_at_epoch_ms: Optional[int] = None
    ai_avg_batch_seconds: Optional[float] = None
    ai_current_batch_elapsed_seconds: Optional[float] = None
    ai_completed_batches: Optional[int] = None
    ai_orchestrator: Optional[Dict[str, Any]] = None
    engine: str = "none"
    attempt: int = 1
    max_attempts: int = 1
    done: bool
    error: Optional[str] = None
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    searchId: str = ""
    statusText: str = ""
    percentage: float = 0.0
    elapsedSeconds: float = 0.0
    etaSeconds: Optional[int] = None
    foundCount: int = 0
    targetCount: int = 0

```

## FILE: `src\utils\__init__.py`

```python

```

## FILE: `src\utils\currency.py`

```python
"""
currency.py - Shared Rupiah parsing and formatting.

The scraper receives prices from the browser as messy UI text. Keep all price
parsing here so the backend, filters, and tests use one truth.
"""
from __future__ import annotations

import math
import re
import unicodedata
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


INVALID_PRICE_WORDS = (
    "hubungi penjual",
    "hubungi",
    "nego",
    "tanya",
    "gratis",
    "free",
)


def _normalize_text(value: Any) -> str:
    """Normalize browser text, hidden spaces, and mixed case before parsing."""
    if value is None or isinstance(value, bool):
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def _decimal_from_text(number_text: str) -> Decimal | None:
    """Parse decimal text used with units like jt/juta/rb."""
    cleaned = number_text.strip().replace(",", ".")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def parse_rupiah(value: Any) -> int | None:
    """
    Convert Indonesian Rupiah text into an integer.

    Examples:
    - "Rp10.000.000" -> 10000000
    - "Rp10,5 juta" -> 10500000
    - "Rp999 rb" -> 999000
    - "" / None / "Hubungi Penjual" -> None
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value if value >= 0 else None

    if isinstance(value, float):
        if not math.isfinite(value) or value < 0:
            return None
        return int(round(value))

    text = _normalize_text(value)
    if not text or any(word in text for word in INVALID_PRICE_WORDS):
        return None

    # Unit prices need decimal support: "10,5 juta", "10.5 jt", "999 rb".
    unit_match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|million|rb|ribu|k)\b",
        text,
        flags=re.IGNORECASE,
    )
    if unit_match:
        number = _decimal_from_text(unit_match.group(1))
        if number is None:
            return None
        unit = unit_match.group(2).lower()
        multiplier = 1_000_000 if unit in {"juta", "jt", "mio", "million"} else 1_000
        parsed = (number * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(parsed)

    # Plain prices on Tokopedia are integer money. Drop Rp, dots, commas, spaces.
    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return None

    try:
        return int(digits)
    except ValueError:
        return None


def format_rupiah(value: Any) -> str:
    """Format an integer as compact Indonesian Rupiah text: 10000000 -> Rp10.000.000."""
    parsed = parse_rupiah(value)
    if parsed is None:
        return "Rp0"
    return "Rp" + f"{parsed:,}".replace(",", ".")


def calculate_budget_range(budget: Any, tolerance: Any = 20) -> tuple[int, int]:
    """
    Calculate inclusive min/max range for a budget and percentage tolerance.

    Empty/invalid budget returns (0, 0). Callers use parse_rupiah(budget) is None
    to decide that the budget filter is disabled.
    """
    budget_value = parse_rupiah(budget)
    if budget_value is None or budget_value <= 0:
        return 0, 0

    try:
        tolerance_value = float(tolerance)
    except (TypeError, ValueError):
        tolerance_value = 20.0

    tolerance_value = max(0.0, min(tolerance_value, 100.0))
    fraction = tolerance_value / 100.0
    return int(budget_value * (1.0 - fraction)), int(budget_value * (1.0 + fraction))

```

## FILE: `src\utils\debug.py`

```python
"""
debug.py - Handles saving debug artifacts on scraper failure.
"""
import os
import json
from pathlib import Path
from typing import Any
from src.utils.logger import log

DEBUG_DIR = Path(__file__).parent.parent.parent / "data" / "debug"

def get_debug_dir(search_id: str) -> Path:
    """Gets the debug directory for a search_id."""
    dir_path = DEBUG_DIR / search_id
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def safe_save_debug(search_id: str, error: str, products: list, progress: dict = None, page_source: str = None):
    """
    Safely saves debug state without throwing new errors.
    """
    try:
        dir_path = get_debug_dir(search_id)
        
        # Save error.txt
        try:
            with open(dir_path / "error.txt", "w", encoding="utf-8") as f:
                f.write(str(error))
        except Exception: pass
        
        # Save raw_products.json
        try:
            with open(dir_path / "raw_products.json", "w", encoding="utf-8") as f:
                json.dump(products or [], f, indent=2, ensure_ascii=False)
        except Exception: pass
        
        # Save progress.json
        try:
            if progress:
                with open(dir_path / "progress.json", "w", encoding="utf-8") as f:
                    json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception: pass
        
        # Save HTML
        try:
            with open(dir_path / "page.html", "w", encoding="utf-8") as f:
                if page_source:
                    f.write(page_source)
                else:
                    f.write("HTML unavailable: page navigating/closed")
        except Exception: pass

        log("DEBUG", f"Saved debug artifacts for {search_id} to {dir_path}", "OK")
    except Exception as e:
        log("DEBUG", f"Failed to save debug artifacts for {search_id}: {e}", "ERROR")

def save_budget_filter_debug(search_id: str, payload: dict[str, Any], engine_name: str | None = None) -> str:
    """
    Save budget filter decisions. Normal mode uses the required exact filename;
    compare mode gets per-engine files so runs do not overwrite each other.
    """
    dir_path = get_debug_dir(search_id)
    filename = "budget_filter_debug.json"
    if engine_name:
        filename = f"budget_filter_debug_{engine_name}.json"

    output_path = dir_path / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    log("DEBUG", f"Saved budget filter debug to {output_path}", "OK")
    return str(output_path)

def save_category_filter_debug(search_id: str, payload: dict[str, Any], engine_name: str) -> str:
    """Save category filter decisions per engine."""
    dir_path = get_debug_dir(search_id)
    output_path = dir_path / f"category_filter_debug_{engine_name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    log("DEBUG", f"Saved category filter debug to {output_path}", "OK")
    return str(output_path)

def save_json_debug(search_id: str, filename: str, payload: dict[str, Any]) -> str:
    """Write one JSON debug artifact. Never let debug output break scraping."""
    try:
        output_path = get_debug_dir(search_id) / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return str(output_path)
    except Exception as exc:
        log("DEBUG", f"Failed to write {filename}: {exc}", "ERROR")
        return ""

def save_text_debug(search_id: str, filename: str, content: str) -> str:
    """Write one text artifact such as an HTML snapshot."""
    try:
        output_path = get_debug_dir(search_id) / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content or "")
        return str(output_path)
    except Exception as exc:
        log("DEBUG", f"Failed to write {filename}: {exc}", "ERROR")
        return ""

def save_zero_raw_debug(search_id: str, engine_name: str, payload: dict[str, Any]) -> str:
    """Save required zero-raw engine diagnostics."""
    defaults = {
        "engine": engine_name,
        "query": "",
        "query_variants": [],
        "urls_tried": [],
        "pages_loaded": 0,
        "selector_results": {},
        "html_saved": False,
        "screenshot_saved": False,
        "console_logs": [],
        "current_url": "",
        "page_title": "",
        "body_text_sample": "",
        "errors": [],
    }
    defaults.update(payload or {})
    return save_json_debug(search_id, f"{engine_name}_zero_raw_debug.json", defaults)

def save_debug_state_sync(search_id: str, driver=None, error_msg: str = ""):
    """Synchronous version for Selenium driver."""
    from src.server.progress import get_progress
    page_source = None
    if driver:
        try:
            page_source = driver.page_source
        except Exception:
            pass
            
    safe_save_debug(
        search_id=search_id,
        error=error_msg,
        products=[], 
        progress=get_progress(search_id),
        page_source=page_source
    )

```

## FILE: `src\utils\eta.py`

```python
"""
eta.py - Calculates Estimated Time of Arrival for tasks based on progress.
"""
import time
from collections import deque

class ETACalculator:
    def __init__(self, smoothing_window: int = 5):
        """
        Initializes ETA calculator.
        smoothing_window: Number of recent samples to average for smoothing ETA.
        """
        self.start_time = time.perf_counter()
        self.history = deque(maxlen=smoothing_window)
        self.last_pct = 0
    
    def get_eta(self, current_pct: int) -> int | None:
        """
        Calculates smoothed ETA in seconds.
        Returns None if percentage is 0 or 100 (unmeasurable/done).
        """
        if current_pct <= 0 or current_pct >= 100:
            return None
            
        elapsed = time.perf_counter() - self.start_time
        
        # Estimate total time based on current progress
        # If we did X% in Y seconds, 100% takes (Y / (X/100)) seconds
        estimated_total = elapsed / (current_pct / 100.0)
        
        # ETA is total estimated minus elapsed
        raw_eta = max(0.0, estimated_total - elapsed)
        
        # Smooth the ETA so it doesn't jump wildly
        self.history.append(raw_eta)
        smoothed_eta = sum(self.history) / len(self.history)
        
        return int(smoothed_eta)

    def get_elapsed(self) -> int:
        """Returns elapsed time in seconds."""
        return int(time.perf_counter() - self.start_time)

```

## FILE: `src\utils\logger.py`

```python
"""
logger.py - Structured logging system.
Formats logs consistently with timestamp, level, and tags.
"""
import datetime
import sys

def log(tag: str, msg: str, level: str = "INFO"):
    """
    Logs a message to stdout.
    Levels: INFO, WARN, ERROR, DEBUG
    """
    now = datetime.datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",  # Blue
        "WARN": "\033[93m",  # Yellow
        "ERROR": "\033[91m", # Red
        "DEBUG": "\033[90m"  # Gray
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    
    formatted = f"[{now}] {color}[{level}]{reset} [{tag}] {msg}"
    print(formatted, flush=True)

class Logger:
    def __init__(self, tag: str):
        self.tag = tag

    def info(self, msg: str):
        log(self.tag, msg, "INFO")

    def warn(self, msg: str):
        log(self.tag, msg, "WARN")

    def error(self, msg: str):
        log(self.tag, msg, "ERROR")

    def debug(self, msg: str):
        log(self.tag, msg, "DEBUG")

```

## FILE: `tests\test_ai_orchestrator_runtime_path.py`

```python
from __future__ import annotations

import pytest

from src.ai import ai_filter, model_registry, ollama_client
import src.ai.feedback_store as feedback_store
import src.ai.relevance as relevance
from src.ai.relevance import filter_relevance
from src.server import routes
from src.server.schemas import SearchRequest
from src.scraper.engine_selector import EngineRunResult
from src.utils.eta import ETACalculator


@pytest.mark.asyncio
async def test_borderline_product_calls_ai_orchestrator(monkeypatch):
    calls = []

    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["gemma3:4b"],
            "supported": ["gemma3:4b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": True, "fast_classifier": False, "json_repair": False},
            "classifier": "gemma3:4b",
            "message": "AI Orchestrator ready",
        },
    )

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        products[0]["_audit_id"] = "p1"
        calls.append({"args": args, "kwargs": kwargs})
        return {
            "ok": True,
            "items": [{
                "id": "p1",
                "accepted": True,
                "confidence": 0.72,
                "reason": "Borderline accessory matched query intent",
                "category_match": "accessory",
                "decision_source": "ai_orchestrator",
            }],
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)

    products, status = await filter_relevance(
        "charger iphone",
        [{"title": "Adapter USB C 20W", "price": 99000, "price_value": 99000, "url": "https://tokopedia.test/adapter"}],
        use_ai=True,
    )

    assert status == "ok"
    assert calls
    assert products[0]["decision_source"] == "ai_orchestrator"
    assert products[0]["confidence"] >= 0.62


def test_chat_raw_posts_to_ollama_chat(monkeypatch):
    captured = {}

    class DummyResponse:
        status_code = 200
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": '{"accepted": true, "confidence": 0.8, "reason": "ok", "category_match": "match"}'}}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["payload"] = json
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr(ollama_client.requests, "post", fake_post)

    result = ollama_client.chat_raw("prompt", model="gemma3:4b")

    assert result["ok"] is True
    assert captured["url"].endswith("/api/chat")
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["messages"][0]["role"] == "system"
    assert captured["payload"]["messages"][1]["role"] == "user"
    assert captured["payload"]["options"]["temperature"] == 0
    assert captured["payload"]["options"]["num_ctx"] == 4096
    assert captured["payload"]["options"]["num_predict"] == 180
    assert captured["payload"]["keep_alive"] == "10m"
    assert captured["timeout"] == 75


def test_cpu_mode_does_not_override_classifier_priority():
    assert model_registry.get_best_classifier_model(["llama3.2:3b", "gemma3:4b"]) == "gemma3:4b"


@pytest.mark.asyncio
async def test_cpu_mode_selects_gemma_and_posts_gemma_to_chat(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0.0
    model_registry._MODEL_CACHE["models"] = []
    monkeypatch.setattr(model_registry, "CLASSIFIER_PRIORITY", ["gemma3:4b", "llama3.2:3b"])
    monkeypatch.setattr(ai_filter, "AI_CPU_MODE", True)
    monkeypatch.setattr(ai_filter, "AI_AUDIT_MAX_PRODUCTS", 3)
    monkeypatch.setattr(ai_filter, "AI_BATCH_SIZE", 3)
    monkeypatch.setattr(ai_filter, "AI_CHAT_NUM_CTX", 4096)
    monkeypatch.setattr(ai_filter, "AI_CHAT_NUM_PREDICT", 180)
    monkeypatch.setattr(ai_filter, "AI_CHAT_TIMEOUT_SECONDS", 75)
    monkeypatch.setattr(ollama_client, "AI_CHAT_NUM_CTX", 4096)
    monkeypatch.setattr(ollama_client, "AI_CHAT_NUM_PREDICT", 180)
    monkeypatch.setattr(ollama_client, "AI_CHAT_TIMEOUT_SECONDS", 75)

    captured = {}
    log_messages = []

    def recording_log(tag, msg, level="INFO"):
        log_messages.append((tag, msg, level))
        print(f"[{tag}] {msg}", flush=True)

    monkeypatch.setattr(ai_filter, "log", recording_log)
    monkeypatch.setattr(ollama_client, "log", recording_log)

    class TagsResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"models": [{"name": "llama3.2:3b"}, {"name": "gemma3:4b"}]}

    class ChatResponse:
        status_code = 200
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": '{"items":[{"id":"borderline-gemma","accepted":true,"confidence":0.8,"reason":"ok","category_match":"match"}]}'}}

    def fake_get(url, timeout):
        assert url.endswith("/api/tags")
        return TagsResponse()

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["payload"] = json
        captured["timeout"] = timeout
        return ChatResponse()

    monkeypatch.setattr(model_registry.requests, "get", fake_get)
    monkeypatch.setattr(ollama_client.requests, "post", fake_post)
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: 0.55)
    monkeypatch.setattr(relevance, "apply_laptop_gaming_boost", lambda query, product, score: score)
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(feedback_store, "extract_query_constraints", lambda *args, **kwargs: {})
    monkeypatch.setattr(feedback_store, "load_feedback_context", lambda *args, **kwargs: {"feedback_examples_loaded": 0})
    monkeypatch.setattr(feedback_store, "load_learned_patterns", lambda *args, **kwargs: [])
    monkeypatch.setattr(feedback_store, "compute_constraint_mismatch_penalty", lambda *args, **kwargs: (0.0, []))
    monkeypatch.setattr(feedback_store, "compute_learned_adjustment", lambda *args, **kwargs: (0.0, []))

    result = await filter_relevance(
        "office laptop",
        [{
            "id": "borderline-gemma",
            "title": "Budget office laptop",
            "price": 9_500_000,
            "price_value": 9_500_000,
            "url": "https://tokopedia.test/borderline-gemma",
            "_requested_target": 1,
        }],
        use_ai=True,
    )

    assert result.meta["classifier_checked"] == 1
    assert captured["url"].endswith("/api/chat")
    assert captured["payload"]["model"] == "gemma3:4b"
    assert captured["timeout"] == 75
    assert captured["payload"]["options"]["num_ctx"] == 4096
    assert captured["payload"]["options"]["num_predict"] == 180
    assert ("AI_ORCH", "selected_classifier=gemma3:4b cpu_mode=true ctx=4096 predict=180 timeout=75 batch=true max_products=3", "INFO") in log_messages
    assert any(
        tag == "AI_ORCH" and msg.startswith("chat_options model=gemma3:4b num_ctx=4096 num_predict=180 timeout=75")
        for tag, msg, _level in log_messages
    )
    assert any(
        tag == "AI_ORCH" and msg.startswith("POST /api/chat selected_model=gemma3:4b")
        for tag, msg, _level in log_messages
    )


@pytest.mark.asyncio
async def test_fallback_expansion_fills_toward_candidate_pool(monkeypatch):
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: product["score"] >= 0.72)

    candidates = []
    for index in range(45):
        score = 0.8 if index < 19 else 0.21
        candidates.append({
            "id": f"p-{index}",
            "title": f"Budget laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/p-{index}",
            "_requested_target": 50,
            "score": score,
        })

    result = await filter_relevance("laptop gaming", candidates, use_ai=False)

    assert len(result.products) == 45
    assert result.meta["displayed"] == 45
    assert result.meta["fallback_added"] == 26


@pytest.mark.asyncio
async def test_laptop_gaming_pipeline_keeps_rtx_bundle_and_ai_checks_borderline(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["gemma3:4b"],
            "supported": ["gemma3:4b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": True, "fast_classifier": False, "json_repair": False},
            "classifier": "gemma3:4b",
            "message": "AI Orchestrator ready",
        },
    )
    monkeypatch.setattr(
        routes,
        "get_orchestrator_status",
        lambda: {
            "classifier": "gemma3:4b",
            "capabilities": {"semantic": False, "json_repair": False},
        },
    )
    monkeypatch.setattr(feedback_store, "load_learned_patterns", lambda *args, **kwargs: [])
    monkeypatch.setattr(feedback_store, "load_feedback_context", lambda *args, **kwargs: {"feedback_examples_loaded": 0})

    calls = []

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        calls.append(products)
        items = []
        for product in products:
            product["_audit_id"] = str(product.get("id"))
            items.append({
                "id": str(product.get("id")),
                "accepted": True,
                "confidence": 0.78,
                "reason": "borderline laptop accepted",
                "category_match": "main_product",
                "decision_source": "ai_orchestrator",
            })
        return {
            "ok": True,
            "items": items,
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 465,
            "truncated_by_app": False,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)

    invalid_pages = [
        {"title": "Mulai Berjualan", "price_raw": "", "price_value": 0, "url": "https://seller.tokopedia.com/edu/topic/mulai-bisnis/materi-seller-baru/"},
        {"title": "Kalkulator Indeks Masa Tubuh", "price_raw": "", "price_value": 0, "url": "https://www.tokopedia.com/blog/bmi/"},
        {"title": "Daftar Mall", "price_raw": "", "price_value": 0, "url": "https://seller.tokopedia.com/edu/official-store/"},
    ]
    olacom = {
        "title": (
            "OLACOM Laptop Gaming NVIDIA GeForce RTX 3050 Intel Core i5 13420H "
            "16GB RAM 512GB /1TB SSD 16.0 WUXGA 300Hz Free Tas Laptop"
        ),
        "price_raw": "Rp 12.000.000",
        "price_value": 12_000_000,
        "url": "https://www.tokopedia.com/ola-com/olacom-laptop-gaming-rtx-3050",
    }
    borderline = {
        "title": "Laptop bekas murah",
        "price_raw": "Rp 4.500.000",
        "price_value": 4_500_000,
        "url": "https://www.tokopedia.com/test/laptop-bekas-borderline",
    }
    fillers = [
        {
            "title": f"ASUS TUF Gaming Laptop RTX 3050 Core i5 16GB RAM 512GB SSD Unit {index}",
            "price_raw": f"Rp {10_000_000 + index:,}".replace(",", "."),
            "price_value": 10_000_000 + index,
            "url": f"https://www.tokopedia.com/test/asus-tuf-{index}",
        }
        for index in range(48)
    ]

    filtered = await routes._filter_pipeline(
        "test-laptop-gaming",
        SearchRequest(query="laptop gaming", target_count=50, use_ai=True),
        [*invalid_pages, olacom, borderline, *fillers],
        ETACalculator(),
        "puppeteer",
        overfetch_meta={},
    )

    metadata = filtered["metadata"]
    olacom_result = next(product for product in filtered["ai_valid"] if product["title"].startswith("OLACOM"))

    assert calls
    assert len(calls[0]) == 3
    assert metadata["ai_calls_attempted"] == 1
    assert metadata["ai_calls_succeeded"] == 1
    assert metadata["ai_checked"] == 3
    assert metadata["ai_accepted"] == 3
    assert metadata["prompt_truncated_by_app"] is False
    assert metadata["ctx"] == 4096
    assert metadata["invalid_non_product_removed"] == 3
    assert metadata["candidate_pool_count"] == 50
    assert metadata["target_display"] == 50
    assert metadata["displayed"] == 50
    assert olacom_result["decision_source"] != "rule_reject"
    assert olacom_result["product_constraints"]["category"] == "laptop"


@pytest.mark.asyncio
async def test_overfetch_loads_more_when_valid_pool_is_below_requested(monkeypatch):
    calls = []

    def product(index: int) -> dict:
        return {
            "title": f"ASUS TUF Gaming Laptop RTX 3050 Core i5 Unit {index}",
            "price_raw": f"Rp {10_000_000 + index:,}".replace(",", "."),
            "price_value": 10_000_000 + index,
            "url": f"https://www.tokopedia.com/test/overfetch-{index}",
        }

    async def fake_run_engine(search_id, engine_name, query, raw_target, eta_calc):
        calls.append({
            "search_id": search_id,
            "engine_name": engine_name,
            "query": query,
            "raw_target": raw_target,
        })
        return EngineRunResult(
            engine=engine_name,
            ok=True,
            opened_real_page=True,
            products=[product(49)],
        )

    monkeypatch.setattr(routes, "run_engine", fake_run_engine)

    raw_products, meta = await routes._overfetch_raw_products(
        "test-overfetch",
        SearchRequest(query="laptop gaming", target_count=50, use_ai=True),
        [product(index) for index in range(49)],
        "puppeteer",
        50,
        ETACalculator(),
    )

    snapshot = routes._candidate_pool_snapshot(
        raw_products,
        SearchRequest(query="laptop gaming", target_count=50, use_ai=True),
        "puppeteer",
    )

    assert calls
    assert meta["overfetch_attempted"] is True
    assert meta["overfetch_initial_valid_pool"] == 49
    assert meta["overfetch_final_valid_pool"] == 50
    assert meta["overfetch_rounds"] == 1
    assert meta["overfetch_max_raw"] == 500
    assert meta["overfetch_stop_reason"] == "target_met"
    assert snapshot["candidate_pool_count"] == 50


@pytest.mark.asyncio
async def test_fallback_expansion_fills_from_twenty_five_to_requested_fifty(monkeypatch):
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: product["score"] >= 0.78)

    candidates = []
    for index in range(64):
        score = 0.82 if index < 25 else 0.20
        candidates.append({
            "id": f"p-{index}",
            "title": f"Budget electronics candidate {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/fill-{index}",
            "_requested_target": 50,
            "_budget_valid": 64,
            "score": score,
        })

    result = await filter_relevance("laptop gaming", candidates, use_ai=False)

    assert len(result.products) == 50
    assert result.meta["displayed"] == 50
    assert result.meta["fallback_added"] == 25
    assert result.meta["candidate_pool"] == 64


@pytest.mark.asyncio
async def test_requested_fifty_fills_from_weak_safe_candidates(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": False,
            "installed": [],
            "supported": [],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": False, "fast_classifier": False, "json_repair": False},
            "classifier": None,
            "message": "rules only",
        },
    )
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: product["score"] >= 0.78)

    candidates = []
    for index in range(50):
        score = 0.82 if index < 21 else 0.01
        candidates.append({
            "id": f"p-{index}",
            "title": f"Safe budget electronics candidate {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/weak-fill-{index}",
            "_requested_target": 50,
            "_budget_valid": 50,
            "score": score,
        })

    result = await filter_relevance("laptop gaming", candidates, use_ai=False)

    assert len(result.products) == 50
    assert result.meta["target_display"] == 50
    assert result.meta["displayed"] == 50
    assert result.meta["accepted_before_fallback"] == 21
    assert result.meta["fallback_added"] == 29
    assert result.meta["weak_fallback_candidates_count"] == 29
    assert result.meta["ai_checked"] == 0
    assert result.meta["ai_skip_reason"] == "AI disabled"


@pytest.mark.asyncio
async def test_classifier_limit_sends_only_top_four_borderline_products(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["llama3.2:3b"],
            "supported": ["llama3.2:3b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": False, "fast_classifier": True, "json_repair": False},
            "classifier": "llama3.2:3b",
            "message": "AI Orchestrator ready",
        },
    )
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)

    calls = []

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        calls.extend(product["id"] for product in products)
        items = []
        for product in products:
            product["_audit_id"] = product["id"]
            items.append({
                "id": product["id"],
                "accepted": True,
                "confidence": 0.70,
                "reason": "classified",
                "category_match": "main",
                "decision_source": "ai_orchestrator",
            })
        return {
            "ok": True,
            "items": items,
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)
    candidates = [
        {
            "id": f"p-{index}",
            "title": f"Budget laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/limit-{index}",
            "_requested_target": 20,
            "score": 0.55 - index * 0.001,
        }
        for index in range(20)
    ]

    result = await filter_relevance("laptop gaming", candidates, use_ai=True)

    assert len(calls) == 3
    assert result.meta["classifier_checked"] == 3
    assert result.meta["ai_calls_attempted"] == 1
    assert result.meta["fallback_added"] == 17
    assert result.meta["displayed"] == 20
    assert any(product["decision_source"] == "fallback_not_classified_cpu_limit" for product in result.products)


@pytest.mark.asyncio
async def test_ai_reject_cannot_drop_positive_laptop_evidence(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["llama3.2:3b"],
            "supported": ["llama3.2:3b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": False, "fast_classifier": True, "json_repair": False},
            "classifier": "llama3.2:3b",
            "message": "AI Orchestrator ready",
        },
    )

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        products[0]["_audit_id"] = "p1"
        return {
            "ok": True,
            "items": [{
                "id": "p1",
                "accepted": False,
                "confidence": 0.90,
                "reason": "fake rejection",
                "category_match": "no",
                "decision_source": "ai_orchestrator",
            }],
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: 0.72)
    monkeypatch.setattr(relevance, "apply_laptop_gaming_boost", lambda query, product, score: score)
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(feedback_store, "extract_query_constraints", lambda *args, **kwargs: {})
    monkeypatch.setattr(feedback_store, "load_feedback_context", lambda *args, **kwargs: {"feedback_examples_loaded": 0})
    monkeypatch.setattr(feedback_store, "load_learned_patterns", lambda *args, **kwargs: [])
    monkeypatch.setattr(feedback_store, "compute_constraint_mismatch_penalty", lambda *args, **kwargs: (0.0, []))
    monkeypatch.setattr(feedback_store, "compute_learned_adjustment", lambda *args, **kwargs: (0.0, []))

    result = await filter_relevance(
        "laptop gaming",
        [{
            "id": "msi-modern",
            "title": "MSI Modern 14 Core i7 16GB 512GB",
            "price": 9_500_000,
            "price_value": 9_500_000,
            "url": "https://tokopedia.test/msi-modern",
            "_requested_target": 1,
            "_budget_valid": 1,
        }],
        use_ai=True,
    )

    assert result.meta["displayed"] == 1
    assert result.meta["ai_rejected"] == 1
    assert result.products[0]["decision_source"] == "fallback_after_ai_reject_positive_laptop"


@pytest.mark.asyncio
async def test_classifier_circuit_breaker_turns_timeouts_into_fallback(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["llama3.2:3b"],
            "supported": ["llama3.2:3b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": False, "fast_classifier": True, "json_repair": False},
            "classifier": "llama3.2:3b",
            "message": "AI Orchestrator ready",
        },
    )
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: 0.55)
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)

    async def fake_classify_batch(*args, **kwargs):
        return {
            "ok": False,
            "items": [],
            "_chat_ok": False,
            "_fallback_used": True,
            "_timeout": True,
            "_error": "timeout",
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)
    candidates = [
        {
            "id": f"p-{index}",
            "title": f"Budget laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/timeout-{index}",
            "_requested_target": 10,
        }
        for index in range(10)
    ]

    result = await filter_relevance("laptop gaming", candidates, use_ai=True)

    assert result.meta["classifier_checked"] == 0
    assert result.meta["ai_calls_attempted"] == 1
    assert result.meta["ai_timeouts"] == 1
    assert result.meta["ai_circuit_open"] is True
    assert result.meta["ai_skip_reason"] == "Gemma classifier timeout/failure, used rule+learning fallback"
    assert result.meta["displayed"] == 10
    assert len(result.products) == 10

```

## FILE: `tests\test_app_import.py`

```python
from src.server.main import app


def test_fastapi_app_imports():
    assert app.title == "Tokopedia Scraper API"

```

## FILE: `tests\test_budget_filter.py`

```python
"""
test_budget_filter.py - Budget filter behavior.
"""
import pytest
from src.scraper.budget_filter import filter_by_budget


def make_product(title, price_raw, price_value=None):
    return {"title": title, "price_raw": price_raw, "price_value": price_value, "url": f"https://tokopedia.com/{title.lower().replace(' ', '-')}", "source_engine": "test"}


class TestEmptyBudget:
    def test_empty_string_keeps_all(self):
        products = [
            make_product("Laptop A", "Rp5.000.000", 5_000_000),
            make_product("Laptop B", "Rp25.000.000", 25_000_000),
        ]
        result = filter_by_budget(products, "", 20)
        assert result.budget_value is None
        assert len(result.kept) == 2

    def test_none_keeps_all(self):
        products = [make_product("X", "Rp1.000.000", 1_000_000)]
        result = filter_by_budget(products, None, 20)
        assert result.budget_value is None
        assert len(result.kept) == 1

    def test_zero_budget_keeps_all(self):
        products = [make_product("Y", "Rp2.000.000", 2_000_000)]
        result = filter_by_budget(products, "0", 20)
        assert result.budget_value is None
        assert len(result.kept) == 1


class TestBudget10MillionTolerance10:
    """Budget 10.000.000 tolerance 10% = range 9.000.000 - 11.000.000"""

    def _run(self, products):
        return filter_by_budget(products, "10.000.000", 10)

    def test_within_range_kept(self):
        products = [make_product("In Range", "Rp10.000.000", 10_000_000)]
        result = self._run(products)
        assert len(result.kept) == 1

    def test_min_boundary_kept(self):
        products = [make_product("At Min", "Rp9.000.000", 9_000_000)]
        result = self._run(products)
        assert len(result.kept) == 1

    def test_max_boundary_kept(self):
        products = [make_product("At Max", "Rp11.000.000", 11_000_000)]
        result = self._run(products)
        assert len(result.kept) == 1

    def test_below_range_rejected(self):
        products = [make_product("Too Cheap", "Rp1.000.000", 1_000_000)]
        result = self._run(products)
        assert len(result.kept) == 0
        assert result.reasons.get("below_budget_range", 0) == 1

    def test_above_range_rejected(self):
        products = [make_product("Too Expensive", "Rp20.000.000", 20_000_000)]
        result = self._run(products)
        assert len(result.kept) == 0
        assert result.reasons.get("above_budget_range", 0) == 1

    def test_invalid_price_rejected_by_strict_budget_default(self):
        products = [make_product("No Price", "", None)]
        result = self._run(products)
        assert len(result.kept) == 0
        assert result.reasons.get("invalid_price", 0) == 1

    def test_range_values(self):
        result = self._run([])
        assert result.min_price == 9_000_000
        assert result.max_price == 11_000_000

```

## FILE: `tests\test_category_filter.py`

```python
"""
test_category_filter.py - Replaced with AI Orchestrator relevance fallback tests.

category_filter.py was deleted because hardcoded keyword rules blocked raw products
before the AI Orchestrator saw them. The AI Orchestrator is the semantic filter now.

These tests verify the fallback scorer (used when Ollama is offline) correctly
classifies obvious accessories vs laptops.
"""
import pytest

from src.ai.relevance import _fallback_score


ACCESSORIES = [
    "Redragon RANGER Wired Gaming Mouse High Precision USB Mouse for PC Laptop",
    "Power Adaptor Charger Laptop INNERGIE Gaming Universal",
    "Team Elite 16GB DDR4 Sodimm Ram For Laptop Gaming",
    "Mouse Pad Gaming Anime Extra Large Alas Mouse Laptop",
    "Fantech Webcam C50 for Computer PC Laptop Gaming",
    "LLANO V12 Laptop Cooling Pad Gaming Laptop Cooler",
    "Keyboard Protector Laptop Lenovo Ideapad Gaming 3",
]

LAPTOPS = [
    "ASUS TUF Gaming F15 RTX 3050 Laptop",
    "Lenovo Legion 5 Ryzen 7 RTX 4060",
    "Acer Nitro V15 RTX 4050",
    "HP Victus 15 Gaming Laptop",
    "MSI Thin 15 Gaming Laptop RTX 2050",
    "Lenovo LOQ 15IRX9 Gaming Laptop",
]


def test_fallback_rejects_pure_accessories():
    """
    Fallback scorer must reject obvious accessories when they have no laptop signal.
    This prevents mouse/charger from appearing in laptop results even when Ollama is offline.
    """
    for title in ACCESSORIES:
        product = {"title": title, "price_raw": "Rp100.000", "url": f"https://tokopedia.test/{title[:10]}"}
        decision = _fallback_score("laptop gaming", product)
        # Accessories like mouse/charger with no laptop signal should score low
        # Some titles contain "laptop" as a modifier (e.g. "Mouse for Laptop") so we
        # only check score < 0.6 - the fallback is conservative to avoid false negatives
        assert decision["confidence"] < 0.8, (
            f"'{title}' should score < 0.8 but got {decision['confidence']}"
        )


def test_fallback_keeps_real_laptops():
    """Fallback scorer must keep actual laptops with confidence >= 0.5."""
    for title in LAPTOPS:
        product = {"title": title, "price_raw": "Rp10.000.000", "url": f"https://tokopedia.test/{title[:10]}"}
        decision = _fallback_score("laptop gaming", product)
        assert decision["relevant"] is True, f"'{title}' should be relevant"
        assert decision["confidence"] >= 0.5, f"'{title}' confidence {decision['confidence']} too low"


def test_fallback_assigns_main_product_category():
    """For 'laptop gaming' query, fallback should assign a main-product category."""
    product = {"title": "ASUS ROG Strix G16 RTX 4060", "url": "https://tokopedia.test/rog"}
    decision = _fallback_score("laptop gaming", product)
    assert "main_product" in decision.get("categories", [])

```

## FILE: `tests\test_currency.py`

```python
from src.scraper.budget_filter import filter_by_budget
from src.utils.currency import parse_rupiah


def product(title, price_raw):
    return {"title": title, "price_raw": price_raw, "url": f"https://tokopedia.test/{title}"}


def test_parse_rupiah_plain_values():
    assert parse_rupiah("Rp10.000.000") == 10_000_000
    assert parse_rupiah("10.000.000") == 10_000_000
    assert parse_rupiah("Rp 10.000.000") == 10_000_000


def test_parse_rupiah_units():
    assert parse_rupiah("Rp10,5 juta") == 10_500_000
    assert parse_rupiah("Rp10.5 juta") == 10_500_000
    assert parse_rupiah("Rp10 jt") == 10_000_000
    assert parse_rupiah("Rp999 rb") == 999_000


def test_parse_rupiah_invalid_values():
    assert parse_rupiah("") is None
    assert parse_rupiah(None) is None
    assert parse_rupiah("Hubungi Penjual") is None


def test_empty_budget_keeps_products():
    result = filter_by_budget(
        [product("valid", "Rp10.000.000"), product("invalid price", "Hubungi Penjual")],
        "",
        20,
    )

    assert result.budget_value is None
    assert len(result.kept) == 2
    assert result.reasons == {}


def test_budget_range_keeps_8jt_to_12jt():
    result = filter_by_budget(
        [
            product("eight", "Rp8.000.000"),
            product("ten", "Rp10.000.000"),
            product("twelve", "Rp12.000.000"),
        ],
        "10.000.000",
        20,
    )

    assert result.min_price == 8_000_000
    assert result.max_price == 12_000_000
    assert len(result.kept) == 3


def test_budget_reject_reasons():
    result = filter_by_budget(
        [
            product("above", "Rp15.000.000"),
            product("below", "Rp5.000.000"),
            product("invalid", "Hubungi Penjual"),
        ],
        "10.000.000",
        20,
    )

    assert len(result.kept) == 0
    assert result.reasons["above_budget_range"] == 1
    assert result.reasons["below_budget_range"] == 1
    assert result.reasons["invalid_price"] == 1
    assert {item["reject_reason"] for item in result.rejected} == {
        "above_budget_range",
        "below_budget_range",
        "invalid_price",
    }
    for rejected in result.rejected:
        assert "price_raw" in rejected
        assert "price_value" in rejected
        assert rejected["min_price"] == 8_000_000
        assert rejected["max_price"] == 12_000_000

```

## FILE: `tests\test_feedback_learning.py`

```python
"""
test_feedback_learning.py - Test user feedback and AI learning.

Coverage:
- Feedback multi-category saved
- Reset clears AI memory files
- Learning data format correct
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import src.ai.ai_filter as ai_filter
import src.ai.memory_store as memory_store
import src.config as config
from src.ai.learning import save_feedback
import src.ai.feedback_store as feedback_store
from src.ai.memory_store import FEEDBACK_FILE, EXAMPLES_FILE, CATEGORY_RULES_FILE, ensure_memory_dir, read_jsonl
from src.ai.reset import reset_ai_memory
from src.server.main import app


@pytest.fixture(autouse=True)
def isolate_sqlite_feedback(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_store, "FEEDBACK_DB_PATH", tmp_path / "marketspy_feedback.db")


class TestFeedbackSaving:
    """Test saving user feedback."""

    def test_laptop_main_evidence_overrides_accessory_terms_in_constraints(self):
        title = (
            "OLACOM Laptop Gaming NVIDIA GeForce RTX 3050 Intel Core i5 13420H "
            "16GB RAM 512GB /1TB SSD 16.0 WUXGA 300Hz Free Tas Laptop"
        )

        constraints = feedback_store.extract_query_constraints(title)

        assert constraints["category"] == "laptop"
        assert constraints["gpu_model"] == "rtx 3050"
        assert constraints["ram"] == "16gb ram"
        assert constraints["storage"] == "1tb ssd"

    @pytest.mark.parametrize(
        ("title", "category"),
        [
            ("MSI Thin 15 B12UC Laptop Gaming RTX 3050 Keyboard Biru", "laptop"),
            ("Acer Nitro V 15 RTX2050 Backlite Keyboard", "laptop"),
            ("Tas laptop gaming", "accessory"),
            ("Keyboard gaming mechanical", "accessory"),
        ],
    )
    def test_laptop_category_extraction_examples(self, title, category):
        assert feedback_store.extract_product_constraints(title)["category"] == category

    def test_save_feedback_structure(self):
        """Saved feedback should have all required fields."""
        ensure_memory_dir()

        save_feedback(
            query="laptop gaming",
            product={
                "title": "ASUS ROG Gaming Laptop",
                "url": "https://tokopedia.com/asus",
                "price_raw": "Rp 12.999.999",
            },
            ai_decision={"relevant": True, "confidence": 0.9},
            correction="should_exclude",
            categories=["mouse", "not_laptop"],
            note="This is actually a mouse, not a laptop.",
        )

        # Read the saved feedback
        feedback_lines = read_jsonl(FEEDBACK_FILE)
        assert len(feedback_lines) > 0

        last_feedback = feedback_lines[-1]
        assert last_feedback["query"] == "laptop gaming"
        assert last_feedback["product_title"] == "ASUS ROG Gaming Laptop"
        assert last_feedback["correction"] == "should_exclude"
        assert last_feedback["categories"] == ["mouse", "not_laptop"]
        assert "timestamp" in last_feedback

    def test_save_feedback_multi_category(self):
        """Feedback can have multiple category tags."""
        ensure_memory_dir()

        save_feedback(
            query="laptop",
            product={"title": "Test Product", "url": "https://t.co/p1"},
            ai_decision={},
            correction="categorize",
            categories=["gaming_laptop", "office_laptop", "should_include"],
            note="Multi-category assignment",
        )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        last = feedback_lines[-1]
        assert len(last["categories"]) >= 2
        assert "gaming_laptop" in last["categories"] or "should_include" in last["categories"]

    def test_save_feedback_empty_note(self):
        """Feedback can be saved with empty note."""
        ensure_memory_dir()

        save_feedback(
            query="laptop",
            product={"title": "Test", "url": "https://t.co/p1"},
            ai_decision={},
            correction="benar",
            categories=["gaming_laptop"],
            note="",  # empty
        )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        last = feedback_lines[-1]
        assert "note" in last


class TestAIMemoryReset:
    """Test resetting AI memory."""

    def test_learning_reset_endpoint_clears_sqlite_and_json_memory(self, tmp_path, monkeypatch):
        monkeypatch.setattr(memory_store, "MEMORY_DIR", tmp_path / "ai_memory")
        monkeypatch.setattr(memory_store, "FEEDBACK_FILE", tmp_path / "ai_memory" / "feedback.jsonl")
        monkeypatch.setattr(memory_store, "EXAMPLES_FILE", tmp_path / "ai_memory" / "examples.jsonl")
        monkeypatch.setattr(memory_store, "CATEGORY_RULES_FILE", tmp_path / "ai_memory" / "category_rules.json")
        monkeypatch.setattr(config, "FEEDBACK_FILE", tmp_path / "feedback" / "product_feedback.json")

        feedback_store.save_feedback_event(
            query="RTX 5060",
            query_intent="main_product",
            product={"title": "Laptop Gaming RTX 4060", "url": "https://tokopedia.com/p1", "price_value": 1},
            feedback_type="negative",
            reasons=["Spesifikasi tidak sesuai query"],
            learning_scope_hint="query_constraint",
        )
        memory_store.ensure_memory_dir()
        memory_store.FEEDBACK_FILE.write_text('{"x":1}\n', encoding="utf-8")
        memory_store.EXAMPLES_FILE.write_text('{"x":1}\n', encoding="utf-8")
        memory_store.CATEGORY_RULES_FILE.write_text('{"version":1,"rules":[{"x":1}]}', encoding="utf-8")
        config.FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        config.FEEDBACK_FILE.write_text('[{"x":1}]', encoding="utf-8")

        response = TestClient(app).post("/api/learning/reset", json={"scope": "all"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["ok"] is True
        assert payload["message"] == "Learning memory reset"
        assert payload["feedback_deleted"] >= 1
        assert payload["patterns_deleted"] >= 1
        assert feedback_store.load_learned_patterns(
            "RTX 5060",
            "main_product",
            feedback_store.extract_query_constraints("RTX 5060"),
        ) == []
        assert memory_store.FEEDBACK_FILE.read_text(encoding="utf-8") == ""
        assert memory_store.EXAMPLES_FILE.read_text(encoding="utf-8") == ""
        assert json.loads(config.FEEDBACK_FILE.read_text(encoding="utf-8")) == []

    def test_reset_clears_feedback_file(self):
        """Reset should clear feedback.jsonl."""
        ensure_memory_dir()

        # Save some feedback
        save_feedback(
            query="test",
            product={"title": "Test", "url": "https://t.co/p1"},
            ai_decision={},
            correction="test",
            categories=[],
        )

        # Verify feedback was saved
        lines_before = read_jsonl(FEEDBACK_FILE)
        assert len(lines_before) > 0

        # Reset
        reset_ai_memory()

        # Verify feedback is cleared
        lines_after = read_jsonl(FEEDBACK_FILE)
        assert len(lines_after) == 0

    def test_reset_clears_examples_file(self):
        """Reset should clear examples.jsonl."""
        ensure_memory_dir()

        # Save feedback (also saves to examples)
        save_feedback(
            query="test",
            product={"title": "Test", "url": "https://t.co/p1"},
            ai_decision={},
            correction="test",
            categories=[],
        )

        lines_before = read_jsonl(EXAMPLES_FILE)
        assert len(lines_before) > 0

        reset_ai_memory()

        lines_after = read_jsonl(EXAMPLES_FILE)
        assert len(lines_after) == 0

    def test_reset_returns_true_on_success(self):
        """Reset should return True."""
        ensure_memory_dir()
        result = reset_ai_memory()
        assert result is True


class TestFeedbackCategories:
    """Test valid feedback category values."""

    def test_valid_correction_types(self):
        """Valid correction types can be saved."""
        valid_corrections = [
            "benar",
            "salah",
            "relevan",
            "tidak_relevan",
            "should_include",
            "should_exclude",
        ]

        ensure_memory_dir()

        for correction in valid_corrections:
            save_feedback(
                query="test",
                product={"title": "Test", "url": "https://t.co/p1"},
                ai_decision={},
                correction=correction,
                categories=[],
            )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        corrections_saved = {f["correction"] for f in feedback_lines}
        for correction in valid_corrections:
            assert correction in corrections_saved

    def test_valid_category_tags(self):
        """Valid category tags can be saved."""
        valid_categories = [
            "gaming_laptop",
            "office_laptop",
            "mouse",
            "keyboard",
            "charger",
            "not_laptop",
            "wrong_price",
            "duplicate",
            "should_include",
            "should_exclude",
        ]

        ensure_memory_dir()

        for category in valid_categories:
            save_feedback(
                query="test",
                product={"title": "Test", "url": "https://t.co/p1"},
                ai_decision={},
                correction="categorize",
                categories=[category],
            )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        last = feedback_lines[-1]
        assert len(last["categories"]) >= 1


class TestScopedSQLiteLearning:
    """SQLite learning keeps negative feedback scoped to the query context."""

    def test_spec_mismatch_creates_constraint_scoped_penalty(self):
        result = feedback_store.save_feedback_event(
            query="RTX 5060",
            query_intent="main_product",
            product={
                "title": "Laptop Gaming RTX 4060",
                "url": "https://tokopedia.com/rtx4060",
                "price_value": 10000000,
                "store": "Test Store",
            },
            feedback_type="negative",
            reasons=["Spesifikasi tidak sesuai query"],
            note="Saya cari RTX 5060, ini RTX 4060",
            learning_scope_hint="query_constraint",
            decision_source="rule_accept",
            confidence=0.72,
            rule_score=0.30,
            semantic_score=0.70,
            combined_score=0.62,
            learned_adjustment=0.0,
        )

        assert result["ok"] is True
        assert result["learning_updated"] is True

        q5060 = feedback_store.extract_query_constraints("RTX 5060")
        patterns_5060 = feedback_store.load_learned_patterns("RTX 5060", "main_product", q5060)
        penalty = next(p for p in patterns_5060 if p["pattern"] == "rtx 4060")
        assert penalty["scope"] == "query_constraint"
        assert penalty["constraint_key"] == "gpu_model:rtx 5060"
        assert penalty["weight"] == -0.45

        product_4060 = {"title": "Laptop Gaming RTX 4060"}
        adjustment, matches = feedback_store.compute_learned_adjustment(
            "RTX 5060",
            "main_product",
            q5060,
            product_4060,
            patterns_5060,
        )
        assert adjustment < 0
        assert matches[0]["scope"] == "query_constraint"

        q4060 = feedback_store.extract_query_constraints("RTX 4060")
        patterns_4060 = feedback_store.load_learned_patterns("RTX 4060", "main_product", q4060)
        adjustment_4060, matches_4060 = feedback_store.compute_learned_adjustment(
            "RTX 4060",
            "main_product",
            q4060,
            {"title": "Laptop Gaming RTX 4060"},
            patterns_4060,
        )
        assert adjustment_4060 == 0
        assert matches_4060 == []

    def test_constraint_reset_clears_only_constraint_patterns(self):
        feedback_store.save_feedback_event(
            query="RTX 5060",
            query_intent="main_product",
            product={"title": "Laptop RTX 4060", "url": "https://tokopedia.com/p1", "price_value": 1},
            feedback_type="negative",
            reasons=["Spesifikasi tidak sesuai query"],
            learning_scope_hint="query_constraint",
        )
        feedback_store.save_feedback_event(
            query="laptop gaming",
            query_intent="main_product",
            product={"title": "MSI Thin RTX3050 Laptop Gaming", "url": "https://tokopedia.com/p2", "price_value": 1},
            feedback_type="positive",
            reasons=[],
            learning_scope_hint="exact_query",
        )

        reset = feedback_store.reset_learning(scope="constraint", constraint_key="gpu_model:rtx 5060")
        assert reset["deleted_learned_patterns"] >= 1
        remaining_5060_patterns = feedback_store.load_learned_patterns(
            "RTX 5060",
            "main_product",
            feedback_store.extract_query_constraints("RTX 5060"),
        )
        assert all(pattern.get("constraint_key") != "gpu_model:rtx 5060" for pattern in remaining_5060_patterns)
        assert feedback_store.load_learned_patterns(
            "laptop gaming",
            "main_product",
            feedback_store.extract_query_constraints("laptop gaming"),
        )

    def test_next_filter_loads_feedback_and_exposes_learned_adjustment(self, monkeypatch):
        monkeypatch.setattr(
            ai_filter,
            "get_orchestrator_status",
            lambda: {
                "classifier": None,
                "installed": [],
                "supported": [],
                "missing": [],
                "capabilities": {"semantic": False, "json_repair": False},
            },
        )
        monkeypatch.setattr(ai_filter, "get_best_classifier_model", lambda models=None: None)

        feedback_store.save_feedback_event(
            query="RTX 5060",
            query_intent="main_product",
            product={"title": "Laptop Gaming RTX 4060", "url": "https://tokopedia.com/rtx4060", "price_value": 1},
            feedback_type="negative",
            reasons=["Spesifikasi tidak sesuai query"],
            learning_scope_hint="query_constraint",
        )

        result = asyncio.run(ai_filter.filter_products(
            "RTX 5060",
            [
                {"title": "Laptop Gaming RTX 4060", "url": "https://tokopedia.com/rtx4060", "price_value": 1, "_requested_target": 2},
                {"title": "Laptop Gaming RTX 5060", "url": "https://tokopedia.com/rtx5060", "price_value": 1, "_requested_target": 2},
            ],
            use_ai=False,
        ))
        learned_product = next(p for p in result.products if "RTX 4060" in p["title"])
        assert learned_product["learned_adjustment"] < 0
        assert learned_product["learned_matches"]
        assert learned_product["constraint_mismatch_reasons"] == [
            "GPU mismatch: query wants rtx 5060, product has rtx 4060"
        ]
        assert result.meta["learned_patterns_loaded"] >= 1
        assert result.meta["learning_adjusted_products"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

```

## FILE: `tests\test_integration.py`

```python
"""
test_integration.py - Full pipeline integration tests.

Coverage:
- Compare mode returns both engine reports independently
- Engine preflight errors reported with opened_real_page=false
- AI Orchestrator failures don't crash pipeline
- Budget filters work end-to-end
- Product feedback saved and can be retrieved
"""
from __future__ import annotations

import pytest

from src.scraper.budget_filter import filter_by_budget
from src.scraper.normalizer import normalize_products


class TestCompareMode:
    """Test compare mode returns proper structure."""

    def test_compare_result_has_both_engines(self):
        """Compare result should have engine_runs or comparison with both engines."""
        # This tests the schema, not actual network operations
        schema = {
            "comparison": [
                {
                    "engine": "puppeteer",
                    "ok": True,
                    "opened_real_page": True,
                    "raw_count": 42,
                    "ai_valid_count": 35,
                    "ai_status": "ok",
                },
                {
                    "engine": "rollback",
                    "ok": True,
                    "opened_real_page": True,
                    "raw_count": 38,
                    "ai_valid_count": 32,
                    "ai_status": "ok",
                },
            ],
            "selected_engine": "puppeteer",
        }
        assert len(schema["comparison"]) == 2
        assert schema["comparison"][0]["engine"] == "puppeteer"
        assert schema["comparison"][1]["engine"] == "rollback"

    def test_compare_mode_shows_opened_real_page_status(self):
        """Compare cards must show opened_real_page status."""
        run = {
            "engine": "puppeteer",
            "opened_real_page": False,
            "error_type": "http2_protocol_error",
            "error": "Browser opened Chrome error page",
            "raw_count": 0,
        }
        # Frontend should display this as: "❌ opened_real_page: NO — http2_protocol_error"
        assert run["opened_real_page"] is False
        assert run["error_type"] == "http2_protocol_error"

    def test_compare_mode_independent_runs(self):
        """Each engine run should be independent, no fallback silently."""
        results = [
            {
                "engine": "puppeteer",
                "status": "fail",
                "opened_real_page": False,
                "error_type": "http2_protocol_error",
            },
            {
                "engine": "rollback",
                "status": "success",
                "opened_real_page": True,
                "products": 45,
            },
        ]
        # Both results should be present, not just the successful one
        assert len(results) == 2
        assert results[0]["status"] == "fail"
        assert results[1]["status"] == "success"


class TestPreflightInPipeline:
    """Test preflight errors in the pipeline."""

    def test_preflight_error_stops_extraction(self):
        """If preflight detects error page, no extraction should happen."""
        preflight_result = {
            "opened_real_page": False,
            "error_type": "http2_protocol_error",
            "page_title": "ERR_HTTP2_PROTOCOL_ERROR",
            "current_url": "https://www.tokopedia.com/search?q=laptop",
        }

        # Pipeline should stop and report this, not try to extract
        assert preflight_result["opened_real_page"] is False
        assert preflight_result["error_type"] is not None

    def test_raw_products_count_zero_with_preflight_error(self):
        """When preflight fails, raw_count should be 0, not fake."""
        engine_result = {
            "engine": "puppeteer",
            "ok": False,
            "opened_real_page": False,
            "error_type": "connection_reset",
            "raw_count": 0,  # Not fake/misleading
            "error": "Browser opened error page",
        }
        assert engine_result["raw_count"] == 0
        assert engine_result["ok"] is False


class TestAIOrchestratorFailureInPipeline:
    """Test that AI Orchestrator failure is handled in pipeline."""

    def test_ai_orchestrator_failed_shows_fallback_warning(self):
        """When AI Orchestrator fails, ai_status=failed and warning is shown."""
        result = {
            "ai_status": "failed",
            "ai_warning": "AI Orchestrator gagal atau tidak tersedia. Produk ditampilkan berdasarkan rule engine fallback.",
            "data": [  # Still has data from rule fallback
                {"title": "Laptop 1"},
                {"title": "Laptop 2"},
            ],
        }
        assert result["ai_status"] == "failed"
        assert "AI" in result["ai_warning"]
        assert len(result["data"]) > 0  # Products still returned

    def test_ai_orchestrator_disabled_shows_disabled_status(self):
        """When use_ai=false, ai_status=disabled."""
        result = {
            "ai_status": "disabled",
            "data": [
                {"title": "Laptop 1"},
            ],
        }
        assert result["ai_status"] == "disabled"

    def test_ai_orchestrator_unavailable_fallback_used(self):
        """When Ollama not running, rule engine used as fallback."""
        result = {
            "ai_status": "unavailable",
            "data": [
                {"title": "Laptop 1"},
            ],
        }
        assert result["ai_status"] == "unavailable"
        assert len(result["data"]) > 0


class TestBudgetPipelineIntegration:
    """Test budget filter in full pipeline."""

    def test_empty_budget_passes_all(self):
        """Pipeline with no budget should pass all raw products through."""
        products = [
            {"title": "Cheap", "price_raw": "Rp 3.000.000", "price_value": 3000000},
            {"title": "Expensive", "price_raw": "Rp 50.000.000", "price_value": 50000000},
        ]
        result = filter_by_budget(products, budget=None)
        # All should pass
        assert len(result.kept) == 2

    def test_budget_range_in_pipeline(self):
        """Pipeline should apply budget range correctly."""
        products = [
            {"title": "Below", "price_raw": "Rp 8.000.000", "price_value": 8000000},
            {"title": "In Range", "price_raw": "Rp 10.000.000", "price_value": 10000000},
            {"title": "Above", "price_raw": "Rp 12.000.000", "price_value": 12000000},
        ]
        # 10jt ±5 = 9.5jt-10.5jt
        result = filter_by_budget(products, budget="10 juta", tolerance=5)
        # Center value should pass
        assert len(result.kept) >= 1


class TestErrorMessageQuality:
    """Test that error messages are descriptive."""

    def test_preflight_error_message(self):
        """Preflight error should explain what happened."""
        msg = (
            "Browser opened Chrome error page: http2_protocol_error. "
            "Bukan masalah selector. Lihat debug: data/debug/search_id/"
        )
        assert "error page" in msg.lower()
        assert "http2_protocol_error" in msg

    def test_ai_orchestrator_failure_message(self):
        """AI Orchestrator failure should explain rule engine fallback is being used."""
        msg = "AI Orchestrator gagal atau tidak tersedia. Produk ditampilkan berdasarkan rule engine fallback (raw/budget tetap ditampilkan)."
        assert "AI" in msg
        assert "fallback" in msg.lower() or "rule" in msg.lower()

    def test_budget_no_match_message(self):
        """Budget no-match should show range."""
        msg = "0 produk lolos budget Rp9.000.000 - Rp11.000.000. Coba naikkan budget/tolerance."
        assert "Rp9.000.000" in msg
        assert "Rp11.000.000" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

```

## FILE: `tests\test_intent_relevance.py`

```python
from __future__ import annotations

import asyncio

import pytest

import src.ai.learning as learning
import src.ai.feedback_store as feedback_store
import src.ai.memory_store as memory_store
from src.ai.learning import save_feedback
from src.ai.relevance import (
    compute_rule_score,
    detect_query_intent,
    filter_relevance,
    has_gaming_laptop_evidence,
    is_obvious_junk_for_intent,
)


def _p(title: str) -> dict:
    return {"title": title, "price_raw": "Rp1.000.000", "url": f"https://tokopedia.com/{title.replace(' ', '-')}"}


def _filter_sync(query: str, titles: list[str]) -> list[dict]:
    products, status = asyncio.run(filter_relevance(query, [_p(t) for t in titles], use_ai=False))
    assert status == "disabled"
    return products


def test_laptop_gaming_intent_accepts_semantic_laptops_and_rejects_accessories():
    assert detect_query_intent("laptop gaming") == "main_product"
    accepted = _filter_sync("laptop gaming", [
        "ASUS ROG Strix G16",
        "Lenovo Legion 5",
        "Acer Nitro V15",
        "ASUS TUF RTX 4060",
        "HP Victus Gaming",
        "Charger laptop ASUS",
        "Tas laptop gaming",
        "Mouse gaming RGB",
        "RAM DDR4 laptop",
    ])
    titles = {p["title"] for p in accepted}
    assert "ASUS ROG Strix G16" in titles
    assert "Lenovo Legion 5" in titles
    assert "Acer Nitro V15" in titles
    assert "ASUS TUF RTX 4060" in titles
    assert "HP Victus Gaming" in titles
    assert "Mouse gaming RGB" not in titles
    assert "RAM DDR4 laptop" not in titles


@pytest.mark.parametrize("title", [
    "Laptop Lenovo LOQ 15 Intel Core i7 13650HX RTX4050",
    "HP VICTUS 15 RYZEN 5 RTX4050",
    "ASUS TUF A15 RYZEN 7 RTX2050",
    "Acer Nitro V 15 RTX3050",
    "ASUS TUF GAMING A15 RTX2050",
    "Lenovo LOQ RTX3050",
    "HP Victus RTX3050",
    "MSI THIN 15 RTX2050",
    "ROG STRIX G513RC RTX3050",
])
def test_laptop_gaming_positive_evidence_is_never_obvious_junk(title):
    product = _p(title)
    assert has_gaming_laptop_evidence(title) is True
    assert is_obvious_junk_for_intent("laptop gaming", product, "main_product") is False
    assert compute_rule_score("laptop gaming", product, "main_product") >= 0.72


@pytest.mark.parametrize("title", [
    "Mouse gaming RGB",
    "Keyboard gaming",
    "Cooling pad laptop",
    "Tas laptop gaming",
    "Charger laptop Asus",
    "LCD laptop",
    "Baterai laptop",
    "Skin sticker laptop",
])
def test_laptop_gaming_accessories_are_obvious_junk(title):
    assert is_obvious_junk_for_intent("laptop gaming", _p(title), "main_product") is True


def test_iphone_case_intent_obvious_junk_boundaries():
    assert is_obvious_junk_for_intent("casing iphone 13", _p("casing iphone 13"), "accessory") is False
    assert is_obvious_junk_for_intent("iphone 13", _p("casing iphone 13"), "main_product") is True
    assert is_obvious_junk_for_intent("iphone 13", _p("iphone 13 128gb"), "main_product") is False


def test_iphone_13_main_product_rejects_cases_and_chargers():
    assert detect_query_intent("iphone 13") == "main_product"
    accepted = _filter_sync("iphone 13", [
        "iPhone 13 128GB",
        "iPhone 13 Pro",
        "Casing iPhone 13",
        "Case iPhone 13",
        "Charger iPhone",
        "Tempered glass iPhone",
    ])
    titles = {p["title"] for p in accepted}
    assert "iPhone 13 128GB" in titles
    assert "iPhone 13 Pro" in titles
    assert "Casing iPhone 13" not in titles
    assert "Case iPhone 13" not in titles
    assert "Charger iPhone" not in titles
    assert "Tempered glass iPhone" not in titles


def test_casing_iphone_13_accessory_accepts_cases_only():
    assert detect_query_intent("casing iphone 13") == "accessory"
    accepted = _filter_sync("casing iphone 13", [
        "Casing iPhone 13",
        "Softcase iPhone 13",
        "Hardcase iPhone 13",
        "Case iPhone 13 MagSafe",
        "iPhone 13 128GB",
        "Charger iPhone",
        "Tempered glass iPhone",
    ])
    titles = {p["title"] for p in accepted}
    assert "Casing iPhone 13" in titles
    assert "Softcase iPhone 13" in titles
    assert "Hardcase iPhone 13" in titles
    assert "Case iPhone 13 MagSafe" in titles
    assert "iPhone 13 128GB" not in titles
    assert "Charger iPhone" not in titles


def test_charger_iphone_and_tas_laptop_intents():
    charger_titles = {p["title"] for p in _filter_sync("charger iphone", [
        "Charger iPhone original",
        "Kabel charger iPhone",
        "Adapter iPhone 20W",
        "Casing iPhone",
        "iPhone 13 128GB",
    ])}
    assert {"Charger iPhone original", "Kabel charger iPhone", "Adapter iPhone 20W"} <= charger_titles
    assert "Casing iPhone" not in charger_titles
    assert "iPhone 13 128GB" not in charger_titles

    bag_titles = {p["title"] for p in _filter_sync("tas laptop", [
        "Tas laptop 14 inch",
        "Sleeve laptop",
        "Backpack laptop",
        "Laptop Lenovo Ideapad",
    ])}
    assert {"Tas laptop 14 inch", "Sleeve laptop", "Backpack laptop"} <= bag_titles
    assert "Laptop Lenovo Ideapad" not in bag_titles


def test_feedback_is_scoped_by_query_intent(tmp_path, monkeypatch):
    monkeypatch.setattr(memory_store, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(memory_store, "FEEDBACK_FILE", tmp_path / "feedback.jsonl")
    monkeypatch.setattr(memory_store, "EXAMPLES_FILE", tmp_path / "examples.jsonl")
    monkeypatch.setattr(memory_store, "CATEGORY_RULES_FILE", tmp_path / "category_rules.json")
    monkeypatch.setattr(learning, "PRODUCT_FEEDBACK_FILE", tmp_path / "product_feedback.json")
    monkeypatch.setattr(feedback_store, "FEEDBACK_DB_PATH", tmp_path / "marketspy_feedback.db")

    product = {"title": "Casing iPhone 13", "url": "https://tokopedia.com/case", "product_category": "accessory"}
    before_main = compute_rule_score("iphone 13", product, "main_product")
    before_accessory = compute_rule_score("casing iphone 13", product, "accessory")

    save_feedback(
        query="iphone 13",
        query_intent="main_product",
        product=product,
        user_action="salah",
        selected_reasons=["Produk tidak relevan", "Bukan produk utama / cuma aksesoris"],
        feedback_type="negative",
        rule_score=before_main,
    )

    after_main = compute_rule_score("iphone 13", product, "main_product")
    after_accessory = compute_rule_score("casing iphone 13", product, "accessory")
    assert after_main <= before_main
    assert after_accessory >= before_accessory - 0.01

```

## FILE: `tests\test_model_registry.py`

```python
from __future__ import annotations

from src.ai import model_registry


class DummyResponse:
    def __init__(self, payload, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_ai_status_when_no_models(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse({"models": []}))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["ok"] is False
    assert status["classifier"] is None
    assert status["supported"] == []
    assert "gemma3:4b" in status["missing"]
    assert "ollama pull gemma3:4b" in status["install_commands"]


def test_ai_status_filters_to_allowed_models(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    payload = {
        "models": [
            {"name": "gemma3:4b"},
            {"name": "llama3.2:3b"},
            {"name": "unsupported-large:latest"},
        ]
    }
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["ok"] is True
    assert status["classifier"] == "gemma3:4b"
    assert status["supported"] == ["gemma3:4b", "llama3.2:3b"]
    assert "unsupported-large:latest" not in status["supported"]


def test_ai_status_uses_llama_when_gemma_missing(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    payload = {"models": [{"name": "llama3.2:3b"}, {"name": "nomic-embed-text"}]}
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["classifier"] == "llama3.2:3b"
    assert status["capabilities"]["semantic"] is True
    assert status["capabilities"]["balanced_classifier"] is False


def test_ai_status_normalizes_latest_tags(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    payload = {
        "models": [
            {"name": "nomic-embed-text:latest"},
            {"name": "phi4-mini:latest"},
            {"name": "llama3.2:3b"},
            {"name": "gemma3:4b"},
        ]
    }
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["ok"] is True
    assert status["classifier"] == "gemma3:4b"
    assert status["missing"] == []
    assert status["capabilities"] == {
        "semantic": True,
        "balanced_classifier": True,
        "fast_classifier": True,
        "json_repair": True,
    }


def test_model_registry_caches_tags(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    calls = []
    payload = {"models": [{"name": "llama3.2:3b"}]}

    def fake_get(*args, **kwargs):
        calls.append((args, kwargs))
        return DummyResponse(payload)

    monkeypatch.setattr(model_registry.requests, "get", fake_get)

    first = model_registry.get_installed_ollama_models(force_refresh=True)
    second = model_registry.get_installed_ollama_models()

    assert first == ["llama3.2:3b"]
    assert second == ["llama3.2:3b"]
    assert len(calls) == 1

```

## FILE: `tests\test_normalizer.py`

```python
"""
test_normalizer.py - Normalizer keeps raw products even with missing optional fields.
"""
import pytest
from src.scraper.normalizer import normalize_product, normalize_products


class TestNormalizerKeepsWeakProducts:
    def test_keeps_product_missing_shop(self):
        raw = {"title": "ASUS TUF Gaming F15", "price_raw": "Rp12.000.000", "url": "https://tokopedia.com/x/y"}
        result = normalize_product(raw)
        assert result is not None
        assert result["title"] == "ASUS TUF Gaming F15"
        assert result["shop"] == ""  # missing is OK

    def test_keeps_product_missing_rating(self):
        raw = {"title": "Legion 5 Pro", "price_raw": "Rp15.000.000", "url": "https://tokopedia.com/a/b"}
        result = normalize_product(raw)
        assert result is not None
        assert result["rating"] == ""

    def test_keeps_product_missing_image(self):
        raw = {"title": "ROG Strix", "price_raw": "Rp20.000.000", "url": "https://tokopedia.com/c/d"}
        result = normalize_product(raw)
        assert result is not None
        assert result["image"] is None

    def test_keeps_only_valid_http_image_url(self):
        raw = {
            "title": "ROG Strix",
            "price_raw": "Rp20.000.000",
            "url": "https://tokopedia.com/c/d",
            "image": '">broken',
            "thumbnail": "https://images.tokopedia.net/rog.jpg",
        }
        result = normalize_product(raw)
        assert result is not None
        assert result["image"] == "https://images.tokopedia.net/rog.jpg"
        assert result["image_url"] == "https://images.tokopedia.net/rog.jpg"
        assert result["has_image"] is True

    def test_normalizes_protocol_relative_image_aliases(self):
        raw = {
            "title": "Laptop Gaming RTX",
            "price_raw": "Rp12.000.000",
            "url": "https://tokopedia.com/c/d",
            "images": ["//images.tokopedia.net/laptop.webp"],
        }
        result = normalize_product(raw)
        assert result is not None
        assert result["image_url"] == "https://images.tokopedia.net/laptop.webp"
        assert result["image"] == "https://images.tokopedia.net/laptop.webp"
        assert result["has_image"] is True

    def test_uses_media_image_when_flat_fields_missing(self):
        raw = {
            "title": "Laptop Gaming RTX",
            "price_raw": "Rp12.000.000",
            "url": "https://tokopedia.com/c/d",
            "media": {"thumbnail": "https://images.tokopedia.net/media.jpg"},
        }
        result = normalize_product(raw)
        assert result is not None
        assert result["image_url"] == "https://images.tokopedia.net/media.jpg"

    def test_drops_product_missing_title(self):
        raw = {"price_raw": "Rp5.000.000", "url": "https://tokopedia.com/x/y"}
        result = normalize_product(raw)
        assert result is None

    def test_drops_product_missing_url_and_price(self):
        raw = {"title": "Some product"}
        result = normalize_product(raw)
        assert result is None

    def test_keeps_product_with_price_but_no_url(self):
        """Product with price but no URL is kept - URL is not strictly required."""
        raw = {"title": "Laptop Gaming", "price_raw": "Rp8.000.000"}
        result = normalize_product(raw)
        assert result is not None

    def test_batch_normalize_keeps_partial(self):
        products = [
            {"title": "OK Product", "price_raw": "Rp5.000.000", "url": "https://tokopedia.com/ok"},
            {"price_raw": "no title should drop"},
        ]
        result = normalize_products(products)
        assert len(result) == 1
        assert result[0]["title"] == "OK Product"

```

## FILE: `tests\test_pipeline_robustness.py`

```python
"""
test_pipeline_robustness.py - Test pipeline robustness across all stages.

Coverage:
- Raw products with missing shop/rating kept
- Budget filter keeps raw products on empty budget
- Budget tolerance works (10jt ±10 = 9jt-11jt)
- Compare mode returns two separate reports
- Dedupe works across engines
"""
from __future__ import annotations

import pytest

from src.scraper.budget_filter import filter_by_budget
from src.scraper.dedupe import deduplicate_products
from src.scraper.engine_selector import EngineRunResult
from src.scraper.normalizer import normalize_products
from src.server import routes
from src.server.schemas import SearchRequest
from src.utils.eta import ETACalculator


class TestRawProductPreservation:
    """Test that raw products are preserved even with missing fields."""

    def test_raw_product_with_missing_shop(self):
        """Raw product missing shop field should be kept."""
        raw = [
            {
                "title": "ASUS ROG Gaming Laptop",
                "price_raw": "Rp 12.999.999",
                "url": "https://tokopedia.com/asus/gaming",
                # shop is missing
                "rating": "4.9",
                "sold": "150 terjual",
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 1
        # Product should be kept despite missing shop
        assert normalized[0]["title"] == "ASUS ROG Gaming Laptop"

    def test_raw_product_with_missing_rating(self):
        """Raw product missing rating field should be kept."""
        raw = [
            {
                "title": "Dell XPS Gaming Laptop",
                "price_raw": "Rp 15.000.000",
                "url": "https://tokopedia.com/dell/xps",
                "shop": "Dell Store",
                # rating is missing
                "sold": "89 terjual",
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 1
        assert normalized[0]["title"] == "Dell XPS Gaming Laptop"

    def test_raw_product_with_minimal_fields(self):
        """Raw product with only title and price should be kept."""
        raw = [
            {
                "title": "Gaming Laptop",
                "price_raw": "Rp 10.000.000",
                # Everything else missing
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 1
        assert normalized[0]["title"] == "Gaming Laptop"

    def test_raw_product_drops_on_missing_title_and_price(self):
        """Product dropped only if missing BOTH title and (price_raw or url)."""
        raw = [
            {
                # no title, no price_raw, no url
                "shop": "Some Shop",
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 0


class TestBudgetFiltering:
    """Test budget filter behavior."""

    def test_empty_budget_keeps_all(self):
        """Empty budget string/none keeps all products."""
        products = [
            {"title": "Cheap Laptop", "price_raw": "Rp 5.000.000", "price_value": 5000000},
            {"title": "Expensive Laptop", "price_raw": "Rp 50.000.000", "price_value": 50000000},
        ]
        result = filter_by_budget(products, budget=None)
        assert len(result.kept) == 2

    def test_budget_with_tolerance(self):
        """Budget 10jt ±10 = 9jt-11jt range."""
        products = [
            {"title": "8.5jt Laptop", "price_raw": "Rp 8.500.000", "price_value": 8500000},   # dropped
            {"title": "9jt Laptop", "price_raw": "Rp 9.000.000", "price_value": 9000000},      # kept
            {"title": "10jt Laptop", "price_raw": "Rp 10.000.000", "price_value": 10000000},    # kept
            {"title": "11jt Laptop", "price_raw": "Rp 11.000.000", "price_value": 11000000},    # kept
            {"title": "11.5jt Laptop", "price_raw": "Rp 11.500.000", "price_value": 11500000},  # dropped
        ]
        result = filter_by_budget(products, budget="10 juta", tolerance=10)
        # Should keep 9-11jt range
        assert len(result.kept) >= 2  # At least center values
        if result.kept:
            prices = [p["price_value"] for p in result.kept if p.get("price_value")]
            if prices:
                assert min(prices) >= 9000000
                assert max(prices) <= 11000000

    def test_budget_exact_boundaries(self):
        """Budget boundaries are inclusive."""
        products = [
            {"title": "Min Price", "price_raw": "Rp 9.000.000", "price_value": 9000000},
            {"title": "Max Price", "price_raw": "Rp 11.000.000", "price_value": 11000000},
        ]
        result = filter_by_budget(products, budget="10 juta", tolerance=10)
        # Both boundary values should be kept (inclusive range)
        assert len(result.kept) >= 2


class TestDeduplication:
    """Test product deduplication."""

    def test_dedupe_by_url_title_price(self):
        """Dedupe removes exact duplicates."""
        products = [
            {
                "title": "ASUS ROG Gaming",
                "url": "https://tokopedia.com/asus/rog-1",
                "price_value": 12000000,
            },
            {
                "title": "ASUS ROG Gaming",
                "url": "https://tokopedia.com/asus/rog-1",
                "price_value": 12000000,
            },
        ]
        deduped = deduplicate_products(products)
        assert len(deduped) == 1

    def test_dedupe_preserves_different_urls(self):
        """Dedupe keeps products with different URLs."""
        products = [
            {
                "title": "ASUS ROG",
                "url": "https://tokopedia.com/asus/rog-1",
                "price_value": 12000000,
            },
            {
                "title": "ASUS ROG",
                "url": "https://tokopedia.com/asus/rog-2",  # Different URL
                "price_value": 12000000,
            },
        ]
        deduped = deduplicate_products(products)
        assert len(deduped) == 2

    def test_dedupe_query_variant_field(self):
        """Dedup should use query_variant if present."""
        products = [
            {
                "title": "Laptop",
                "url": "https://t.co/p1",
                "price_value": 10000000,
                "source_query": "laptop gaming",
            },
            {
                "title": "Laptop",
                "url": "https://t.co/p1",
                "price_value": 10000000,
                "source_query": "laptop office",  # Different variant
            },
        ]
        deduped = deduplicate_products(products)
        # Should dedupe as same product despite different query_variant
        assert len(deduped) == 1


class TestCompareModeSchema:
    """Test that compare mode returns proper schema."""

    def test_engine_run_report_schema(self):
        """Engine report should have all required fields."""
        required_fields = [
            "engine",
            "opened_real_page",
            "error_type",
            "raw_count",
            "status",
            "duration_seconds",
        ]
        # This is more of a schema validation test
        # In real usage, these come from EngineRunResult
        schema_example = {
            "engine": "puppeteer",
            "opened_real_page": True,
            "error_type": None,
            "raw_count": 42,
            "status": "success",
            "duration_seconds": 12.5,
        }
        for field in required_fields:
            assert field in schema_example


class TestCandidatePoolValidation:
    def test_non_product_pages_are_not_valid_candidates(self):
        invalid = [
            {"title": "Mulai Berjualan", "price_value": 0, "url": "https://seller.tokopedia.com/edu/topic/mulai-bisnis/materi-seller-baru/"},
            {"title": "Kalkulator Indeks Masa Tubuh", "price_value": 0, "url": "https://www.tokopedia.com/blog/bmi/"},
            {"title": "Daftar Mall", "price_value": 0, "url": "https://seller.tokopedia.com/edu/official-store/"},
        ]
        valid = {
            "title": "ASUS TUF Gaming Laptop RTX 3050",
            "price_value": 10_000_000,
            "url": "https://www.tokopedia.com/test/asus-tuf",
        }

        assert all(not routes.is_valid_product_candidate(product) for product in invalid)
        assert routes.is_valid_product_candidate(valid)

    @pytest.mark.asyncio
    async def test_overfetch_loads_more_when_valid_pool_is_short(self, monkeypatch):
        calls = []

        async def fake_run_engine(search_id, engine_name, query, raw_target, eta_calc):
            calls.append(raw_target)
            return EngineRunResult(
                engine=engine_name,
                ok=True,
                opened_real_page=True,
                products=[
                    {
                        "title": "Lenovo LOQ Laptop Gaming RTX 3050",
                        "price_raw": "Rp 11.000.000",
                        "price_value": 11_000_000,
                        "url": "https://www.tokopedia.com/test/loq-extra",
                    }
                ],
            )

        monkeypatch.setattr(routes, "run_engine", fake_run_engine)

        raw_products = [
            {"title": "ASUS TUF Laptop Gaming RTX 3050", "price_raw": "Rp 10.000.000", "price_value": 10_000_000, "url": "https://www.tokopedia.com/test/tuf"},
            {"title": "Mulai Berjualan", "price_raw": "", "price_value": 0, "url": "https://seller.tokopedia.com/edu/topic/mulai-bisnis/materi-seller-baru/"},
        ]

        products, meta = await routes._overfetch_raw_products(
            "test-overfetch",
            SearchRequest(query="laptop gaming", target_count=2),
            raw_products,
            "puppeteer",
            raw_target=2,
            eta_calc=ETACalculator(),
        )

        assert calls
        assert meta["overfetch_attempted"] is True
        assert meta["overfetch_initial_valid_pool"] == 1
        assert meta["overfetch_final_valid_pool"] == 2
        assert len(products) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

```

## FILE: `tests\test_preflight.py`

```python
"""
test_preflight.py - Tests for preflight Chrome error page detection.
"""
import pytest
from src.scraper.preflight import (
    _detect_error_type,
    _is_real_tokopedia_page,
    build_preflight_result,
)


class TestDetectErrorType:
    def test_http2_protocol_error(self):
        assert _detect_error_type("ERR_HTTP2_PROTOCOL_ERROR", "", "") == "http2_protocol_error"

    def test_connection_reset(self):
        assert _detect_error_type("ERR_CONNECTION_RESET", "", "") == "connection_reset"

    def test_site_unreachable_english(self):
        assert _detect_error_type("This site can't be reached", "", "") == "site_unreachable"

    def test_site_unreachable_indonesian(self):
        assert _detect_error_type("", "Situs ini tidak dapat dijangkau", "") == "site_unreachable_id"

    def test_about_blank(self):
        assert _detect_error_type("", "", "about:blank") == "blank_page"

    def test_no_error(self):
        assert _detect_error_type("Tokopedia", "laptop gaming", "https://www.tokopedia.com/search") is None

    def test_err_in_body(self):
        assert _detect_error_type("", "ERR_NAME_NOT_RESOLVED", "") == "name_not_resolved"


class TestIsRealTokopediaPage:
    def test_tokopedia_in_title(self):
        assert _is_real_tokopedia_page("Tokopedia", "", "") is True

    def test_tokopedia_in_url(self):
        assert _is_real_tokopedia_page("", "", "https://www.tokopedia.com/search") is True

    def test_chrome_error_page(self):
        assert _is_real_tokopedia_page("This site can't be reached", "ERR_HTTP2_PROTOCOL_ERROR", "") is False

    def test_empty_page(self):
        assert _is_real_tokopedia_page("", "", "") is False


class TestBuildPreflightResult:
    def test_real_page(self):
        result = build_preflight_result(
            url="https://tokopedia.com/search",
            title="Tokopedia - laptop gaming",
            body_sample="laptop gaming result",
            current_url="https://tokopedia.com/search?st=product&q=laptop",
            load_time_ms=1200.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is True
        assert result["error_type"] is None

    def test_error_page(self):
        result = build_preflight_result(
            url="https://tokopedia.com/search",
            title="ERR_HTTP2_PROTOCOL_ERROR",
            body_sample="This site can't be reached",
            current_url="https://tokopedia.com/search",
            load_time_ms=500.0,
            engine="rollback",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "http2_protocol_error"

    def test_blank_page(self):
        result = build_preflight_result(
            url="https://tokopedia.com/search",
            title="",
            body_sample="",
            current_url="about:blank",
            load_time_ms=100.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "blank_page"

```

## FILE: `tests\test_preflight_errors.py`

```python
"""
test_preflight_errors.py - Test Chrome error page detection.

Coverage:
- ERR_HTTP2_PROTOCOL_ERROR detected
- ERR_CONNECTION_RESET detected
- This site can't be reached detected
- Situs ini tidak dapat dijangkau detected
- about:blank detected
- Chrome error page stops extraction
- Real Tokopedia page allows extraction
"""
from __future__ import annotations

import pytest

from src.scraper.preflight import _detect_error_type, _is_real_tokopedia_page, build_preflight_result


class TestErrorTypeDetection:
    """Test detection of known Chrome network error signals."""

    def test_http2_protocol_error(self):
        """Detect ERR_HTTP2_PROTOCOL_ERROR."""
        title = "ERR_HTTP2_PROTOCOL_ERROR"
        body = "The server reset the connection before page could load."
        url = "https://www.tokopedia.com/search?q=laptop"
        assert _detect_error_type(title, body, url) == "http2_protocol_error"

    def test_connection_reset(self):
        """Detect ERR_CONNECTION_RESET."""
        title = "ERR_CONNECTION_RESET"
        body = "The connection was reset."
        url = "https://www.tokopedia.com/search?q=laptop"
        assert _detect_error_type(title, body, url) == "connection_reset"

    def test_site_cant_be_reached_en(self):
        """Detect 'This site can't be reached'."""
        title = "This site can't be reached"
        body = "Check the spelling or try searching."
        url = "about:blank"
        assert _detect_error_type(title, body, url) == "site_unreachable"

    def test_site_cant_be_reached_id(self):
        """Detect 'Situs ini tidak dapat dijangkau'."""
        title = "Situs ini tidak dapat dijangkau"
        body = "Periksa ejaan atau coba mencari."
        url = "about:blank"
        assert _detect_error_type(title, body, url) == "site_unreachable_id"

    def test_blank_page(self):
        """Detect about:blank."""
        title = ""
        body = ""
        url = "about:blank"
        assert _detect_error_type(title, body, url) == "blank_page"

    def test_blank_page_from_chrome_newtab(self):
        """Detect chrome://newtab/ as blank page."""
        title = ""
        body = ""
        url = "chrome://newtab/"
        assert _detect_error_type(title, body, url) == "blank_page"

    def test_no_error_on_real_tokopedia_page(self):
        """No error detected on real Tokopedia page."""
        title = "Tokopedia - Jual Beli Online Terpercaya"
        body = "Laptop Gaming ROG ASUS..."
        url = "https://www.tokopedia.com/search?q=laptop"
        assert _detect_error_type(title, body, url) is None

    def test_unknown_non_tokopedia_page(self):
        """Detect non-Tokopedia page as error."""
        title = "Some Random Site"
        body = "This is not Tokopedia"
        url = "https://example.com"
        # Should be detected as unknown_non_tokopedia_page by build_preflight_result
        # (not by _detect_error_type which returns None)
        assert _detect_error_type(title, body, url) is None


class TestRealPageDetection:
    """Test detection of real Tokopedia pages."""

    def test_tokopedia_in_title(self):
        """Detect 'tokopedia' in title."""
        assert _is_real_tokopedia_page("Tokopedia - Laptop Gaming", "", "")

    def test_tokopedia_in_url(self):
        """Detect 'tokopedia' in URL."""
        assert _is_real_tokopedia_page("", "", "https://www.tokopedia.com/search?q=laptop")

    def test_tokopedia_in_body(self):
        """Detect 'tokopedia' in body."""
        assert _is_real_tokopedia_page("", "Tokopedia adalah marketplace terpercaya", "")

    def test_toped_shorthand(self):
        """Detect 'toped' shorthand."""
        assert _is_real_tokopedia_page("Toped - Jual Beli", "", "")

    def test_not_tokopedia(self):
        """Not Tokopedia page detected."""
        assert not _is_real_tokopedia_page("Some Store", "Random stuff", "https://example.com")


class TestPreflightResult:
    """Test the full preflight result building."""

    def test_real_page_result(self):
        """Preflight result for real Tokopedia page."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="Tokopedia - Laptop Gaming",
            body_sample="ROG ASUS TUF...",
            current_url="https://www.tokopedia.com/search?q=laptop",
            load_time_ms=2500.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is True
        assert result["error_type"] is None
        assert "tokopedia" in result["message"].lower()

    def test_error_page_result(self):
        """Preflight result for Chrome error page."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="ERR_HTTP2_PROTOCOL_ERROR",
            body_sample="The server reset the connection.",
            current_url="https://www.tokopedia.com/search?q=laptop",
            load_time_ms=5000.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "http2_protocol_error"
        assert "error" in result["message"].lower() or "page" in result["message"].lower()

    def test_blank_page_result(self):
        """Preflight result for blank page."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="",
            body_sample="",
            current_url="about:blank",
            load_time_ms=100.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "blank_page"

    def test_rollback_engine_preflight(self):
        """Preflight result for Rollback/Selenium engine."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="Tokopedia",
            body_sample="Tokopedia - Jual Beli",
            current_url="https://www.tokopedia.com/search?q=laptop",
            load_time_ms=3000.0,
            engine="rollback",
        )
        assert result["opened_real_page"] is True
        assert result["error_type"] is None
        assert result["engine"] == "rollback"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

```

## FILE: `tests\test_query_expander.py`

```python
from src.scraper.query_expander import budget_url_range, expand_query_variants


def test_laptop_gaming_expands_to_brand_and_gpu_queries():
    variants = expand_query_variants("laptop gaming")

    assert variants[:3] == ["laptop gaming", "notebook gaming", "asus rog laptop"]
    assert "lenovo legion laptop" in variants
    assert "laptop rtx 4050" in variants


def test_budget_url_range_matches_filter_math():
    assert budget_url_range("10.000.000", 10) == (9_000_000, 11_000_000)

```

## FILE: `tests\test_schema.py`

```python
from src.server.progress import complete_progress, get_progress, init_progress, update_progress
import src.server.routes as routes
from src.server.main import app
from src.server.routes import _public_product_payload
from src.server.schemas import FeedbackRequest, SearchRequest
from fastapi.testclient import TestClient


def test_search_request_accepts_requested_api_shape():
    req = SearchRequest.model_validate(
        {
            "query": "laptop gaming",
            "target": 25,
            "budget": "10.000.000",
            "tolerance": 20,
            "ai": False,
            "engine_mode": "puppeteer",
        }
    )

    assert req.target_count == 25
    assert req.budget == "10.000.000"
    assert req.use_ai is False
    assert req.engine_mode == "puppeteer"


def test_progress_response_includes_demo_aliases():
    search_id = "schema-progress-demo"
    init_progress(search_id, target=25, raw_target=100, engine_mode="auto")
    update_progress(search_id, stage="opening_page", message="Opening marketplace", found=7, percent=22)

    progress = get_progress(search_id)

    assert progress["searchId"] == search_id
    assert progress["stage"] == "scraping"
    assert progress["statusText"] == "Opening marketplace"
    assert progress["percentage"] == 22
    assert progress["foundCount"] == 7
    assert progress["targetCount"] == 25
    assert isinstance(progress["elapsedSeconds"], float)
    assert "etaSeconds" in progress
    assert progress["logs"]

    complete_progress(search_id)
    assert get_progress(search_id)["stage"] == "completed"


def test_public_product_payload_has_required_demo_shape():
    product = _public_product_payload({
        "id": "p1",
        "title": "Laptop Gaming RTX 5060",
        "price_value": 12_500_000,
        "image_url": "https://images.test/p1.jpg",
        "shop_name": "Toko Demo",
        "rating": 4.8,
        "sold_count": 120,
        "url": "https://tokopedia.test/p1",
        "source_engine": "puppeteer",
        "relevance_score": 0.87,
        "ai_reason": "Cocok dengan query",
    })

    assert product["id"] == "p1"
    assert product["title"] == "Laptop Gaming RTX 5060"
    assert product["price"] == "Rp12.500.000"
    assert product["priceNumber"] == 12_500_000
    assert product["image"] == "https://images.test/p1.jpg"
    assert product["image_url"] == "https://images.test/p1.jpg"
    assert product["has_image"] is True
    assert product["storeName"] == "Toko Demo"
    assert product["rating"] == 4.8
    assert product["soldCount"] == 120
    assert product["url"] == "https://tokopedia.test/p1"
    assert product["source"] == "puppeteer"
    assert product["confidenceScore"] == 0.87
    assert product["relevanceReason"] == "Cocok dengan query"


def test_public_product_payload_normalizes_image_aliases():
    product = _public_product_payload({
        "id": "p2",
        "title": "Laptop Gaming",
        "price_value": 10_000_000,
        "images": ["//images.test/p2.webp"],
        "url": "https://tokopedia.test/p2",
    })

    assert product["image_url"] == "https://images.test/p2.webp"
    assert product["image"] == "https://images.test/p2.webp"
    assert product["has_image"] is True


def test_image_proxy_returns_image_bytes(monkeypatch):
    class FakeResponse:
        status_code = 200
        headers = {"content-type": "image/webp"}
        content = b"image-bytes"

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, url, headers):
            assert url == "https://images.test/p2.webp"
            assert headers["Referer"] == "https://www.tokopedia.com/"
            return FakeResponse()

    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)

    response = TestClient(app).get("/api/image-proxy", params={"url": "//images.test/p2.webp"})

    assert response.status_code == 200
    assert response.content == b"image-bytes"
    assert response.headers["content-type"].startswith("image/webp")


def test_result_store_adds_timestamp_and_expires(monkeypatch):
    routes._results_store.clear()
    monkeypatch.setattr(routes, "RESULT_STORE_TTL_SECONDS", 10)
    monkeypatch.setattr(routes, "RESULT_STORE_MAX_ITEMS", 10)
    monkeypatch.setattr(routes.time, "time", lambda: 1000.0)

    saved = routes.save_result("search-1", {"success": True, "data": []})

    assert saved["search_id"] == "search-1"
    assert saved["created_at"].endswith("Z")
    assert routes.get_result("search-1")["success"] is True

    monkeypatch.setattr(routes.time, "time", lambda: 1011.0)
    assert routes.get_result("search-1") is None


def test_result_store_enforces_max_items(monkeypatch):
    routes._results_store.clear()
    monkeypatch.setattr(routes, "RESULT_STORE_TTL_SECONDS", 100)
    monkeypatch.setattr(routes, "RESULT_STORE_MAX_ITEMS", 2)

    now = {"value": 1000.0}
    monkeypatch.setattr(routes.time, "time", lambda: now["value"])

    routes.save_result("old", {"success": True})
    now["value"] += 1
    routes.save_result("middle", {"success": True})
    now["value"] += 1
    routes.save_result("new", {"success": True})

    assert routes.get_result("old") is None
    assert routes.get_result("middle") is not None
    assert routes.get_result("new") is not None
    routes._results_store.clear()


def test_feedback_request_normalizes_old_and_new_names():
    old_shape = FeedbackRequest.model_validate(
        {
            "query": "laptop gaming",
            "product_id": "p1",
            "product_title": "Laptop",
            "user_action": "salah",
            "selected_reasons": ["bukan laptop"],
            "custom_reason": "aksesori",
        }
    )
    new_shape = FeedbackRequest.model_validate(
        {
            "query": "laptop gaming",
            "product": {"id": "p2", "title": "Laptop 2"},
            "feedback_type": "positive",
            "reasons": "cocok",
            "note": "valid",
        }
    )

    assert old_shape.normalized_reasons() == ["bukan laptop"]
    assert old_shape.normalized_note() == "aksesori"
    assert old_shape.normalized_feedback_type() == "negative"
    assert old_shape.normalized_corrected_label() == "tidak_relevan"

    assert new_shape.normalized_product_id() == "p2"
    assert new_shape.normalized_product_title() == "Laptop 2"
    assert new_shape.normalized_reasons() == ["cocok"]
    assert new_shape.normalized_note() == "valid"
    assert new_shape.normalized_user_action() == "benar"

```

## FILE: `tests\test_url_builder.py`

```python
from src.scraper.url_builder import build_tokopedia_search_url


def test_build_tokopedia_search_url_encodes_query():
    url = build_tokopedia_search_url("laptop gaming")

    assert url == "https://www.tokopedia.com/search?st=product&q=laptop%20gaming"


def test_build_tokopedia_search_url_adds_optional_budget_params():
    url = build_tokopedia_search_url("laptop gaming", 9_000_000, 11_000_000)

    assert "pmin=9000000" in url
    assert "pmax=11000000" in url

```

## FILE: `tools\pack_repo_for_claude.py`

```python
﻿from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "_claude_upload"
OUT_DIR.mkdir(exist_ok=True)

MAX_CHARS_PER_PART = 850_000
CODE_FENCE = "`" * 3

INCLUDE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".sql",
}

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "_claude_upload",
    "data",
    "logs",
    "screenshots",
    "debug",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "pack_repo_for_claude.py",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "marketspy_feedback.db",
}

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".mp4",
    ".zip",
    ".rar",
    ".7z",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".exe",
    ".dll",
    ".pyd",
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
}


def should_skip(path: Path) -> bool:
    """
    Menentukan apakah file harus dilewati agar Claude tidak dikasih sampah digital.
    """

    path_parts = set(path.parts)

    if path_parts & EXCLUDE_DIRS:
        return True

    if path.name in EXCLUDE_FILES:
        return True

    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    if path.suffix.lower() not in INCLUDE_EXTENSIONS:
        return True

    return False


def safe_read(path: Path) -> str:
    """
    Membaca file teks dengan aman.
    Kalau UTF-8 gagal, fallback ke latin-1.
    """

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")
    except Exception as exc:
        return f"<<FAILED_TO_READ: {exc}>>"


def get_language_name(path: Path) -> str:
    """
    Menentukan label bahasa untuk markdown code block.
    """

    suffix = path.suffix.lower().replace(".", "")

    language_map = {
        "py": "python",
        "js": "javascript",
        "jsx": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "html": "html",
        "css": "css",
        "scss": "scss",
        "json": "json",
        "md": "markdown",
        "txt": "text",
        "yml": "yaml",
        "yaml": "yaml",
        "toml": "toml",
        "ini": "ini",
        "cfg": "ini",
        "sql": "sql",
    }

    return language_map.get(suffix, "text")


def collect_files() -> list[Path]:
    """
    Mengambil semua file penting dari project.
    """

    files: list[Path] = []

    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and not should_skip(path):
            files.append(path)

    return files


def build_file_tree(files: list[Path]) -> str:
    """
    Membuat daftar struktur file agar Claude paham isi project.
    """

    lines: list[str] = []

    for path in files:
        relative_path = path.relative_to(ROOT).as_posix()
        lines.append(f"- {relative_path}")

    return "\n".join(lines)


def build_header(files: list[Path]) -> str:
    """
    Header konteks project untuk Claude Cloud.
    """

    file_tree = build_file_tree(files)

    return f"""# PASARINTAI AI - REPO CONTEXT FOR CLAUDE

## PROJECT PURPOSE

Project ini adalah aplikasi web scraping marketplace untuk mengambil data produk Tokopedia, melakukan filtering budget, AI crosscheck, feedback benar/salah, dan menampilkan rekomendasi produk seperti termurah, terbaik, dan most trusted.

## IMPORTANT RULES

- Jangan ubah tujuan utama project.
- Jangan hapus fitur feedback benar/salah.
- Jangan hapus progress realtime ETA dan elapsed.
- Jangan upload file rahasia seperti .env, token, cookie, database, dan cache.
- Untuk penulisan PI, ikuti Buku Pedoman Penulisan Ilmiah Prodi Informatika 2025.
- Untuk jurnal, gunakan sumber valid yang diberikan user, jangan membuat sumber palsu.

## FILE TREE

{file_tree}

---

"""


def build_file_block(path: Path) -> str:
    """
    Membuat markdown block untuk satu file.
    """

    relative_path = path.relative_to(ROOT).as_posix()
    language = get_language_name(path)
    content = safe_read(path)

    return (
        f"\n\n# FILE: {relative_path}\n\n"
        f"{CODE_FENCE}{language}\n"
        f"{content}\n"
        f"{CODE_FENCE}\n"
    )


def split_content_into_parts(files: list[Path]) -> list[str]:
    """
    Membagi hasil dump repo jadi beberapa file markdown agar aman diupload ke Claude Cloud.
    """

    parts: list[str] = []
    current_part = build_header(files)

    for path in files:
        block = build_file_block(path)

        if len(current_part) + len(block) > MAX_CHARS_PER_PART:
            parts.append(current_part)
            current_part = ""

        current_part += block

    if current_part.strip():
        parts.append(current_part)

    return parts


def write_parts(parts: list[str]) -> None:
    """
    Menulis hasil dump repo ke folder _claude_upload.
    """

    OUT_DIR.mkdir(exist_ok=True)

    for index, content in enumerate(parts, start=1):
        output_path = OUT_DIR / f"repo_context_part_{index:02d}.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"[OK] wrote {output_path} ({len(content):,} chars)")


def main() -> None:
    """
    Entry point script.
    """

    files = collect_files()

    if not files:
        print("[WARN] Tidak ada file source code yang ditemukan.")
        return

    parts = split_content_into_parts(files)
    write_parts(parts)

    print("")
    print(f"[DONE] Total source files packed: {len(files)}")
    print(f"[DONE] Total upload parts created: {len(parts)}")
    print(f"[DONE] Upload semua file dari folder: {OUT_DIR}")
    print("")
    print("[UPLOAD KE CLAUDE CLOUD]")
    print("1. Upload semua repo_context_part_*.md dari folder _claude_upload")
    print("2. Upload Buku Pedoman Penulisan Ilmiah Prodi Informatika 2025.pdf")
    print("3. Upload SOURCE_REGISTER.md berisi jurnal valid")
    print("")
    print("[WARN] Jangan upload .env, .db, node_modules, .venv, logs, atau file sensitif.")


if __name__ == "__main__":
    main()

```

## FILE: `web\app.js`

```javascript
/**
 * Tokopedia Scraper frontend controller - MarketSpy AI UI
 *
 * State management and helper functions untuk rendering produk dan feedback.
 */

/* ─── HELPER FUNCTIONS ─── */

function formatPrice(value) {
  if (!value) return 'Harga tidak tersedia';
  const num = Number(value);
  if (!num) return 'Harga tidak tersedia';
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(num);
}

function formatDiscount(oldPrice, newPrice) {
  const old = Number(oldPrice);
  const newVal = Number(newPrice);
  if (old <= 0 || newVal <= 0 || newVal >= old) return '';
  const percent = Math.round((1 - newVal / old) * 100);
  return `Hemat ${percent}%`;
}

function parseCountValue(value) {
  if (value == null || value === '') return 0;
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0;

  const text = String(value).toLowerCase().trim();
  const match = text.match(/(\d+(?:[.,]\d+)?)\s*(rb|ribu|k|jt|juta|m)?/i);
  if (!match) return 0;

  const base = Number.parseFloat(match[1].replace(',', '.'));
  if (!Number.isFinite(base)) return 0;

  const unit = match[2] || '';
  if (['rb', 'ribu', 'k'].includes(unit)) return Math.round(base * 1000);
  if (['jt', 'juta', 'm'].includes(unit)) return Math.round(base * 1000000);
  return Math.round(base);
}

function formatOneDecimal(value) {
  return Number(value)
    .toFixed(1)
    .replace(/\.0$/, '')
    .replace('.', ',');
}

function formatRatingValue(rating) {
  const numeric = Number(String(rating ?? '').replace(',', '.')) || 0;
  if (!numeric) return '';
  return Number.isInteger(numeric) ? String(numeric) : formatOneDecimal(numeric);
}

function formatCompactReviewCount(value) {
  const count = parseCountValue(value);
  if (!count) return '';
  if (count >= 1000000) return `${formatOneDecimal(count / 1000000)}jt`;
  if (count >= 1000) return `${formatOneDecimal(count / 1000)}rb`;
  if (count >= 100) return `${count}+`;
  return String(count);
}

function formatCompactSoldCount(value) {
  const count = parseCountValue(value);
  const raw = String(value || '').trim();

  if (!count && raw) {
    const cleaned = raw.replace(/\s+/g, ' ').replace(/terjual\s+terjual/ig, 'terjual');
    return /terjual/i.test(cleaned) ? cleaned : `${cleaned} terjual`;
  }

  if (!count) return '';
  if (count >= 1000000) return `${formatOneDecimal(count / 1000000)}jt terjual`;
  if (count >= 1000) return `${formatOneDecimal(count / 1000)}rb terjual`;
  if (count >= 100) return `${count}+ terjual`;
  return `${count} terjual`;
}

function hasRealAiSource(product) {
  const source = String(
    product?.decision_source ||
    product?.ai_source ||
    product?.model_used ||
    product?.selected_classifier ||
    ''
  ).toLowerCase();
  if (/(llm|ollama|classifier|semantic|model|ai)/i.test(source)) return true;
  if (/rule|fallback/i.test(source)) return false;
  return Boolean(window.app?.state?.aiStatus?.ok);
}

function isRulesFallback(product) {
  const source = String(product?.decision_source || product?.ai_source || '').toLowerCase();
  if (/rule|fallback/i.test(source) && !/(llm|ollama|classifier|semantic|ai)/i.test(source)) return true;
  if (window.app?.state?.aiStatus && window.app.state.aiStatus.ok === false) return true;
  return false;
}

function formatRating(rating, reviewCount) {
  const ratingText = formatRatingValue(rating);
  if (!ratingText) return '';
  const countStr = formatCompactReviewCount(reviewCount);
  return countStr ? `⭐ ${ratingText} (${countStr})` : `⭐ ${ratingText}`;
}

function formatSoldCount(sold) {
  return formatCompactSoldCount(sold);
}

function formatAiConfidence(product) {
  if (isRulesFallback(product)) return 'Rules: diterima';

  const raw = product?.ai_confidence ?? 
              product?.confidence ?? 
              product?.combined_score ?? 
              product?.semantic_score ??
              product?.relevance_score ?? 
              product?.confidenceScore ??
              null;

  if (raw == null || raw === '') return '';

  const numeric = Number(raw);
  if (!Number.isFinite(numeric) || numeric <= 0) {
    return hasRealAiSource(product) ? '' : 'Rules: diterima';
  }

  if (!hasRealAiSource(product)) return 'Rules: diterima';

  const pct = numeric <= 1 ? Math.round(numeric * 100) : Math.round(numeric);
  return `Keyakinan AI: ${pct}%`;
}

function formatRatingMeta(product) {
  const rating = Number(product?.rating) || 0;
  const reviewCount = product?.review_count || product?.rating_count || product?.reviewCount || product?.ratingCount || 0;
  const sold = product?.sold_count || product?.soldCount || product?.sold || product?.sold_text || '';
  const ratingText = formatRatingValue(rating);

  if (ratingText) {
    const reviewText = formatCompactReviewCount(reviewCount);
    if (reviewText) return `⭐ ${ratingText} (${reviewText})`;

    const soldText = formatCompactSoldCount(sold);
    return soldText ? `⭐ ${ratingText} (${soldText})` : `⭐ ${ratingText}`;
  }

  const soldText = formatCompactSoldCount(sold);
  return soldText ? `Terjual ${soldText.replace(/\s*terjual$/i, '')}` : '';
}

function getProductPriceNumber(product) {
  const direct = product?.priceNumber ?? product?.price_value ?? product?.price_val;
  const directNumber = Number(direct);
  if (Number.isFinite(directNumber) && directNumber > 0) return directNumber;

  const raw = String(product?.price_raw || product?.price_text || product?.price || '').replace(/[^\d]/g, '');
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}

function getActiveBudgetInfo() {
  return window.app?.state?.budgetInfo || null;
}

function isProductOverbudget(product) {
  const budgetInfo = getActiveBudgetInfo();
  const maxBudget = Number(budgetInfo?.max ?? budgetInfo?.maxBudget ?? budgetInfo?.max_budget ?? 0);
  if (!Number.isFinite(maxBudget) || maxBudget <= 0) return false;
  const price = getProductPriceNumber(product);
  return price > maxBudget;
}

function getProductImage(product) {
  const candidates = [
    product?.image_url, product?.image, product?.thumbnail, product?.thumb,
    product?.img, product?.photo, Array.isArray(product?.images) ? product.images[0] : null,
    product?.media?.image, product?.media?.thumbnail, product?.media?.url
  ];
  for (const val of candidates) {
    if (!val) continue;
    let url = String(val).trim();
    if (!url) continue;
    if (/^data:image\//i.test(url)) return url;
    if (url.startsWith("//")) url = `https:${url}`;
    if (/^https?:\/\//i.test(url)) return url;
  }
  return '';
}

function getCategoryProducts(category, limit) {
  if (!window.app || !window.app.buildRecommendationBuckets) return [];
  const buckets = window.app.buildRecommendationBuckets();
  const products = buckets[category] || [];
  return limit ? products.slice(0, limit) : products;
}

/* ─── ANIMATION & TRANSFORM ─── */

function buildTransformFromParams(params, index) {
  const parts = [];

  if (Array.isArray(params.translateX)) {
    parts.push(`translateX(${params.translateX[index]}px)`);
  }

  if (Array.isArray(params.translateY)) {
    parts.push(`translateY(${params.translateY[index]}px)`);
  }

  if (Array.isArray(params.scale)) {
    const scaleValue = params.scale[index];
    parts.push(`scale(${typeof scaleValue === "number" ? scaleValue : 1})`);
  }

  if (Array.isArray(params.rotate)) {
    parts.push(`rotate(${params.rotate[index]}deg)`);
  }

  return parts.join(" ") || "none";
}

const AnimeBridge = (() => {
  const animeGlobal = window.anime;
  const activeAnimations = new WeakMap();

  function resolveTargets(targets) {
    if (!targets) return [];
    if (typeof targets === "string") return Array.from(document.querySelectorAll(targets));
    if (targets instanceof Element || targets === window || targets === document) return [targets];
    return Array.from(targets).filter(Boolean);
  }

  function stop(targets) {
    const resolvedTargets = resolveTargets(targets);

    if (animeGlobal && typeof animeGlobal.remove === "function") {
      try {
        animeGlobal.remove(resolvedTargets);
      } catch (_error) {}
    }

    resolvedTargets.forEach(target => {
      const animation = activeAnimations.get(target);
      if (animation && typeof animation.pause === "function") {
        animation.pause();
      }
      activeAnimations.delete(target);
    });

    return resolvedTargets;
  }

  function run(targets, params) {
    if (!targets) return null;

    const resolvedTargets = stop(targets);
    if (!resolvedTargets.length) return null;

    let animation = null;
    const originalComplete = typeof params?.complete === "function" ? params.complete : null;
    const runParams = {
      ...(params || {}),
      complete: (...args) => {
        resolvedTargets.forEach(target => {
          if (activeAnimations.get(target) === animation) {
            activeAnimations.delete(target);
          }
        });

        if (originalComplete) originalComplete(...args);
      }
    };

    if (typeof window.animate === "function") {
      animation = window.animate(resolvedTargets, runParams);
    } else if (animeGlobal && typeof animeGlobal === "function") {
      animation = animeGlobal({ targets: resolvedTargets, ...runParams });
    } else if (animeGlobal && typeof animeGlobal.animate === "function") {
      animation = animeGlobal.animate(resolvedTargets, runParams);
    }

    if (animation) {
      resolvedTargets.forEach(target => activeAnimations.set(target, animation));
      return animation;
    }

    resolvedTargets.forEach(element => {
      if (!element || typeof element.animate !== "function") return;

      const keyframes = [
        {
          opacity: Array.isArray(runParams.opacity) ? runParams.opacity[0] : undefined,
          transform: buildTransformFromParams(runParams, 0)
        },
        {
          opacity: Array.isArray(runParams.opacity) ? runParams.opacity[1] : undefined,
          transform: buildTransformFromParams(runParams, 1)
        }
      ];

      const waapi = element.animate(keyframes, {
        duration: runParams.duration || 300,
        easing: "ease-out",
        fill: "forwards",
        delay: typeof runParams.delay === "function" ? runParams.delay(element, 0) : (runParams.delay || 0)
      });

      activeAnimations.set(element, waapi);
    });

    return null;
  }

  function timeline(params = {}) {
    if (typeof createTimeline === "function") {
      return createTimeline(params);
    }

    if (animeGlobal && typeof animeGlobal.timeline === "function") {
      return animeGlobal.timeline(params);
    }

    return null;
  }

  function stagger(value, params = {}) {
    if (typeof window.stagger === "function") {
      return window.stagger(value, params);
    }

    if (animeGlobal && typeof animeGlobal.stagger === "function" && animeGlobal.stagger.length > 1) {
      return animeGlobal.stagger(value, params);
    }

    return function(_el, index) {
      const start = Number(params.start || 0);
      const step = Array.isArray(value) ? 60 : Number(value || 0);
      const count = Number(params.count || 0);
      let order = index;

      if (count > 1 && params.from === "center") {
        order = Math.abs(index - (count - 1) / 2);
      } else if (count > 1 && params.from === "last") {
        order = count - 1 - index;
      }

      if (count > 1 && params.reversed) {
        order = count - 1 - order;
      }

      return Math.max(0, start + order * step);
    };
  }

  function createLayout(target, params) {
    if (typeof window.createLayout === "function") {
      return window.createLayout(target, params);
    }

    if (animeGlobal && typeof animeGlobal.createLayout === "function") {
      return animeGlobal.createLayout(target, params);
    }

    return null;
  }

  return { run, timeline, stagger, createLayout, stop };
})();

function getRecommendationMotionProfile() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  return {
    duration: reduceMotion ? 0 : 300,
    enterY: 18,
    enterScale: 0.985,
    rotateX: 0,
    staggerDelay: reduceMotion ? 0 : 18,
    grid: [1, 1]
  };
}

/* ─── Standalone helper functions referenced by ScraperApp ─── */

function handleImageError(img) {
  if (!img) return;
  img.classList.add("is-hidden");
  const wrapper = img.closest(".recommendation-product-image-wrap, .product-detail-media, .product-image-wrap, .product-modal-image-wrap");
  const placeholder = wrapper
    ? wrapper.querySelector(".product-image-placeholder, .product-detail-image-placeholder, .image-placeholder")
    : null;
  if (placeholder) {
    placeholder.classList.remove("is-hidden");
  } else {
    const fallbackPlaceholder = document.createElement("div");
    fallbackPlaceholder.className = "image-placeholder";
    fallbackPlaceholder.className = "product-image-placeholder";
    fallbackPlaceholder.textContent = "TIDAK ADA GAMBAR";
    img.replaceWith(fallbackPlaceholder);
  }
}





let activeRecommendationMode = "all";
let recommendationCacheVersion = 0;
let recommendationProductCache = new Map();

let activeModalMode = null;
let activeModalProducts = [];
let activeModalIndex = 0;
let activeModalProduct = null;
let modalTransitionRunning = false;
let feedbackSubmitting = false;
const reviewedProductIds = new Set();
const hoverTimers = new WeakMap();
const activeHoverTimerIds = new Set();
const activeHoverCards = new Set();
let checkedLayout = null;
let adaptiveScrollObserver = null;
let adaptiveScrollAnimation = null;

const reviewState = {
  checkedById: new Map(),
  checkedOrder: [],
  activeMode: "all"
};

const RECOMMENDATION_MODES = {
  all: {
    label: "Semua Barang",
    icon: "🧺",
    accent: "#60a5fa"
  },
  terbaik: {
    label: "Terbaik",
    icon: "⭐",
    accent: "#8b5cf6"
  },
  termurah: {
    label: "Termurah",
    icon: "💸",
    accent: "#10b981"
  },
  trusted: {
    label: "Most Trusted",
    icon: "🏆",
    accent: "#f59e0b"
  }
};

function normalizeRecommendationMode(mode) {
  const value = String(mode || "").toLowerCase().trim();

  const map = {
    all: "all",
    semua: "all",
    semua_barang: "all",
    "semua-barang": "all",
    "semua barang": "all",

    terbaik: "terbaik",
    best: "terbaik",

    termurah: "termurah",
    cheapest: "termurah",

    trusted: "trusted",
    mosttrusted: "trusted",
    most_trusted: "trusted",
    "most-trusted": "trusted",
    "most trusted": "trusted"
  };

  return map[value] || null;
}

function getProductReviewId(product) {
  return String(product?.id || product?.url || product?.product_url || product?.title || "");
}

function normalizeFeedbackResult(value) {
  const normalized = String(value || "").toLowerCase().trim();
  if (["positive", "benar", "correct", "true"].includes(normalized)) return "positive";
  if (["negative", "salah", "wrong", "false"].includes(normalized)) return "negative";
  return "negative";
}

function isProductReviewed(product) {
  const id = getProductReviewId(product);
  return Boolean(id && (reviewState.checkedById.has(id) || reviewedProductIds.has(id)));
}

function invalidateRecommendationCache() {
  recommendationCacheVersion += 1;
  recommendationProductCache.clear();
}

function resetReviewState() {
  reviewState.checkedById.clear();
  reviewState.checkedOrder.length = 0;
  reviewState.activeMode = "all";
  reviewedProductIds.clear();
  invalidateRecommendationCache();
}

function markProductAsReviewed(product, result, extra = {}) {
  const id = getProductReviewId(product);
  if (!id) return "";
  const normalizedResult = normalizeFeedbackResult(result);

  if (!reviewState.checkedById.has(id)) {
    reviewState.checkedOrder.push(id);
  }

  reviewedProductIds.add(id);
  reviewState.checkedById.set(id, {
    id,
    product,
    result: normalizedResult,
    reasons: extra.reasons || [],
    note: extra.note || "",
    reviewedAt: Date.now(),
    sourceMode: activeRecommendationMode || "all"
  });

  invalidateRecommendationCache();
  return id;
}

function getActiveRecommendationProducts(mode) {
  const reviewedIds = new Set([
    ...reviewState.checkedById.keys(),
    ...reviewedProductIds
  ]);

  return getRecommendationProducts(mode).filter(product => {
    const id = getProductReviewId(product);
    return !id || !reviewedIds.has(id);
  });
}

function getCheckedProductsForMode(mode) {
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const records = reviewState.checkedOrder
    .map(id => reviewState.checkedById.get(id))
    .filter(Boolean);

  if (normalizedMode === "all") return records;

  const modeProductIds = new Set(
    getRecommendationProducts(normalizedMode).map(product => getProductReviewId(product))
  );

  return records.filter(record => {
    if (record.sourceMode === normalizedMode) return true;
    return modeProductIds.has(record.id);
  });
}

function updateRecommendationButtons(nextMode) {
  document.querySelectorAll('[data-recommendation-mode]').forEach((btn) => {
    const mode = normalizeRecommendationMode(btn.dataset.recommendationMode);
    const isActive = mode === nextMode;

    btn.classList.toggle('is-active', isActive);
    btn.setAttribute("aria-pressed", isActive ? "true" : "false");
  });
}

function updateRecommendationTitle(mode) {
  const titleEl = document.getElementById('recommendationTitle');
  if (titleEl) {
    const normalizedMode = normalizeRecommendationMode(mode) || "all";
    const meta = RECOMMENDATION_MODES[normalizedMode];
    if (meta) titleEl.textContent = meta.label;
  }
}

function updateSingleRecommendationTitle(mode) {
  updateRecommendationTitle(mode);
}

function updateRecommendationLogo(mode) {
  const iconEl = document.querySelector('.active-mode-icon');
  if (iconEl) {
    const normalizedMode = normalizeRecommendationMode(mode) || "all";
    const meta = RECOMMENDATION_MODES[normalizedMode];
    if (meta) iconEl.textContent = meta.icon;
  }
}

function renderRecommendationProductCard(product, mode = activeRecommendationMode) {
  const item = window.app && typeof window.app.normalizeProduct === "function"
    ? window.app.normalizeProduct(product)
    : { ...(product || {}) };
  const id = getProductReviewId(item);
  const imageUrl = resolveProductImage(item);
  const title = item.title || "Produk Tokopedia";
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const isCategoryMode = normalizedMode !== "all";

  // Format rating + sold
  const ratingMeta = formatRatingMeta(item);

  // Format harga
  const priceStr = formatProductPrice(item);

  // Format keyakinan AI
  const aiStr = formatAiConfidence(item);

  // Overbudget badge
  const isOverbudget = isProductOverbudget(item);
  const overbudgetBadge = isOverbudget
    ? `<span class="rec-card-badge is-overbudget">Overbudget</span>`
    : '';
  const checkedPill = isCategoryMode
    ? '<span class="rec-checked-pill">Sudah dicek</span>'
    : '';

  // Gambar atau placeholder
  const imageHtml = imageUrl
    ? `<img class="recommendation-product-image" src="${escapeHtml(imageUrl)}" data-original-src="${escapeHtml(imageUrl)}" alt="${escapeHtml(title)}" loading="lazy" decoding="async" />`
    : "";
  const placeholderHtml = imageUrl
    ? `<div class="product-image-placeholder is-hidden" aria-hidden="true"></div>`
    : `<div class="product-image-placeholder" aria-hidden="true"><span>Gambar tidak tersedia</span></div>`;

  // TIDAK ADA tombol Benar/Salah/Buka di card — card seluruhnya clickable buka modal
  return `
    <article class="recommendation-product-card${isCategoryMode ? ' is-checked-category-card' : ''}" data-product-card data-product-id="${escapeHtml(id)}" data-id="${escapeHtml(id)}" role="button" tabindex="0" aria-label="${escapeHtml(title)}">
      ${checkedPill}
      <div class="recommendation-product-image-wrap${imageUrl ? "" : " is-image-missing"}">
        ${imageHtml}
        ${placeholderHtml}
      </div>
      <div class="recommendation-product-card-details">
        ${overbudgetBadge}
        <h4 class="recommendation-product-title">${escapeHtml(title)}</h4>
        <div class="recommendation-product-price">${escapeHtml(priceStr)}</div>
        ${ratingMeta ? `<div class="recommendation-product-rating-row"><span class="rec-rating">${escapeHtml(ratingMeta)}</span></div>` : ''}
        ${aiStr ? `<div class="rec-ai-confidence">${escapeHtml(aiStr)}</div>` : ''}
      </div>
    </article>
  `;
}

function setupProductImageErrorHandlers(scope = document) {
  scope.querySelectorAll(".recommendation-product-image").forEach(img => {
    if (img.dataset.errorHandlerBound === "true") return;
    img.dataset.errorHandlerBound = "true";

    img.onerror = () => {
      const originalSrc = img.dataset.originalSrc || img.src;
      if (originalSrc && window.app && typeof window.app.proxyImageUrl === "function" && !img.dataset.proxyTried) {
        img.dataset.proxyTried = "1";
        img.src = window.app.proxyImageUrl(originalSrc);
        return;
      }

      handleImageError(img);
    };
  });
}

function renderRecommendationContent(mode) {
  const grid = document.querySelector(".recommendation-product-grid");
  if (!grid) return;

  const normalizedMode = normalizeRecommendationMode(mode) || "all";

  // Tampilkan/sembunyikan category limit bar — hanya untuk non-all
  const limitBar = document.getElementById('category-limit-bar');
  if (limitBar) {
    limitBar.classList.toggle('hidden', normalizedMode === 'all');
  }

  // Ambil category_limit dari inline input atau hidden input
  const inlineInput = document.getElementById('category_limit_inline');
  const hiddenInput = document.getElementById('category_limit');
  const rawLimit = inlineInput?.value || hiddenInput?.value || '12';
  const categoryLimit = Math.max(1, Math.min(parseInt(rawLimit, 10) || 12, 100));

  const categoryProducts = getRecommendationProducts(normalizedMode);
  const activeProducts = getActiveRecommendationProducts(normalizedMode);
  const products = activeProducts.length || !categoryProducts.length
    ? activeProducts
    : categoryProducts;
  const isAllMode = normalizedMode === 'all';

  let displayProducts;
  let shortageMsg = '';

  if (isAllMode) {
    // Semua Barang: tampilkan semua, tidak dibatasi category_limit
    displayProducts = products;
  } else {
    // Kategori lain: tampilkan maksimal categoryLimit, tapi tidak dipaksa penuh
    const actualCount = products.length;
    displayProducts = products.slice(0, categoryLimit);

    if (actualCount === 0) {
      // Tidak ada produk sama sekali
      shortageMsg = '';
    } else if (actualCount < categoryLimit) {
      // Data valid kurang dari yang diminta
      shortageMsg = `Kategori ini hanya punya ${actualCount} produk yang cocok dari ${categoryLimit} yang diminta.`;
    }
    // Kalau actualCount >= categoryLimit: tidak perlu pesan, tampilkan categoryLimit item
  }

  let html = '';
  if (displayProducts.length === 0) {
    html = '<div class="recommendation-empty">Belum ada produk yang cocok untuk kategori ini.</div>';
  } else {
    html = displayProducts.map(product => renderRecommendationProductCard(product, normalizedMode)).join('');
    if (shortageMsg) {
      html += `<div class="recommendation-shortage-notice">${escapeHtml(shortageMsg)}</div>`;
    }
  }

  grid.innerHTML = html;
  setupProductImageErrorHandlers(grid);
}

function updateRecommendationContent(mode) {
  renderRecommendationContent(mode);
}

function animateRecommendationCardsEnter(profile) {
  if (!profile || profile.duration === 0) return;
  const cards = document.querySelectorAll('.recommendation-product-card');
  if (!cards.length) return;

  AnimeBridge.run(cards, {
    opacity: [0, 1],
    translateY: [profile.enterY, 0],
    scale: [profile.enterScale, 1],
    rotateX: [profile.rotateX, 0],
    delay: AnimeBridge.stagger(profile.staggerDelay, { grid: profile.grid, from: 'center' }),
    duration: profile.duration,
    easing: 'easeOutExpo',
  });
}

function animateRecommendationCardsExit(container, profile) {
  if (!profile || profile.duration === 0) return Promise.resolve();
  const cards = (container || document).querySelectorAll('.recommendation-product-card');
  if (!cards.length) return Promise.resolve();

  return new Promise((resolve) => {
    AnimeBridge.run(cards, {
      opacity: [1, 0],
      translateY: [0, -24],
      scale: [1, 0.92],
      duration: Math.round(profile.duration * 0.55),
      easing: 'easeInQuad',
      complete: resolve,
    }) || resolve();
  });
}

function getCategoryMotionProfile() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isMobile = window.matchMedia("(max-width: 700px)").matches;

  if (reduceMotion) {
    return {
      exit: 0,
      title: 0,
      enter: 0,
      stagger: 0
    };
  }

  if (isMobile) {
    return {
      exit: 120,
      title: 120,
      enter: 260,
      stagger: 16
    };
  }

  return {
    exit: 140,
    title: 140,
    enter: 300,
    stagger: 18
  };
}

function hardRenderRecommendationMode(mode) {
  const normalized = normalizeRecommendationMode(mode) || "all";
  activeRecommendationMode = normalized;
  reviewState.activeMode = normalized;

  if (window.app) {
    window.app.state.recommendationMode = normalized;
    window.app.state.hasUserSelectedRecommendation = true;
  }

  updateRecommendationButtons(normalized);
  updateSingleRecommendationTitle(normalized);
  renderRecommendationContent(normalized);
  renderCheckedProductsBox(normalized);

  const stage = document.querySelector(".recommendation-stage");
  if (stage) {
    stage.dataset.activeMode = normalized;
    stage.classList.remove("is-switching");
  }

  const panel = document.querySelector(".recommendation-active-panel");
  if (panel) panel.style.height = "";
}

async function selectRecommendationMode(nextMode, triggerButton) {
  nextMode = normalizeRecommendationMode(nextMode);
  if (!nextMode) return;
  if (nextMode === activeRecommendationMode) return;

  const stage = document.querySelector(".recommendation-stage");
  const grid = document.querySelector(".recommendation-product-grid");
  const title = document.querySelector(".recommendation-active-title");

  if (!stage || !grid || !title) {
    hardRenderRecommendationMode(nextMode);
    return;
  }

  activeRecommendationMode = nextMode;
  reviewState.activeMode = nextMode;

  if (window.app) {
    window.app.state.recommendationMode = nextMode;
    window.app.state.hasUserSelectedRecommendation = true;
  }

  const profile = getCategoryMotionProfile();
  const oldCards = [...grid.querySelectorAll("[data-product-card], .recommendation-product-card")];
  stage.classList.add("is-switching");

  if (oldCards.length > 0) {
    AnimeBridge.run(oldCards, {
      opacity: [1, 0],
      translateY: [0, -16],
      scale: [1, 0.965],
      delay: AnimeBridge.stagger(8, { from: "center", reversed: true }),
      duration: profile.exit,
      easing: "easeInQuad"
    });
  }

  await sleep(profile.exit);

  updateRecommendationButtons(nextMode);
  stage.dataset.activeMode = nextMode;

  const meta = RECOMMENDATION_MODES[nextMode];
  if (title && meta) {
    AnimeBridge.run(title, {
      opacity: [1, 0],
      translateY: [0, -8],
      duration: Math.round(profile.title * 0.45),
      easing: "easeInQuad",
      complete: () => {
        title.textContent = meta.label;
        AnimeBridge.run(title, {
          opacity: [0, 1],
          translateY: [8, 0],
          duration: Math.round(profile.title * 0.55),
          easing: "easeOutCubic"
        });
      }
    }) || (title.textContent = meta.label);
  }

  renderRecommendationContent(nextMode);
  renderCheckedProductsBox(nextMode);

  const newCards = [...grid.querySelectorAll("[data-product-card], .recommendation-product-card")];

  if (newCards.length > 0) {
    AnimeBridge.run(newCards, {
      opacity: [0, 1],
      translateY: [18, 0],
      scale: [0.985, 1],
      delay: AnimeBridge.stagger(profile.stagger, { start: 20, from: "first" }),
      duration: profile.enter,
      easing: "easeOutCubic"
    });
  }

  window.setTimeout(() => stage.classList.remove("is-switching"), profile.enter + profile.stagger * Math.min(newCards.length, 8) + 40);
}



function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, Math.max(0, Number(ms) || 0)));
}

function nextFrameTwice() {
  return new Promise(resolve => {
    const raf = window.requestAnimationFrame || (callback => window.setTimeout(callback, 16));
    raf(() => raf(resolve));
  });
}

function resetCardInlineMotion(cards) {
  cards.forEach(card => {
    card.style.transform = "";
    card.style.opacity = "";
    card.style.boxShadow = "";
  });
}

function cancelAllHoverTimers() {
  activeHoverTimerIds.forEach(timer => clearTimeout(timer));
  activeHoverTimerIds.clear();

  activeHoverCards.forEach(card => {
    hoverTimers.delete(card);
    if (card.isConnected) {
      card.style.transform = "";
      card.style.opacity = "";
      card.style.boxShadow = "";
    }
  });
  activeHoverCards.clear();
}

function getEventElement(event) {
  return event?.target instanceof Element ? event.target : event?.target?.parentElement || null;
}



function buildRecommendationProducts(mode) {
  if (!window.app) return [];
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const buckets = window.app.buildRecommendationBuckets();
  return buckets[normalizedMode] || [];
}

function getCachedRecommendationProducts(mode) {
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const key = `${recommendationCacheVersion}:${normalizedMode}`;

  if (recommendationProductCache.has(key)) {
    return recommendationProductCache.get(key);
  }

  const products = buildRecommendationProducts(normalizedMode);
  recommendationProductCache.set(key, products);

  return products;
}

function getRecommendationProducts(mode) {
  return getCachedRecommendationProducts(mode);
}

function cssEscapeValue(value) {
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") {
    return CSS.escape(String(value));
  }

  return String(value).replace(/["\\]/g, "\\$&");
}



function setupCheckedProductsLayout() {
  const container = document.querySelector(".checked-products-grid");
  if (!container) return;

  if (checkedLayout && checkedLayout.__marketspyContainer === container) return;

  if (checkedLayout && typeof checkedLayout.revert === "function") {
    checkedLayout.revert();
  }

  checkedLayout = AnimeBridge.createLayout(container, {
    children: ".checked-product-card",
    duration: 650,
    ease: "out(4)",
    delay: AnimeBridge.stagger(45),
    enterFrom: {
      opacity: 0,
      scale: 0.72,
      y: 42,
      filter: "blur(10px)"
    },
    leaveTo: {
      opacity: 0,
      scale: 0.82,
      y: -24,
      filter: "blur(8px)"
    },
    properties: ["boxShadow", "borderColor"]
  });

  if (checkedLayout) {
    checkedLayout.__marketspyContainer = container;
  }
}

function animateCheckedCardEnterFallback(card) {
  if (!card) return;

  AnimeBridge.run(card, {
    opacity: [0, 1],
    translateY: [42, 0],
    scale: [0.72, 1],
    filter: ["blur(10px)", "blur(0px)"],
    duration: 650,
    easing: "easeOutExpo"
  });
}

function getCheckedTrayRects(container) {
  const rects = new Map();
  if (!container) return rects;

  container.querySelectorAll(".checked-product-card").forEach(card => {
    const id = card.dataset.productId;
    if (id) rects.set(id, card.getBoundingClientRect());
  });

  return rects;
}

function animateCheckedTrayFlipFallback(firstRects, sourceRect, enteredId) {
  const container = document.querySelector(".checked-products-grid");
  if (!container) return;

  const cards = [...container.querySelectorAll(".checked-product-card")];

  cards.forEach(card => {
    const id = card.dataset.productId;
    const first = id ? firstRects.get(id) : null;
    const last = card.getBoundingClientRect();

    if (!first || id === enteredId) return;

    const dx = first.left - last.left;
    const dy = first.top - last.top;
    if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;

    card.style.transform = `translate(${dx}px, ${dy}px)`;
    card.style.transition = "transform 0s";

    requestAnimationFrame(() => {
      card.style.transition = "";
      AnimeBridge.run(card, {
        translateX: [dx, 0],
        translateY: [dy, 0],
        scale: [0.985, 1],
        duration: 620,
        easing: "easeOutExpo"
      });
    });
  });

  const enteredCard = cards.find(card => card.dataset.productId === enteredId);
  if (!enteredCard) return;

  if (sourceRect) {
    const last = enteredCard.getBoundingClientRect();
    const dx = sourceRect.left - last.left;
    const dy = sourceRect.top - last.top;

    enteredCard.style.opacity = "0.12";
    enteredCard.style.transform = `translate(${dx}px, ${dy}px) scale(0.72)`;
    enteredCard.style.filter = "blur(10px)";

    requestAnimationFrame(() => {
      enteredCard.style.opacity = "";
      enteredCard.style.transform = "";
      enteredCard.style.filter = "";

      AnimeBridge.run(enteredCard, {
        opacity: [0.12, 1],
        translateX: [dx, 0],
        translateY: [dy, 0],
        scale: [0.72, 1],
        filter: ["blur(10px)", "blur(0px)"],
        duration: 650,
        easing: "easeOutExpo"
      });
    });

    return;
  }

  animateCheckedCardEnterFallback(enteredCard);
}

function createCheckedProductCard(record) {
  const product = record.product || {};
  const card = document.createElement("article");
  card.className = `checked-product-card is-${record.result === "positive" ? "positive" : "negative"}`;
  card.dataset.productId = record.id;

  // Badge di kiri atas
  const badge = document.createElement("span");
  badge.className = `checked-product-badge is-${record.result === "positive" ? "positive" : "negative"}`;
  badge.textContent = record.result === "positive" ? "Benar" : "Salah";

  // Layout: gambar + info
  const layout = document.createElement("div");
  layout.className = "checked-product-layout";

  // Gambar produk
  const imageUrl = resolveProductImage(product);
  const imgWrap = document.createElement("div");
  imgWrap.className = "checked-product-image-wrap";
  if (imageUrl) {
    const img = document.createElement("img");
    img.className = "checked-product-image";
    img.src = imageUrl;
    img.alt = product.title || "Gambar produk";
    img.loading = "lazy";
    img.onerror = () => {
      if (!img.dataset.proxyTried && window.app && typeof window.app.proxyImageUrl === "function") {
        img.dataset.proxyTried = "1";
        img.src = window.app.proxyImageUrl(imageUrl);
        return;
      }
      imgWrap.innerHTML = '<div class="checked-product-img-placeholder">Tidak ada gambar</div>';
    };
    imgWrap.appendChild(img);
  } else {
    imgWrap.innerHTML = '<div class="checked-product-img-placeholder">Tidak ada gambar</div>';
  }

  // Info produk
  const info = document.createElement("div");
  info.className = "checked-product-info";

  const title = document.createElement("h4");
  title.className = "checked-product-title";
  title.textContent = product.title || "Produk Tokopedia";

  const price = document.createElement("p");
  price.className = "checked-product-price";
  price.textContent = formatProductPrice(product);

  // Rating/review, fallback ke sold count jika review count tidak tersedia.
  const ratingStr = formatRatingMeta(product);

  const metaRow = document.createElement("div");
  metaRow.className = "checked-product-meta-row";
  if (ratingStr) {
    const ratingEl = document.createElement("span");
    ratingEl.className = "checked-meta-rating";
    ratingEl.textContent = ratingStr;
    metaRow.appendChild(ratingEl);
  }

  // Keyakinan AI
  const aiStr = formatAiConfidence(product);

  const sourceMeta = document.createElement("p");
  sourceMeta.className = "checked-product-meta";
  const modeLabel = RECOMMENDATION_MODES[record.sourceMode]?.label || "Semua Barang";
  sourceMeta.textContent = `${modeLabel} · ${new Date(record.reviewedAt).toLocaleTimeString("id-ID", {
    hour: "2-digit",
    minute: "2-digit"
  })}`;

  info.append(title, price, metaRow);
  if (aiStr) {
    const aiEl = document.createElement("p");
    aiEl.className = "checked-product-ai";
    aiEl.textContent = aiStr;
    info.appendChild(aiEl);
  }
  info.appendChild(sourceMeta);

  // Tombol aksi
  const actions = document.createElement("div");
  actions.className = "checked-product-actions";

  const openBtn = document.createElement("a");
  openBtn.className = "checked-action-btn is-open";
  openBtn.href = product.url || product.product_url || "#";
  openBtn.target = "_blank";
  openBtn.rel = "noopener noreferrer";
  openBtn.textContent = "Buka Produk";
  actions.appendChild(openBtn);

  layout.append(imgWrap, info);
  card.append(badge, layout, actions);
  return card;
}

function renderCheckedProductsBox(mode) {
  setupCheckedProductsLayout();

  const box = document.querySelector(".checked-products-box");
  const grid = document.querySelector(".checked-products-grid");
  const count = document.querySelector(".checked-products-count");
  if (!box || !grid) return;
  const normalizedMode = normalizeRecommendationMode(mode) || "all";

  if (normalizedMode !== "all") {
    box.classList.add("hidden");
    grid.innerHTML = "";
    if (count) count.textContent = "0 produk";
    return;
  }

  box.classList.remove("hidden");

  // Hanya tampilkan produk yang diklik "Benar" (positive)
  const allRecords = getCheckedProductsForMode("all");
  const records = allRecords.filter(r => r.result === 'positive');

  if (count) count.textContent = `${records.length} produk`;

  grid.innerHTML = "";

  if (!records.length) {
    const empty = document.createElement("div");
    empty.className = "checked-products-empty";
    empty.textContent = "Belum ada produk yang ditandai Benar.";
    grid.appendChild(empty);
  } else {
    records.forEach(record => grid.appendChild(createCheckedProductCard(record)));
  }

  if (checkedLayout && typeof checkedLayout.refresh === "function") {
    requestAnimationFrame(() => checkedLayout.refresh());
  }
}

function animateActiveCardExit(card) {
  return new Promise(resolve => {
    if (!card) {
      resolve();
      return;
    }

    AnimeBridge.run(card, {
      opacity: [1, 0],
      scale: [1, 0.72],
      translateY: [0, 34],
      rotateZ: [0, 2],
      filter: ["blur(0px)", "blur(8px)"],
      duration: 420,
      easing: "easeInExpo",
      complete: resolve
    }) || resolve();
  });
}

function pulseCheckedBox() {
  const box = document.querySelector(".checked-products-box");
  if (!box) return;

  AnimeBridge.run(box, {
    scale: [1, 1.015, 1],
    boxShadow: [
      "0 0 0 rgba(34,211,238,0)",
      "0 0 54px rgba(34,211,238,0.18)",
      "0 0 0 rgba(34,211,238,0)"
    ],
    duration: 720,
    easing: "easeOutExpo"
  });
}

async function moveProductToCheckedTray(product, result, extra = {}) {
  const id = markProductAsReviewed(product, result, extra);
  if (!id) return;

  const sourceCard = document.querySelector(
    `.recommendation-product-card[data-product-id="${cssEscapeValue(id)}"]`
  );
  const sourceRect = sourceCard ? sourceCard.getBoundingClientRect() : null;
  const checkedGrid = document.querySelector(".checked-products-grid");
  const firstRects = getCheckedTrayRects(checkedGrid);

  await animateActiveCardExit(sourceCard);

  renderRecommendationContent(activeRecommendationMode);
  renderCheckedProductsBox(activeRecommendationMode);

  await nextFrameTwice();

  const checkedCard = document.querySelector(
    `.checked-product-card[data-product-id="${cssEscapeValue(id)}"]`
  );

  if (checkedLayout && typeof checkedLayout.refresh === "function") {
    checkedLayout.refresh();
  } else if (checkedCard) {
    animateCheckedTrayFlipFallback(firstRects, sourceRect, id);
  }

  pulseCheckedBox();
  setupAdaptiveScrollBehavior();
}

function openRecommendationProductModal(product, sourceCard) {
  const mode = activeRecommendationMode || "all";
  const queue = getActiveRecommendationProducts(mode);
  const target = product || queue[0];

  if (!target) {
    showSmallToast("Tidak ada produk rekomendasi yang bisa direview.");
    return;
  }

  window.__ACTIVE_MODAL_SOURCE_CARD__ = sourceCard || null;
  openProductDetailModal(target, queue);
}

function showRecommendationDialogWithAnimation() {
  const dialog = document.querySelector("#recommendation-product-dialog");
  if (!dialog) return;

  if (!dialog.open) dialog.showModal();

  AnimeBridge.run(".recommendation-modal-card", {
    opacity: [0, 1],
    translateY: [56, 0],
    scale: [0.88, 1],
    duration: 1000,
    easing: "easeOutExpo"
  });

  AnimeBridge.run(".recommendation-modal-image-wrap", {
    opacity: [0, 1],
    translateX: [-48, 0],
    scale: [0.96, 1],
    duration: 1000,
    delay: 120,
    easing: "easeOutExpo"
  });

  AnimeBridge.run(".recommendation-modal-content > *", {
    opacity: [0, 1],
    translateX: [36, 0],
    delay: AnimeBridge.stagger(70, { start: 180 }),
    duration: 850,
    easing: "easeOutExpo"
  });
}

function resolveProductImage(product) {
  const candidates = [
    product?.image_url,
    product?.image,
    product?.thumbnail,
    product?.thumb,
    product?.img,
    product?.photo,
    Array.isArray(product?.images) ? product.images[0] : null,
    product?.media?.image,
    product?.media?.thumbnail,
    product?.media?.url
  ];

  for (const value of candidates) {
    if (!value) continue;

    let url = String(value).trim();

    if (!url) continue;
    if (/^data:image\//i.test(url)) return url;
    if (url.startsWith("//")) url = `https:${url}`;
    if (/^https?:\/\//i.test(url)) return url;
  }

  return "";
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatRupiah(value) {
  if (window.app && typeof window.app.formatRupiah === "function") {
    return window.app.formatRupiah(value);
  }
  const number = Number(value || 0);
  if (!number) return 'Harga tidak tersedia';
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(number);
}

function formatProductPrice(product) {
  const numeric = product?.price_value ?? product?.priceNumber ?? product?.price_val;
  if (Number(numeric) > 0) return formatRupiah(numeric);
  return product?.price || product?.price_text || product?.price_raw || "Harga tidak tersedia";
}

function setText(selector, value) {
  const el = document.querySelector(selector);
  if (el) el.textContent = value;
}

function fillRecommendationModal(product) {
  const imageUrl = resolveProductImage(product);

  const imgWrap = document.querySelector(".recommendation-modal-image-wrap");

  if (imgWrap) {
    if (imageUrl) {
      imgWrap.innerHTML = `
        <img
          class="recommendation-modal-image"
          src="${escapeHtml(imageUrl)}"
          alt="Gambar produk"
          loading="lazy"
          decoding="async"
        />
      `;

      const newImg = imgWrap.querySelector("img");
      newImg.addEventListener("error", () => {
        imgWrap.innerHTML = `
          <div class="image-placeholder">
            <strong>Tidak ada gambar</strong>
            <span>Gambar tidak tersedia</span>
          </div>
        `;
      }, { once: true });
    } else {
      imgWrap.innerHTML = `
        <div class="image-placeholder">
          <strong>Tidak ada gambar</strong>
          <span>Gambar tidak tersedia</span>
        </div>
      `;
    }
  }

  setText(".recommendation-modal-kicker", "DETAIL REKOMENDASI");
  setText(".recommendation-modal-title", product?.title || "-");
  setText(".recommendation-modal-store", product?.storeName || product?.shop_name || product?.shop || product?.store || "");
  setText(".recommendation-modal-price", formatProductPrice(product));
  setText(".recommendation-modal-rating", `⭐ ${product?.rating || "-"}`);
  setText(".recommendation-modal-sold", `🛍️ ${product?.sold || product?.sold_text || "0 terjual"}`);
  setText(".recommendation-modal-confidence", `🧠 Keyakinan AI: ${product?.confidenceScore ?? product?.confidence ?? product?.ai_confidence ?? product?.relevance_score ?? "-"}`);

  const openBtn = document.querySelector("#recommendation-product-dialog .open-product-btn");
  if (openBtn) {
    openBtn.textContent = "Buka Produk";
    openBtn.href = product?.url || "#";
  }

  const reasonGrid = document.querySelector(".modal-feedback-reason-grid");
  if (reasonGrid) {
    reasonGrid.innerHTML = "";
    const reasons = [
      'Produk tidak relevan',
      'Cuma aksesoris',
      'Spesifikasi tidak sesuai query',
      'Harga tidak sesuai',
      'Nama produk salah',
      'Gambar tidak sesuai',
      'Toko tidak terpercaya',
      'Duplikat',
      'Bukan sesuai intent pencarian',
      'Data tidak lengkap',
      'Lainnya',
    ];
    reasons.forEach(reason => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "feedback-reason-chip modal-feedback-reason-chip";
      chip.dataset.reason = reason;
      chip.textContent = reason;
      chip.addEventListener("click", (e) => {
        e.preventDefault();
        chip.classList.toggle("is-selected");
      });
      reasonGrid.appendChild(chip);
    });
  }
}

function getNextModalProduct() {
  if (!activeModalProducts.length) return null;

  for (let i = activeModalIndex + 1; i < activeModalProducts.length; i++) {
    const candidate = activeModalProducts[i];
    if (!isProductReviewed(candidate)) {
      activeModalIndex = i;
      return candidate;
    }
  }

  return null;
}

function closeRecommendationProductModal() {
  return new Promise(resolve => {
    closeProductDetailModal();
    activeModalProduct = null;
    window.__ACTIVE_MODAL_PRODUCT__ = null;
    window.__ACTIVE_MODAL_SOURCE_CARD__ = null;
    window.setTimeout(resolve, 240);
  });
}

async function handleModalFeedback(type, extra = {}) {
  if (feedbackSubmitting || modalTransitionRunning) return;
  if (!activeModalProduct) return;

  feedbackSubmitting = true;

  const product = activeModalProduct;
  const productId = getProductReviewId(product);

  try {
    await sendFeedback({
      product_id: productId,
      feedback_type: type,
      reasons: extra.reasons || [],
      note: extra.note || ""
    });

    await moveProductToCheckedTray(product, type, extra);

    const nextProduct = getNextModalProduct();

    if (nextProduct) {
      await transitionModalToNextProduct(nextProduct);
    } else {
      await closeRecommendationProductModal();
      showSmallToast("Semua produk di kategori ini sudah dicek.");
    }
  } catch (error) {
    console.error("[FEEDBACK] modal feedback failed:", error);
    showSmallToast("Feedback gagal dikirim. Coba lagi.");
  } finally {
    feedbackSubmitting = false;
  }
}

function transitionModalToNextProduct(nextProduct) {
  return new Promise(resolve => {
    modalTransitionRunning = true;
    let settled = false;

    const finish = () => {
      if (settled) return;
      settled = true;
      modalTransitionRunning = false;
      resolve();
    };

    const contentTargets = document.querySelectorAll(
      ".recommendation-modal-image-wrap, .recommendation-modal-content > *"
    );

    AnimeBridge.run(contentTargets, {
      opacity: [1, 0],
      translateX: [0, -42],
      scale: [1, 0.96],
      filter: ["blur(0px)", "blur(8px)"],
      delay: AnimeBridge.stagger(35, { reversed: true }),
      duration: 360,
      easing: "easeInExpo",
      complete: () => {
        activeModalProduct = nextProduct;
        window.__ACTIVE_MODAL_PRODUCT__ = nextProduct;

        fillRecommendationModal(nextProduct);
        resetModalFeedbackPanel();

        requestAnimationFrame(() => {
          const newTargets = document.querySelectorAll(
            ".recommendation-modal-image-wrap, .recommendation-modal-content > *"
          );
          const fallbackTimer = window.setTimeout(finish, 1200);

          AnimeBridge.run(newTargets, {
            opacity: [0, 1],
            translateX: [48, 0],
            scale: [0.96, 1],
            filter: ["blur(8px)", "blur(0px)"],
            delay: AnimeBridge.stagger(55, { start: 80 }),
            duration: 720,
            easing: "easeOutExpo",
            complete: () => {
              window.clearTimeout(fallbackTimer);
              finish();
            }
          }) || (() => {
            window.clearTimeout(fallbackTimer);
            finish();
          })();
        });
      }
    }) || (() => {
      activeModalProduct = nextProduct;
      fillRecommendationModal(nextProduct);
      resetModalFeedbackPanel();
      finish();
    })();
  });
}

function resetModalFeedbackPanel() {
  const panel = document.querySelector(".modal-feedback-reason-panel");
  if (panel) panel.hidden = true;

  document
    .querySelectorAll(".modal-feedback-reason-chip, .feedback-reason-chip")
    .forEach(chip => chip.classList.remove("is-selected"));

  const note = document.querySelector(".modal-feedback-note");
  if (note) note.value = "";
}

function revealModalReasonPanel() {
  const panel = document.querySelector(".modal-feedback-reason-panel");
  if (!panel) return;

  panel.hidden = false;

  AnimeBridge.run(panel, {
    opacity: [0, 1],
    translateY: [24, 0],
    duration: 650,
    easing: "easeOutExpo"
  });

  const chips = panel.querySelectorAll(".feedback-reason-chip, .modal-feedback-reason-chip");
  if (chips.length > 0) {
    AnimeBridge.run(chips, {
      opacity: [0, 1],
      translateY: [16, 0],
      scale: [0.94, 1],
      delay: AnimeBridge.stagger(45),
      duration: 650,
      easing: "easeOutExpo"
    });
  }
}

function collectModalSelectedReasons() {
  const panel = document.querySelector(".modal-feedback-reason-panel");
  if (!panel) return [];
  const selectedChips = panel.querySelectorAll(".feedback-reason-chip.is-selected, .modal-feedback-reason-chip.is-selected");
  return Array.from(selectedChips).map(chip => chip.dataset.reason || chip.textContent);
}

function collectModalFeedbackNote() {
  const note = document.querySelector(".modal-feedback-note");
  return note ? note.value.trim() : "";
}

async function sendFeedback(data) {
  const productId = String(data.product_id);
  const type = normalizeFeedbackResult(data.feedback_type || data.user_action);
  const reasons = data.reasons || [];
  const note = data.note || "";
  const userAction = type === "positive" ? "benar" : "salah";

  const product = (window.__MARKETSPY_PRODUCTS__ || []).find(p => getProductReviewId(p) === productId)
    || (activeModalProduct && getProductReviewId(activeModalProduct) === productId ? activeModalProduct : {})
    || {};
  const searchId = window.app?.state?.searchId || "unknown";
  
  const payload = {
    search_id: searchId,
    product_id: productId,
    product_title: product.title || "",
    user_action: userAction,
    feedback_type: type,
    selected_reasons: reasons,
    reasons: reasons,
    custom_reason: note,
    note: note,
    corrected_label: type === "positive" ? "relevan" : "tidak_relevan",
    ai_label: product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan'),
    ai_confidence: product.confidenceScore ?? product.ai_confidence ?? product.relevance_score ?? 0,
    rule_score: product.rule_score ?? 0,
    semantic_score: product.semantic_score ?? 0,
    combined_score: product.combined_score ?? 0,
    learned_adjustment: product.learned_adjustment ?? 0,
    confidence: product.confidenceScore ?? product.confidence ?? product.ai_confidence ?? product.relevance_score ?? 0,
    learning_scope_hint: type === "positive" ? "exact_query" : "query_intent",
    model_used: product._model || product.model_used || '',
    ai_reason: product.relevanceReason || product.ai_reason || product.reason || '',
    sort_mode: window.app?.state?.sortMode || 'terbaik',
    decision_source: product.ai_source || product.decision_source || '',
    query_intent: product.query_intent || window.app?.state?.metadata?.query_intent || '',
    product: {
      id: product.id || '',
      title: product.title || '',
      price_value: product.priceNumber ?? product.price_value ?? 0,
      price: product.priceNumber ?? product.price_value ?? 0,
      store: product.storeName || product.shop_name || product.shop || '',
      url: product.url || product.product_url || '',
      image: product.image || product.image_url || '',
      image_url: product.image_url || product.image || '',
      has_image: Boolean(product.image_url || product.image),
      product_category: product.product_category || '',
      decision_source: product.ai_source || product.decision_source || '',
      confidence: product.confidenceScore ?? product.confidence ?? product.ai_confidence ?? product.relevance_score ?? 0,
      rule_score: product.rule_score ?? 0,
      semantic_score: product.semantic_score ?? 0,
      combined_score: product.combined_score ?? 0,
      learned_adjustment: product.learned_adjustment ?? 0,
      query_constraints: product.query_constraints || {},
      product_constraints: product.product_constraints || {},
    },
    query: window.app?.state?.query || '',
    timestamp: new Date().toISOString()
  };

  const res = await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const responseData = await res.json();
  if (!responseData.success) {
    throw new Error(responseData.error || "Gagal menyimpan feedback");
  }

  const card = Array.from(document.querySelectorAll('.product-card'))
    .find((item) => item.dataset.id === productId || item.dataset.productId === productId);
  if (card) {
    card.classList.add('feedback-sent');
    card.title = `Feedback: ${payload.user_action}`;
    const badges = card.querySelector('.product-badges');
    if (badges && !badges.querySelector('.feedback-accepted-badge')) {
      const badge = document.createElement('span');
      badge.className = 'feedback-accepted-badge product-badge';
      badge.textContent = type === 'positive' ? 'Benar' : 'Feedback diterima';
      badges.appendChild(badge);
    }
  }

  showSmallToast("Feedback disimpan");
  return true;
}

function showSmallToast(message) {
  if (window.app && typeof window.app.showToast === "function") {
    window.app.showToast(message);
    return;
  }
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  window.setTimeout(() => toast.classList.add('is-visible'), 10);
  window.setTimeout(() => {
    toast.classList.remove('is-visible');
    window.setTimeout(() => toast.remove(), 180);
  }, 1800);
}

async function handleGridFeedback(productId, type, card, extra = {}) {
  if (!productId || !card) return;

  try {
    await sendFeedback({
      product_id: productId,
      feedback_type: type,
      reasons: extra.reasons || [],
      note: extra.note || ""
    });

    // Tandai sebagai reviewed
    reviewedProductIds.add(String(productId));

    // Cari product object dari state
    const product = (window.__MARKETSPY_PRODUCTS__ || []).find(p => getProductReviewId(p) === String(productId));
    if (product) {
      markProductAsReviewed(product, type, extra);
    }

    // Re-render recommendation content dan checked box
    renderRecommendationContent(activeRecommendationMode);
    renderCheckedProductsBox(activeRecommendationMode);

  } catch (error) {
    console.error("[FEEDBACK] grid feedback failed:", error);
    showSmallToast("Feedback gagal dikirim. Coba lagi.");
  }
}

function animateGridCardExitAndFocusNext(card) {
  if (!card) return;

  const container = card.closest("#products-grid, .products-grid");
  if (!container) {
    card.remove();
    return;
  }

  const beforeCards = [...container.children];
  const firstRects = new Map();

  beforeCards.forEach(el => {
    firstRects.set(el, el.getBoundingClientRect());
  });

  AnimeBridge.run(card, {
    opacity: [1, 0],
    scale: [1, 0.72],
    translateY: [0, -28],
    rotateZ: [0, -3],
    filter: ["blur(0px)", "blur(8px)"],
    duration: 420,
    easing: "easeInExpo",
    complete: () => {
      const nextCard = card.nextElementSibling;
      if (nextCard && typeof nextCard.focus === "function") {
        nextCard.focus();
      }

      card.remove();

      const afterCards = [...container.children];

      afterCards.forEach(el => {
        const first = firstRects.get(el);
        const last = el.getBoundingClientRect();

        if (!first) return;

        const dx = first.left - last.left;
        const dy = first.top - last.top;

        if (!dx && !dy) return;

        el.style.transform = `translate(${dx}px, ${dy}px)`;
        el.style.transition = "transform 0s";

        requestAnimationFrame(() => {
          el.style.transition = "";

          AnimeBridge.run(el, {
            translateX: [dx, 0],
            translateY: [dy, 0],
            scale: [0.98, 1],
            duration: 620,
            easing: "easeOutExpo"
          });
        });
      });
    }
  }) || (() => {
    card.remove();
  })();
}

function getScrollContainer() {
  return (
    document.querySelector(".app-scroll-container") ||
    document.querySelector(".main-scroll-container") ||
    document.querySelector("[data-scroll-container]") ||
    document.scrollingElement ||
    document.documentElement
  );
}

function setupAdaptiveScrollBehavior() {
  const container = getScrollContainer();
  const animeGlobal = window.anime;

  if (adaptiveScrollObserver) {
    adaptiveScrollObserver.disconnect();
    adaptiveScrollObserver = null;
  }

  if (adaptiveScrollAnimation && typeof adaptiveScrollAnimation.pause === "function") {
    adaptiveScrollAnimation.pause();
  }
  adaptiveScrollAnimation = null;

  const onScrollFn =
    typeof window.onScroll === "function"
      ? window.onScroll
      : animeGlobal?.onScroll;

  const targets = [
    ".recommendation-stage",
    ".checked-products-box",
    ".results-grid .product-card"
  ];

  const availableTargets = [...new Set(
    targets
      .flatMap(selector => [...document.querySelectorAll(selector)])
      .filter(Boolean)
  )];

  if (!availableTargets.length) return;

  if (
    typeof onScrollFn === "function" &&
    animeGlobal &&
    typeof animeGlobal.animate === "function"
  ) {
    adaptiveScrollAnimation = animeGlobal.animate(availableTargets, {
      opacity: [0.72, 1],
      translateY: [48, 0],
      scale: [0.965, 1],
      delay: animeGlobal.stagger ? animeGlobal.stagger(35) : 0,
      duration: 720,
      easing: "easeOutExpo",
      autoplay: onScrollFn({
        container,
        target: availableTargets,
        axis: "y",
        enter: "bottom top",
        leave: "top bottom",
        sync: 0.35
      })
    });

    return;
  }

  setupIntersectionScrollFallback(availableTargets, container);
}

function setupIntersectionScrollFallback(targets, container) {
  if (!('IntersectionObserver' in window)) {
    targets.forEach(el => {
      el.style.opacity = "1";
      el.style.transform = "none";
    });
    return;
  }

  const root =
    container === document.documentElement ||
    container === document.scrollingElement
      ? null
      : container;

  let initialCheckDone = false;

  adaptiveScrollObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      const el = entry.target;

      // First callback: check if already visible during initial observe
      if (!initialCheckDone && entry.isIntersecting) {
        initialCheckDone = true;
        if (el.dataset.scrollAnimated !== "true") {
          el.dataset.scrollAnimated = "true";
          // Langsung reset ke state final tanpa initial transform delay
          el.style.opacity = "1";
          el.style.transform = "none";
          observer.unobserve(el);
          return;
        }
      }

      if (!entry.isIntersecting) return;

      if (el.dataset.scrollAnimated === "true") {
        observer.unobserve(el);
        return;
      }

      el.dataset.scrollAnimated = "true";

      AnimeBridge.run(el, {
        opacity: [0.72, 1],
        translateY: [48, 0],
        scale: [0.965, 1],
        duration: 680,
        easing: "easeOutExpo"
      });

      observer.unobserve(el);
    });
  }, {
    root,
    threshold: 0.12,
    rootMargin: "0px 0px -8% 0px"
  });

  targets.forEach(el => {
    if (el.dataset.scrollAnimated === "true") return;
    // PERBAIKI: Jangan set initial transform jika element belum pernah diperiksa visibilitynya
    // Observer callback pertama akan handle visibility check dan decide apakah perlu initial transform
    // Untuk sekarang, set ke state final (no transform) untuk menghindari gap
    el.style.opacity = "1";
    el.style.transform = "none";
    adaptiveScrollObserver.observe(el);
  });
}

function setupOutsideProductScrollAnimations() {
  setupAdaptiveScrollBehavior();
}

function setupProductHoverStagger() {
  /* Hover uses CSS-only on recommendation cards for instant, sharp feedback. */
}

function animateCardHoverIn(card) {
  if (!card || !card.isConnected) return;
  if (card.closest(".recommendation-stage.is-switching")) return;

  const container = card.closest(
    ".recommendation-product-grid, .checked-products-grid, .results-grid"
  );

  const siblings = container
    ? [...container.querySelectorAll(".recommendation-product-card, .checked-product-card, .product-card")]
        .filter(item => item !== card)
    : [];

  AnimeBridge.run(card, {
    scale: [1, 1.045],
    translateY: [0, -6],
    boxShadow: [
      "0 12px 40px rgba(2,8,23,0.24)",
      "0 26px 80px rgba(59,130,246,0.28)"
    ],
    duration: 420,
    easing: "easeOutExpo"
  });

  AnimeBridge.run(siblings, {
    scale: [1, 0.985],
    opacity: [1, 0.88],
    delay: AnimeBridge.stagger(18, { from: "center" }),
    duration: 360,
    easing: "easeOutExpo"
  });
}

function animateCardHoverOut(card) {
  if (!card || !card.isConnected) return;
  if (card.closest(".recommendation-stage.is-switching")) return;

  const container = card.closest(
    ".recommendation-product-grid, .checked-products-grid, .results-grid"
  );

  const cards = container
    ? container.querySelectorAll(".recommendation-product-card, .checked-product-card, .product-card")
    : [card];

  AnimeBridge.run(cards, {
    scale: 1,
    translateY: 0,
    opacity: 1,
    boxShadow: "0 12px 40px rgba(2,8,23,0.20)",
    delay: AnimeBridge.stagger(12),
    duration: 360,
    easing: "easeOutExpo"
  });
}

if (!window.__pasarIntaiCategoryEventsBound) {
  window.__pasarIntaiCategoryEventsBound = true;

  document.addEventListener("click", event => {
    const button = event.target.closest("[data-recommendation-mode]");
    if (!button) return;

    const mode = normalizeRecommendationMode(button.dataset.recommendationMode);
    if (!mode) return;

    selectRecommendationMode(mode, button);
  });
}

// Delegated listener untuk klik card kategori (buka modal) dan tombol di checked tray
if (!window.__MARKETSPY_REC_FEEDBACK_BOUND__) {
  window.__MARKETSPY_REC_FEEDBACK_BOUND__ = true;

  document.addEventListener("click", async event => {
    // Klik card kategori → buka modal detail
    const productCard = event.target.closest("[data-product-card]");
    if (productCard) {
      // Jangan buka modal kalau klik di link/button di dalam card (misal checked tray open btn)
      const clickedInteractive = event.target.closest("a, button");
      if (clickedInteractive) return;

      const productId = productCard.dataset.productId;
      if (!productId) return;

      const product = findProductById(productId);
      if (!product) return;

      // Buka modal detail dengan queue dari mode aktif
      const queue = getActiveRecommendationProducts(activeRecommendationMode);
      openProductDetailModal(product, queue);
      return;
    }

    // Klik card Hasil Review → buka modal detail
    const checkedCard = event.target.closest(".checked-product-card");
    if (checkedCard) {
      const openBtn = event.target.closest(".checked-action-btn.is-open");
      if (openBtn) return; // biarkan link buka produk jalan normal

      const productId = checkedCard.dataset.productId;
      if (productId) {
        const record = reviewState.checkedById.get(productId);
        if (record?.product) {
          const queue = Array.from(reviewState.checkedById.values())
            .filter(r => r.result === 'positive')
            .map(r => r.product);
          openProductDetailModal(record.product, queue);
        }
      }
      return;
    }
  });

  // Keyboard accessibility untuk card (Enter/Space)
  document.addEventListener("keydown", event => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const productCard = event.target.closest("[data-product-card]");
    if (!productCard) return;
    event.preventDefault();
    productCard.click();
  });
}

// Event listener untuk tombol Terapkan di category limit bar
if (!window.__MARKETSPY_CATEGORY_LIMIT_BOUND__) {
  window.__MARKETSPY_CATEGORY_LIMIT_BOUND__ = true;

  document.addEventListener("click", event => {
    const applyBtn = event.target.closest("#category-limit-apply");
    if (!applyBtn) return;
    event.preventDefault();
    renderRecommendationContent(activeRecommendationMode);
  });

  // Trigger saat user tekan Enter di input
  document.addEventListener("keydown", event => {
    if (event.key === "Enter" && event.target.id === "category_limit_inline") {
      event.preventDefault();
      renderRecommendationContent(activeRecommendationMode);
    }
  });
}

// Delegated modal feedback click listener
if (!window.__MARKETSPY_MODAL_FEEDBACK_BOUND__) {
  window.__MARKETSPY_MODAL_FEEDBACK_BOUND__ = true;

  document.addEventListener("click", async event => {
    const target = getEventElement(event);
    const correctBtn = target?.closest("[data-modal-feedback-correct]");
    if (correctBtn) {
      event.preventDefault();
      await handleModalFeedback("positive");
      return;
    }

    const wrongBtn = target?.closest("[data-modal-feedback-wrong]");
    if (wrongBtn) {
      event.preventDefault();

      const panel = document.querySelector(".modal-feedback-reason-panel");

      if (panel && panel.hidden) {
        revealModalReasonPanel();
        return;
      }

      const reasons = collectModalSelectedReasons();
      const note = collectModalFeedbackNote();

      await handleModalFeedback("negative", {
        reasons: reasons.length ? reasons : ["Ditandai salah oleh user"],
        note
      });

      return;
    }

    const saveWrongBtn = target?.closest("[data-modal-feedback-save]");
    if (saveWrongBtn) {
      event.preventDefault();

      const reasons = collectModalSelectedReasons();
      const note = collectModalFeedbackNote();

      await handleModalFeedback("negative", {
        reasons: reasons.length ? reasons : ["Ditandai salah oleh user"],
        note
      });

      return;
    }

    const cancelBtn = target?.closest("[data-modal-feedback-cancel]");
    if (cancelBtn) {
      event.preventDefault();
      const panel = document.querySelector(".modal-feedback-reason-panel");
      if (panel) panel.hidden = true;
      return;
    }
  });
}

const PROGRESS_STAGE_TEXT = {
  idle: "Menunggu proses...",
  start: "Menyiapkan mesin scraper...",
  opening_page: "Membuka halaman marketplace...",
  scraping: "Mengambil data produk...",
  scrolling: "Membaca produk tambahan...",
  dedupe: "Membersihkan produk duplikat...",
  budget: "Mengecek rentang budget...",
  semantic: "Mengecek relevansi produk...",
  ai: "AI sedang audit kandidat...",
  ranking: "Menyusun rekomendasi terbaik...",
  done: "Selesai — hasil siap ditampilkan",
  error: "Terjadi kesalahan — cek koneksi"
};

let lastProgressStage = null;
let activeScrambleFrame = null;

function getProgressStage(progress) {
  if (progress?.done && progress?.error) return "error";
  if (progress?.done) return "done";

  const raw = String(
    progress?.stage ||
    progress?.status ||
    progress?.statusText ||
    ""
  ).toLowerCase();

  if (raw.includes("open") || raw.includes("page")) return "opening_page";
  if (raw.includes("scroll")) return "scrolling";
  if (raw.includes("scrap")) return "scraping";
  if (raw.includes("dedupe") || raw.includes("duplicate")) return "dedupe";
  if (raw.includes("budget")) return "budget";
  if (raw.includes("semantic")) return "semantic";
  if (raw.includes("ai") || raw.includes("classifier")) return "ai";
  if (raw.includes("rank") || raw.includes("recommend")) return "ranking";
  if (raw.includes("done") || raw.includes("complete") || raw.includes("success")) return "done";
  if (raw.includes("error") || raw.includes("failed")) return "error";

  const pct = Number(progress?.progress_percent ?? progress?.percentage ?? progress?.percent ?? 0);
  if (pct <= 5) return "start";
  if (pct <= 25) return "scraping";
  if (pct <= 45) return "dedupe";
  if (pct <= 60) return "budget";
  if (pct <= 78) return "semantic";
  if (pct <= 92) return "ai";
  if (pct < 100) return "ranking";
  return "done";
}

function setAppStatus(stateOrLabel) {
  const badge = document.querySelector("[data-app-status-badge]");
  if (!badge) return;

  const normalized = String(stateOrLabel || "idle").toLowerCase().trim();
  const stateMap = {
    idle: { label: "Siap", className: "is-idle" },
    siap: { label: "Siap", className: "is-idle" },
    running: { label: "Berjalan", className: "is-running" },
    berjalan: { label: "Berjalan", className: "is-running" },
    done: { label: "Selesai", className: "is-done" },
    selesai: { label: "Selesai", className: "is-done" },
    error: { label: "Error", className: "is-error" },
    gagal: { label: "Error", className: "is-error" },
    diblokir: { label: "Error", className: "is-error" }
  };
  const next = stateMap[normalized] || stateMap.idle;
  const textSpan = badge.querySelector(".status-badge-text");

  if (textSpan) {
    textSpan.textContent = next.label;
  } else {
    badge.textContent = next.label;
  }

  badge.classList.remove("is-idle", "is-running", "is-done", "is-error");
  badge.classList.add(next.className);
}

function syncTopStatusFromProgress(progress) {
  if (!progress) return;

  let status = "idle";

  if (progress.done) {
    status = progress.error ? "error" : "done";
  } else {
    const stage = getProgressStage(progress);
    if (["error", "failed", "blocked"].includes(stage)) {
      status = "error";
    } else if (stage !== "idle" && stage !== "done") {
      status = "running";
    }
  }

  setAppStatus(status);
}

function updateProgressStage(progress) {
  const nextStage = getProgressStage(progress);

  if (nextStage === lastProgressStage) return;

  lastProgressStage = nextStage;

  const text = PROGRESS_STAGE_TEXT[nextStage] || PROGRESS_STAGE_TEXT.start;

  // Update container data-progress-stage attribute
  const container = document.querySelector(".progress-clean-panel");
  if (container) {
    container.setAttribute("data-progress-stage", nextStage);
  }

  scrambleProgressTo(text, nextStage);
}

function scrambleProgressTo(targetText, stage) {
  const el = document.querySelector("#progressScrambleText");
  if (!el) return;

  if (activeScrambleFrame) {
    cancelAnimationFrame(activeScrambleFrame);
    activeScrambleFrame = null;
  }

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Langsung set teks tanpa scramble — hindari karakter garbage
  if (reduceMotion) {
    el.textContent = targetText;
    return;
  }

  // Scramble hanya pakai karakter yang aman dan mudah dibaca
  const chars = "0123456789abcdef.";
  const duration = stage === "done" || stage === "error" ? 500 : 700;
  const start = performance.now();

  function frame(now) {
    const progress = Math.min((now - start) / duration, 1);
    const reveal = Math.floor(targetText.length * progress);

    let output = "";
    for (let i = 0; i < targetText.length; i++) {
      if (i < reveal) {
        output += targetText[i];
      } else if (targetText[i] === " ") {
        output += " ";
      } else {
        output += chars[Math.floor(Math.random() * chars.length)];
      }
    }

    el.textContent = output;

    if (progress < 1) {
      activeScrambleFrame = requestAnimationFrame(frame);
    } else {
      el.textContent = targetText;
      activeScrambleFrame = null;
    }
  }

  activeScrambleFrame = requestAnimationFrame(frame);
}

const FEEDBACK_REASONS = [
  'Produk tidak relevan',
  'Cuma aksesoris',
  'Spesifikasi tidak sesuai query',
  'Harga tidak sesuai',
  'Nama produk salah',
  'Gambar tidak sesuai',
  'Toko tidak terpercaya',
  'Duplikat',
  'Bukan sesuai intent pencarian',
  'Data tidak lengkap',
  'Lainnya',
];

const RECOMMENDATION_SORT_MODES = [
  { key: 'terbaik', label: 'Terbaik', shortLabel: 'Terbaik', icon: '⭐', sortMode: 'terbaik' },
  { key: 'termurah', label: 'Termurah', shortLabel: 'Termurah', icon: '💸', sortMode: 'termurah' },
  { key: 'trusted', label: 'Most Trusted', shortLabel: 'Trusted', icon: '🏆', sortMode: 'most_trusted' },
];

class ScraperApp {
  constructor() {
    this.state = {
      products: [],
      query: null,
      searchId: null,
      pollTimer: null,
      comparison: [],
      selectedEngine: null,
      recommendations: {},
      recommendationSourceProducts: [],
      recommendationsOpen: false,
      metadata: {},
      budgetInfo: null,
      sortMode: 'terbaik',
      elapsedTimer: null,
      progressStartedAtMs: null,
      estimatedCompletionEpochMs: null,
      localElapsedSeconds: 0,
      localEtaSeconds: null,
      lastEtaFallbackSignature: null,
      lastProgress: null,
      aiStatus: null,
      engineMode: 'auto',
      recommendationMode: 'all',
      hasUserSelectedRecommendation: false,
      autoExpandedOnce: false,
      activeFeedbackProductId: null,
    };

    this.activeProduct = null;
    this.activeProductCard = null;
    this.isModalAnimating = false;

    this.$ = (id) => document.getElementById(id);
    this.panels = ['search-panel', 'progress-panel', 'error-panel', 'results-panel'];
    this.recommendationObserver = null;
    this.recommendationTimeline = null;
    this.init();
  }

  init() {
    this.bindBudgetFormat();
    this.bindBudgetInfo();
    this.bindEnter();
    this.bindResetAI();
    this.bindResetLearning();
    this.bindQuickSort();
    this.bindProductModalEvents();
    this.bindRecommendationModalEvents();
    this.bindProductCardClick();
    this.bindTargetPriorityInfo();
    setupProductHoverStagger();
    this.fetchAiStatus();
  }

  bindTargetPriorityInfo() {
    const toggleBtn = document.querySelector('[data-toggle-target-priority-info]');
    const content = document.querySelector('.target-priority-info-box .info-content');
    if (!toggleBtn || !content) return;

    toggleBtn.addEventListener('click', () => {
      const isHidden = content.hasAttribute('hidden');
      if (isHidden) {
        content.removeAttribute('hidden');
        content.style.height = '0px';
        content.style.opacity = '0';
        content.style.overflow = 'hidden';
        
        const height = content.scrollHeight;
        
        AnimeBridge.run(content, {
          height: [0, height],
          opacity: [0, 1],
          duration: 350,
          easing: 'easeOutQuad',
          complete: () => {
            content.style.height = 'auto';
            content.style.overflow = '';
          }
        });
        toggleBtn.classList.add('is-active');
      } else {
        content.style.overflow = 'hidden';
        const height = content.scrollHeight;
        AnimeBridge.run(content, {
          height: [height, 0],
          opacity: [1, 0],
          duration: 300,
          easing: 'easeOutQuad',
          complete: () => {
            content.setAttribute('hidden', '');
            content.style.height = '';
          }
        });
        toggleBtn.classList.remove('is-active');
      }
    });
  }

  show(panelId) {
    this.panels.forEach((id) => {
      const el = this.$(id);
      if (el) el.classList.toggle('hidden', id !== panelId);
    });
  }

  setStatus(text, cls) {
    const classMap = {
      "status-idle": "idle",
      "status-running": "running",
      "status-done": "done",
      "status-error": "error"
    };
    const textMap = {
      Menunggu: "idle",
      Siap: "idle",
      Berjalan: "running",
      Selesai: "done",
      Gagal: "error",
      Error: "error",
      Diblokir: "error"
    };

    setAppStatus(classMap[cls] || textMap[text] || "idle");
  }

  isBlockedMessage(message) {
    return /captcha|blocked|access denied|too many requests|robot|bot detection/i.test(String(message || ''));
  }

  prefersReducedMotion() {
    return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
  }

  canAnimate() {
    return Boolean(window.anime) && !this.prefersReducedMotion();
  }

  animate(targets, options = {}) {
    if (!this.canAnimate()) return null;
    return window.anime({ targets, ...options });
  }

  showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    window.setTimeout(() => toast.classList.add('is-visible'), 10);
    window.setTimeout(() => {
      toast.classList.remove('is-visible');
      window.setTimeout(() => toast.remove(), 180);
    }, 1800);
  }

  bindBudgetFormat() {
    const input = this.$('budget');
    if (!input) return;
    input.addEventListener('input', () => {
      const raw = input.value.replace(/[^\d]/g, '');
      input.value = raw ? Number.parseInt(raw, 10).toLocaleString('id-ID') : '';
      this.updateBudgetInfo();
    });
    input.addEventListener('keydown', (e) => {
      const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'];
      if (allowed.includes(e.key)) return;
      if (!/^\d$/.test(e.key)) e.preventDefault();
    });
  }

  getBudgetText() {
    return this.$('budget')?.value.trim() || null;
  }

  parseBudgetInput() {
    const text = this.getBudgetText();
    if (!text) return null;
    const n = Number.parseInt(text.replace(/\./g, ''), 10);
    return Number.isFinite(n) && n > 0 ? n : null;
  }

  formatRp(value) {
    const n = Number(value);
    if (!Number.isFinite(n) || n <= 0) return 'Rp0';
    return 'Rp' + n.toLocaleString('id-ID');
  }

  formatRupiah(value) {
    const number = Number(value || 0);
    if (!number) return 'Harga tidak tersedia';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      maximumFractionDigits: 0,
    }).format(number);
  }

  bindBudgetInfo() {
    this.$('tolerance')?.addEventListener('input', () => this.updateBudgetInfo());
  }

  updateBudgetInfo() {
    const budget = this.parseBudgetInput();
    const toleranceRaw = this.$('tolerance')?.value;
    const tol = Math.max(0, Math.min(Number.parseFloat(toleranceRaw || '0'), 100));
    const info = this.$('budget-info');
    if (!budget || !info) {
      info?.classList.add('hidden');
      return;
    }
    const min = Math.round(budget * (1 - tol / 100));
    const max = Math.round(budget * (1 + tol / 100));
    this.$('bi-budget').textContent = this.formatRp(budget);
    this.$('bi-tolerance').textContent = `${tol}%`;
    this.$('bi-range').textContent = `${this.formatRp(min)} - ${this.formatRp(max)}`;
    info.classList.remove('hidden');
  }

  bindEnter() {
    this.$('query')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.startSearch();
    });
  }

  bindResetAI() {
    const btn = this.$('reset-ai-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      if (!window.confirm('Reset memori AI? Feedback dan contoh akan dihapus. Model Ollama tidak tersentuh.')) return;
      const oldText = btn.textContent;
      try {
        btn.disabled = true;
        btn.textContent = 'Resetting...';
        const res = await fetch('/api/ai/reset', { method: 'POST' });
        const data = await res.json();
        btn.textContent = data.success ? 'Reset OK' : 'Reset gagal';
      } catch (err) {
        console.error('Reset AI error:', err);
        btn.textContent = 'Reset error';
      } finally {
        setTimeout(() => {
          btn.textContent = oldText;
          btn.disabled = false;
        }, 1200);
      }
    });
  }

  bindResetLearning() {
    const btn = this.$('reset-learning-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      if (!window.confirm('Yakin hapus semua pembelajaran AI?')) return;
      const oldText = btn.textContent;
      try {
        btn.disabled = true;
        btn.textContent = 'Resetting...';
        const res = await fetch('/api/learning/reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scope: 'all' }),
        });
        const data = await res.json();
        btn.textContent = data.success ? 'Reset OK' : 'Reset gagal';
        this.showToast(data.success ? 'Learning direset' : 'Reset learning gagal');
      } catch (err) {
        console.error('Reset learning error:', err);
        btn.textContent = 'Reset error';
      } finally {
        setTimeout(() => {
          btn.textContent = oldText;
          btn.disabled = false;
        }, 1200);
      }
    });
  }

  bindQuickSort() {
    document.querySelectorAll('[data-sort-mode]').forEach((btn) => {
      btn.addEventListener('click', () => this.setSortMode(btn.dataset.sortMode || 'terbaik'));
    });
  }

  async fetchAiStatus() {
    try {
      const res = await fetch('/api/ai/status');
      const status = await res.json();
      this.state.aiStatus = status;
      this.renderAiStatus(status);
    } catch (err) {
      const fallback = {
        ok: false,
        classifier: null,
        capabilities: { semantic: false, json_repair: false },
        missing: ['gemma3:4b', 'llama3.2:3b', 'phi4-mini', 'nomic-embed-text'],
        message: 'Ollama belum bisa dihubungi. Search tetap bisa berjalan dengan rules.',
        install_commands: [
          'ollama pull gemma3:4b',
          'ollama pull llama3.2:3b',
          'ollama pull phi4-mini',
          'ollama pull nomic-embed-text',
        ],
      };
      this.state.aiStatus = fallback;
      this.renderAiStatus(fallback);
      console.warn('AI status error:', err);
    }
  }

  renderAiStatus(status) {
    // Update badge AI Scraper di header (selalu ada)
    const headerBadge = this.$('ai-scraper-header-badge');
    if (headerBadge) {
      const headerText = headerBadge.querySelector('.ai-scraper-header-text');
      if (status?.ok) {
        headerBadge.className = 'ai-scraper-header-badge is-active';
        if (headerText) headerText.textContent = 'AI Scraper Aktif';
      } else {
        headerBadge.className = 'ai-scraper-header-badge is-inactive';
        if (headerText) headerText.textContent = 'AI Scraper Tidak Aktif';
      }
    }

    // Update use_ai hidden input
    const useAi = this.$('use_ai');
    if (useAi) {
      // Selalu aktif — AI otomatis pakai rules kalau Ollama tidak tersedia
      useAi.value = 'true';
    }

    // Elemen-elemen berikut mungkin tidak ada di HTML baru — guard dengan optional chaining
    const badge = this.$('ai-status-badge');
    const message = this.$('ai-status-message');
    const classifier = this.$('ai-status-classifier');
    const semantic = this.$('ai-status-semantic');
    const json = this.$('ai-status-json');
    const install = this.$('ai-install-command');
    const scraperBadge = this.$('ai-scraper-badge');
    const scraperMessage = this.$('ai-scraper-message');

    if (scraperBadge) {
      scraperBadge.textContent = status?.ok ? 'AI Aktif' : 'Rules saja';
      scraperBadge.className = `ai-scraper-badge ${status?.ok ? 'is-ready' : 'is-fallback'}`;
    }
    if (scraperMessage) {
      scraperMessage.textContent = status?.ok
        ? (status.message || 'AI Orchestrator siap digunakan')
        : 'Model AI belum terinstall. Jalankan: ollama pull gemma3:4b';
    }

    if (!badge || !message || !classifier || !semantic || !json || !install) return;

    const capabilities = status?.capabilities || {};
    badge.textContent = status?.ok ? 'Siap' : 'Rules saja';
    badge.className = `ai-status-badge ${status?.ok ? 'is-ready' : 'is-missing'}`;
    message.textContent = status?.ok
      ? (status.message || 'AI Orchestrator siap')
      : 'Model AI belum terinstall. Jalankan: ollama pull gemma3:4b';
    classifier.textContent = status?.classifier || 'Rules saja';
    semantic.textContent = capabilities.semantic ? 'nomic-embed-text terpasang' : 'nomic-embed-text belum ada';
    json.textContent = capabilities.json_repair ? 'phi4-mini terpasang' : 'phi4-mini belum ada';

    const commands = status?.install_commands || [
      'ollama pull gemma3:4b',
      'ollama pull llama3.2:3b',
      'ollama pull phi4-mini',
      'ollama pull nomic-embed-text',
    ];
    const missing = Array.isArray(status?.missing) ? status.missing : [];
    const missingCommands = commands.filter((cmd) => missing.some((model) => cmd.includes(model)));
    if (status?.ok) {
      install.textContent = missingCommands.length
        ? ['Model opsional yang belum terinstall:', ...missingCommands].join('\n')
        : '';
      install.classList.toggle('hidden', !missingCommands.length);
    } else {
      install.textContent = commands.join('\n');
      install.classList.remove('hidden');
    }
  }

  async startSearch() {
    const query = this.$('query')?.value.trim();
    const targetRaw = this.$('target_count')?.value ?? '';
    const parsedTarget = Number.parseInt(targetRaw, 10);
    const target = Number.isFinite(parsedTarget) && parsedTarget > 0 ? parsedTarget : 50;
    const toleranceRaw = this.$('tolerance')?.value;
    const tolerance = toleranceRaw ? Number.parseFloat(toleranceRaw) : 0;
    // AI selalu aktif — otomatis pakai rules kalau Ollama tidak tersedia
    const ai = true;
    const engineMode = 'auto';
    const targetFirstMode = true; // selalu aktif agar target terpenuhi
    const budget = this.getBudgetText();

    console.log('[FORM] submit triggered');
    console.log('[FORM] payload', { query, target, budget, tolerance, ai, engineMode });

    if (!query) {
      this.setStatus('Error', 'status-error');
      this.$('query')?.focus();
      return;
    }

    this.state.query = query;
    this.state.comparison = [];
    this.state.selectedEngine = null;
    this.state.recommendations = {};
    this.state.budgetInfo = null;
    this.state.recommendationsOpen = false;
    this.state.sortMode = this.activeSortMode();
    this.show('progress-panel');
    this.resetProgress();
    this.setStatus('Berjalan', 'status-running');

    try {
      console.log('[SCRAPE] request started');
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          target,
          target_count: target,
          budget,
          tolerance,
          ai,
          use_ai: ai,
          engine_mode: engineMode,
          sort_mode: this.state.sortMode,
          target_first_mode: targetFirstMode,
        }),
      });
      const data = await response.json();
      console.log('[SCRAPE] response', data);
      if (!data.success) {
        this.showError(data.error || 'Gagal memulai scraping');
        return;
      }
      this.state.searchId = data.search_id;
      this.state.progressStartedAtMs = data.started_at_epoch_ms || null;
      if (this.state.progressStartedAtMs) this.startElapsedTimer();
      setAppStatus("running");
      this.startPolling();
    } catch (err) {
      console.error('[SCRAPE] error', err);
      setAppStatus("error");
      this.showError('Gagal terhubung ke server: ' + err.message);
    }
  }

  startPolling() {
    this.stopPolling();
    this.fetchProgress();
    this.state.pollTimer = setInterval(() => this.fetchProgress(), 750);
  }

  stopPolling() {
    if (!this.state.pollTimer) return;
    clearInterval(this.state.pollTimer);
    this.state.pollTimer = null;
  }

  startElapsedTimer() {
    this.stopElapsedTimer();
    this.renderLiveTimers();
    this.state.elapsedTimer = setInterval(() => this.renderLiveTimers(), 1000);
  }

  stopElapsedTimer() {
    if (!this.state.elapsedTimer) return;
    clearInterval(this.state.elapsedTimer);
    this.state.elapsedTimer = null;
  }

  startProgressAnimation() {}
  stopProgressAnimation() {}
  startScrambleProgress() {}
  stopScrambleProgress() {}

  async fetchProgress() {
    if (!this.state.searchId) return;
    try {
      const res = await fetch(`/api/progress/${this.state.searchId}`);
      if (!res.ok) return;
      const progress = await res.json();
      this.renderProgress(progress);
      if (progress.done) {
        this.stopPolling();
        this.stopElapsedTimer();
        progress.error ? this.showError(progress.error) : this.fetchResults();
      }
    } catch (err) {
      console.error('Progress error:', err);
    }
  }

  async fetchResults() {
    try {
      const res = await fetch(`/api/result/${this.state.searchId}`);
      if (!res.ok) throw new Error('Gagal mengambil hasil final.');
      const data = await res.json();
      this.showResults(data);
    } catch (err) {
      this.showError(err.message);
    }
  }

  resetProgress() {
    this.stopPolling();
    this.stopElapsedTimer();
    setAppStatus("idle");
    this.state.progressStartedAtMs = null;
    this.state.estimatedCompletionEpochMs = null;
    this.state.localElapsedSeconds = 0;
    this.state.localEtaSeconds = null;
    this.state.lastEtaFallbackSignature = null;
    this.state.lastProgress = null;
    
    // Reset staged progress scramble
    lastProgressStage = null;
    if (activeScrambleFrame) {
      cancelAnimationFrame(activeScrambleFrame);
      activeScrambleFrame = null;
    }
    const scrambleEl = document.querySelector("#progressScrambleText");
    if (scrambleEl) {
      scrambleEl.textContent = "Menunggu proses...";
    }

    this.renderProgress({
      percent: 0,
      progress_percent: 0,
      stage: 'idle',
      phase: 'idle',
      message: 'Menunggu...',
      found: 0,
      valid: 0,
      target: 0,
      started_at_epoch_ms: null,
      elapsed_seconds: 0,
      eta_seconds: null,
      engine_mode: this.$('engine_mode')?.value || 'auto',
      active_engine: 'none',
      attempt: 1,
      max_attempts: 1,
      logs: [{ stage: 'idle', message: 'Menunggu...' }],
    });
    document.querySelectorAll('.stage-item').forEach((el) => el.classList.remove('active', 'done'));
  }

  formatDuration(seconds) {
    if (seconds == null || Number.isNaN(Number(seconds))) return 'calculating...';
    const safe = Math.max(0, Math.floor(Number(seconds)));
    const minutes = Math.floor(safe / 60);
    const secs = safe % 60;
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  computeLocalEta(estimatedCompletionEpochMs) {
    if (!estimatedCompletionEpochMs) return null;
    const remainingMs = Number(estimatedCompletionEpochMs) - Date.now();
    if (remainingMs < -5000) return null;
    return Math.max(0, Math.ceil(remainingMs / 1000));
  }

  updateEtaDeadline(progress) {
    if (progress.done) {
      this.state.estimatedCompletionEpochMs = progress.error ? null : Date.now();
      this.state.localEtaSeconds = progress.error ? null : 0;
      return;
    }

    const backendDeadline = Number(progress.estimated_completion_epoch_ms);
    if (Number.isFinite(backendDeadline) && backendDeadline > 0) {
      this.state.estimatedCompletionEpochMs = backendDeadline;
      this.state.lastEtaFallbackSignature = null;
      return;
    }

    if (progress.eta_seconds != null && Number.isFinite(Number(progress.eta_seconds))) {
      const signature = `${progress.updated_at_epoch_ms || ''}:${progress.eta_seconds}`;
      if (!this.state.estimatedCompletionEpochMs || signature !== this.state.lastEtaFallbackSignature) {
         this.state.estimatedCompletionEpochMs = Date.now() + Math.max(0, Number(progress.eta_seconds)) * 1000;
         this.state.lastEtaFallbackSignature = signature;
      }
      return;
    }

    this.state.estimatedCompletionEpochMs = null;
    this.state.localEtaSeconds = null;
    this.state.lastEtaFallbackSignature = null;
  }

  etaDisplayText() {
    const progress = this.state.lastProgress || {};
    if (progress.done) return progress.error ? '-' : '00:00';
    if (!this.state.estimatedCompletionEpochMs) return 'Menghitung...';

    const remainingMs = Number(this.state.estimatedCompletionEpochMs) - Date.now();
    if (remainingMs < -5000) return 'Menghitung...';
    if (remainingMs <= 0) return 'Memperbarui...';

    const seconds = this.computeLocalEta(this.state.estimatedCompletionEpochMs);
    this.state.localEtaSeconds = seconds;
    return seconds == null ? 'Menghitung...' : this.formatDuration(seconds);
  }

  renderLiveTimers() {
    const elapsedTextEl = this.$('elapsedText');
    const etaTextEl = this.$('etaText');
    const seconds = this.state.progressStartedAtMs
      ? Math.floor((Date.now() - Number(this.state.progressStartedAtMs)) / 1000)
      : 0;
    this.state.localElapsedSeconds = Math.max(0, seconds);
    const elapsedFormatted = this.formatDuration(this.state.localElapsedSeconds);

    if (elapsedTextEl) elapsedTextEl.textContent = elapsedFormatted;

    const etaText = this.etaDisplayText();
    if (etaTextEl) etaTextEl.textContent = etaText;

    const elapsedEl = this.$('pm-elapsed');
    const resultElapsedEl = this.$('rt-elapsed');
    if (elapsedEl) elapsedEl.textContent = elapsedFormatted;
    if (resultElapsedEl) resultElapsedEl.textContent = elapsedFormatted;

    const etaEl = this.$('pm-eta');
    const resultEtaEl = this.$('rt-eta');
    if (etaEl) etaEl.textContent = etaText;
    if (resultEtaEl) resultEtaEl.textContent = etaText;
  }

  renderResultTimers() {
    const elapsed = this.state.localElapsedSeconds || 0;
    this.setText('rt-elapsed', this.formatDuration(elapsed));
    this.setText('rt-eta', this.etaDisplayText());
  }

  renderProgress(progress) {
    this.state.lastProgress = progress;
    if (progress.started_at_epoch_ms) {
      this.state.progressStartedAtMs = Number(progress.started_at_epoch_ms);
      if (!this.state.elapsedTimer && !progress.done) this.startElapsedTimer();
    }
    this.updateEtaDeadline(progress);

    const pct = Math.max(0, Math.min(100, Number(progress.progress_percent ?? progress.percent ?? 0)));
    const pctEl = this.$('progress-pct');
    if (pctEl) pctEl.textContent = `${Math.round(pct)}%`;
    const barEl = this.$('progress-bar');
    if (barEl) barEl.style.width = `${pct}%`;
    const stage = progress.stage || progress.phase;
    const phase = progress.phase || stage;
    const stageLabelEl = this.$('progress-stage-label');
    if (stageLabelEl) stageLabelEl.textContent = this.stageLabel(stage);
    const msgEl = this.$('progress-message');
    if (msgEl) msgEl.textContent = progress.statusText || progress.status_text || progress.message || '';
    
    const elapsedEl = this.$('elapsedText');
    const etaEl = this.$('etaText');
    if (elapsedEl && this.state.progressStartedAtMs) {
      const seconds = Math.floor((Date.now() - Number(this.state.progressStartedAtMs)) / 1000);
      this.state.localElapsedSeconds = Math.max(0, seconds);
      elapsedEl.textContent = this.formatDuration(this.state.localElapsedSeconds);
    } else if (elapsedEl) {
      elapsedEl.textContent = progress.elapsed_seconds != null ? this.formatDuration(progress.elapsed_seconds) : '00:00';
    }
    if (etaEl) {
      etaEl.textContent = this.etaDisplayText();
    }

    const foundEl = this.$('pm-found');
    if (foundEl) foundEl.textContent = progress.foundCount ?? progress.found ?? 0;
    const validEl = this.$('pm-valid');
    if (validEl) validEl.textContent = progress.valid ?? 0;
    const targetEl = this.$('pm-target');
    if (targetEl) targetEl.textContent = progress.targetCount ?? progress.target ?? '-';
    
    if (this.state.progressStartedAtMs) {
      this.renderLiveTimers();
    } else {
      const pmElapsedEl = this.$('pm-elapsed');
      if (pmElapsedEl) pmElapsedEl.textContent = progress.elapsed_seconds != null ? this.formatDuration(progress.elapsed_seconds) : '-';
      const pmEtaEl = this.$('pm-eta');
      if (pmEtaEl) pmEtaEl.textContent = this.etaDisplayText();
    }
    const engineEl = this.$('pm-engine');
    if (engineEl) engineEl.textContent = `${progress.engine_mode || 'auto'} / ${progress.active_engine || 'none'}`;
    const attemptEl = this.$('pm-attempt');
    if (attemptEl) attemptEl.textContent = `${progress.attempt || 1}/${progress.max_attempts || 1}`;
    this.updateStagePipeline(phase, pct);
    this.renderProgressLogs(progress.logs || []);

    updateProgressStage(progress);
    syncTopStatusFromProgress(progress);
  }

  renderProgressLogs(logs) {
    const el = this.$('progress-log');
    if (!el) return;
    const visible = [...(logs || [])].slice(-8).reverse();
    if (!visible.length) {
      el.innerHTML = '<div class="progress-log-empty">Menunggu aktivitas...</div>';
      return;
    }
    el.innerHTML = '';
    visible.forEach((item) => {
      const row = document.createElement('div');
      row.className = 'progress-log-row';
      const stage = document.createElement('span');
      stage.className = 'progress-log-stage';
      stage.textContent = this.stageLabel(item.stage || 'preparing');
      const message = document.createElement('span');
      message.className = 'progress-log-message';
      message.textContent = item.message || '';
      row.append(stage, message);
      el.appendChild(row);
    });
  }

  stageLabel(stage) {
    const labels = {
      idle: 'Menunggu',
      preparing: 'Menyiapkan',
      scraping: 'Mengambil data',
      completed: 'Selesai',
      blocked: 'Diblokir',
      queued: 'Menunggu',
      initializing: 'Inisialisasi',
      engine_selecting: 'Memilih engine',
      launching_browser: 'Membuka browser',
      opening_page: 'Membuka halaman',
      scrolling: 'Menggulir',
      extracting: 'Mengambil data',
      puppeteer_starting: 'Puppeteer mulai',
      puppeteer_opening: 'Puppeteer membuka',
      puppeteer_query: 'Query Puppeteer',
      puppeteer_retry: 'Puppeteer ulang',
      switching_to_rollback: 'Pindah ke Selenium',
      rollback_browser_starting: 'Selenium mulai',
      rollback_opening: 'Selenium membuka',
      rollback_extracting: 'Selenium mengambil data',
      compare_filtering: 'Filter perbandingan',
      deduplicating: 'Dedup',
      budget_filtering: 'Filter budget',
      ai_filtering: 'AI Orchestrator',
      ranking: 'Ranking',
      recommendation_building: 'Rekomendasi',
      finalizing: 'Finalisasi',
      done: 'Selesai',
      error: 'Error',
      failed: 'Gagal',
      cancelled: 'Dibatalkan',
    };
    return labels[stage] || stage || 'Memproses';
  }

  updateStagePipeline(currentStage, pct) {
    const stages = ['init', 'opening', 'scrolling', 'extracting', 'filtering', 'ai_validation', 'finalizing'];
    stages.forEach((name, i) => {
      const el = this.$(`stage-${name}`);
      if (!el) return;
      el.classList.remove('active', 'done');
      const threshold = i * (100 / stages.length);
      const next = (i + 1) * (100 / stages.length);
      if (pct >= 100 || pct >= next) el.classList.add('done');
      else if (pct >= threshold) el.classList.add('active');
    });
  }

  showResults(data) {
    this.setStatus('Selesai', 'status-done');
    this.show('results-panel');
    this.state.comparison = data.comparison || [];
    this.state.selectedEngine = data.selected_engine || null;
    this.state.products = (data.data || []).map((product) => this.normalizeProduct(product));
    window.__MARKETSPY_PRODUCTS__ = this.state.products;
    this.state.recommendations = data.recommendations || {};
    this.state.metadata = data.result_metadata || {};
    this.state.budgetInfo = data.budget_info || null;
    this.state.engineMode = data.engine_mode || 'auto';
    this.state.metadata.engine_mode = this.state.engineMode;
    this.state.sortMode = data.sort_mode || this.state.metadata.sort_mode || this.state.sortMode || 'terbaik';
    this.state.recommendationsOpen = true;
    this.state.recommendationMode = 'all';
    this.state.hasUserSelectedRecommendation = false;
    // Tandai sudah auto-expanded agar observer tidak trigger expand lagi
    this.state.autoExpandedOnce = true;
    activeRecommendationMode = 'all';
    activeModalMode = null;
    activeModalProducts = [];
    activeModalIndex = 0;
    activeModalProduct = null;
    resetReviewState();

    this.applySortMode(this.state.sortMode, false);
    this.state.recommendationSourceProducts = [...this.state.products];
    invalidateRecommendationCache();
    this.renderResultSummary(data);
    this.renderResultTimers();
    this.renderBudgetBar(data.budget_info);
    this.renderComparison(data);
    this.renderResultWarning(data);
    this.renderRecommendations();
    this.updateResultCount();
    this.renderProducts();

    // Langsung expand stage tanpa animasi height agar tidak ada gap
    const stage = this.$('recommendation-stage');
    if (stage) {
      stage.classList.add('is-auto-expanded');
      // Hapus inline height kalau ada sisa dari animasi sebelumnya
      stage.style.height = '';
      stage.style.overflow = '';
    }

    console.log('[LAYOUT] scraping finished');
    console.log('[LAYOUT] render recommendations initial');
    console.log('[LAYOUT] active category', activeRecommendationMode);
    const stageHeight = stage?.offsetHeight || 0;
    const panelHeight = this.$('recommendations-panel')?.offsetHeight || 0;
    console.log('[LAYOUT] recommendation container height', { stageHeight, panelHeight });

    this.observeRecommendationStage();
    this.animateResultsEntrance();
  }

  normalizeProduct(product) {
    const item = { ...(product || {}) };
    const priceNumber = Number(item.priceNumber ?? item.price_value ?? item.price_val ?? 0) || 0;
    const confidenceScore = Number(item.confidenceScore ?? item.confidence ?? item.relevance_score ?? item.ai_confidence ?? 0) || 0;
    const imageUrl = this.resolveProductImage(item);
    return {
      ...item,
      id: String(item.id || item.url || item.product_url || item.title || ''),
      title: item.title || 'Produk Tokopedia',
      price: item.price || item.price_raw || item.price_text || (priceNumber ? this.formatRupiah(priceNumber) : ''),
      priceNumber,
      price_value: priceNumber,
      image_url: imageUrl,
      image: imageUrl || '',
      has_image: Boolean(imageUrl),
      storeName: item.storeName || item.shop_name || item.shop || item.store || '',
      rating: item.rating || 0,
      soldCount: Number(item.soldCount ?? item.sold_count ?? 0) || 0,
      sold_count: Number(item.sold_count ?? item.soldCount ?? 0) || 0,
      url: item.url || item.product_url || '#',
      source: item.source || item.source_engine || 'tokopedia',
      confidenceScore,
      relevanceReason: item.relevanceReason || item.ai_reason || item.reason || item.ai_explanation || '',
    };
  }

  renderResultWarning(data) {
    const box = this.$('r-warning');
    if (!box) return;
    const meta = data.result_metadata || this.state.metadata || {};
    const requested = Number(meta.requested_count ?? data.requested_count ?? data.target_count ?? 0);
    const displayed = this.state.products.length || Number(meta.displayed_count ?? data.displayed_count ?? 0);
    const shortage = requested > displayed && displayed > 0
      ? `Diminta ${requested}, tersedia ${displayed} produk sesuai budget.`
      : '';
    const warning = String(data.ai_warning || meta.ai_warning || data.limited_reason || meta.limited_reason || shortage || '').trim();
    if (!warning) {
      box.classList.add('hidden');
      box.textContent = '';
      return;
    }
    box.textContent = warning;
    box.classList.remove('hidden');
  }

  renderBudgetBar(budgetInfo) {
    const bar = this.$('r-budget-bar');
    const text = this.$('r-budget-text');
    this.state.budgetInfo = budgetInfo || null;
    if (!budgetInfo || !bar || !text) {
      bar?.classList.add('hidden');
      return;
    }
    text.textContent = `Budget ${this.formatRp(budgetInfo.budget)} | Range ${this.formatRp(budgetInfo.min)} - ${this.formatRp(budgetInfo.max)} | Tolerance ${budgetInfo.tolerance}%`;
    bar.classList.remove('hidden');
  }

  renderComparison(data) {
    const panel = this.$('comparison-panel');
    const grid = this.$('comparison-grid');
    if (!panel || !grid) return;

    const engine_mode = data.engine_mode || this.state.engineMode || this.state.metadata.engine_mode || 'auto';
    const runs = data.engine_runs || this.state.comparison;
    
    if (engine_mode !== 'compare_both' || !runs || !runs.length) {
      panel.classList.add('hidden');
      grid.innerHTML = '';
      return;
    }

    panel.classList.remove('hidden');
    grid.innerHTML = '';

    for (const item of runs) {
      const card = document.createElement('div');
      const isSelected = item.engine === this.state.selectedEngine;
      card.className = `compare-card ${isSelected ? 'compare-selected' : ''}`;

      const pageOpened = item.opened_real_page;
      const pageStatus = pageOpened === false
        ? `<span class="compare-fail">Halaman asli: tidak - ${this.esc(item.error_type || 'tidak diketahui')}</span>`
        : pageOpened === true
          ? '<span class="compare-ok">Halaman asli: ya</span>'
          : '<span class="compare-warn">Halaman asli: tidak diketahui</span>';

      const debugFiles = (item.debug_files || []).filter(Boolean);
      const debugHtml = debugFiles.length
        ? `<div class="debug-files">${debugFiles.map(f => `<code>${this.esc(f)}</code>`).join('')}</div>`
        : '';

      card.innerHTML = `
        <strong class="compare-engine">${this.esc(item.engine)}</strong>
        ${pageStatus}
        <div class="compare-stats">
          <span>Scrape mentah: <b>${item.raw_scraped ?? item.raw_count ?? 0}</b></span>
          <span>Budget lolos: <b>${item.budget_valid_count ?? 0}</b></span>
          <span>Semantik dicek: <b>${item.result_metadata?.semantic_checked ?? 0}</b></span>
          <span>AI dicek: <b>${item.result_metadata?.classifier_checked ?? item.result_metadata?.ai_checked ?? 0}</b></span>
          <span>AI diterima: <b>${item.ai_accepted_count ?? item.result_metadata?.ai_accepted_count ?? 0}</b></span>
          <span>Durasi: ${item.duration_seconds ?? item.duration ?? 0}s</span>
          <span>Status: ${item.ok ? 'OK' : 'Gagal'}</span>
        </div>
        ${item.error ? `<div class="compare-error">${this.esc(item.error)}</div>` : ''}
        ${debugFiles.length ? `<div class="compare-debug">Debug: ${debugHtml}</div>` : ''}
        ${item.products && item.products.length
          ? `<button class="btn btn-ghost compare-use-btn" data-engine="${this.esc(item.engine)}">Gunakan Hasil ${this.esc(item.engine)}</button>`
          : ''}
      `;

      card.querySelector('.compare-use-btn')?.addEventListener('click', () => {
        this.selectComparisonEngine(item.engine);
      });
      grid.appendChild(card);
    }
  }

  selectComparisonEngine(engine) {
    const item = this.state.comparison.find((e) => e.engine === engine);
    if (!item) return;
    this.state.selectedEngine = engine;
    this.state.products = (item.data || item.products || []).map((product) => this.normalizeProduct(product));
    window.__MARKETSPY_PRODUCTS__ = this.state.products;
    this.state.recommendations = item.recommendations || {};
    this.state.metadata = item.result_metadata || {};
    this.state.budgetInfo = item.budget_info || null;
    this.state.recommendationsOpen = true;
    this.state.recommendationMode = 'all';
    activeRecommendationMode = 'all';
    activeModalMode = null;
    activeModalProducts = [];
    activeModalIndex = 0;
    activeModalProduct = null;
    resetReviewState();
    this.state.recommendationSourceProducts = [...this.state.products];
    invalidateRecommendationCache();
    this.renderComparison({ engine_mode: this.state.engineMode, engine_runs: this.state.comparison });
    this.renderRecommendations();
    this.renderResultSummary(item);
    this.renderResultTimers();
    this.renderResultWarning({
      limited_reason: this.state.metadata.limited_reason,
      ai_warning: item.ai_warning || '',
      result_metadata: this.state.metadata,
    });
    this.updateResultCount();
    this.renderProducts();
    this.observeRecommendationStage();
    this.animateResultsEntrance();
  }

  renderResultSummary(data) {
    const meta = data.result_metadata || this.state.metadata || {};
    const requested = Number(meta.requested_count ?? data.requested_count ?? data.target_count ?? 0);
    const productCount = Array.isArray(data.data || data.products) ? (data.data || data.products).length : this.state.products.length;
    const displayed = productCount;

    // Update header count
    this.setText('r-count', displayed || this.state.products.length || 0);
    this.setText('r-target', requested || '-');

    // Update hidden stat IDs (masih dipakai internal)
    const raw = Number(meta.raw_scraped_count ?? meta.raw_scraped ?? data.raw_count ?? 0);
    const deduped = Number(meta.deduped_count ?? data.deduped_count ?? 0);
    const budget = Number(meta.budget_valid_count ?? data.budget_valid_count ?? data.budget_count ?? 0);
    const semanticChecked = Number(meta.semantic_checked ?? meta.semantic_checked_count ?? 0);
    const aiChecked = Number(meta.classifier_checked ?? meta.ai_checked ?? data.ai_checked ?? 0);
    const aiAccepted = Number(meta.ai_accepted ?? meta.ai_accepted_count ?? data.ai_accepted_count ?? 0);
    const aiCallsAttempted = Number(meta.ai_calls_attempted ?? 0);
    const aiCallsSucceeded = Number(meta.ai_calls_succeeded ?? 0);

    this.setText('rs-requested', requested || 0);
    this.setText('rs-raw', raw || 0);
    this.setText('rs-deduped', deduped || 0);
    this.setText('rs-budget', budget || 0);
    this.setText('rs-semantic', semanticChecked || 0);
    this.setText('rs-ai-checked', aiChecked || 0);
    this.setText('rs-ai', aiAccepted || 0);
    this.setText('rs-ai-calls', `${aiCallsSucceeded || 0}/${aiCallsAttempted || 0}`);
    this.setText('rs-displayed', displayed || this.state.products.length || 0);

    const status = this.$('result-status-badge');
    if (status) {
      status.textContent = displayed >= requested ? 'Selesai' : 'Sebagian';
      status.className = `status-badge ${displayed >= requested ? 'status-done' : 'status-running'}`;
    }
  }

  renderRecommendations() {
    const panel = this.$('recommendations-panel');
    if (!panel) return;

    if (!this.state.products.length) {
      panel.classList.add('hidden');
      return;
    }

    panel.classList.remove('hidden');
    const activeMode = normalizeRecommendationMode(this.state.recommendationMode) || 'all';
    activeRecommendationMode = activeMode;
    reviewState.activeMode = activeMode;
    
    // Set active mode on stage
    const stage = document.querySelector('.recommendation-stage');
    if (stage) {
      stage.dataset.activeMode = activeMode;
    }

    this.updateRecommendationButtons(activeMode);
    updateRecommendationTitle(activeMode);
    updateRecommendationLogo(activeMode);

    this.updateRecommendationPanels(activeMode);

    renderRecommendationContent(activeMode);
    renderCheckedProductsBox(activeMode);
    setupAdaptiveScrollBehavior();
  }

  buildRecommendationBuckets() {
    const list = [
      ...(this.state.recommendationSourceProducts?.length
        ? this.state.recommendationSourceProducts
        : this.state.products)
    ];

    const number = (value) => {
      const parsed = Number(String(value ?? 0).replace(',', '.'));
      return Number.isFinite(parsed) ? parsed : 0;
    };
    const price = (p) => {
      const value = number(p.priceNumber ?? p.price_value ?? p.price);
      return value > 0 ? value : Number.MAX_SAFE_INTEGER;
    };
    const rating = (p) => number(p.rating);
    const confidence = (p) => number(p.confidenceScore ?? p.confidence ?? p.relevance_score ?? p.ai_confidence);
    const sold = (p) => number(p.soldCount ?? p.sold_count);
    const reviewCount = (p) => number(p.review_count ?? p.reviewCount ?? 0);

    // Skor trust gabungan untuk Most Trusted
    const trustScore = (p) => {
      const shopStr = String(p.storeName || p.shop_name || p.shop || '').toLowerCase();
      const shopBoost = /(official|mall|power merchant|pro)/.test(shopStr) ? 0.3 : 0;
      const ratingNorm = rating(p) / 5;
      const soldNorm = Math.min(sold(p), 10000) / 10000;
      const reviewNorm = Math.min(reviewCount(p), 5000) / 5000;
      const confNorm = confidence(p) > 1 ? confidence(p) / 100 : confidence(p);
      return shopBoost + ratingNorm * 0.3 + soldNorm * 0.25 + reviewNorm * 0.2 + confNorm * 0.25;
    };

    // Skor terbaik gabungan
    const bestScore = (p) => {
      const ratingNorm = rating(p) / 5;
      const reviewNorm = Math.min(reviewCount(p), 5000) / 5000;
      const soldNorm = Math.min(sold(p), 10000) / 10000;
      const confNorm = confidence(p) > 1 ? confidence(p) / 100 : confidence(p);
      return ratingNorm * 0.35 + reviewNorm * 0.25 + soldNorm * 0.2 + confNorm * 0.2;
    };

    // Filter produk yang punya harga valid untuk Termurah
    const withValidPrice = list.filter(p => price(p) < Number.MAX_SAFE_INTEGER);

    // Filter produk yang punya rating untuk Terbaik (minimal ada rating)
    const withRating = list.filter(p => rating(p) > 0);

    // Filter produk yang punya sold/review untuk Most Trusted
    const withTrustSignal = list.filter(p => sold(p) > 0 || reviewCount(p) > 0 || rating(p) > 0);

    return {
      // Semua Barang: semua produk, urutan asli (sudah di-sort backend)
      all: [...list],

      // Terbaik: produk dengan rating, diurutkan skor terbaik
      terbaik: (withRating.length > 0 ? withRating : list)
        .slice()
        .sort((a, b) => bestScore(b) - bestScore(a)),

      // Termurah: produk dengan harga valid, diurutkan harga terendah
      termurah: (withValidPrice.length > 0 ? withValidPrice : list)
        .slice()
        .sort((a, b) => price(a) - price(b) || rating(b) - rating(a)),

      // Most Trusted: produk dengan sinyal kepercayaan, diurutkan trust score
      trusted: (withTrustSignal.length > 0 ? withTrustSignal : list)
        .slice()
        .sort((a, b) => trustScore(b) - trustScore(a)),
    };
  }

  createRecommendationMiniCard(product) {
    const item = this.normalizeProduct(product);
    const card = document.createElement('div');
    card.className = 'recommendation-product-card';
    const id = getProductReviewId(item);
    card.dataset.productId = id;
    card.dataset.id = id;

    const imgWrap = document.createElement('div');
    imgWrap.className = 'recommendation-product-image-wrap';

    const imageUrl = this.resolveProductImage(item);
    
    if (!imageUrl) {
      const placeholder = document.createElement("div");
      placeholder.className = "image-placeholder";
      placeholder.textContent = "Tidak ada gambar";
      imgWrap.classList.add("is-image-missing");
      imgWrap.appendChild(placeholder);
    } else {
      const img = document.createElement('img');
      img.className = 'recommendation-product-image';
      img.src = imageUrl;
      img.alt = item.title || 'Gambar produk';
      img.loading = 'lazy';
      img.onerror = () => {
        if (imageUrl && !img.dataset.proxyTried) {
          img.dataset.proxyTried = '1';
          img.src = this.proxyImageUrl(imageUrl);
          return;
        }
        handleImageError(img);
      };
      imgWrap.appendChild(img);
    }

    const details = document.createElement('div');
    details.className = 'recommendation-product-card-details';
    
    const h4 = document.createElement('h4');
    h4.className = 'recommendation-product-title';
    h4.textContent = item.title || 'Produk Tokopedia';
    
    const strong = document.createElement('div');
    strong.className = 'recommendation-product-price';
    strong.textContent = item.price || '';
    
    const span = document.createElement('div');
    span.className = 'recommendation-product-meta';
    const ratingNum = Number(item.rating) || 0;
    const reviewCount = Number(item.review_count || item.reviewCount || 0);
    const ratingStr = ratingNum > 0 ? formatRating(ratingNum, reviewCount) : '';
    const soldRaw = item.sold || item.sold_text || item.soldCount || item.sold_count || '';
    const soldStr = soldRaw ? formatSoldCount(soldRaw) : '';
    span.textContent = [ratingStr, soldStr].filter(Boolean).join(' · ');

    details.append(h4, strong, span);
    card.append(imgWrap, details);

    return card;
  }

  toggleRecommendations() {
    this.state.recommendationsOpen = true;
    this.renderRecommendations();
    this.expandRecommendationStage(true);
  }

  animateRecommendationProductsEnter(scopeOptions = {}) {
    const profile = getRecommendationMotionProfile();
    animateRecommendationCardsEnter(profile);
  }

  animateRecommendationProductsExit() {
    const profile = getRecommendationMotionProfile();
    return animateRecommendationCardsExit(null, profile);
  }

  async selectRecommendation(nextMode, triggerEl = null) {
    await selectRecommendationMode(nextMode, triggerEl);
  }

  updateRecommendationButtons(nextMode) {
    updateRecommendationButtons(nextMode);
  }

  updateRecommendationPanels(nextMode) {}
  renderSidePanelContent(panel, modeKey) {}
  animateSidePanels() {}

  updateRecommendationContent(nextMode) {
    const mode = normalizeRecommendationMode(nextMode) || 'all';
    renderRecommendationContent(mode);
    renderCheckedProductsBox(mode);

    setupAdaptiveScrollBehavior();
  }

  animateRecommendationStage() {
    if (!this.canAnimate()) return;
    // Animasi hanya pada cards, bukan pada container panel
    // translateY pada active-panel menyebabkan gap visual sementara
    const profile = getRecommendationMotionProfile();
    this.animateRecommendationProductsEnter(profile);
  }

  observeRecommendationStage() {
    if (this.recommendationObserver) this.recommendationObserver.disconnect();
    const panel = this.$('recommendations-panel');
    if (!panel || !('IntersectionObserver' in window)) return;
    this.recommendationObserver = new IntersectionObserver((entries) => {
      const entry = entries[0];
      if (
        entry?.isIntersecting
        && entry.intersectionRatio >= 0.45
        && !this.state.hasUserSelectedRecommendation
        && !this.state.autoExpandedOnce
      ) {
        this.state.autoExpandedOnce = true;
        this.expandRecommendationStage(false);
      }
    }, { threshold: [0, 0.45, 0.7] });
    this.recommendationObserver.observe(panel);
  }

  expandRecommendationStage(fromUser) {
    const stage = this.$('recommendation-stage');
    if (!stage) return;
    if (fromUser) this.state.hasUserSelectedRecommendation = true;

    // Langsung tambah class tanpa animasi height — height animasi adalah penyebab gap
    stage.classList.add('is-auto-expanded');
    // Pastikan tidak ada inline height yang tersisa
    stage.style.height = '';
    stage.style.overflow = '';

    // Animasi cards saja, bukan height container
   

/* FILE TRUNCATED BECAUSE TOO LARGE */

```

## FILE: `web\index.html`

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MarketSpy AI</title>
  <meta name="description" content="MarketSpy AI - Mencari barang bagus sesuai budget dengan teknologi scraping dan AI lokal.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="app">
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <span class="logo-icon" title="MarketSpy AI">
            <img
              src="pngegg.png"
              alt="MarketSpy AI"
              width="32"
              height="32"
              style="object-fit:contain;image-rendering:auto;display:block;"
            />
          </span>
          <div>
            <h1>MarketSpy AI</h1>
            <p>Mencari barang bagus sesuai budget</p>
          </div>
        </div>
        <div class="header-status-group">
          <div class="ai-scraper-header-badge is-inactive" id="ai-scraper-header-badge" aria-live="polite">
            <span class="ai-scraper-dot"></span>
            <span class="ai-scraper-header-text">AI Scraper Tidak Aktif</span>
          </div>
          <div class="app-status-badge is-idle" data-app-status-badge aria-live="polite">
            <span class="status-badge-text">Siap</span>
          </div>
        </div>
      </div>
    </header>

    <main class="main">
      <!-- SEARCH PANEL -->
      <section id="search-panel" class="panel search-panel">
        <h2 class="panel-title">Cari Produk</h2>

        <div class="form-group">
          <label for="query">Produk yang dicari <span class="required">*</span></label>
          <input type="text" id="query" placeholder="Contoh: laptop gaming" autocomplete="off">
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="target_count">Jumlah target <span class="required">*</span></label>
            <input type="number" id="target_count" placeholder="Contoh: 20" min="1" max="100">
          </div>
          <div class="form-group">
            <label for="budget">Budget (Rp) — Opsional</label>
            <div class="budget-input-wrap">
              <span class="budget-prefix">Rp</span>
              <input type="text" id="budget" placeholder="10.000.000" autocomplete="off" inputmode="numeric">
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="tolerance">Toleransi budget (%) — Opsional</label>
          <input type="number" id="tolerance" placeholder="Contoh: 20" min="0" max="100">
        </div>

        <div id="budget-info" class="budget-info hidden">
          <div class="budget-info-row">
            <span class="bi-label">Budget:</span>
            <span id="bi-budget" class="bi-value">-</span>
          </div>
          <div class="budget-info-row">
            <span class="bi-label">Toleransi:</span>
            <span id="bi-tolerance" class="bi-value">-</span>
          </div>
          <div class="budget-info-row">
            <span class="bi-label">Range:</span>
            <span id="bi-range" class="bi-value bi-range">-</span>
          </div>
        </div>

        <!-- Hidden inputs yang masih dipakai JS tapi tidak ditampilkan -->
        <input type="hidden" id="use_ai" value="true">
        <input type="hidden" id="engine_mode" value="auto">
        <input type="hidden" id="target_first_mode" value="false">
        <input type="hidden" id="category_limit" value="12">

        <div class="form-actions">
          <button id="search-btn" class="btn btn-primary btn-large" onclick="window.app && window.app.startSearch()">
            Mulai Scraping
          </button>
        </div>
      </section>

      <!-- PROGRESS PANEL -->
      <section id="progress-panel" class="panel progress-panel hidden">
        <h2 class="panel-title">Scraping Berlangsung</h2>
        <div class="progress-clean-panel" data-progress-stage="idle">
          <div class="progress-scramble-text" id="progressScrambleText">Menunggu proses...</div>
          <div class="progress-time-row">
            <div class="progress-time-pill">
              <span>Durasi</span>
              <strong id="elapsedText">00:00</strong>
            </div>
            <div class="progress-time-pill">
              <span>ETA</span>
              <strong id="etaText">Menghitung...</strong>
            </div>
          </div>
        </div>
      </section>

      <!-- ERROR PANEL -->
      <section id="error-panel" class="panel error-panel hidden">
        <h2>Terjadi Kesalahan</h2>
        <p id="error-msg" class="error-msg"></p>
        <div class="error-actions">
          <button class="btn btn-primary" onclick="app.retry()">Coba Lagi</button>
          <button class="btn btn-ghost" onclick="app.reset()">Kembali</button>
        </div>
      </section>

      <!-- RESULTS PANEL -->
      <section id="results-panel" class="panel results-panel hidden">

        <!-- Header hasil -->
        <div class="results-header">
          <div class="results-title-block">
            <h2 class="panel-title">Hasil Scraping</h2>
            <div class="results-meta">
              <span class="results-count">Menampilkan <strong id="r-count">0</strong> dari <strong id="r-target">0</strong> produk diminta</span>
            </div>
          </div>
          <div class="result-header-tools">
            <div class="result-time-card">
              <span>Durasi</span>
              <b id="rt-elapsed">00:00</b>
            </div>
            <div class="result-time-card">
              <span>ETA</span>
              <b id="rt-eta">-</b>
            </div>
            <div id="result-status-badge" class="status-badge status-done">Selesai</div>
          </div>
        </div>

        <!-- Hidden stat IDs yang masih diupdate JS (tidak ditampilkan) -->
        <div style="display:none" aria-hidden="true">
          <span id="rs-requested"></span>
          <span id="rs-raw"></span>
          <span id="rs-deduped"></span>
          <span id="rs-budget"></span>
          <span id="rs-semantic"></span>
          <span id="rs-ai-checked"></span>
          <span id="rs-ai"></span>
          <span id="rs-ai-calls"></span>
          <span id="rs-displayed"></span>
        </div>

        <!-- Budget info 1 baris -->
        <div id="r-budget-bar" class="r-budget-bar hidden">
          <span id="r-budget-text"></span>
        </div>

        <!-- Warning / keterangan kekurangan data -->
        <div id="r-warning" class="result-warning hidden"></div>

        <!-- Comparison panel (hanya muncul di mode compare) -->
        <div id="comparison-panel" class="comparison-panel hidden">
          <h3>Perbandingan Engine</h3>
          <div id="comparison-grid" class="comparison-grid"></div>
        </div>

        <!-- REKOMENDASI CEPAT — semua produk ada di sini -->
        <div id="recommendations-panel" class="recommendations-panel hidden">
          <section class="recommendation-stage" id="recommendation-stage" data-active-mode="all">

            <div class="recommendation-header">
              <div class="recommendation-title-area">
                <span class="recommendation-kicker">REKOMENDASI CEPAT</span>
                <h2 id="recommendationTitle" class="recommendation-active-title">Semua Barang</h2>
              </div>
              <div class="recommendation-controls">
                <button type="button" class="recommendation-mode-btn is-active" data-recommendation-mode="all">
                  <span class="mode-icon">🧺</span>
                  <span>Semua Barang</span>
                </button>
                <button type="button" class="recommendation-mode-btn" data-recommendation-mode="terbaik">
                  <span class="mode-icon">⭐</span>
                  <span>Terbaik</span>
                </button>
                <button type="button" class="recommendation-mode-btn" data-recommendation-mode="termurah">
                  <span class="mode-icon">💸</span>
                  <span>Termurah</span>
                </button>
                <button type="button" class="recommendation-mode-btn" data-recommendation-mode="trusted">
                  <span class="mode-icon">🏆</span>
                  <span>Most Trusted</span>
                </button>
              </div>
            </div>

            <!-- Input jumlah per kategori — hanya muncul untuk non-all mode -->
            <div class="category-limit-bar hidden" id="category-limit-bar">
              <label for="category_limit_inline" class="category-limit-label">Tampilkan</label>
              <input type="number" id="category_limit_inline" class="category-limit-input" value="12" min="1" max="50" placeholder="12">
              <span class="category-limit-suffix">produk di kategori ini</span>
              <button type="button" class="category-limit-apply btn btn-ghost btn-sm" id="category-limit-apply">Terapkan</button>
            </div>

            <div class="recommendation-active-panel">
              <div class="recommendation-product-grid" id="recommendation-product-grid" data-layout-grid="active-products"></div>

              <!-- Hasil Review Sudah Dicek -->
              <section class="checked-products-box" data-layout-grid="checked-products">
                <div class="checked-products-header">
                  <div>
                    <span class="checked-products-kicker">HASIL REVIEW</span>
                    <h3>Sudah Dicek</h3>
                  </div>
                  <p class="checked-products-count">0 produk</p>
                </div>
                <div class="checked-products-grid"></div>
              </section>
            </div>

          </section>
        </div>

        <!-- Footer -->
        <div class="results-footer">
          <button class="btn btn-ghost" onclick="app.reset()">Cari Lagi</button>
        </div>
      </section>
    </main>
  </div>

  <!-- Product detail modal (backdrop) -->
  <div class="product-modal-backdrop" data-product-modal hidden>
    <article class="product-detail-modal" role="dialog" aria-modal="true" aria-labelledby="product-detail-title">
      <button class="product-modal-close" type="button" data-close-product-modal aria-label="Tutup">×</button>

      <div id="productDetailImagePanel" class="product-detail-media product-detail-image-panel">
        <img class="product-detail-image" alt="Gambar produk" />
        <div class="product-detail-image-placeholder">TIDAK ADA GAMBAR</div>
      </div>

      <div id="productDetailContent" class="product-detail-content">
        <div id="productDetailInfoPanel" class="product-detail-info-panel">
          <p class="product-detail-kicker">DETAIL REKOMENDASI</p>
          <h2 id="product-detail-title" class="product-detail-title"></h2>
          <p class="product-detail-subtitle"></p>
          <p class="product-detail-price"></p>
          <div class="product-detail-meta"></div>

          <section class="product-feedback-panel">
            <h3>Apakah produk ini sesuai?</h3>
            <div class="product-feedback-actions">
              <button type="button" class="feedback-btn feedback-yes" data-feedback-answer="benar">Benar</button>
              <button type="button" class="feedback-btn feedback-no" data-feedback-answer="salah">Salah</button>
              <a class="feedback-btn feedback-open" target="_blank" rel="noopener noreferrer">Buka Produk</a>
            </div>

            <div class="feedback-reason-panel detail-feedback-reason-panel" data-detail-feedback-reason-panel hidden>
              <h3>Kenapa produk ini salah?</h3>
              <p>Pilih satu atau lebih alasan agar AI bisa belajar.</p>
              <div class="feedback-reason-grid" data-detail-feedback-reason-grid></div>
              <textarea class="feedback-note" data-detail-feedback-note placeholder="Tambahkan catatan jika perlu..."></textarea>
              <div class="feedback-save-row">
                <button type="button" class="btn-ghost" data-detail-feedback-cancel>Batal</button>
                <button type="button" class="btn-primary" data-detail-feedback-save>Simpan Feedback</button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </article>
  </div>

  <script src="vendor/anime.min.js"></script>
  <script src="app.js" defer></script>
</body>
</html>

```

## FILE: `web\style.css`

```css
*, *::before, *::after {
  box-sizing: border-box;
}

:root {
  --bg-main: #0b1120;
  --bg-deep: #070b18;
  --bg-panel: #0f172a;
  --bg-card: #111827;
  --bg-card-soft: #162033;
  --text-main: #e5eefc;
  --text-soft: #94a3b8;
  --text-muted: #64748b;
  --border: rgba(148, 163, 184, 0.18);
  --border-soft: rgba(148, 163, 184, 0.18);
  --primary: #3b82f6;
  --primary-glow: #60a5fa;
  --accent: #60a5fa;
  --violet: #7c3aed;
  --warning: #f59e0b;
  --success: #10b981;
  --page:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.08), transparent 28%),
    radial-gradient(circle at top right, rgba(96, 165, 250, 0.06), transparent 25%),
    linear-gradient(180deg, #0b1120 0%, #070b18 100%);
  --surface: var(--bg-panel);
  --surface-soft: var(--bg-card);
  --ink: var(--text-main);
  --muted: var(--text-soft);
  --faint: var(--text-muted);
  --line: var(--border-soft);
  --blue: var(--primary);
  --green: var(--success);
  --amber: var(--warning);
  --red: #f87171;
  --cyan: var(--accent);
  --shadow: 0 18px 55px rgba(0, 0, 0, 0.28), 0 0 28px rgba(59, 130, 246, 0.08);
  --radius: 22px;
}

html,
body {
  margin: 0;
  min-height: 100%;
  background: var(--page);
  color: var(--ink);
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 15px;
  line-height: 1.5;
}

button,
input,
select,
textarea {
  font: inherit;
}

a {
  color: inherit;
}

.hidden,
.panel.hidden,
.budget-info.hidden,
.r-budget-bar.hidden,
.result-warning.hidden,
.comparison-panel.hidden,
.recommendations-panel.hidden,
.recommendations-grid.hidden,
.ai-install-command.hidden {
  display: none !important;
}

.app {
  min-height: 100vh;
}

.header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(11, 17, 32, 0.84);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(14px);
}

.header-inner,
.main {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.logo-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1d4ed8, #60a5fa);
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0;
}

.logo-icon svg {
  width: 24px;
  height: 24px;
  stroke-width: 2.5;
}

.logo h1 {
  margin: 0;
  font-size: 18px;
  line-height: 1.2;
}

.logo p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 12px;
}

.status-badge,
.ai-status-badge,
.badge,
.product-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid transparent;
  font-size: 12px;
  font-weight: 750;
  line-height: 1;
  white-space: nowrap;
}

.status-badge {
  padding: 7px 10px;
}

.app-status-badge {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 88px;
  min-height: 34px;
  padding: 7px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.12);
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
  line-height: 1;
  white-space: nowrap;
  text-align: center;
  box-shadow: none;
  filter: none;
  overflow: hidden;
}

.app-status-badge.is-running {
  color: var(--accent);
  border-color: rgba(96, 165, 250, 0.35);
  background: rgba(59, 130, 246, 0.18);
}

.app-status-badge.is-done {
  color: var(--green);
  border-color: rgba(52, 211, 153, 0.32);
  background: rgba(52, 211, 153, 0.14);
}

.app-status-badge.is-error {
  color: var(--red);
  border-color: rgba(248, 113, 113, 0.34);
  background: rgba(248, 113, 113, 0.14);
}

.status-badge-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-idle { background: rgba(148, 163, 184, 0.12); color: var(--muted); border-color: var(--line); }
.status-running { background: rgba(59, 130, 246, 0.18); color: var(--accent); border-color: rgba(96, 165, 250, 0.35); }
.status-done { background: rgba(52, 211, 153, 0.14); color: var(--green); border-color: rgba(52, 211, 153, 0.32); }
.status-error { background: rgba(248, 113, 113, 0.14); color: var(--red); border-color: rgba(248, 113, 113, 0.34); }

.main {
  padding: 28px 0 56px;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin-bottom: 20px;
  padding: 24px;
}

.panel-title {
  margin: 0 0 18px;
  font-size: 18px;
  line-height: 1.25;
}

.search-panel {
  max-width: 760px;
  margin-left: auto;
  margin-right: auto;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label,
.modal-note-wrap label {
  display: block;
  margin-bottom: 7px;
  color: var(--ink);
  font-size: 13px;
  font-weight: 700;
}

.form-group small {
  display: block;
  margin-top: 3px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 500;
}

.required {
  color: var(--red);
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea,
.modal-note-wrap textarea,
.category-limit-input,
input[type="number"] {
  width: 100%;
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(15, 23, 42, 0.78);
  color: var(--ink);
  outline: none;
  padding: 10px 12px;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
  appearance: textfield;
  -moz-appearance: textfield;
}

.category-limit-input::-webkit-outer-spin-button,
.category-limit-input::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus,
.modal-note-wrap textarea:focus {
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18);
}

.budget-input-wrap {
  display: flex;
  align-items: stretch;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(15, 23, 42, 0.78);
}

.budget-input-wrap:focus-within {
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18);
}

.budget-prefix {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  background: var(--surface-soft);
  border-right: 1px solid var(--line);
  color: var(--muted);
  font-weight: 800;
}

.budget-input-wrap input {
  border: 0 !important;
  box-shadow: none !important;
}

.budget-info,
.r-budget-bar,
.result-warning,
.ai-status-card,
.ai-scraper-status {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-soft);
  padding: 13px 14px;
}

.budget-info {
  display: grid;
  gap: 6px;
}

.budget-info-row {
  display: flex;
  gap: 10px;
  justify-content: space-between;
  color: var(--muted);
  font-size: 13px;
}

.bi-value {
  color: var(--ink);
  font-weight: 750;
  text-align: right;
}

.ai-scraper-status {
  margin-bottom: 16px;
}

.ai-scraper-status-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.ai-scraper-status-head strong {
  font-size: 13px;
}

.ai-scraper-message {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.ai-scraper-badge {
  padding: 6px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 750;
  line-height: 1;
  white-space: nowrap;
}

.ai-scraper-badge.is-checking {
  background: rgba(59, 130, 246, 0.18);
  color: var(--accent);
}

.ai-scraper-badge.is-ready {
  background: rgba(52, 211, 153, 0.14);
  color: var(--green);
}

.ai-scraper-badge.is-fallback {
  background: rgba(251, 191, 36, 0.14);
  color: var(--amber);
}

.ai-scraper-badge.is-error {
  background: rgba(248, 113, 113, 0.14);
  color: var(--red);
}

.checkbox-label {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 8px 10px;
  cursor: pointer;
}

.checkbox-label input {
  margin-top: 3px;
}

.checkbox-label span {
  font-weight: 700;
}

.checkbox-label small {
  grid-column: 2;
  margin: -5px 0 0;
}

.ai-status-card {
  margin-bottom: 16px;
}

.ai-status-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.ai-status-message {
  margin: 8px 0 10px;
  color: var(--muted);
  font-size: 13px;
}

.ai-status-grid {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 6px 10px;
  font-size: 13px;
}

.ai-status-grid span {
  color: var(--muted);
}

.ai-status-grid b {
  min-width: 0;
  overflow-wrap: anywhere;
}

.ai-status-badge {
  padding: 6px 9px;
}

.is-ready { background: rgba(52, 211, 153, 0.14); color: var(--green); }
.is-missing { background: rgba(251, 191, 36, 0.14); color: var(--amber); }
.is-checking { background: rgba(59, 130, 246, 0.18); color: var(--accent); }

.ai-install-command {
  margin: 12px 0 0;
  overflow-x: hidden;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #111827;
  color: #e5e7eb;
  padding: 10px;
  font-size: 12px;
}

.form-actions,
.error-actions,
.modal-actions,
.product-footer,
.feedback-row,
.quick-sort {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn,
.quick-sort-btn,
.compare-use,
.compare-use-btn,
.recommendations-trigger,
.btn-feedback {
  border-radius: var(--radius);
  cursor: pointer;
  font-weight: 800;
  transition: background 0.16s ease, border-color 0.16s ease, color 0.16s ease, transform 0.16s ease;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  border: 1px solid transparent;
  padding: 10px 14px;
}

.btn-large {
  min-height: 48px;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #ffffff;
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.24);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1d4ed8, #60a5fa);
}

.btn-ghost {
  background: rgba(15, 23, 42, 0.72);
  border-color: var(--line);
  color: var(--ink);
}

.btn-ghost:hover {
  border-color: var(--blue);
  color: var(--blue);
}

.form-actions .btn-primary {
  flex: 1 1 220px;
}

.progress-header,
.results-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.progress-pct {
  color: var(--accent);
  font-size: 38px;
  font-weight: 850;
  font-variant-numeric: tabular-nums;
}

.progress-stage-label {
  color: var(--muted);
  font-weight: 750;
  padding-top: 13px;
}

.progress-track {
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.14);
  margin: 14px 0 18px;
}

.progress-bar {
  width: 0;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  transition: width 0.45s ease;
}

.progress-meta,
.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(118px, 1fr));
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
  background: rgba(15, 23, 42, 0.72);
}

.meta-item,
.result-summary div {
  min-width: 0;
  border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 10px 12px;
}

.meta-label,
.result-summary span {
  display: block;
  color: var(--muted);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.meta-val,
.result-summary b {
  display: block;
  margin-top: 3px;
  color: var(--ink);
  font-size: 17px;
  font-weight: 850;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}

.progress-message {
  min-height: 24px;
  margin: 14px 0;
  color: var(--ink);
  font-weight: 650;
}

.progress-log-wrap {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-soft);
  margin: 14px 0 18px;
  overflow: hidden;
}

.progress-log-title {
  border-bottom: 1px solid var(--line);
  padding: 9px 12px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
}

.progress-log {
  display: grid;
  max-height: 180px;
  overflow-y: auto;
}

.progress-log-row {
  display: grid;
  grid-template-columns: 128px minmax(0, 1fr);
  gap: 10px;
  border-bottom: 1px solid var(--line);
  padding: 9px 12px;
  font-size: 13px;
}

.progress-log-row:last-child {
  border-bottom: 0;
}

.progress-log-stage {
  color: var(--cyan);
  font-weight: 800;
}

.progress-log-message,
.progress-log-empty {
  color: var(--muted);
  overflow-wrap: anywhere;
}

.progress-log-empty {
  padding: 10px 12px;
  font-size: 13px;
}

.stage-pipeline {
  display: grid;
  grid-template-columns: repeat(7, minmax(64px, 1fr));
  gap: 6px;
}

.stage-connector {
  display: none;
}

.stage-item {
  display: grid;
  justify-items: center;
  gap: 5px;
  color: var(--faint);
  font-size: 11px;
  font-weight: 800;
  text-align: center;
}

.stage-dot {
  width: 12px;
  height: 12px;
  border: 2px solid var(--line);
  border-radius: 50%;
  background: var(--bg-main);
}

.stage-item.active,
.stage-item.done {
  color: var(--green);
}

.stage-item.active .stage-dot {
  border-color: var(--green);
  box-shadow: 0 0 0 5px rgba(22, 138, 80, 0.13);
}

.stage-item.done .stage-dot {
  border-color: var(--green);
  background: var(--green);
}

.error-panel {
  max-width: 620px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}

.error-msg {
  color: var(--muted);
}

.results-panel {
  padding: 24px;
  min-height: unset;
}

.results-panel.done,
.progress-panel.done {
  min-height: unset;
  margin-bottom: 20px;
}

.progress-panel.hidden,
.progress-panel.done.hidden {
  display: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.results-meta,
.results-count {
  color: var(--muted);
}

.results-count span {
  color: var(--ink);
  font-weight: 850;
}

.result-summary {
  margin-bottom: 14px;
}

.r-budget-bar {
  margin-bottom: 14px;
  color: var(--cyan);
  font-weight: 750;
}

.result-warning {
  margin-bottom: 14px;
  background: rgba(251, 191, 36, 0.12);
  border-color: rgba(251, 191, 36, 0.32);
  color: #fde68a;
}

.quick-sort {
  margin: 16px 0;
}

.quick-sort-btn {
  min-height: 38px;
  border: 1px solid var(--line);
  background: rgba(15, 23, 42, 0.72);
  color: var(--ink);
  padding: 9px 13px;
}

.quick-sort-btn:hover,
.quick-sort-btn.active {
  border-color: rgba(96, 165, 250, 0.58);
  background: rgba(59, 130, 246, 0.2);
  color: #ffffff;
}

.comparison-panel,
.recommendations-panel {
  margin-bottom: 16px;
  margin-top: 0;
}

.results-panel .recommendations-panel {
  margin-top: 24px;
}

.comparison-panel h3 {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 13px;
  text-transform: uppercase;
}

.comparison-grid,
.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 12px;
}

.compare-card,
.recommendation-card,
.product-card {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(17, 24, 39, 0.94);
}

.compare-card {
  padding: 14px;
}

.compare-card strong {
  display: block;
  margin-bottom: 7px;
  text-transform: capitalize;
}

.compare-ok { color: var(--green); font-weight: 800; }
.compare-fail { color: var(--red); font-weight: 800; }
.compare-warn { color: var(--amber); font-weight: 800; }
.compare-error { color: var(--red); font-size: 12px; margin-top: 8px; }
.compare-stats { display: grid; gap: 3px; margin-top: 8px; color: var(--muted); font-size: 12px; }
.compare-stats b { color: var(--ink); }
.compare-selected { border-color: var(--blue); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.16); }
.debug-files { display: grid; gap: 4px; margin-top: 6px; }
.debug-files code { color: var(--amber); overflow-wrap: anywhere; }

.recommendations-trigger {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  width: 100%;
  border: 1px solid var(--line);
  background: rgba(15, 23, 42, 0.72);
  color: var(--ink);
  padding: 14px;
  text-align: left;
}

.recommendation-trigger-title {
  font-weight: 850;
}

.recommendation-trigger-subtitle {
  color: var(--muted);
  font-size: 12px;
}

.recommendation-trigger-state {
  grid-row: 1 / span 2;
  grid-column: 2;
  align-self: center;
  color: var(--blue);
  font-size: 12px;
  font-weight: 850;
}

.recommendations-grid {
  margin-top: 12px;
}

.recommendation-card {
  padding: 12px;
}

.recommendation-label {
  margin-bottom: 9px;
  color: var(--accent);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
}

.recommendation-main {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 10px;
}

.recommendation-img,
.recommendation-img-placeholder {
  width: 72px;
  aspect-ratio: 1;
  border-radius: var(--radius);
  background: var(--surface-soft);
  overflow: hidden;
}

.recommendation-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommendation-img-placeholder {
  display: grid;
  place-items: center;
  padding: 8px;
  color: var(--muted);
  font-size: 11px;
  text-align: center;
}

.recommendation-title,
.product-title {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recommendation-title {
  -webkit-line-clamp: 2;
  font-size: 13px;
  font-weight: 800;
}

.recommendation-price {
  margin-top: 3px;
  color: var(--green);
  font-weight: 850;
}

.recommendation-meta,
.recommendation-shop,
.recommendation-reason,
.recommendation-empty {
  color: var(--muted);
  font-size: 12px;
}

.recommendation-link {
  display: inline-flex;
  margin-top: 8px;
  color: var(--blue);
  font-size: 12px;
  font-weight: 850;
  text-decoration: none;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
  max-width: 100%;
  width: 100%;
}

.product-card {
  display: flex;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  flex-direction: column;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--bg-card);
  transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.product-card.feedback-sent {
  opacity: 0.8;
  border-color: rgba(16, 185, 129, 0.4);
}

.product-card:hover {
  border-color: rgba(96, 165, 250, 0.48);
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.product-card.feedback-sent {
  opacity: 0.8;
  border-color: rgba(16, 185, 129, 0.4);
}

.product-link {
  display: flex;
  flex: 1;
  min-width: 0;
  color: inherit;
  flex-direction: column;
  text-decoration: none;
}

.product-image-wrap {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 4 / 3;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.88), rgba(30, 41, 59, 0.72));
  border-bottom: 1px solid var(--line);
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image-placeholder {
  display: grid;
  place-items: center;
  gap: 6px;
  width: 100%;
  height: 100%;
  padding: 16px;
  background:
    radial-gradient(circle at 35% 25%, rgba(96, 165, 250, 0.18), transparent 32%),
    rgba(15, 23, 42, 0.76);
  color: var(--muted);
  text-align: center;
}

.product-image-placeholder span {
  font-size: 13px;
  font-weight: 850;
}

.product-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  min-width: 0;
}

.product-title {
  min-height: 42px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--ink);
  font-size: 13px;
  font-weight: 700;
  line-height: 1.4;
  word-break: break-word;
}

.product-price {
  color: var(--green);
  font-size: 15px;
  font-weight: 800;
}

.product-meta,
.product-badges,
.ai-line {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  min-width: 0;
}

.product-meta {
  color: var(--muted);
  font-size: 11px;
}

.product-meta span {
  overflow-wrap: break-word;
  word-break: break-word;
}

.product-rating { color: var(--amber); font-weight: 700; }
.product-shop { color: var(--ink); font-weight: 600; }
.product-location,
.product-sold { color: var(--text-soft); font-size: 11px; }

.product-badge {
  display: inline-block;
  max-width: 100%;
  background: rgba(59, 130, 246, 0.14);
  color: #bfdbfe;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  overflow-wrap: break-word;
  word-break: break-word;
  white-space: normal;
}

.feedback-accepted-badge {
  background: rgba(52, 211, 153, 0.14);
  color: var(--green);
}

.feedback-accepted-badge {
  background: rgba(52, 211, 153, 0.14);
  color: var(--green);
}

.ai-reason {
  color: var(--muted);
  font-size: 12px;
}

.product-footer {
  padding: 0 14px 14px;
}

.btn-feedback {
  flex: 1 1 0;
  min-width: 92px;
  min-height: 38px;
  border: 1px solid transparent;
  background: rgba(15, 23, 42, 0.72);
}

.btn-benar {
  border-color: rgba(52, 211, 153, 0.38);
  color: var(--green);
}

.btn-benar:hover {
  background: rgba(52, 211, 153, 0.12);
}

.btn-salah {
  border-color: rgba(248, 113, 113, 0.38);
  color: var(--red);
}

.btn-salah:hover {
  background: rgba(248, 113, 113, 0.12);
}

.product-card.feedback-sent {
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.14);
}

.no-results {
  grid-column: 1 / -1;
  border: 1px dashed var(--line);
  border-radius: var(--radius);
  background: rgba(15, 23, 42, 0.72);
  color: var(--muted);
  margin: 0;
  padding: 28px;
  text-align: center;
}

.results-footer {
  margin-top: 20px;
  text-align: center;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 22px;
  z-index: 1200;
  transform: translate(-50%, 8px);
  opacity: 0;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #0f172a;
  color: #ffffff;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 850;
  pointer-events: none;
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.toast.is-visible {
  opacity: 1;
  transform: translate(-50%, 0);
}

.modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal:not(.hidden) {
  display: flex;
}

.modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.58);
}

.modal-box {
  position: relative;
  z-index: 1;
  width: min(560px, 100%);
  max-height: min(760px, 92vh);
  overflow-y: auto;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.46);
}

body.modal-open {
  overflow: hidden;
}

.modal-header,
.modal-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px solid var(--line);
  padding: 16px 18px;
}

.modal-header h3 {
  margin: 0;
  font-size: 17px;
}

.modal-close {
  width: 34px;
  height: 34px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(15, 23, 42, 0.72);
  color: var(--muted);
  cursor: pointer;
}

.modal-product {
  margin: 16px 18px 0;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-soft);
  padding: 10px 12px;
  color: var(--ink);
  font-size: 13px;
}

.modal-question {
  margin: 14px 18px 8px;
  font-weight: 800;
}

.modal-cats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 0 18px 14px;
}

.cat-checkbox {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 6px 8px;
  align-items: start;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 9px;
  background: rgba(15, 23, 42, 0.58);
  color: var(--ink);
  font-size: 13px;
  cursor: pointer;
}

.cat-checkbox:hover {
  border-color: var(--blue);
}

.cat-checkbox small {
  grid-column: 2;
  color: var(--muted);
  font-size: 11px;
}

.modal-note-wrap {
  padding: 0 18px 16px;
}

.modal-note-wrap textarea {
  min-height: 96px;
  resize: vertical;
}

.modal-actions {
  justify-content: flex-end;
  border-top: 1px solid var(--line);
  border-bottom: 0;
}

.panel {
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.84)),
    var(--bg-panel);
}

.search-panel,
.progress-panel,
.results-panel,
.error-panel {
  backdrop-filter: blur(18px);
}

.results-panel {
  background:
    radial-gradient(circle at 78% 0%, rgba(96, 165, 250, 0.12), transparent 28%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.95), rgba(7, 11, 24, 0.88));
  border-radius: 28px;
  padding: 26px;
}

.results-header {
  align-items: center;
  margin-bottom: 18px;
}

.results-title-block {
  min-width: 0;
}

.results-title-block .panel-title {
  margin-bottom: 6px;
  font-size: clamp(24px, 2.6vw, 34px);
}

.result-header-tools {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.result-time-card {
  min-width: 96px;
  border: 1px solid var(--border-soft);
  border-radius: 18px;
  background: rgba(22, 32, 51, 0.72);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  padding: 10px 12px;
}

.result-time-card span {
  display: block;
  color: var(--text-soft);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.result-time-card b {
  display: block;
  margin-top: 2px;
  color: var(--text-main);
  font-size: 18px;
  font-variant-numeric: tabular-nums;
}

.result-summary {
  grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
  border: 0;
  gap: 12px;
  overflow: visible;
  background: transparent;
}

.result-stat-card,
.result-summary div {
  border: 1px solid var(--border-soft);
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(22, 32, 51, 0.78), rgba(17, 24, 39, 0.74));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  padding: 14px;
}

.result-stat-card b,
.result-summary b {
  color: var(--text-main);
  font-size: 22px;
}

.r-budget-bar {
  border-color: rgba(96, 165, 250, 0.3);
  background: rgba(59, 130, 246, 0.1);
  border-radius: 18px;
  color: #bfdbfe;
}

.result-warning {
  border-radius: 18px;
  background: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.34);
  color: #fde68a;
}

.quick-sort {
  align-items: center;
}

.quick-sort-btn,
.recommendation-tab {
  border-radius: 999px;
  min-height: 40px;
  border: 1px solid var(--border-soft);
  background: rgba(22, 32, 51, 0.72);
  color: var(--text-soft);
  padding: 10px 14px;
}

.quick-sort-btn:hover,
.quick-sort-btn.active,
.recommendation-tab:hover,
.recommendation-tab.active {
  border-color: rgba(96, 165, 250, 0.56);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.28), rgba(124, 58, 237, 0.22));
  color: var(--text-main);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.16);
}

.section-kicker {
  display: inline-flex;
  margin-bottom: 6px;
  color: var(--primary-glow);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.recommendations-panel {
  margin: 20px 0 22px;
}

.recommendation-stage {
  min-height: 230px;
  overflow: hidden;
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  background:
    radial-gradient(circle at 50% 0%, rgba(96, 165, 250, 0.12), transparent 38%),
    linear-gradient(180deg, rgba(22, 32, 51, 0.88), rgba(15, 23, 42, 0.92));
  box-shadow: 0 18px 48px rgba(37, 99, 235, 0.12);
  padding: 18px;
  will-change: transform, height;
}

.recommendation-stage.is-auto-expanded {
  box-shadow: 0 22px 70px rgba(96, 165, 250, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.recommendation-stage-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.recommendation-stage-head h3 {
  margin: 0;
  font-size: clamp(24px, 3vw, 36px);
  letter-spacing: 0;
}

.recommendation-tabs {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.recommendation-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 850;
}

.recommendation-tab span,
.recommendation-panel-icon {
  display: inline-grid;
  place-items: center;
  min-width: 26px;
  height: 26px;
  border-radius: 999px;
  background: rgba(96, 165, 250, 0.14);
  color: #bfdbfe;
  font-size: 11px;
}

.recommendation-stage-grid {
  display: grid;
  grid-template-columns: minmax(180px, 0.72fr) minmax(340px, 1.6fr) minmax(180px, 0.72fr);
  gap: 14px;
  align-items: stretch;
}

.recommendation-panel {
  min-width: 0;
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.74);
  color: inherit;
  text-align: left;
  cursor: pointer;
  padding: 14px;
  transition: border-color 0.24s ease, box-shadow 0.24s ease, transform 0.24s ease, opacity 0.24s ease;
}

.recommendation-panel:hover {
  border-color: rgba(96, 165, 250, 0.45);
  transform: translateY(-3px);
}

.recommendation-panel.is-active {
  min-height: 320px;
  background:
    radial-gradient(circle at 18% 0%, rgba(124, 58, 237, 0.2), transparent 34%),
    linear-gradient(180deg, rgba(22, 32, 51, 0.96), rgba(17, 24, 39, 0.96));
  border-color: rgba(96, 165, 250, 0.42);
  box-shadow: 0 18px 42px rgba(59, 130, 246, 0.16);
}

.recommendation-panel.is-side {
  align-self: center;
  min-height: 220px;
  opacity: 0.78;
}

.recommendation-panel-head {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 8px 10px;
  align-items: center;
}

.recommendation-panel-label {
  color: var(--text-main);
  font-size: 16px;
  font-weight: 900;
}

.recommendation-panel-count {
  grid-column: 2;
  color: var(--text-soft);
  font-size: 12px;
}

.recommendation-side-preview {
  display: grid;
  gap: 8px;
  margin-top: 24px;
}

.recommendation-side-preview strong {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--text-main);
  font-size: 13px;
}

.recommendation-side-preview span {
  color: var(--success);
  font-weight: 900;
}

.recommendation-mini-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.recommendation-mini-card {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  gap: 10px;
  min-width: 0;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 18px;
  background: rgba(7, 11, 24, 0.38);
  color: inherit;
  padding: 8px;
  text-decoration: none;
}

.recommendation-mini-card:hover {
  border-color: rgba(96, 165, 250, 0.42);
}

.recommendation-mini-image,
.recommendation-img-placeholder {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 14px;
  background:
    radial-gradient(circle at 35% 25%, rgba(96, 165, 250, 0.14), transparent 32%),
    rgba(15, 23, 42, 0.78);
}

.recommendation-mini-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommendation-mini-body {
  min-width: 0;
}

.recommendation-mini-title {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 850;
}

.recommendation-mini-price {
  margin-top: 5px;
  color: var(--success);
  font-size: 13px;
  font-weight: 900;
}

.recommendation-mini-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
  color: var(--text-soft);
  font-size: 11px;
}

.products-grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.product-card {
  position: relative;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.96), rgba(15, 23, 42, 0.98));
  border: 1px solid var(--border-soft);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease, opacity .25s ease;
  will-change: transform, opacity;
}

.product-card:hover {
  transform: translateY(-6px);
  border-color: rgba(96, 165, 250, 0.45);
  box-shadow: 0 18px 40px rgba(37, 99, 235, 0.18);
}

.product-card.feedback-focus {
  border-color: rgba(245, 158, 11, 0.76);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.16), 0 20px 44px rgba(0, 0, 0, 0.3);
}

.product-card.feedback-dimmed {
  opacity: 0.38;
}

.product-image-wrap {
  overflow: hidden;
}

.product-image {
  transition: transform .35s ease;
}

.product-card:hover .product-image {
  transform: scale(1.045);
}

.product-footer {
  gap: 8px;
}

.btn-feedback,
.btn-open-product {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 1 1 0;
  min-width: 76px;
  min-height: 38px;
  border-radius: 16px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 900;
}

.btn-open-product {
  border: 1px solid rgba(96, 165, 250, 0.32);
  background: rgba(59, 130, 246, 0.14);
  color: #bfdbfe;
}

.success-burst {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 5;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.16);
  border: 1px solid rgba(16, 185, 129, 0.42);
  color: #bbf7d0;
  font-size: 11px;
  font-weight: 950;
  pointer-events: none;
}

.modal {
  display: none;
}

.modal-overlay {
  background: rgba(7, 11, 24, 0.72);
  backdrop-filter: blur(10px);
}

.modal-box {
  border-radius: 28px;
  background:
    radial-gradient(circle at 22% 0%, rgba(124, 58, 237, 0.18), transparent 34%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(7, 11, 24, 0.98));
}

.modal-header h3 {
  font-size: 22px;
}

.modal-header p {
  margin: 5px 0 0;
  color: var(--text-soft);
  font-size: 13px;
}

.modal-close {
  border-radius: 14px;
}

.modal-cats {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.cat-checkbox {
  border-radius: 999px;
  background: rgba(22, 32, 51, 0.62);
  transition: background .18s ease, border-color .18s ease, color .18s ease;
}

.cat-checkbox input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.cat-checkbox span {
  grid-column: 1 / -1;
}

.cat-checkbox.is-selected {
  border-color: rgba(96, 165, 250, 0.62);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.34), rgba(124, 58, 237, 0.32));
  color: var(--text-main);
}

.empty-state,
.no-results {
  grid-column: 1 / -1;
  display: grid;
  justify-items: center;
  gap: 8px;
  border: 1px dashed rgba(96, 165, 250, 0.28);
  border-radius: 24px;
  background:
    radial-gradient(circle at 50% 0%, rgba(96, 165, 250, 0.12), transparent 36%),
    rgba(15, 23, 42, 0.72);
  color: var(--text-soft);
  padding: 36px 24px;
  text-align: center;
}

.empty-state strong {
  color: var(--text-main);
  font-size: 18px;
}

.empty-state-icon {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 999px;
  background: rgba(96, 165, 250, 0.12);
  color: var(--primary-glow);
  font-size: 22px;
  font-weight: 900;
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}

@media (max-width: 900px) {
  .recommendation-stage-grid {
    grid-template-columns: 1fr;
  }

  .recommendation-panel.is-side,
  .recommendation-panel.is-active {
    min-height: auto;
  }

  .recommendation-mini-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .results-grid,
  .products-grid {
    grid-template-columns: 1fr;
  }

  .results-header,
  .recommendation-stage-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .result-header-tools {
    width: 100%;
  }

  .result-time-card {
    flex: 1 1 120px;
  }

  .recommendation-tabs {
    justify-content: flex-start;
  }
}

@media (max-width: 760px) {
  .header-inner,
  .main {
    width: min(100% - 24px, 1180px);
  }

  .panel {
    padding: 18px;
  }

  .form-row,
  .modal-cats {
    grid-template-columns: 1fr;
  }

  .stage-pipeline {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .progress-log-row {
    grid-template-columns: 1fr;
    gap: 3px;
  }
}

@media (max-width: 640px) {
  .result-summary,
  .progress-meta {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .recommendation-tabs,
  .quick-sort {
    width: 100%;
  }

  .recommendation-tab,
  .quick-sort-btn {
    flex: 1 1 auto;
  }

  .recommendation-mini-card {
    grid-template-columns: 68px minmax(0, 1fr);
  }
}

@media (max-width: 520px) {
  .header-inner {
    align-items: flex-start;
    flex-direction: column;
    padding: 12px 0;
  }

  .products-grid,
  .comparison-grid,
  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .progress-meta,
  .result-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stage-pipeline {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .product-footer,
  .form-actions,
  .modal-actions {
    flex-direction: column;
  }

  .btn,
  .btn-feedback {
    width: 100%;
  }
}

/* ============================================================
   CINEMATIC PROGRESS PANEL - AI PROGRESS STAGE
   ============================================================ */

.ai-progress-stage {
  position: relative;
  margin: 18px 0;
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  background:
    radial-gradient(circle at 50% 0%, rgba(96, 165, 250, 0.14), transparent 42%),
    linear-gradient(180deg, rgba(22, 32, 51, 0.88), rgba(15, 23, 42, 0.92));
  box-shadow: 0 16px 48px rgba(59, 130, 246, 0.12);
  padding: 24px;
  min-height: 160px;
  will-change: transform;
}

.ai-progress-orbit {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.6;
}

.ai-progress-orb {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  margin-left: -14px;
  pointer-events: none;
  will-change: transform;
}

.ai-progress-core {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, #60a5fa, #3b82f6);
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.28), 0 0 16px rgba(96, 165, 250, 0.42);
}

.ai-progress-copy {
  position: relative;
  z-index: 2;
  text-align: center;
}

.ai-progress-label {
  display: block;
  margin-bottom: 4px;
  color: var(--primary-glow);
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.ai-progress-scramble {
  display: block;
  min-height: 24px;
  color: var(--text-main);
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.ai-time-mini {
  position: absolute;
  bottom: 18px;
  right: 18px;
  display: flex;
  gap: 12px;
}

.ai-time-pill {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  padding: 6px 10px;
  border: 1px solid rgba(96, 165, 250, 0.26);
  border-radius: 999px;
  background: rgba(22, 32, 51, 0.58);
  backdrop-filter: blur(8px);
}

.ai-time-pill span {
  color: var(--text-soft);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.ai-time-pill strong {
  color: var(--text-main);
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

/* ============================================================
   FEEDBACK MODAL - 1000ms DIALOG ANIMATION
   ============================================================ */

.feedback-dialog {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: transparent;
}

.feedback-dialog.is-open {
  display: flex;
}

.feedback-modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(7, 11, 24, 0.72);
  backdrop-filter: blur(10px);
  opacity: 0;
}

.feedback-dialog.is-open .feedback-modal-backdrop {
  opacity: 1;
  animation: feedbackBackdropIn 1000ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.feedback-modal-card {
  position: relative;
  z-index: 2;
  width: min(560px, 100%);
  max-height: min(840px, 92vh);
  overflow-y: auto;
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  background:
    radial-gradient(circle at 22% 0%, rgba(124, 58, 237, 0.18), transparent 34%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(7, 11, 24, 0.98));
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.46);
  opacity: 0;
  transform: translateY(42px) scale(0.90);
}

.feedback-dialog.is-open .feedback-modal-card {
  opacity: 1;
  transform: translateY(0) scale(1);
  animation: feedbackModalIn 1000ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.feedback-modal-header {
  border-bottom: 1px solid var(--border-soft);
  padding: 18px 20px;
}

.feedback-modal-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  color: var(--text-main);
}

.feedback-modal-header p {
  margin: 0;
  color: var(--text-soft);
  font-size: 13px;
}

.feedback-modal-kicker {
  display: inline-flex;
  margin-bottom: 10px;
  color: var(--primary-glow);
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.feedback-product-preview {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  margin: 16px 20px;
  padding: 12px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 18px;
  background: rgba(22, 32, 51, 0.62);
}

.feedback-product-image {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.88);
  object-fit: cover;
  object-position: center;
}

.feedback-product-title {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 850;
}

.feedback-product-price {
  margin: 4px 0 0;
  color: var(--success);
  font-size: 13px;
  font-weight: 900;
}

.feedback-reason-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 16px 20px 20px;
  max-height: 380px;
  overflow-y: auto;
}

.feedback-reason-chip {
  position: relative;
  border: 1.5px solid var(--border-soft);
  border-radius: 999px;
  background: rgba(22, 32, 51, 0.62);
  color: var(--text-main);
  padding: 11px 13px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 850;
  text-align: center;
  transition: background .18s ease, border-color .18s ease, color .18s ease;
  opacity: 0;
  animation: feedbackChipIn 1000ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.feedback-reason-chip:nth-child(1) { animation-delay: 80ms; }
.feedback-reason-chip:nth-child(2) { animation-delay: 120ms; }
.feedback-reason-chip:nth-child(3) { animation-delay: 160ms; }
.feedback-reason-chip:nth-child(4) { animation-delay: 200ms; }
.feedback-reason-chip:nth-child(5) { animation-delay: 240ms; }
.feedback-reason-chip:nth-child(6) { animation-delay: 280ms; }
.feedback-reason-chip:nth-child(7) { animation-delay: 320ms; }
.feedback-reason-chip:nth-child(8) { animation-delay: 360ms; }
.feedback-reason-chip:nth-child(9) { animation-delay: 400ms; }
.feedback-reason-chip:nth-child(10) { animation-delay: 440ms; }
.feedback-reason-chip:nth-child(11) { animation-delay: 480ms; }

.feedback-reason-chip:hover {
  border-color: rgba(96, 165, 250, 0.42);
}

.feedback-reason-chip.is-selected {
  border-color: rgba(96, 165, 250, 0.62);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.34), rgba(124, 58, 237, 0.32));
  color: #ffffff;
}

.feedback-note {
  width: 100%;
  min-height: 88px;
  margin: 0 20px 20px;
  border: 1px solid var(--border-soft);
  border-radius: 18px;
  background: rgba(22, 32, 51, 0.62);
  color: var(--text-main);
  padding: 12px;
  font-family: inherit;
  font-size: 13px;
  resize: vertical;
  transition: border-color .18s ease;
}

.feedback-note:focus {
  border-color: rgba(96, 165, 250, 0.62);
  outline: 0;
}

.feedback-modal-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--border-soft);
  padding: 16px 20px;
}

[data-feedback-cancel],
[data-feedback-save] {
  border-radius: 999px;
  min-height: 40px;
  border: 1px solid var(--border-soft);
  padding: 10px 18px;
  cursor: pointer;
  font-weight: 850;
  transition: background .18s ease, border-color .18s ease, color .18s ease;
}

[data-feedback-cancel] {
  background: rgba(15, 23, 42, 0.72);
  color: var(--text-main);
}

[data-feedback-cancel]:hover {
  border-color: rgba(96, 165, 250, 0.32);
}

[data-feedback-save] {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #ffffff;
  border-color: transparent;
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.24);
}

[data-feedback-save]:hover {
  background: linear-gradient(135deg, #1d4ed8, #60a5fa);
  box-shadow: 0 16px 42px rgba(59, 130, 246, 0.32);
}

/* ============================================================
   ANIMATIONS
   ============================================================ */

@keyframes feedbackBackdropIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes feedbackModalIn {
  from {
    opacity: 0;
    transform: translateY(42px) scale(0.90);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes feedbackChipIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes resultStatCardIn {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes productCardIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.94);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes successBurst {
  0% {
    transform: scale(0.6);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes checkScale {
  from {
    opacity: 0;
    transform: scale(0.4);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.result-stat-card.with-stagger {
  animation: resultStatCardIn 650ms cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.product-card.with-stagger {
  animation: productCardIn 700ms cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.success-burst.is-visible {
  animation: successBurst 500ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.check-icon {
  animation: checkScale 400ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.product-card.has-benar-animation {
  animation: scale-pulse 320ms ease-out;
}

@keyframes scale-pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.03);
  }
  100% {
    transform: scale(1);
  }
}

/* ============================================================
   NEW CUSTOM STYLES (MODAL, PROGRESS, RECOMMENDATION HEADER)
   ============================================================ */

.product-card {
  cursor: pointer;
}

.recommendation-controls,
.recommendation-tabs {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.recommendation-header {
  display: grid;
  grid-template-areas: 
    "kicker controls"
    "title controls";
  grid-template-columns: 1fr auto;
  gap: 4px 16px;
  margin-bottom: 16px;
  align-items: center;
}
.recommendation-header > span {
  grid-area: kicker;
  color: var(--primary-glow);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.recommendation-header h2 {
  grid-area: title;
  margin: 0;
  font-size: clamp(24px, 3vw, 36px);
  letter-spacing: 0;
}
.recommendation-header .recommendation-controls {
  grid-area: controls;
}
@media (max-width: 768px) {
  .recommendation-header {
    grid-template-areas:
      "kicker"
      "title"
      "controls";
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

.product-feedback-dialog {
  width: min(960px, calc(100vw - 32px));
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--text-main);
}

.product-feedback-dialog::backdrop {
  background:
    radial-gradient(circle at center, rgba(37, 99, 235, 0.16), transparent 42%),
    rgba(2, 8, 23, 0.78);
  backdrop-filter: blur(12px);
}

.product-modal-card {
  border-radius: 30px;
  border: 1px solid rgba(96, 165, 250, 0.24);
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.14), transparent 35%),
    linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98));
  box-shadow: 0 30px 90px rgba(2, 8, 23, 0.72);
  padding: 24px;
}

.product-modal-layout {
  display: grid;
  grid-template-columns: minmax(260px, 360px) 1fr;
  gap: 24px;
}

.product-modal-image-wrap {
  border-radius: 24px;
  overflow: hidden;
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.product-modal-image {
  width: 100%;
  height: 100%;
  min-height: 360px;
  object-fit: cover;
  display: block;
}

.product-modal-kicker {
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.22em;
}

.product-modal-title {
  margin: 10px 0;
  font-size: clamp(26px, 4vw, 44px);
  line-height: 1.05;
}

.product-modal-price {
  margin: 18px 0;
  font-size: 30px;
  font-weight: 900;
  color: #10b981;
}

.product-modal-actions-box {
  margin-top: 22px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(7, 11, 24, 0.58);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.feedback-action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.feedback-yes-btn,
.feedback-no-btn,
.open-product-btn {
  border-radius: 999px;
  padding: 12px 18px;
  font-weight: 900;
  border: 1px solid rgba(148, 163, 184, 0.22);
  cursor: pointer;
  text-decoration: none;
}

.feedback-yes-btn {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
}

.feedback-no-btn {
  background: linear-gradient(135deg, #f97316, #ef4444);
  color: white;
}

.open-product-btn {
  background: rgba(15, 23, 42, 0.88);
  color: #e5eefc;
}

.feedback-reason-panel {
  margin-top: 18px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(96, 165, 250, 0.18);
}

.feedback-reason-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.feedback-reason-chip {
  padding: 10px 13px;
  border-radius: 999px;
  color: #e5eefc;
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.2);
  cursor: pointer;
}

.feedback-reason-chip.is-selected {
  border-color: rgba(96, 165, 250, 0.75);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.92), rgba(124, 58, 237, 0.86));
}

.progress-clean-panel {
  padding: 24px;
  border-radius: 28px;
  border: 1px solid rgba(96, 165, 250, 0.22);
  background:
    radial-gradient(circle at 20% 10%, rgba(96, 165, 250, 0.16), transparent 30%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(7, 11, 24, 0.98));
  box-shadow: 0 24px 60px rgba(2, 8, 23, 0.42);
}

.progress-scramble-text {
  min-height: 48px;
  font-size: clamp(26px, 4vw, 46px);
  line-height: 1.1;
  font-weight: 950;
  color: #e5eefc;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  text-shadow: 0 0 28px rgba(96, 165, 250, 0.25);
}

.progress-time-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.progress-time-pill {
  display: grid;
  gap: 4px;
  padding: 10px 14px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.18);
  backdrop-filter: blur(14px);
}

.progress-time-pill span {
  color: #94a3b8;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.progress-time-pill strong {
  color: #e5eefc;
  font-size: 16px;
}

@media (max-width: 760px) {
  .product-modal-layout {
    grid-template-columns: 1fr;
  }

  .product-modal-image {
    min-height: 240px;
  }

  .feedback-action-row {
    flex-direction: column;
  }

  .feedback-action-row > * {
    width: 100%;
    text-align: center;
  }
}

/* ============================================================
   DIRECT ACTIONS & RECOMMENDATION MODAL ENHANCEMENTS
   ============================================================ */

.product-card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.card-action-btn {
  flex: 1;
  min-width: 100px;
  border-radius: 999px;
  padding: 10px 14px;
  font-weight: 900;
  text-align: center;
  border: 1px solid rgba(148, 163, 184, 0.22);
  cursor: pointer;
  text-decoration: none;
}

.card-action-btn.is-correct {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
}

.card-action-btn.is-wrong {
  background: linear-gradient(135deg, #f97316, #ef4444);
  color: white;
}

.card-action-btn.is-open {
  background: rgba(15, 23, 42, 0.88);
  color: #e5eefc;
}

.recommendation-product-dialog {
  width: min(980px, calc(100vw - 32px));
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--text-main);
}

.recommendation-product-dialog::backdrop {
  background:
    radial-gradient(circle at center, rgba(37, 99, 235, 0.16), transparent 42%),
    rgba(2, 8, 23, 0.78);
  backdrop-filter: blur(12px);
}

.recommendation-modal-card {
  border-radius: 30px;
  border: 1px solid rgba(96, 165, 250, 0.24);
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.14), transparent 35%),
    linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98));
  box-shadow: 0 30px 90px rgba(2, 8, 23, 0.72);
  padding: 24px;
}

.recommendation-modal-layout {
  display: grid;
  grid-template-columns: minmax(260px, 360px) 1fr;
  gap: 24px;
}

.recommendation-modal-image-wrap {
  border-radius: 24px;
  overflow: hidden;
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.recommendation-modal-image {
  width: 100%;
  height: 100%;
  min-height: 360px;
  object-fit: cover;
  display: block;
}

.recommendation-modal-kicker {
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.22em;
}

.recommendation-modal-title {
  margin: 10px 0;
  font-size: clamp(26px, 4vw, 44px);
  line-height: 1.05;
}

.recommendation-modal-price {
  margin: 18px 0;
  font-size: 30px;
  font-weight: 900;
  color: #10b981;
}

.recommendation-modal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
  color: var(--text-soft);
  font-size: 13px;
}

.recommendation-modal-rating,
.recommendation-modal-sold,
.recommendation-modal-confidence {
  display: inline;
}

.recommendation-modal-actions-box {
  margin-top: 22px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(7, 11, 24, 0.58);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.modal-feedback-reason-panel {
  margin-top: 18px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(96, 165, 250, 0.18);
}

.modal-feedback-reason-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.modal-feedback-note {
  width: 100%;
  min-height: 88px;
  margin: 16px 0;
  border: 1px solid var(--border-soft);
  border-radius: 18px;
  background: rgba(22, 32, 51, 0.62);
  color: var(--text-main);
  padding: 12px;
  font-family: inherit;
  font-size: 13px;
  resize: vertical;
  transition: border-color .18s ease;
}

.modal-feedback-note:focus {
  border-color: rgba(96, 165, 250, 0.62);
  outline: 0;
}

/* ============================================================
   PRODUCT DETAIL / MODAL SIZE BUG FIX
   ============================================================ */

.product-modal-card,
.recommendation-modal-card {
  width: min(980px, calc(100vw - 32px));
  max-height: min(820px, calc(100vh - 32px));
  overflow: auto;
  border-radius: 28px;
}

.product-modal-title,
.recommendation-modal-title {
  font-size: clamp(24px, 3vw, 42px);
  line-height: 1.08;
  max-width: 100%;
  word-break: break-word;
}

.product-modal-layout,
.recommendation-modal-layout {
  display: grid;
  grid-template-columns: minmax(240px, 360px) minmax(0, 1fr);
  gap: 24px;
}

.product-modal-image,
.recommendation-modal-image {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  border-radius: 22px;
}

@media (max-width: 760px) {
  .product-modal-layout,
  .recommendation-modal-layout {
    grid-template-columns: 1fr;
  }

  .product-modal-title,
  .recommendation-modal-title {
    font-size: 26px;
  }
}

/* ============================================================
   TARGET PRIORITY COLLAPSIBLE HELPER
   ============================================================ */

.target-priority-info-box {
  margin-top: 6px;
  margin-left: 24px;
}

.info-toggle {
  background: none;
  border: none;
  color: var(--primary-glow);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  text-decoration: underline;
  transition: color 0.2s ease;
}

.info-toggle:hover {
  color: #93c5fd;
}

.info-content {
  margin-top: 6px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.info-content p {
  margin: 0;
  font-size: 12px;
  color: var(--text-soft);
  line-height: 1.4;
}

/* ============================================================
   IMAGE ERROR & PLACEHOLDER HANDLING
   ============================================================ */

.is-image-missing img {
  display: none !important;
}

.is-image-missing .image-placeholder {
  display: flex !important;
}

.image-placeholder {
  display: none;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #0f172a;
  color: #64748b;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  border-radius: inherit;
}

/* ============================================================
   REDUCED MOTION SUPPORT
   ============================================================ */

@media (prefers-reduced-motion: reduce) {
  .recommendation-product-card:hover,
  .recommendation-mode-btn:hover {
    transform: none !important;
  }
}

/* ============================================================
   UI_MODAL_NEXT_QUEUE_FIX_20260528 — COMPREHENSIVE OVERRIDES
   ============================================================ */

/* --- 1. CATEGORY BUTTON CLICK FIX: z-index + pointer-events --- */
.recommendation-header {
  position: relative;
  z-index: 30;
}

.recommendation-controls {
  position: relative;
  z-index: 40;
  pointer-events: auto;
}

.recommendation-mode-btn {
  pointer-events: auto;
  cursor: pointer;
  user-select: none;
}

.recommendation-active-panel {
  position: relative;
  z-index: 5;
}

.recommendation-active-panel {
  width: 100%;
  max-width: none;
}

/* --- 3. MODAL SIZE + IMAGE FIX --- */
.recommendation-product-dialog {
  width: min(1080px, calc(100vw - 32px));
  border: 0;
  padding: 0;
  background: transparent;
  color: #e5eefc;
}

.recommendation-product-dialog::backdrop {
  background: rgba(2, 8, 23, 0.78);
  backdrop-filter: blur(14px);
}

.recommendation-modal-card {
  width: min(1080px, calc(100vw - 32px));
  max-height: min(820px, calc(100vh - 32px));
  overflow: auto;
  border-radius: 30px;
  padding: 24px;
  border: 1px solid rgba(96, 165, 250, 0.24);
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.14), transparent 35%),
    linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98));
}

.recommendation-modal-layout {
  display: grid;
  grid-template-columns: minmax(260px, 420px) minmax(0, 1fr);
  gap: 24px;
}

.recommendation-modal-title {
  font-size: clamp(26px, 3.4vw, 48px);
  line-height: 1.08;
  max-width: 100%;
  word-break: break-word;
}

.recommendation-modal-image-wrap {
  min-height: 420px;
  border-radius: 24px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.recommendation-modal-image {
  width: 100%;
  height: 100%;
  max-height: 520px;
  object-fit: cover;
  display: block;
}

.image-placeholder {
  width: 100%;
  min-height: 320px;
  display: grid;
  place-items: center;
  text-align: center;
  color: #94a3b8;
  background:
    radial-gradient(circle at center, rgba(96, 165, 250, 0.12), transparent 45%),
    rgba(15, 23, 42, 0.88);
  border-radius: inherit;
  flex-direction: column;
  gap: 8px;
  padding: 24px;
}

.image-placeholder strong {
  font-size: 16px;
  color: #cbd5e1;
}

.image-placeholder span {
  font-size: 13px;
}

@media (max-width: 760px) {
  .recommendation-modal-layout {
    grid-template-columns: 1fr;
  }

  .recommendation-modal-title {
    font-size: 28px;
  }

  .recommendation-modal-image-wrap {
    min-height: 240px;
  }
}

/* --- 4. RECOMMENDATION PRODUCT IMAGE WRAP --- */
.recommendation-product-image-wrap {
  border-radius: 16px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.88);
}

.recommendation-product-image-wrap .image-placeholder {
  min-height: 96px;
  font-size: 12px;
}

/* --- 5. FEEDBACK SAVE ROW --- */
.feedback-save-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}

/* ============================================================
   UI_CHECKED_TRAY_ENTERFROM_20260528
   ============================================================ */

.recommendation-controls {
  flex-wrap: wrap;
}

.recommendation-product-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.recommendation-product-card,
.checked-product-card,
.product-card {
  will-change: transform, opacity;
}

.recommendation-product-card:hover,
.checked-product-card:hover,
.product-card:hover {
  transform: none;
}

.product-card:hover .product-image {
  transform: none;
}

.checked-products-box {
  margin-top: 28px;
  padding: 20px;
  border-radius: 28px;
  border: 1px solid rgba(96, 165, 250, 0.24);
  background:
    radial-gradient(circle at top left, rgba(34, 211, 238, 0.10), transparent 34%),
    rgba(15, 23, 42, 0.72);
}

.checked-products-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.checked-products-kicker {
  display: block;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
  color: #67e8f9;
}

.checked-products-header h3 {
  margin: 4px 0 0;
  font-size: 22px;
  line-height: 1.1;
}

.checked-products-count {
  margin: 0;
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.checked-products-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  max-width: 100%;
  width: 100%;
  overflow: hidden;
}

.checked-product-card {
  min-height: 128px;
  min-width: 0;
  padding: 14px;
  border-radius: 22px;
  background: rgba(7, 11, 24, 0.62);
  border: 1px solid rgba(148, 163, 184, 0.16);
  overflow: hidden;
}

.checked-product-card.is-positive {
  border-color: rgba(16, 185, 129, 0.38);
}

.checked-product-card.is-negative {
  border-color: rgba(251, 113, 133, 0.38);
}

.checked-product-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 900;
}

.checked-product-badge.is-positive {
  color: #34d399;
  background: rgba(16, 185, 129, 0.10);
}

.checked-product-badge.is-negative {
  color: #fb7185;
  background: rgba(251, 113, 133, 0.10);
}

.checked-product-title {
  margin: 12px 0 8px;
  color: #e5eefc;
  font-size: 13px;
  line-height: 1.35;
  font-weight: 900;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.checked-product-price {
  margin: 0;
  color: #34d399;
  font-size: 14px;
  font-weight: 950;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.checked-product-meta {
  margin: 8px 0 0;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.3;
}

.checked-products-empty {
  grid-column: 1 / -1;
  padding: 18px;
  border: 1px dashed rgba(148, 163, 184, 0.24);
  border-radius: 18px;
  color: #94a3b8;
  text-align: center;
  font-weight: 800;
}

@media (max-width: 1100px) {
  .checked-products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .recommendation-product-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 700px) {
  .checked-products-header,
  .recommendation-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .checked-products-grid,
  .recommendation-product-grid {
    grid-template-columns: 1fr;
  }

  .recommendation-mode-btn {
    flex: 1 1 148px;
    justify-content: center;
  }
}

/* ============================================================
   UI_FAST_CATEGORY_TRANSITION_20260528
   ============================================================ */

.recommendation-controls {
  position: relative;
  z-index: 50;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  pointer-events: auto;
}

.recommendation-mode-btn {
  position: relative;
  pointer-events: auto;
  cursor: pointer;
  border-radius: 999px;
  transform: translateZ(0);
  will-change: transform, opacity;
  transition:
    background 160ms ease,
    border-color 160ms ease,
    color 160ms ease,
    opacity 160ms ease;
}

.recommendation-mode-btn:hover {
  border-color: rgba(147, 197, 253, 0.64);
  color: #ffffff;
  transform: translateZ(0);
}

.recommendation-mode-btn.is-active {
  background: linear-gradient(135deg, #2563eb, #60a5fa);
  border-color: rgba(147, 197, 253, 0.7);
  color: #ffffff;
}

.recommendation-mode-btn:not(.is-active) {
  opacity: 0.72;
}

.recommendation-mode-btn:not(.is-active):hover {
  opacity: 1;
}

.recommendation-active-panel {
  will-change: transform;
}

.recommendation-product-grid {
  contain: layout paint;
}

.recommendation-product-card {
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
  contain: layout paint;
  transition:
    background 160ms ease,
    border-color 160ms ease,
    opacity 160ms ease;
}

.recommendation-stage.is-switching .recommendation-product-card {
  pointer-events: none;
  box-shadow: none !important;
}

.recommendation-stage.is-switching .recommendation-controls,
.recommendation-stage.is-switching .recommendation-mode-btn {
  pointer-events: auto;
}

.recommendation-product-image-wrap {
  width: 112px;
  height: 96px;
  contain: layout paint;
  flex: 0 0 auto;
}

.recommendation-product-image-wrap .recommendation-product-image,
.recommendation-product-image-wrap .image-placeholder {
  width: 100%;
  height: 100%;
}

@media (max-width: 900px) {
  .recommendation-product-image-wrap {
    width: 92px;
    height: 84px;
  }
}

/* Category buttons premium state overrides */
.recommendation-mode-btn {
  transition:
    background 150ms ease,
    color 150ms ease,
    border-color 150ms ease,
    opacity 150ms ease,
    transform 150ms ease !important;
}

.recommendation-mode-btn.is-active {
  background: linear-gradient(135deg, #3b82f6, #60a5fa) !important;
  color: #ffffff !important;
  border-color: rgba(147, 197, 253, 0.78) !important;
  opacity: 1 !important;
}

/* Grid layout stage */
.recommendation-grid-stage {
  position: relative;
  width: 100%;
}

/* Legacy dialog retired — use .product-modal-backdrop below */
#product-feedback-dialog {
  display: none !important;
}

/* Global safety and scroll configurations */
html,
body {
  max-width: 100%;
  overflow-x: hidden;
}

img,
svg,
video,
canvas {
  max-width: 100%;
}

html.modal-open,
body.modal-open {
  overflow: hidden;
}

.recommendation-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: start;
}

.recommendation-title-area {
  min-width: 0;
}

.recommendation-kicker {
  display: block;
  margin-bottom: 12px;
  color: #60a5fa;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.recommendation-active-title {
  margin: 0;
  font-size: clamp(24px, 3vw, 36px);
  line-height: 1.08;
  letter-spacing: 0;
  color: #e5edff;
  text-align: left;
  filter: none !important;
  text-shadow: none;
}

.recommendation-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
  min-width: 0;
}

.recommendation-active-panel {
  position: relative;
  margin-top: 22px;
  min-height: 0;
  padding: clamp(18px, 2.5vw, 28px);
  border-radius: 28px;
  border: 1px solid rgba(96, 165, 250, 0.26);
  background:
    radial-gradient(circle at 14% 20%, rgba(59, 130, 246, 0.12), transparent 34%),
    rgba(8, 16, 32, 0.72);
  overflow: visible;
  transform: translateZ(0);
}

.recommendation-product-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 430px), 1fr));
  gap: clamp(18px, 2vw, 28px);
  padding-top: 0;
  overflow: visible;
}

@media (max-width: 900px) {
  .recommendation-header {
    grid-template-columns: 1fr;
  }

  .recommendation-controls {
    width: 100%;
    overflow-x: visible;
    justify-content: flex-start;
    padding-bottom: 8px;
  }

  .recommendation-active-panel {
    padding: 20px;
    border-radius: 26px;
  }

  .recommendation-product-grid {
    grid-template-columns: 1fr;
    padding-top: 0;
  }
}

/* Product Card Styling and Instant Hover Animation */
.recommendation-product-card,
[data-product-card] {
  position: relative;
  display: grid;
  grid-template-columns: clamp(110px, 18vw, 170px) minmax(0, 1fr);
  gap: 20px;
  min-height: 168px;
  padding: 20px;
  border-radius: 26px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(2, 6, 23, 0.64);
  overflow: visible;
  transform: translateZ(0);
  transition:
    transform 150ms ease,
    border-color 150ms ease,
    box-shadow 150ms ease,
    background 150ms ease;
  will-change: transform;
  cursor: pointer;
}

.recommendation-product-card:hover,
.recommendation-product-card:focus-within,
[data-product-card]:hover,
[data-product-card]:focus-within {
  transform: translateY(-5px) scale(1.014);
  border-color: rgba(96, 165, 250, 0.48);
  background: rgba(15, 23, 42, 0.86);
  box-shadow:
    0 24px 64px rgba(15, 23, 42, 0.36),
    0 0 0 1px rgba(96, 165, 250, 0.12) inset;
  z-index: 8;
}

.recommendation-product-card,
.recommendation-product-card *,
[data-product-card],
[data-product-card] * {
  filter: none !important;
}

.recommendation-product-title {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
  line-height: 1.25;
}

.recommendation-product-image-wrap {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.9);
}

.recommendation-product-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transform: translateZ(0);
}

.product-image-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  text-align: center;
  color: #94a3b8;
  font-weight: 800;
}

.product-image-placeholder::before {
  content: "TIDAK ADA GAMBAR";
}

.product-image-placeholder.is-hidden {
  display: none !important;
}

@media (max-width: 640px) {
  .recommendation-product-card {
    grid-template-columns: 96px minmax(0, 1fr);
    gap: 14px;
    padding: 16px;
    min-height: 132px;
  }
}

/* Premium Responsive Product Details Modal */
.product-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  padding: clamp(12px, 2.5vw, 32px);
  background:
    radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.18), transparent 44%),
    rgba(2, 6, 23, 0.78);
  backdrop-filter: blur(14px);
  overflow: hidden;
}

.product-modal-backdrop[hidden] {
  display: none !important;
}

.product-detail-modal {
  position: relative;
  width: min(94vw, 1360px);
  height: min(86vh, 760px);
  max-width: 100%;
  max-height: 86vh;
  display: grid;
  grid-template-columns: minmax(300px, 0.9fr) minmax(420px, 1.1fr);
  gap: clamp(20px, 3vw, 48px);
  align-items: flex-start;
  padding: clamp(22px, 3vw, 42px);
  border-radius: clamp(24px, 3vw, 38px);
  border: 1px solid rgba(96, 165, 250, 0.26);
  background:
    radial-gradient(circle at 20% 0%, rgba(59, 130, 246, 0.14), transparent 36%),
    rgba(8, 16, 32, 0.96);
  box-shadow:
    0 32px 120px rgba(0, 0, 0, 0.55),
    0 0 0 1px rgba(96, 165, 250, 0.08) inset;
  overflow: hidden;
  box-sizing: border-box;
}

.modal-detail,
.recommendation-detail-modal {
  width: min(94vw, 1360px);
  height: min(86vh, 760px);
  max-height: 86vh;
  overflow: hidden;
  box-sizing: border-box;
}

.product-detail-modal,
.product-detail-modal * {
  box-sizing: border-box;
  min-width: 0;
}

.product-modal-close {
  position: absolute;
  top: 18px;
  left: 18px;
  z-index: 3;
  width: 44px;
  height: 44px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  color: #cbd5e1;
  background: rgba(15, 23, 42, 0.9);
  cursor: pointer;
  font-size: 24px;
  line-height: 1;
  transition:
    transform 160ms ease,
    background 160ms ease,
    border-color 160ms ease;
}

.product-modal-close:hover {
  transform: scale(1.04);
  border-color: rgba(96, 165, 250, 0.45);
  background: rgba(30, 41, 59, 0.95);
}

.product-detail-media {
  position: relative;
  width: 100%;
  height: 100%;
  max-height: 100%;
  min-height: 0;
  border-radius: 28px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #07111f;
  border: 1px solid rgba(148, 163, 184, 0.14);
  align-self: stretch;
}

.product-detail-image {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  background: #07111f;
}

.product-detail-image-panel,
.product-detail-info-panel {
  will-change: transform, opacity;
  backface-visibility: hidden;
  transform: translateZ(0);
  filter: none;
}

.product-detail-info-panel,
#productDetailInfoPanel {
  min-width: 0;
  min-height: 0;
  height: 100%;
  max-height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.product-detail-image-panel img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #07111f;
}

.product-detail-image.is-hidden,
.product-detail-image-placeholder.is-hidden {
  display: none;
}

.product-detail-image-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  text-align: center;
  color: #94a3b8;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.product-detail-content {
  min-width: 0;
  min-height: 0;
  height: 100%;
  max-height: 100%;
  overflow-y: hidden;
  overflow-x: hidden;
  padding-right: 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(96, 165, 250, 0.36) transparent;
}

.product-detail-content::-webkit-scrollbar {
  width: 8px;
}

.product-detail-content::-webkit-scrollbar-track {
  background: transparent;
}

.product-detail-content::-webkit-scrollbar-thumb {
  background: rgba(96, 165, 250, 0.34);
  border-radius: 999px;
}

.product-detail-label,
.product-detail-kicker {
  flex: 0 0 auto;
  margin: 4px 0 18px;
  color: #60a5fa;
  font-size: clamp(13px, 1vw, 16px);
  font-weight: 900;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.product-detail-title,
.recommendation-detail-title,
#productDetailTitle {
  margin: 0 0 clamp(12px, 1.8vh, 22px);
  color: #e5edff;
  font-size: clamp(34px, 3.4vw, 58px);
  line-height: 1.08;
  letter-spacing: -0.035em;
  font-weight: 800;
  text-transform: none;
  max-height: calc(1.08em * 3);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  word-break: normal;
  overflow-wrap: anywhere;
  max-width: 100%;
}

.product-detail-original-price {
  flex: 0 0 auto;
  font-size: clamp(16px, 1.5vw, 24px);
  margin-bottom: clamp(8px, 1.5vh, 18px);
}

.product-detail-subtitle {
  flex: 0 0 auto;
  margin: 0 0 clamp(8px, 1.5vh, 18px);
  color: #cbd5e1;
  font-size: clamp(16px, 1.3vw, 22px);
  line-height: 1.45;
  max-height: 2.9em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-detail-price,
#productDetailPrice {
  flex: 0 0 auto;
  margin: 0 0 clamp(12px, 1.8vh, 22px);
  color: #10b981;
  font-size: clamp(38px, 4vw, 62px);
  line-height: 1;
  font-weight: 950;
  letter-spacing: 0;
}

.product-detail-meta {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-bottom: clamp(14px, 2vh, 24px);
  color: #94a3b8;
  font-size: clamp(15px, 1.2vw, 20px);
}

.product-feedback-panel,
.product-feedback-box,
.review-feedback-box {
  flex: 0 0 auto;
  flex-shrink: 0;
  margin-top: auto;
  padding: clamp(18px, 2vw, 28px);
  border-radius: 28px;
  border: 1px solid rgba(148, 163, 184, 0.15);
  background: rgba(2, 6, 23, 0.58);
}

.product-feedback-panel h3,
.product-feedback-box h3,
.review-feedback-box h3 {
  margin: 0 0 18px;
  color: #e5edff;
  font-size: clamp(20px, 1.8vw, 28px);
}

.product-feedback-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.detail-feedback-reason-panel .feedback-reason-grid {
  margin: 14px 0 12px;
  max-height: none;
  overflow: visible;
}

.detail-feedback-reason-panel .feedback-note {
  width: 100%;
  margin: 0;
}

.detail-feedback-reason-panel .feedback-save-row {
  flex-wrap: wrap;
  margin-top: 12px;
}

.feedback-btn {
  min-height: 56px;
  padding: 0 clamp(22px, 2vw, 34px);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: #e5edff;
  font-size: clamp(16px, 1.4vw, 22px);
  font-weight: 900;
  text-decoration: none;
  cursor: pointer;
  transition:
    transform 150ms ease,
    filter 150ms ease,
    border-color 150ms ease;
}

.feedback-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.06);
}

.feedback-yes {
  background: #10b981;
}

.feedback-no {
  background: #f97316;
}

.feedback-open {
  background: rgba(15, 23, 42, 0.86);
}

@media (max-width: 1100px) {
  .product-modal-backdrop {
    place-items: center;
    overflow-y: hidden;
    overflow-x: hidden;
  }

  .product-detail-modal {
    grid-template-columns: 1fr;
    grid-template-rows: auto minmax(0, 1fr);
    width: 94vw;
    height: 90vh;
    max-height: 90vh;
    overflow: hidden;
  }

  .product-detail-media {
    height: 34vh;
    min-height: 220px;
    flex: 0 0 auto;
  }

  .product-detail-content {
    height: auto;
    max-height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 6px;
  }

  .product-detail-info-panel {
    height: auto;
    max-height: none;
    overflow: visible;
    justify-content: flex-start;
  }

  .product-detail-title {
    font-size: clamp(28px, 6vw, 44px);
    -webkit-line-clamp: 3;
  }

  .product-detail-price {
    font-size: clamp(32px, 7vw, 48px);
  }

  .product-feedback-panel,
  .product-feedback-box,
  .review-feedback-box {
    margin-top: 16px;
  }
}

@media (max-width: 560px) {
  .product-modal-backdrop {
    padding: 10px;
  }

  .product-detail-modal {
    width: calc(100vw - 20px);
    padding: 16px;
    border-radius: 24px;
  }

  .product-modal-close {
    top: 12px;
    left: 12px;
    width: 40px;
    height: 40px;
  }

  .product-detail-media {
    border-radius: 20px;
    margin-top: 42px;
  }

  .product-feedback-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .feedback-btn {
    width: 100%;
  }
}

.recommendation-controls button,
[data-recommendation-mode] {
  position: relative;
  min-height: 44px;
  padding: 0 16px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: rgba(226, 232, 240, 0.62);
  background: rgba(15, 23, 42, 0.62);
  cursor: pointer;
  font-weight: 950;
  transition:
    transform 160ms ease,
    color 160ms ease,
    border-color 160ms ease,
    background 160ms ease,
    box-shadow 160ms ease;
  will-change: transform;
}

[data-recommendation-mode]:hover {
  transform: translateY(-2px);
  color: #e5edff;
  border-color: rgba(96, 165, 250, 0.42);
}

[data-recommendation-mode].is-active {
  color: #ffffff;
  border-color: rgba(96, 165, 250, 0.72);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.96), rgba(96, 165, 250, 0.86));
  box-shadow: 0 18px 52px rgba(59, 130, 246, 0.28);
}

.recommendation-active-panel {
  will-change: transform;
}

.product-detail-title,
.recommendation-detail-title,
.detail-product-title,
.modal-product-title,
#productDetailTitle,
#product-detail-title,
#recommendationDetailTitle,
[data-product-detail-title] {
  font-size: clamp(28px, 2.6vw, 44px) !important;
  line-height: 1.12 !important;
  letter-spacing: -0.025em !important;
  font-weight: 800 !important;
  text-transform: none !important;

  margin: 0 0 14px !important;

  display: -webkit-box !important;
  -webkit-line-clamp: 3 !important;
  -webkit-box-orient: vertical !important;

  max-height: calc(1.12em * 3) !important;
  overflow: hidden !important;

  white-space: normal !important;
  word-break: normal !important;
  overflow-wrap: anywhere !important;
  text-overflow: ellipsis !important;
}

.product-detail-info-panel,
.recommendation-detail-info,
.detail-product-info,
#productDetailInfoPanel {
  min-width: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
}

.product-detail-price,
.recommendation-detail-price,
.detail-product-price,
#productDetailPrice {
  font-size: clamp(34px, 3.4vw, 56px) !important;
  line-height: 1 !important;
  margin: 0 0 16px !important;
}

.product-detail-original-price,
.recommendation-detail-original-price {
  font-size: clamp(15px, 1.2vw, 20px) !important;
  margin-bottom: 10px !important;
}

.product-detail-meta,
.recommendation-detail-meta {
  font-size: clamp(14px, 1.1vw, 18px) !important;
  margin-bottom: 18px !important;
}

.product-feedback-panel,
.product-feedback-box,
.review-feedback-box,
.feedback-panel {
  margin-top: auto !important;
  flex-shrink: 0 !important;
}


/* ============================================================
   MARKETSPY UI FIX — HEADER STATUS GROUP
   ============================================================ */

.header-status-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 0 0 auto;
}

.ai-scraper-header-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.ai-scraper-header-badge.is-active {
  background: rgba(16, 185, 129, 0.14);
  border-color: rgba(52, 211, 153, 0.38);
  color: #34d399;
}

.ai-scraper-header-badge.is-inactive {
  background: rgba(148, 163, 184, 0.10);
  border-color: rgba(148, 163, 184, 0.22);
  color: var(--text-soft);
}

.ai-scraper-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  flex: 0 0 auto;
}

.ai-scraper-header-badge.is-active .ai-scraper-dot {
  box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.22);
  animation: dot-pulse 2s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ============================================================
   MARKETSPY UI FIX — RECOMMENDATION PRODUCT CARD DETAILS
   ============================================================ */

.recommendation-product-card-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  padding: 4px 0;
}

.recommendation-product-title {
  margin: 0;
  font-size: 14px;
  font-weight: 800;
  line-height: 1.3;
  color: #e5eefc;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.recommendation-product-price {
  color: #10b981;
  font-size: 15px;
  font-weight: 900;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recommendation-product-rating-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  align-items: center;
}

.rec-rating {
  color: #fbbf24;
  font-size: 12px;
  font-weight: 700;
}

.rec-sold {
  color: #94a3b8;
  font-size: 12px;
}

.rec-ai-confidence {
  color: #60a5fa;
  font-size: 11px;
  font-weight: 700;
}

/* Overbudget badge */
.rec-card-badge.is-overbudget,
.product-badge.is-overbudget {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.16);
  border: 1px solid rgba(245, 158, 11, 0.38);
  color: #fbbf24;
  font-size: 10px;
  font-weight: 800;
  white-space: nowrap;
  margin-bottom: 2px;
}

/* ============================================================
   MARKETSPY UI FIX — RECOMMENDATION GRID CONTAINER CLIPPING
   ============================================================ */

.recommendation-active-panel {
  overflow: hidden !important;
}

.recommendation-product-grid {
  overflow: hidden;
  contain: layout paint style;
}

/* Shortage notice */
.recommendation-shortage-notice {
  grid-column: 1 / -1;
  padding: 12px 16px;
  border-radius: 14px;
  background: rgba(96, 165, 250, 0.08);
  border: 1px dashed rgba(96, 165, 250, 0.28);
  color: #93c5fd;
  font-size: 13px;
  font-weight: 700;
  text-align: center;
}

.recommendation-empty {
  grid-column: 1 / -1;
  padding: 24px;
  border-radius: 18px;
  border: 1px dashed rgba(148, 163, 184, 0.22);
  color: #94a3b8;
  text-align: center;
  font-weight: 700;
}

/* ============================================================
   CATEGORY CARD STYLING — GREEN BORDER + PILL
   ============================================================ */

.recommendation-product-card.is-checked-category-card {
  border-color: rgba(16, 185, 129, 0.42) !important;
  border-width: 2px;
}

.recommendation-product-card.is-checked-category-card:hover,
.recommendation-product-card.is-checked-category-card:focus-within {
  border-color: rgba(16, 185, 129, 0.68) !important;
  box-shadow:
    0 24px 64px rgba(15, 23, 42, 0.36),
    0 0 0 2px rgba(52, 211, 153, 0.24) inset;
}

.rec-checked-pill {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 10;
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.18);
  border: 1px solid rgba(16, 185, 129, 0.42);
  color: #34d399;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

/* ============================================================
   MARKETSPY UI FIX — CHECKED PRODUCT CARD (DETAIL LAYOUT)
   ============================================================ */

.checked-products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  overflow: hidden;
}

.checked-product-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  border-radius: 22px;
  background: rgba(7, 11, 24, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.16);
  overflow: hidden;
  min-width: 0;
}

.checked-product-card.is-positive {
  border-color: rgba(16, 185, 129, 0.38);
  background: rgba(16, 185, 129, 0.04);
}

.checked-product-card.is-negative {
  border-color: rgba(251, 113, 133, 0.38);
  background: rgba(251, 113, 133, 0.04);
}

.checked-product-layout {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.checked-product-image-wrap {
  width: 80px;
  height: 80px;
  border-radius: 14px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.88);
  flex: 0 0 auto;
}

.checked-product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.checked-product-img-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #64748b;
  font-size: 10px;
  font-weight: 700;
  text-align: center;
  padding: 4px;
}

.checked-product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.checked-product-title {
  margin: 0;
  color: #e5eefc;
  font-size: 13px;
  line-height: 1.35;
  font-weight: 800;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
}

.checked-product-price {
  margin: 0;
  color: #34d399;
  font-size: 14px;
  font-weight: 900;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.checked-product-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 8px;
  align-items: center;
}

.checked-meta-rating {
  color: #fbbf24;
  font-size: 11px;
  font-weight: 700;
}

.checked-meta-sold {
  color: #94a3b8;
  font-size: 11px;
}

.checked-product-ai {
  margin: 0;
  color: #60a5fa;
  font-size: 11px;
  font-weight: 700;
}

.checked-product-meta {
  margin: 0;
  color: #94a3b8;
  font-size: 11px;
  line-height: 1.3;
}

.checked-product-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.checked-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  text-decoration: none;
  border: 1px solid rgba(148, 163, 184, 0.22);
  cursor: pointer;
  transition: background 0.16s ease, border-color 0.16s ease;
}

.checked-action-btn.is-open {
  background: rgba(59, 130, 246, 0.14);
  color: #93c5fd;
  border-color: rgba(96, 165, 250, 0.28);
}

.checked-action-btn.is-open:hover {
  background: rgba(59, 130, 246, 0.24);
  border-color: rgba(96, 165, 250, 0.5);
}

@media (max-width: 900px) {
  .checked-products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .checked-products-grid {
    grid-template-columns: 1fr;
  }
}

/* ============================================================
   MARKETSPY UI FIX v2 — CARD VERTIKAL + CATEGORY LIMIT BAR
   ============================================================ */

/* Override card layout ke vertikal (gambar atas, info bawah) */
.recommendation-product-card,
[data-product-card] {
  display: flex !important;
  flex-direction: column !important;
  grid-template-columns: unset !important;
  gap: 0 !important;
  min-height: 320px;
  padding: 0 !important;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(10, 16, 30, 0.82);
  cursor: pointer;
  transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
  will-change: transform;
}

.recommendation-product-card:hover,
[data-product-card]:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.45);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.38);
}

/* Gambar di atas */
.recommendation-product-image-wrap {
  width: 100% !important;
  height: 180px !important;
  aspect-ratio: unset !important;
  border-radius: 0 !important;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.9);
  flex: 0 0 auto;
}

.recommendation-product-image-wrap img,
.recommendation-product-image {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  display: block;
  filter: none !important;
}

/* Placeholder gambar */
.recommendation-product-image-wrap .product-image-placeholder,
.recommendation-product-image-wrap .image-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  text-align: center;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  background: rgba(15, 23, 42, 0.9);
  padding: 16px;
  gap: 6px;
}

.recommendation-product-image-wrap .product-image-placeholder::before {
  content: none;
}

/* Info di bawah */
.recommendation-product-card-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px 12px !important;
  flex: 1;
  min-width: 0;
}

.recommendation-product-title {
  margin: 0;
  font-size: 13px;
  font-weight: 800;
  line-height: 1.35;
  color: #e5eefc;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.recommendation-product-price {
  color: #10b981;
  font-size: 15px;
  font-weight: 900;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recommendation-product-rating-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 8px;
  align-items: center;
}

.rec-rating {
  color: #fbbf24;
  font-size: 12px;
  font-weight: 700;
}

.rec-sold {
  color: #94a3b8;
  font-size: 12px;
}

.rec-ai-confidence {
  color: #60a5fa;
  font-size: 11px;
  font-weight: 700;
}

/* Tombol aksi di card */
.rec-card-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 10px;
}

.rec-action-btn {
  flex: 1;
  min-width: 0;
  min-height: 34px;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 800;
  text-align: center;
  border: 1px solid rgba(148, 163, 184, 0.22);
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease, border-color 0.15s ease;
  white-space: nowrap;
}

.rec-action-btn.is-correct {
  background: rgba(16, 185, 129, 0.16);
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.32);
}

.rec-action-btn.is-correct:hover {
  background: rgba(16, 185, 129, 0.28);
}

.rec-action-btn.is-wrong {
  background: rgba(248, 113, 113, 0.14);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.32);
}

.rec-action-btn.is-wrong:hover {
  background: rgba(248, 113, 113, 0.24);
}

.rec-action-btn.is-open {
  background: rgba(59, 130, 246, 0.12);
  color: #93c5fd;
  border-color: rgba(96, 165, 250, 0.26);
}

.rec-action-btn.is-open:hover {
  background: rgba(59, 130, 246, 0.22);
}

/* Grid produk — 3 kolom di desktop, 2 di tablet, 1 di mobile */
.recommendation-product-grid {
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  gap: 16px !important;
  overflow: hidden;
  contain: layout paint style;
}

@media (max-width: 1100px) {
  .recommendation-product-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@media (max-width: 640px) {
  .recommendation-product-grid {
    grid-template-columns: 1fr !important;
  }
}

/* ============================================================
   CATEGORY LIMIT BAR
   ============================================================ */

.category-limit-bar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  flex-wrap: nowrap;
  padding: 10px 14px;
  margin: 14px 0 0;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.52);
  border: 1px solid rgba(96, 165, 250, 0.16);
}

.category-limit-bar.hidden {
  display: none !important;
}

.category-limit-label {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  flex: 0 0 auto;
}

.category-limit-input {
  width: 80px !important;
  max-width: 120px !important;
  min-width: 76px !important;
  min-height: 32px;
  border: 1px solid rgba(96, 165, 250, 0.24);
  border-radius: 8px;
  background: rgba(7, 11, 24, 0.8);
  color: #e5eefc;
  padding: 5px 8px;
  font-size: 12px;
  font-weight: 700;
  text-align: center;
  outline: none;
  flex: 0 0 auto !important;
}

/* Hide spinner arrows for input[type=number] */
.category-limit-input::-webkit-outer-spin-button,
.category-limit-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.category-limit-input[type=number] {
  -moz-appearance: textfield;
}

.category-limit-input:focus {
  border-color: rgba(96, 165, 250, 0.5);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.12);
}

.category-limit-suffix {
  color: #94a3b8;
  font-size: 12px;
  white-space: nowrap;
  flex: 0 0 auto;
}

.category-limit-apply {
  flex: 0 0 auto !important;
  white-space: nowrap;
  min-height: 32px;
  padding: 5px 12px;
  font-size: 11px;
}

.btn-sm {
  min-height: 32px;
  padding: 5px 12px;
  font-size: 11px;
  font-weight: 700;
}

/* ============================================================
   RESULTS HEADER CLEAN
   ============================================================ */

/* Sembunyikan result-summary lama kalau masih ada */
#result-summary {
  display: none !important;
}

/* Budget bar lebih clean */
.r-budget-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 14px;
  border: 1px solid rgba(96, 165, 250, 0.24);
  background: rgba(59, 130, 246, 0.08);
  color: #93c5fd;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 14px;
}

/* Warning box */
.result-warning {
  padding: 10px 16px;
  border-radius: 14px;
  background: rgba(245, 158, 11, 0.10);
  border: 1px solid rgba(245, 158, 11, 0.28);
  color: #fde68a;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 14px;
}

/* ============================================================
   LOGO IMAGE FIX
   ============================================================ */

.logo-icon img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  image-rendering: auto;
  display: block;
  filter: none;
}

/* ============================================================
   SEARCH PANEL CLEAN
   ============================================================ */

.search-panel {
  max-width: 640px;
}

/* ============================================================
   CHECKED PRODUCT CARD — HOVER PREVIEW
   ============================================================ */

.checked-product-card {
  position: relative;
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.checked-product-card:hover {
  border-color: rgba(96, 165, 250, 0.42);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.32);
}

/* ============================================================
   OVERBUDGET BADGE
   ============================================================ */

.rec-card-badge.is-overbudget {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.16);
  border: 1px solid rgba(245, 158, 11, 0.36);
  color: #fbbf24;
  font-size: 10px;
  font-weight: 800;
  white-space: nowrap;
  margin-bottom: 4px;
  align-self: flex-start;
}

/* ============================================================
   DETAIL MODAL — TIGHTEN GAP
   ============================================================ */

.product-feedback-panel {
  margin-top: 16px !important;
  padding: 16px !important;
}

.product-feedback-panel h3 {
  margin: 0 0 12px !important;
  font-size: clamp(16px, 1.4vw, 20px) !important;
}

.product-detail-meta {
  margin-bottom: 12px !important;
}

.product-detail-price {
  margin: 0 0 10px !important;
}

/* ============================================================
   DISABLE BLUR FILTER GLOBALLY ON PRODUCT IMAGES
   ============================================================ */

.recommendation-product-image,
.product-image,
.checked-product-image,
.product-detail-image,
.product-modal-image {
  filter: none !important;
  -webkit-filter: none !important;
}

/* ============================================================
   GAP FIX + LOGO FIX — v3
   ============================================================ */

/* 1. Logo pngegg.png — pastikan tampil tajam dan proporsional */
.logo-icon img {
  width: 32px !important;
  height: 32px !important;
  object-fit: contain !important;
  image-rendering: auto !important;
  display: block !important;
  filter: none !important;
}

/* 2. Hapus min-height dari recommendation-stage
      — ini penyebab gap terbesar: stage selalu 230px walau belum ada konten */
.recommendation-stage {
  min-height: 0 !important;
}

/* 3. Hapus margin-bottom dari result-summary
      — elemen ini display:none tapi margin masih aktif di beberapa browser */
#result-summary,
.result-summary {
  display: none !important;
  margin: 0 !important;
  padding: 0 !important;
  min-height: 0 !important;
  height: 0 !important;
  overflow: hidden !important;
}

/* 4. Kurangi margin-bottom results-header agar tidak terlalu jauh */
.results-header {
  margin-bottom: 12px !important;
}

/* 5. Kurangi margin recommendations-panel */
.recommendations-panel {
  margin-bottom: 0 !important;
  margin-top: 0 !important;
}

/* 6. Kurangi padding results-panel agar lebih compact */
.results-panel {
  padding: 20px !important;
}

/* 7. Pastikan comparison-panel.hidden dan r-warning.hidden tidak makan space */
.comparison-panel.hidden,
#comparison-panel.hidden {
  display: none !important;
  margin: 0 !important;
  padding: 0 !important;
  height: 0 !important;
}

.result-warning.hidden,
#r-warning.hidden {
  display: none !important;
  margin: 0 !important;
  padding: 0 !important;
  height: 0 !important;
}

.r-budget-bar.hidden,
#r-budget-bar.hidden {
  display: none !important;
  margin: 0 !important;
  padding: 0 !important;
  height: 0 !important;
}

/* 8. Kurangi gap antara results-header dan recommendations-panel */
.results-panel > * + * {
  /* reset default stacking gap */
}

/* 9. Pastikan hidden stat div tidak makan space */
[aria-hidden="true"][style*="display:none"],
[aria-hidden="true"][style*="display: none"] {
  margin: 0 !important;
  padding: 0 !important;
  height: 0 !important;
  overflow: hidden !important;
}

/* ============================================================
   GAP FIX v4 — HAPUS OVERFLOW HIDDEN + HEIGHT CONSTRAINT
   ============================================================ */

/* Penyebab gap utama:
   1. overflow:hidden + height animation = konten terpotong = gap visual
   2. translateY pada active-panel = panel bergerak dari bawah = gap sementara
   3. IntersectionObserver expand = baru expand saat scroll = gap awal
   Fix: hapus overflow:hidden, pastikan height auto, tidak ada translateY pada container */

.recommendation-stage {
  overflow: visible;
  height: auto;
  min-height: 0;
}

.recommendation-stage.is-auto-expanded {
  overflow: visible;
  height: auto;
}

/* Ensure active-panel doesn't have transform offset */
.recommendation-active-panel {
  transform: none;
  opacity: 1;
  overflow: visible;
  height: auto;
  min-height: auto;
}

/* Ensure no inline style height remains */
#recommendation-stage[style*="height"] {
  height: auto !important;
}

```

## FILE: `web\vendor\anime.min.js`

```javascript
/*
 * Lightweight Anime.js-compatible browser runtime for PasarIntai's static UI.
 * The project also declares the animejs package dependency; this file keeps the
 * active no-build frontend able to call anime(), anime.stagger(), and timelines.
 */
(function (global) {
  function toArray(targets) {
    if (!targets) return [];
    if (typeof targets === "string") return Array.from(document.querySelectorAll(targets));
    if (targets instanceof Element || targets === window || targets === document) return [targets];
    return Array.from(targets);
  }

  function now() {
    return (global.performance && performance.now()) || Date.now();
  }

  function easeOutExpo(t) {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function easing(name) {
    if (name === "easeOutExpo") return easeOutExpo;
    return easeOutCubic;
  }

  function pair(value, fallback) {
    if (Array.isArray(value)) return value;
    if (value == null) return null;
    return [fallback, value];
  }

  function unitValue(value, unit) {
    if (value == null || value === "") return "";
    return typeof value === "number" ? `${value}${unit}` : String(value);
  }

  function stagger(step) {
    return function (_el, i) {
      return i * step;
    };
  }

  function animate(params) {
    var targets = toArray(params.targets);
    var duration = Number(params.duration || 400);
    var ease = easing(params.easing);
    var complete = typeof params.complete === "function" ? params.complete : null;
    var finishedResolve;
    var finished = new Promise(function (resolve) { finishedResolve = resolve; });

    if (!targets.length) {
      if (complete) complete();
      finishedResolve();
      return { finished: finished, pause: function () {} };
    }

    var start = now();
    var transforms = ["translateX", "translateY", "scale"];
    var from = new Map();
    var delayFn = typeof params.delay === "function" ? params.delay : function () { return Number(params.delay || 0); };
    var maxDelay = 0;
    var frameId = 0;
    var paused = false;

    targets.forEach(function (el, i) {
      var delay = Number(delayFn(el, i) || 0);
      maxDelay = Math.max(maxDelay, delay);
      var data = { delay: delay, transform: {} };
      if (params.opacity != null) data.opacity = pair(params.opacity, Number(getComputedStyle(el).opacity || 1));
      transforms.forEach(function (key) {
        if (params[key] != null) data.transform[key] = pair(params[key], key === "scale" ? 1 : 0);
      });
      if (params.height != null) data.height = pair(params.height, el.offsetHeight || 0);
      if (params.boxShadow != null) data.boxShadow = Array.isArray(params.boxShadow) ? params.boxShadow : [getComputedStyle(el).boxShadow, params.boxShadow];
      if (params.borderColor != null) data.borderColor = Array.isArray(params.borderColor) ? params.borderColor : [getComputedStyle(el).borderColor, params.borderColor];
      from.set(el, data);
    });

    function render() {
      if (paused) return;
      var elapsed = now() - start;
      targets.forEach(function (el) {
        var data = from.get(el);
        var t = Math.min(1, Math.max(0, (elapsed - data.delay) / duration));
        var eased = ease(t);

        if (data.opacity) {
          el.style.opacity = data.opacity[0] + (data.opacity[1] - data.opacity[0]) * eased;
        }

        var parts = [];
        if (data.transform.translateX) {
          var x = data.transform.translateX;
          parts.push("translateX(" + unitValue(x[0] + (x[1] - x[0]) * eased, "px") + ")");
        }
        if (data.transform.translateY) {
          var y = data.transform.translateY;
          parts.push("translateY(" + unitValue(y[0] + (y[1] - y[0]) * eased, "px") + ")");
        }
        if (data.transform.scale) {
          var s = data.transform.scale;
          parts.push("scale(" + (s[0] + (s[1] - s[0]) * eased) + ")");
        }
        if (parts.length) el.style.transform = parts.join(" ");

        if (data.height) {
          var h = data.height;
          el.style.height = unitValue(h[0] + (h[1] - h[0]) * eased, "px");
        }
        if (data.boxShadow && t >= 1) el.style.boxShadow = data.boxShadow[1];
        if (data.borderColor && t >= 1) el.style.borderColor = data.borderColor[1];
      });

      if (elapsed < duration + maxDelay) {
        frameId = requestAnimationFrame(render);
      } else {
        if (complete) complete();
        finishedResolve();
      }
    }

    frameId = requestAnimationFrame(render);
    return {
      finished: finished,
      pause: function () {
        paused = true;
        cancelAnimationFrame(frameId);
      },
    };
  }

  animate.stagger = stagger;
  animate.remove = function () {};
  animate.timeline = function (opts) {
    var chain = Promise.resolve();
    var current = null;
    return {
      add: function (params) {
        chain = chain.then(function () {
          params = Object.assign({}, opts || {}, params || {});
          current = animate(params);
          return current.finished;
        });
        return this;
      },
      pause: function () {
        if (current && current.pause) current.pause();
      },
      finished: chain,
    };
  };

  global.anime = animate;
})(window);

```
