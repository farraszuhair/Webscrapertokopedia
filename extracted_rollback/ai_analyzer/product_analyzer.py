import json
import re
import os
import logging
import asyncio
import requests
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


def extract_json(text):
    import re
    import json

    try:
        cleaned_text = str(text or "").strip()
        match = re.search(r"\[.*\]", cleaned_text, re.DOTALL)
        if not match:
            match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if not match:
            return None

        cleaned = match.group()
        cleaned = re.sub(r",\s*}", "}", cleaned)
        cleaned = re.sub(r",\s*]", "]", cleaned)
        return json.loads(cleaned)
    except Exception:
        return None


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def tags(self) -> requests.Response:
        return requests.get(f"{self.base_url}/api/tags", timeout=10)

    def chat(self, payload: Dict[str, Any]) -> Optional[str]:
        logger.info(f"[DEBUG] Using timeout: {self.timeout}")
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()
        full_response = ""
        for raw_line in response.iter_lines():
            if not raw_line:
                continue
            full_response += raw_line.decode("utf-8", errors="ignore") + "\n"

        chunks: List[str] = []
        for line in full_response.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload_line = json.loads(line)
            except Exception:
                continue
            message = payload_line.get("message") or {}
            content = message.get("content")
            if content:
                chunks.append(content)
            if payload_line.get("done") is True:
                break

        return "".join(chunks) if chunks else None

@dataclass
class AnalysisResult:
    nama_produk: str
    harga: int
    harga_display: str
    nama_toko: str
    trust_score: float
    trust_label: str
    trust_alasan: str
    skor_value: float
    rekomendasi: str
    catatan_ai: str
    rating_toko: float
    terjual: str
    badge_toko: str
    lokasi_toko: str
    url_produk: str
    url_gambar: str

class ProductAIAnalyzer:
    OLLAMA_URL = "http://localhost:11434"
    DEFAULT_MODEL = "qwen2.5:14b"

    def __init__(self, model: Optional[str] = None, ollama_url: Optional[str] = None):
        self.model = model or os.getenv("OLLAMA_MODEL", self.DEFAULT_MODEL)
        self.ollama_url = (ollama_url or os.getenv("OLLAMA_URL", self.OLLAMA_URL)).replace("/api/generate", "").replace("/api/chat", "")
        self._ollama_available: Optional[bool] = None
        self.client = OllamaClient(base_url=self.ollama_url, timeout=120)

    def force_model(self, model_name: str) -> None:
        self.model = model_name

    def get_active_model(self) -> str:
        return self.model

    async def _check_ollama_health(self) -> bool:
        if self._ollama_available is not None:
            return self._ollama_available
        try:
            r = await asyncio.to_thread(self.client.tags)
            self._ollama_available = (r.status_code == 200)
        except Exception:
            self._ollama_available = False
        return self._ollama_available

    def _build_analysis_prompt(self, products_batch: List[dict], banned_items: List[str]) -> str:
        simplified_batch = []
        for i, p in enumerate(products_batch):
            simplified_batch.append({
                "index": i,
                "nama": str(p.get("nama", ""))[:100], 
                "harga": p.get("harga", 0),
                "toko": str(p.get("toko", ""))[:50],
                "rating": p.get("rating_toko", 0.0),
                "terjual": p.get("terjual", "0")
            })

        products_json = json.dumps(simplified_batch, ensure_ascii=False)
        
        banned_text = ""
        if banned_items:
            banned_list = ", ".join(banned_items[-5:]) 
            banned_text = (
                "User preference: Avoid previously hidden items, but do not fully exclude them. "
                "Influence preference max 30%.\n"
                f"Contoh item tersembunyi sebelumnya: {banned_list}."
            )

        return f"""Tugas Anda adalah sebagai AI Analis E-commerce. Evaluasi data JSON berikut.
{banned_text}
DATA PRODUK:
{products_json}

ATURAN SKORING:
1. trust_score (0-100): Jika Rating > 4.7 dan Terjual > 50, maka 80-100.
2. skor_value (0-100): Jika Harga masuk akal (termurah) dan asli, maka 90+.

Return ONLY valid JSON.
No explanation.
No markdown.
No extra text.
OUTPUT WAJIB JSON MURNI (Array of Objects). Tanpa markdown, tanpa penjelasan di luar JSON.
FORMAT:
[
  {{"index": 0, "trust_score": 90.0, "trust_label": "Terpercaya", "trust_alasan": "Toko memiliki rating tinggi", "skor_value": 85.0, "rekomendasi": "DIREKOMENDASIKAN", "catatan_ai": "Sangat layak beli."}}
]"""

    async def _call_ollama(self, prompt: str, retries: int = 2) -> Optional[str]:
        cpu_threads = max(2, min(6, (os.cpu_count() or 4) // 2))
        model_chain = [self.model]
        if self.model != "qwen2.5:7b":
            model_chain.append("qwen2.5:7b")
        
        for model_name in model_chain:
            payload = {
                "model": model_name,
                "stream": True,
                "messages": [{"role": "user", "content": prompt}],
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_ctx": 1536,
                    "num_predict": 180,
                    "num_thread": cpu_threads
                }
            }
            for attempt in range(1, retries + 1):
                try:
                    result = await asyncio.to_thread(self.client.chat, payload)
                    if result:
                        self._ollama_available = True
                        return result
                except requests.RequestException as e:
                    logger.warning(f"[WARN] Ollama request error model={model_name} attempt={attempt}/{retries}: {e}")
                except Exception as e:
                    logger.warning(f"[WARN] Ollama unknown error model={model_name} attempt={attempt}/{retries}: {e}")
                await asyncio.sleep(1)
            logger.warning(f"[WARN] Model fallback triggered: {model_name} failed.")
        self._ollama_available = False
        return None

    def _parse_ai_response(self, response_text: str) -> List[dict]:
        if not response_text:
            return []
        cleaned = re.sub(r"```json|```", "", response_text.strip())
        logger.info(f"[AI RAW] {cleaned[:200]}")
        parsed = extract_json(cleaned)
        logger.info(f"[AI PARSED] {parsed if parsed is not None else 'None'}")
        if parsed is None:
            logger.error("Gagal parse JSON dari AI")
            return []
        if isinstance(parsed, dict):
            return [parsed]
        if isinstance(parsed, list):
            return parsed
        logger.error("Gagal parse JSON dari AI: format bukan dict/list")
        return []

    async def validate_search_relevance(self, query: str, products: List[dict]) -> Dict[str, Any]:
        sample = []
        for p in (products or [])[:8]:
            sample.append(
                {
                    "nama": str(p.get("nama", ""))[:120],
                    "toko": str(p.get("toko", ""))[:60],
                    "harga": int(p.get("harga", 0) or 0),
                }
            )

        prompt = (
            "Evaluate whether the products match the user query.\n\n"
            "Return ONLY JSON:\n"
            "{\n"
            '  "valid": boolean,\n'
            '  "reason": string,\n'
            '  "suggestion": string\n'
            "}\n\n"
            "No explanation. No markdown.\n\n"
            f"query: {query}\n"
            f"products: {json.dumps(sample, ensure_ascii=False)}"
        )
        raw = await self._call_ollama(prompt, retries=1)
        if not raw:
            return {"valid": True, "reason": "validator unavailable", "suggestion": ""}
        parsed = extract_json(raw)
        logger.info(f"[VALIDATION] {parsed}")
        if not isinstance(parsed, dict):
            return {"valid": True, "reason": "invalid validator JSON", "suggestion": ""}
        return {
            "valid": bool(parsed.get("valid", True)),
            "reason": str(parsed.get("reason", "")),
            "suggestion": str(parsed.get("suggestion", "")).strip(),
        }

    async def analyze(self, products_dict: List[dict], batch_size: int = 10, limit: int = 10, banned_items: List[str] = None) -> List[AnalysisResult]:
        results = []
        is_healthy = await self._check_ollama_health()
        
        if not is_healthy:
            logger.warning("Ollama tidak sehat/tersedia. Gunakan fallback lokal tanpa memanggil model.")
            fallback_source = products_dict[:limit]
            for p in fallback_source:
                harga_val = p.get('harga', 0)
                harga_formatted = f"Rp {harga_val:,}".replace(",", ".")
                fallback_score = 70.0 if float(p.get("rating_toko", 0.0)) >= 4.5 else 55.0
                results.append(
                    AnalysisResult(
                        nama_produk=str(p.get("nama", "")),
                        harga=int(harga_val),
                        harga_display=str(harga_formatted),
                        nama_toko=str(p.get("toko", "N/A")),
                        trust_score=fallback_score,
                        trust_label="Perlu Verifikasi",
                        trust_alasan="Fallback lokal dipakai karena Ollama tidak aktif",
                        skor_value=fallback_score,
                        rekomendasi="PERTIMBANGKAN",
                        catatan_ai="Mode fallback lokal aktif.",
                        rating_toko=float(p.get("rating_toko", 0.0)),
                        terjual=str(p.get("terjual", "0")),
                        badge_toko=str(p.get("badge", "Regular Merchant")),
                        lokasi_toko=str(p.get("lokasi", "N/A")),
                        url_produk=str(p.get("url", "")),
                        url_gambar=str(p.get("image", ""))
                    )
                )
            return results

        try:
            valid_products = [p for p in products_dict if float(p.get("rating_toko", 0.0)) >= 4.5]
            if len(valid_products) < limit:
                valid_products = products_dict
                
            sorted_products = sorted(valid_products, key=lambda x: float(x.get("harga", 0.0) or float('inf')))
        except Exception as e:
            logger.warning(f"Sorting gagal, fallback: {e}")
            sorted_products = products_dict

        # BATASI JUMLAH PRODUK YANG MASUK AI (Max 10-20 saja biar ringan)
        limited_products = sorted_products[:limit]
        logger.info(f"Memproses {len(limited_products)} produk terbaik ke Ollama...")

        # LOOPING BATCH (Dibagi per batch_size misal 10)
        for i in range(0, len(limited_products), batch_size):
            batch = limited_products[i:i + batch_size]
            prompt = self._build_analysis_prompt(batch, banned_items)
            
            logger.info(f"Mengirim batch produk ke Ollama... Mohon tunggu.")
            raw_response = None if self._ollama_available is False else await self._call_ollama(prompt)
            
            ai_data_list = self._parse_ai_response(raw_response) if raw_response else []
            handled_indices = set()
            
            for ai_item in ai_data_list:
                idx = ai_item.get("index")
                if idx is not None and 0 <= idx < len(batch):
                    handled_indices.add(idx)
                    p = batch[idx]
                    harga_val = p.get('harga', 0)
                    harga_formatted = f"Rp {harga_val:,}".replace(",", ".")
                    
                    res = AnalysisResult(
                        nama_produk=str(p.get("nama", "")),
                        harga=int(harga_val),
                        harga_display=str(harga_formatted),
                        nama_toko=str(p.get("toko", "N/A")),
                        trust_score=float(ai_item.get("trust_score", 0)),
                        trust_label=str(ai_item.get("trust_label", "N/A")),
                        trust_alasan=str(ai_item.get("trust_alasan", "")),
                        skor_value=float(ai_item.get("skor_value", 0)),
                        rekomendasi=str(ai_item.get("rekomendasi", "TIDAK DIREKOMENDASIKAN")),
                        catatan_ai=str(ai_item.get("catatan_ai", "")),
                        rating_toko=float(p.get("rating_toko", 0.0)),
                        terjual=str(p.get("terjual", "0")),
                        badge_toko=str(p.get("badge", "Regular Merchant")),
                        lokasi_toko=str(p.get("lokasi", "N/A")),
                        url_produk=str(p.get("url", "")),
                        url_gambar=str(p.get("image", ""))
                    )
                    results.append(res)

            # Fallback: jika AI output parsial/error, produk tetap ditampilkan.
            for idx, p in enumerate(batch):
                if idx in handled_indices:
                    continue
                harga_val = p.get('harga', 0)
                harga_formatted = f"Rp {harga_val:,}".replace(",", ".")
                fallback_score = 70.0 if float(p.get("rating_toko", 0.0)) >= 4.5 else 55.0
                results.append(
                    AnalysisResult(
                        nama_produk=str(p.get("nama", "")),
                        harga=int(harga_val),
                        harga_display=str(harga_formatted),
                        nama_toko=str(p.get("toko", "N/A")),
                        trust_score=fallback_score,
                        trust_label="Perlu Verifikasi",
                        trust_alasan="Fallback lokal dipakai karena AI error/timeout",
                        skor_value=fallback_score,
                        rekomendasi="PERTIMBANGKAN",
                        catatan_ai="AI sedang padat, produk tetap ditampilkan agar kamu tetap bisa bandingkan opsi terbaik.",
                        rating_toko=float(p.get("rating_toko", 0.0)),
                        terjual=str(p.get("terjual", "0")),
                        badge_toko=str(p.get("badge", "Regular Merchant")),
                        lokasi_toko=str(p.get("lokasi", "N/A")),
                        url_produk=str(p.get("url", "")),
                        url_gambar=str(p.get("image", ""))
                    )
                )
        return results