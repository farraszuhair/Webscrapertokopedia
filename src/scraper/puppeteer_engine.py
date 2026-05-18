import asyncio
import json
import sys
from typing import Tuple, List, Dict, Any
from pathlib import Path
from src.utils.logger import log
from src.server.progress import update_progress

class PuppeteerEngine:
    name = "puppeteer"
    
    def __init__(self, search_id: str):
        self.search_id = search_id

    async def scrape(self, query: str, raw_target: int, eta_calc) -> Tuple[bool, List[Dict[str, Any]], str]:
        worker_path = Path(__file__).parent / "puppeteer_worker.js"
        
        # Initialize variables before loop to prevent UnboundLocalError
        success = False
        products = []
        last_error = "Unknown Error"
        
        for attempt in range(1, 3):
            log(f"[{self.search_id}]", f"[PUPPETEER] Opening Tokopedia attempt {attempt}/2", "INFO")
            
            # Reset state per attempt
            success = False
            products = []
            process = None
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "node", str(worker_path),
                    "--query", query,
                    "--target", str(raw_target),
                    "--search-id", self.search_id,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                while True:
                    # Timeout the readline to prevent hangs
                    try:
                        line = await asyncio.wait_for(process.stdout.readline(), timeout=30.0)
                    except asyncio.TimeoutError:
                        last_error = "Node process timeout while reading stdout"
                        log(f"[{self.search_id}]", f"[PUPPETEER] {last_error}", "WARN")
                        break

                    if not line:
                        break
                        
                    line_str = line.decode('utf-8').strip()
                    if not line_str:
                        continue
                        
                    try:
                        data = json.loads(line_str)
                        msg_type = data.get("type")
                        
                        if msg_type == "progress":
                            stage = data.get("stage", "running")
                            update_progress(
                                self.search_id,
                                engine=self.name,
                                stage=stage,
                                attempt=attempt,
                                max_attempts=2,
                                percent=data.get("percent", 0),
                                message=data.get("message", ""),
                                elapsed_seconds=eta_calc.get_elapsed()
                            )
                        elif msg_type == "done":
                            products = data.get("products", [])
                            success = True
                            break
                        elif msg_type == "error":
                            last_error = data.get("error", "Unknown puppeteer error")
                            break
                    except json.JSONDecodeError:
                        log(f"[{self.search_id}]", f"[PUPPETEER] Invalid JSON from Node: {line_str[:100]}", "WARN")
                
                # Check exit code and stderr safely
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    if process.returncode is None:
                        process.terminate()
                        last_error = "Puppeteer process did not exit cleanly, terminated."
                        
                if process.returncode is not None and process.returncode != 0:
                    stderr_output = ""
                    if process.stderr:
                        stderr_bytes = await process.stderr.read()
                        stderr_output = stderr_bytes.decode('utf-8').strip()
                    last_error = f"Node exited with {process.returncode}. Stderr: {stderr_output}"
                    success = False
                    
            except asyncio.CancelledError:
                log(f"[{self.search_id}]", "[PUPPETEER] Task cancelled, killing subprocess...", "WARN")
                if process and process.returncode is None:
                    try:
                        process.kill()
                    except Exception:
                        pass
                raise
            except Exception as e:
                last_error = f"Puppeteer Python exception: {str(e)}"
                success = False
                
            if success and products:
                return True, products, ""
                
            log(f"[{self.search_id}]", f"[PUPPETEER] Attempt {attempt} failed: {last_error}", "WARN")
            
        return False, [], f"Puppeteer failed after 2 attempts: {last_error}"
