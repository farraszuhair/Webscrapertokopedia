from src.server.schemas import SearchRequest


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
