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

