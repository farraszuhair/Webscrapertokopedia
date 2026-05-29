from src.server.progress import complete_progress, get_progress, init_progress, update_progress
import src.server.routes as routes
from src.server.main import app
from src.server.routes import _public_product_payload
from src.server.schemas import FeedbackRequest, SearchRequest
from fastapi.testclient import TestClient


def test_search_request_accepts_requested_api_shape():
    req = SearchRequest.model_validate(
        {
            "query": "laptop gaming",
            "target": 25,
            "budget": "10.000.000",
            "tolerance": 20,
            "ai": False,
            "engine_mode": "puppeteer",
        }
    )

    assert req.target_count == 25
    assert req.budget == "10.000.000"
    assert req.use_ai is False
    assert req.engine_mode == "puppeteer"


def test_progress_response_includes_demo_aliases():
    search_id = "schema-progress-demo"
    init_progress(search_id, target=25, raw_target=100, engine_mode="auto")
    update_progress(search_id, stage="opening_page", message="Opening marketplace", found=7, percent=22)

    progress = get_progress(search_id)

    assert progress["searchId"] == search_id
    assert progress["stage"] == "scraping"
    assert progress["statusText"] == "Opening marketplace"
    assert progress["percentage"] == 22
    assert progress["foundCount"] == 7
    assert progress["targetCount"] == 25
    assert isinstance(progress["elapsedSeconds"], float)
    assert "etaSeconds" in progress
    assert progress["logs"]

    complete_progress(search_id)
    assert get_progress(search_id)["stage"] == "completed"


def test_public_product_payload_has_required_demo_shape():
    product = _public_product_payload({
        "id": "p1",
        "title": "Laptop Gaming RTX 5060",
        "price_value": 12_500_000,
        "image_url": "https://images.test/p1.jpg",
        "shop_name": "Toko Demo",
        "rating": 4.8,
        "sold_count": 120,
        "url": "https://tokopedia.test/p1",
        "source_engine": "puppeteer",
        "relevance_score": 0.87,
        "ai_reason": "Cocok dengan query",
    })

    assert product["id"] == "p1"
    assert product["title"] == "Laptop Gaming RTX 5060"
    assert product["price"] == "Rp12.500.000"
    assert product["priceNumber"] == 12_500_000
    assert product["image"] == "https://images.test/p1.jpg"
    assert product["image_url"] == "https://images.test/p1.jpg"
    assert product["has_image"] is True
    assert product["storeName"] == "Toko Demo"
    assert product["rating"] == 4.8
    assert product["soldCount"] == 120
    assert product["url"] == "https://tokopedia.test/p1"
    assert product["source"] == "puppeteer"
    assert product["confidenceScore"] == 0.87
    assert product["relevanceReason"] == "Cocok dengan query"


def test_public_product_payload_normalizes_image_aliases():
    product = _public_product_payload({
        "id": "p2",
        "title": "Laptop Gaming",
        "price_value": 10_000_000,
        "images": ["//images.test/p2.webp"],
        "url": "https://tokopedia.test/p2",
    })

    assert product["image_url"] == "https://images.test/p2.webp"
    assert product["image"] == "https://images.test/p2.webp"
    assert product["has_image"] is True


def test_image_proxy_returns_image_bytes(monkeypatch):
    class FakeResponse:
        status_code = 200
        headers = {"content-type": "image/webp"}
        content = b"image-bytes"

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, url, headers):
            assert url == "https://images.test/p2.webp"
            assert headers["Referer"] == "https://www.tokopedia.com/"
            return FakeResponse()

    monkeypatch.setattr(routes.httpx, "AsyncClient", FakeAsyncClient)

    response = TestClient(app).get("/api/image-proxy", params={"url": "//images.test/p2.webp"})

    assert response.status_code == 200
    assert response.content == b"image-bytes"
    assert response.headers["content-type"].startswith("image/webp")


def test_result_store_adds_timestamp_and_expires(monkeypatch):
    routes._results_store.clear()
    monkeypatch.setattr(routes, "RESULT_STORE_TTL_SECONDS", 10)
    monkeypatch.setattr(routes, "RESULT_STORE_MAX_ITEMS", 10)
    monkeypatch.setattr(routes.time, "time", lambda: 1000.0)

    saved = routes.save_result("search-1", {"success": True, "data": []})

    assert saved["search_id"] == "search-1"
    assert saved["created_at"].endswith("Z")
    assert routes.get_result("search-1")["success"] is True

    monkeypatch.setattr(routes.time, "time", lambda: 1011.0)
    assert routes.get_result("search-1") is None


def test_result_store_enforces_max_items(monkeypatch):
    routes._results_store.clear()
    monkeypatch.setattr(routes, "RESULT_STORE_TTL_SECONDS", 100)
    monkeypatch.setattr(routes, "RESULT_STORE_MAX_ITEMS", 2)

    now = {"value": 1000.0}
    monkeypatch.setattr(routes.time, "time", lambda: now["value"])

    routes.save_result("old", {"success": True})
    now["value"] += 1
    routes.save_result("middle", {"success": True})
    now["value"] += 1
    routes.save_result("new", {"success": True})

    assert routes.get_result("old") is None
    assert routes.get_result("middle") is not None
    assert routes.get_result("new") is not None
    routes._results_store.clear()


def test_feedback_request_normalizes_old_and_new_names():
    old_shape = FeedbackRequest.model_validate(
        {
            "query": "laptop gaming",
            "product_id": "p1",
            "product_title": "Laptop",
            "user_action": "salah",
            "selected_reasons": ["bukan laptop"],
            "custom_reason": "aksesori",
        }
    )
    new_shape = FeedbackRequest.model_validate(
        {
            "query": "laptop gaming",
            "product": {"id": "p2", "title": "Laptop 2"},
            "feedback_type": "positive",
            "reasons": "cocok",
            "note": "valid",
        }
    )

    assert old_shape.normalized_reasons() == ["bukan laptop"]
    assert old_shape.normalized_note() == "aksesori"
    assert old_shape.normalized_feedback_type() == "negative"
    assert old_shape.normalized_corrected_label() == "tidak_relevan"

    assert new_shape.normalized_product_id() == "p2"
    assert new_shape.normalized_product_title() == "Laptop 2"
    assert new_shape.normalized_reasons() == ["cocok"]
    assert new_shape.normalized_note() == "valid"
    assert new_shape.normalized_user_action() == "benar"
