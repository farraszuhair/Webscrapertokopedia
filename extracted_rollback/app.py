from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import asyncio
import logging
import json
import os
import re
import threading
import uuid
from scraper.tokopedia_scraper import TokopediaScraper
from ai_analyzer.product_analyzer import ProductAIAnalyzer
from ai_analyzer.mistake_tracker import AIMistakeTracker, ProductAnalyzerWithLearning
from ai_analyzer.verified_products import VerifiedProductTracker
from ai_analyzer.budget_filter import BudgetFilter

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='[SERVER] %(message)s')
logger = logging.getLogger(__name__)

mistake_tracker = AIMistakeTracker()
verified_tracker = VerifiedProductTracker()
base_analyzer = ProductAIAnalyzer()
learning_analyzer = ProductAnalyzerWithLearning(base_analyzer, mistake_tracker)
budget_filter = BudgetFilter()
active_searches = {}
verified_products = set()
progress_state = {}
feedback_scores = {}
hidden_products = {}


def _parse_budget_value(raw_budget):
    if raw_budget is None:
        return None
    if isinstance(raw_budget, (int, float)):
        return int(raw_budget)
    cleaned = re.sub(r"[^\d]", "", str(raw_budget))
    return int(cleaned) if cleaned else None


def _normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", "", str(name).lower())).strip()


def _verification_key(product_name: str, product_url: str) -> str:
    normalized_name = _normalize_name(product_name)
    normalized_url = str(product_url or "").split("?")[0].strip().lower()
    return f"{normalized_name}-{normalized_url}"


def _product_key(product_name: str, store: str) -> str:
    return f"{_normalize_name(product_name)}-{_normalize_name(store)}"


def _simplify_query(query: str) -> str:
    words = [w for w in re.split(r"\s+", str(query).strip()) if w]
    if len(words) <= 2:
        return " ".join(words)
    return " ".join(words[:2])


def _pre_filter_relevance(items, query: str, cap: int = 10):
    q_words = [w for w in _normalize_name(query).split() if len(w) >= 3]
    if not q_words:
        return (items or [])[:cap]
    filtered = []
    for item in items or []:
        name = _normalize_name(item.get("nama", ""))
        if any(w in name for w in q_words):
            filtered.append(item)
        if len(filtered) >= cap:
            break
    return filtered if filtered else (items or [])[:cap]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    # Prevent repeated 404 noise from browser auto favicon request.
    return "", 204


@app.route('/api/search', methods=['POST'])
def search_api():
    req_data = request.get_json() or {}
    keyword = (req_data.get('keyword') or req_data.get('query') or '').strip()
    banned_items = req_data.get('banned_items', [])
    budget = _parse_budget_value(req_data.get('budget'))
    budget_tolerance = float(req_data.get('budget_tolerance', 10.0))
    scrape_target = int(req_data.get('scrape_target', 100))
    scrape_target = max(10, min(scrape_target, 200))
    search_id = req_data.get("search_id") or str(uuid.uuid4())
    cancel_event = threading.Event()
    active_searches[search_id] = cancel_event
    progress_state[search_id] = {"percent": 0, "stage": "starting"}

    if not keyword:
        return jsonify({"status": "error", "message": "Keyword tidak boleh kosong!"}), 400

    def generate():
        def send_status(msg, progress=None, extra=None):
            data = {"message": msg}
            if progress is not None:
                data["progress"] = progress
                progress_state[search_id]["percent"] = int(progress)
            progress_state[search_id]["stage"] = msg
            logger.info(f"[PROGRESS] {progress_state[search_id].get('percent', 0)} {progress_state[search_id].get('stage', '')}")
            if extra:
                data.update(extra)
                progress_state[search_id].update(extra)
            return f"data: {json.dumps(data)}\n\n"

        def is_cancelled():
            return cancel_event.is_set()

        yield send_status(f"🚀 MENGINISIALISASI PENCARIAN: {keyword}...", 0)
        yield f"data: {json.dumps({'status': 'meta', 'search_id': search_id})}\n\n"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            forced_model = "qwen2.5:14b"
            learning_analyzer.analyzer.force_model(forced_model)
            env_model = os.getenv("OLLAMA_MODEL")
            logger.info(f"[AI MODEL] forced={forced_model} env={env_model} active={learning_analyzer.analyzer.get_active_model()}")

            if is_cancelled():
                yield f"data: {json.dumps({'status': 'cancelled', 'message': 'Pencarian dibatalkan user.'})}\n\n"
                return

            scraper = TokopediaScraper(headless=False)
            validation_attempt = 0
            max_validation_retry = 2
            active_query = keyword
            validation_info = {"status": "normal", "reason": "", "attempts": 0}
            scraped_data = []

            while validation_attempt <= max_validation_retry:
                yield send_status(f"Scraping data... ({active_query})", 20)
                scraped_data = loop.run_until_complete(
                    scraper.search(active_query, max_halaman=3, max_items=scrape_target, should_cancel=is_cancelled)
                )
                if not scraped_data:
                    logger.info(f"[SCRAPER] retry {validation_attempt + 1}")
                    yield send_status(f"⚠️ DATA KOSONG, RETRY SCRAPING {validation_attempt + 1}/2...", 20)
                    validation_attempt += 1
                    continue

                validate_sample = _pre_filter_relevance(scraped_data, keyword, cap=8)
                validation = loop.run_until_complete(
                    learning_analyzer.analyzer.validate_search_relevance(keyword, validate_sample)
                )
                logger.info(f"[VALIDATION] {validation}")
                if validation.get("valid", True):
                    break

                if validation_attempt >= max_validation_retry:
                    validation_info = {
                        "status": "low_confidence",
                        "reason": validation.get("reason", "validator rejected results"),
                        "attempts": validation_attempt + 1,
                    }
                    break

                validation_attempt += 1
                logger.info(f"[RETRY] {validation_attempt}")
                suggested = (validation.get("suggestion") or "").strip()
                active_query = suggested or _simplify_query(active_query) or keyword
                yield send_status(
                    f"🔁 Re-search karena relevansi rendah (attempt {validation_attempt}/{max_validation_retry})",
                    20
                )

            if not scraped_data:
                yield send_status("ℹ️ DATA TIDAK DITEMUKAN", 100)
                yield f"data: {json.dumps({'status': 'empty', 'message': 'Data tidak ditemukan'})}\n\n"
                return

            yield send_status(f"📦 BERHASIL MENGAMBIL {len(scraped_data)} PRODUK...", 50, {
                "scraped_count": len(scraped_data),
                "target_count": scrape_target
            })
            if is_cancelled():
                yield f"data: {json.dumps({'status': 'cancelled', 'message': 'Scraping dibatalkan user.'})}\n\n"
                return

            if budget:
                min_price = min((int(p.get("harga", 0)) for p in scraped_data if p.get("harga")), default=0)
                max_budget = int(budget * (1 + (budget_tolerance / 100.0)))
                if min_price and min_price > max_budget:
                    yield f"data: {json.dumps({'status': 'cancelled', 'message': f'Stop otomatis: harga termurah Rp {min_price:,} di atas budget+tol ({max_budget:,}).'.replace(',', '.')})}\n\n"
                    return

            yield send_status("Analyzing with AI...", 70, {"scraped_count": len(scraped_data), "target_count": scrape_target})

            active_model = learning_analyzer.analyzer.get_active_model()
            ai_limit = min(10, scrape_target)
            ai_batch_size = 2 if ai_limit <= 8 else 3
            try:
                analyzed_data, warnings = loop.run_until_complete(
                    learning_analyzer.analyze_with_learning(
                        scraped_data,
                        batch_size=ai_batch_size,
                        limit=ai_limit,
                        banned_items=banned_items
                    )
                )
                yield send_status(
                    f"🧠 AI CROSSCHECK SELESAI: {len(analyzed_data)} data tervalidasi...",
                    90,
                    {"analyzed_count": len(analyzed_data), "scraped_count": len(scraped_data), "target_count": scrape_target}
                )
                fallback_mode = False
            except Exception as ai_error:
                logger.warning(f"[AI] fallback mode due to error: {ai_error}")
                analyzed_data = []
                warnings = [f"AI fallback aktif: {ai_error}"]
                fallback_mode = True
                yield send_status(
                    "Finalizing results... (AI fallback aktif)",
                    90,
                    {"analyzed_count": 0, "scraped_count": len(scraped_data), "target_count": scrape_target}
                )
            if is_cancelled():
                yield f"data: {json.dumps({'status': 'cancelled', 'message': 'Analisis dibatalkan user.'})}\n\n"
                return

            if fallback_mode:
                analyzed_list = []
                for raw in scraped_data[:scrape_target]:
                    harga_val = int(raw.get("harga", 0) or 0)
                    analyzed_list.append({
                        "nama_produk": str(raw.get("nama", "")),
                        "harga": harga_val,
                        "harga_display": f"Rp {harga_val:,}".replace(",", "."),
                        "nama_toko": str(raw.get("toko", "N/A")),
                        "trust_score": 58.0,
                        "trust_label": "Fallback",
                        "trust_alasan": "AI gagal, gunakan data scraping langsung",
                        "skor_value": 58.0,
                        "rekomendasi": "PERTIMBANGKAN",
                        "catatan_ai": "completed with fallback",
                        "rating_toko": float(raw.get("rating_toko", 0.0) or 0.0),
                        "terjual": str(raw.get("terjual", "0")),
                        "badge_toko": str(raw.get("badge", "Regular Merchant")),
                        "lokasi_toko": str(raw.get("lokasi", "N/A")),
                        "url_produk": str(raw.get("url", "")),
                        "url_gambar": str(raw.get("image", "")),
                        "marketplace": "tokopedia",
                    })
            else:
                analyzed_list = [
                    {
                        "nama_produk": item.nama_produk,
                        "harga": item.harga,
                        "harga_display": item.harga_display,
                        "nama_toko": item.nama_toko,
                        "trust_score": item.trust_score,
                        "trust_label": item.trust_label,
                        "trust_alasan": item.trust_alasan,
                        "skor_value": item.skor_value,
                        "rekomendasi": item.rekomendasi,
                        "catatan_ai": item.catatan_ai,
                        "rating_toko": item.rating_toko,
                        "terjual": item.terjual,
                        "badge_toko": item.badge_toko,
                        "lokasi_toko": item.lokasi_toko,
                        "url_produk": item.url_produk,
                        "url_gambar": item.url_gambar,
                        "marketplace": "tokopedia",
                    }
                    for item in analyzed_data
                ]

            if budget:
                filtered_list, budget_info = budget_filter.filter_by_budget(
                    analyzed_list, budget=budget, tolerance_percent=budget_tolerance
                )
                filtered_list = [
                    budget_filter.add_budget_info_to_product(product, budget)
                    for product in filtered_list
                ]
                final_results = filtered_list
            else:
                budget_info = None
                final_results = analyzed_list

            final_results = [
                p for p in final_results
                if _product_key(p.get("nama_produk", ""), p.get("nama_toko", "")) not in hidden_products
            ]

            yield send_status(
                "✅ SELESAI! MENYIAPKAN DATA FINAL..." if not fallback_mode else "✅ Completed with fallback",
                100
            )
            response_data = {
                "status": "success",
                "data": final_results,
                "warnings": warnings,
                "quality": validation_info,
                "meta": {
                    "target_count": scrape_target,
                    "scraped_count": len(scraped_data),
                    "analyzed_count": len(analyzed_data),
                    "final_count": len(final_results),
                },
            }
            if budget_info:
                response_data["budget_info"] = budget_info
            yield f"data: {json.dumps(response_data)}\n\n"

        except Exception as e:
            logger.error(f"Error dalam stream: {e}", exc_info=True)
            yield send_status(f"❌ ERROR SERVER: {str(e)}", 0)
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        finally:
            loop.close()
            active_searches.pop(search_id, None)
            progress_state.pop(search_id, None)

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/api/search/cancel', methods=['POST'])
def cancel_search_api():
    req_data = request.get_json() or {}
    search_id = req_data.get("search_id")
    if not search_id:
        return jsonify({"status": "error", "message": "search_id wajib diisi"}), 400
    event = active_searches.get(search_id)
    if not event:
        return jsonify({"status": "error", "message": "search_id tidak ditemukan / sudah selesai"}), 404
    event.set()
    return jsonify({"status": "success", "message": "Proses scraping dibatalkan"}), 200


@app.route('/api/progress', methods=['GET'])
def get_progress():
    search_id = request.args.get("search_id", "")
    if not search_id:
        return jsonify({"status": "error", "message": "search_id wajib"}), 400
    return jsonify(progress_state.get(search_id, {"percent": 0, "stage": "idle"})), 200


@app.route('/api/feedback/mistake', methods=['POST'])
def report_ai_mistake():
    try:
        req_data = request.get_json()
        mistake_tracker.record_mistake(
            product_name=req_data.get('product_name', ''),
            product_url=req_data.get('product_url', ''),
            ai_analysis=req_data.get('ai_analysis', {}),
            user_feedback=req_data.get('feedback', ''),
            correction=req_data.get('correction', {})
        )
        return jsonify({"status": "success", "message": "Kesalahan AI tercatat!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/feedback/action', methods=['POST'])
def feedback_action():
    try:
        req_data = request.get_json() or {}
        product_name = _normalize_name(req_data.get("product_name", ""))
        store = _normalize_name(req_data.get("store", ""))
        action = req_data.get("action", "")
        key = f"{product_name}-{store}"
        score = feedback_scores.get(key, 0.0)
        if action == "keep":
            score += 1.0
            hidden_products.pop(key, None)
        elif action == "delete":
            score -= 0.5
            hidden_products[key] = True
        elif action == "undo_delete":
            score += 0.5
            hidden_products.pop(key, None)
        feedback_scores[key] = max(-3.0, min(3.0, score))
        return jsonify({"status": "success", "score": feedback_scores[key]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/delete', methods=['POST'])
def delete_product():
    try:
        req_data = request.get_json() or {}
        product_name = req_data.get("product_name", "")
        store = req_data.get("store", "")
        key = _product_key(product_name, store)
        hidden_products[key] = True
        return jsonify({"status": "success", "message": "Produk disembunyikan", "key": key}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/delete/undo', methods=['POST'])
def undo_delete_product():
    try:
        req_data = request.get_json() or {}
        product_name = req_data.get("product_name", "")
        store = req_data.get("store", "")
        key = _product_key(product_name, store)
        hidden_products.pop(key, None)
        return jsonify({"status": "success", "message": "Produk ditampilkan kembali", "key": key}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/verify/product', methods=['POST'])
def verify_product():
    try:
        req_data = request.get_json()
        product_name = req_data.get('product_name', '')
        product_url = req_data.get('product_url', '')
        key = _verification_key(product_name, product_url)
        if key in verified_products:
            logger.info("[DUPLICATE] Skipped")
            return jsonify({
                "status": "duplicate",
                "message": "Produk sudah ada",
                "product": {"product_name": product_name, "product_url": product_url}
            }), 200

        verified_products.add(key)
        verified_tracker.record_verification(
            product_name=product_name,
            product_url=product_url,
            ai_analysis=req_data.get('ai_analysis', {}),
            user_note=req_data.get('user_note', '')
        )
        logger.info("[NEW] Product saved")
        return jsonify({
            "status": "new",
            "message": "Produk baru disimpan",
            "product": {"product_name": product_name, "product_url": product_url}
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)