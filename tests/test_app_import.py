from src.server.main import app


def test_fastapi_app_imports():
    assert app.title == "Tokopedia Scraper API"
