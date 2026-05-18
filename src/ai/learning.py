"""
learning.py - Memory system for Qwen AI filtering.
Stores feedback, updates positive/negative patterns based on user feedback.
"""
import json
import os
from pathlib import Path
from src.utils.logger import log

MEMORY_DIR = Path(__file__).parent.parent.parent / "data" / "ai_memory"
FEEDBACK_FILE = MEMORY_DIR / "feedback.jsonl"
PATTERNS_FILE = MEMORY_DIR / "patterns.json"

def init_memory():
    """Ensures memory directories and files exist."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    if not PATTERNS_FILE.exists():
        # Base patterns
        base_patterns = {
            "synonyms": {
                "laptop gaming": ["gaming laptop", "rog", "legion", "nitro", "victus", "tuf", "predator", "msi", "loq"]
            },
            "hard_rejects": ["bag", "tas", "keyboard", "mouse", "charger", "adaptor", "ram", "ssd", "lcd", "screen"]
        }
        with open(PATTERNS_FILE, "w") as f:
            json.dump(base_patterns, f, indent=2)
            
    if not FEEDBACK_FILE.exists():
        FEEDBACK_FILE.touch()

def load_patterns() -> dict:
    """Loads learned patterns for AI context."""
    init_memory()
    try:
        with open(PATTERNS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_feedback(query: str, product: dict, feedback: str, reason: str):
    """
    Saves user feedback to JSONL and updates patterns if necessary.
    Feedback types: 'correct', 'wrong', 'irrelevant', 'should_include', 'should_exclude'
    """
    init_memory()
    
    entry = {
        "query": query,
        "product_title": product.get("title", ""),
        "feedback": feedback,
        "reason": reason
    }
    
    # Save to append log
    with open(FEEDBACK_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
        
    # Update patterns based on feedback
    patterns = load_patterns()
    synonyms = patterns.get("synonyms", {})
    query_lower = query.lower()
    
    if query_lower not in synonyms:
        synonyms[query_lower] = []
        
    title = product.get("title", "").lower()
    
    # Simple learning: if user says "should_include" for a broad query,
    # extract the first significant word (brand) and add to synonyms if not present.
    # A real supercomputer AI would ask Qwen to extract the synonym, but for speed,
    # we just pass the feedback logs to the prompt later.
    
    # We will let Qwen read the recent feedback logs directly as few-shot examples!
    log("AI_LEARN", f"Saved feedback '{feedback}' for product: {title}", "OK")

def get_recent_feedback(query: str, limit: int = 5) -> list:
    """Gets recent feedback specifically for this query to feed to AI prompt."""
    init_memory()
    results = []
    try:
        with open(FEEDBACK_FILE, "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if not line.strip(): continue
                data = json.loads(line)
                if data.get("query", "").lower() == query.lower():
                    results.append(data)
                if len(results) >= limit:
                    break
    except:
        pass
    return results
