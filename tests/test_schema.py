from src.server.progress import complete_progress, get_progress, init_progress, update_progress
import src.server.routes as routes
from src.server.main import app
from src.server.routes import _public_product_payload
from src.server.schemas import SearchRequest
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
