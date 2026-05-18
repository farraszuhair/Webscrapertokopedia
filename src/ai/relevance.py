"""
relevance.py - Multi-layer relevance filtering.
Uses rules for obvious rejects, and Qwen for semantic decisions.
"""
import json
import re
from typing import List, Dict, Any
from src.utils.logger import log
from src.ai.qwen_client import ask_qwen
from src.ai.learning import load_patterns, get_recent_feedback

def is_broad_query(query: str) -> bool:
    """Detects if query is broad (e.g. 'laptop gaming') which needs looser filtering."""
    broad_terms = ["murah", "gaming", "editing", "terbaik", "bagus"]
    q = query.lower()
    for term in broad_terms:
        if term in q:
            return True
    return False

def layer1_rule_reject(title: str, patterns: dict) -> bool:
    """
    Hard reject obvious unrelated items based on patterns.
    Returns True if it SHOULD BE REJECTED.
    """
    title_lower = title.lower()
    rejects = patterns.get("hard_rejects", [])
    
    # If the title is literally just "mouse" or contains "tas laptop"
    for r in rejects:
        if f" {r} " in f" {title_lower} ":
            return True
    return False

async def layer3_qwen_validate(query: str, product: Dict[str, Any], patterns: dict, recent_feedback: list) -> Dict[str, Any]:
    """
    Asks Qwen to validate the product.
    """
    title = product.get("title", "")
    price = product.get("price_text", "")
    
    # Construct few-shot examples from feedback
    feedback_context = ""
    if recent_feedback:
        feedback_context = "Recent User Feedback for similar queries:\n"
        for fb in recent_feedback:
            feedback_context += f"- Product '{fb['product_title']}': User marked as {fb['feedback']} because '{fb['reason']}'.\n"

    synonyms = patterns.get("synonyms", {}).get(query.lower(), [])
    synonym_context = f"Known synonyms/brands for this query: {', '.join(synonyms)}." if synonyms else ""

    prompt = f"""
You are an expert e-commerce product validator.
User searched for: "{query}"

Product Title: "{title}"
Product Price: "{price}"

{synonym_context}
{feedback_context}

Task: Determine if this product is highly relevant to the user's search.
Rule: If the search is a broad category like 'laptop gaming', accept related brands (ROG, Legion, Nitro, etc) even if the exact words 'laptop gaming' are missing. Do not accept accessories (bags, mouse, charger) unless explicitly searched for.

Respond in strict JSON only:
{{
  "relevant": true/false,
  "confidence": 0.0 to 1.0,
  "category": "detected_category",
  "reason": "short explanation"
}}
"""
    
    ai_response = await ask_qwen(prompt)
    if ai_response and "relevant" in ai_response:
        return ai_response
        
    # Fallback if AI fails or times out
    return {
        "relevant": True, # Fail open
        "confidence": 0.5,
        "category": "unknown",
        "reason": "AI validation failed, fallback accepted"
    }

async def filter_relevance(query: str, products: List[Dict[str, Any]], use_ai: bool = True) -> List[Dict[str, Any]]:
    """
    Runs the multi-layer pipeline on a batch of products.
    """
    patterns = load_patterns()
    recent_feedback = get_recent_feedback(query)
    is_broad = is_broad_query(query)
    
    valid_products = []
    
    for p in products:
        title = p.get("title", "")
        
        # Layer 1: Rule-based hard reject
        if layer1_rule_reject(title, patterns):
            p["relevance_score"] = 0.0
            p["ai_reason"] = "Rule: Hard reject pattern matched."
            continue
            
        # Layer 2: Fast exact match (if it contains exact words, auto-pass to save time)
        query_words = set(query.lower().split())
        title_words = set(re.findall(r'\w+', title.lower()))
        
        if query_words.issubset(title_words):
            p["relevance_score"] = 1.0
            p["ai_reason"] = "Rule: Exact keyword match."
            valid_products.append(p)
            continue
            
        # Layer 3: Qwen AI
        if use_ai:
            decision = await layer3_qwen_validate(query, p, patterns, recent_feedback)
            p["relevance_score"] = decision.get("confidence", 0.5)
            p["ai_reason"] = decision.get("reason", "")
            
            threshold = 0.6 if is_broad else 0.8
            if decision.get("relevant") and p["relevance_score"] >= threshold:
                valid_products.append(p)
        else:
            # AI disabled means do not run semantic rejection. Keep anything
            # that survived hard rejects so Qwen-off mode remains usable.
            p["relevance_score"] = 0.5 if is_broad else 0.4
            p["ai_reason"] = "AI disabled: accepted after hard reject rules."
            valid_products.append(p)
                
    return valid_products
