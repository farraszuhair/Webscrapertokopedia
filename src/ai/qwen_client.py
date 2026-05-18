"""
qwen_client.py - Handles communication with local Ollama Qwen 2.5:14B.
"""
import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional
from src.utils.logger import log

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:14b"

async def ask_qwen(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Sends prompt to Qwen and expects a JSON response.
    Returns parsed JSON dict or None if failure.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json" # Force strict JSON output
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response", "")
                    
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        log("AI", f"Qwen returned invalid JSON: {response_text}", "WARN")
                        return None
                else:
                    log("AI", f"Ollama HTTP error: {response.status}", "WARN")
                    return None
    except asyncio.TimeoutError:
        log("AI", "Qwen timeout.", "WARN")
        return None
    except Exception as e:
        log("AI", f"Qwen connection error: {e}", "WARN")
        return None
