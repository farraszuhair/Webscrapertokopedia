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
