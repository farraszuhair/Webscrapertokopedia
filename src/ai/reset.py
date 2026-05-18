"""
reset.py - Handles clearing out corrupted or old AI learning memory.
"""
import os
import shutil
from src.utils.logger import log
from src.ai.learning import MEMORY_DIR, init_memory

def reset_ai_memory():
    """Deletes all learned memory files and reinitializes fresh base files."""
    log("AI_RESET", "Initiating AI memory reset...", "WARN")
    
    if MEMORY_DIR.exists():
        try:
            shutil.rmtree(MEMORY_DIR)
            log("AI_RESET", "Old memory directory deleted.", "OK")
        except Exception as e:
            log("AI_RESET", f"Failed to delete memory dir: {e}", "ERROR")
            return False
            
    # Recreate clean base patterns
    init_memory()
    log("AI_RESET", "Memory reset to clean base state.", "OK")
    return True
