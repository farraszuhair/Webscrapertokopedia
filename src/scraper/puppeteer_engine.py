import asyncio
import json
import sys
from typing import Tuple, List, Dict, Any
from pathlib import Path
from src.utils.logger import log
from src.server.progress import update_progress
from src.server.lifecycle import get_scrape_task

class PuppeteerEngine:
    name = "puppeteer"
    
    def __init__(self, search_id: str):
        self.search_id = search_id

    async def scrape(self, query: str, raw_target: int, eta_calc) -> Tuple[bool, List[Dict[str, Any]], str]:
        worker_path = Path(__file__).parent / "puppeteer_worker.js"
        
        for attempt in range(1, 3):
            log(f"[{self.search_id}]", f"[PUPPETEER] Opening Tokopedia attempt {attempt}/2", "INFO")
            
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
                    line = await process.stdout.readline()
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
                        pass
                
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.terminate()
                    
            except asyncio.CancelledError:
                log(f"[{self.search_id}]", "[PUPPETEER] Task cancelled, killing subprocess...", "WARN")
                if process and process.returncode is None:
                    try:
                        process.terminate()
                    except:
                        pass
                raise
            except Exception as e:
                last_error = str(e)
                
            if success and products:
                return True, products, ""
                
            log(f"[{self.search_id}]", f"[PUPPETEER] Attempt {attempt} failed: {last_error}", "WARN")
            
        return False, [], last_error
