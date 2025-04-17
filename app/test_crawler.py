import pytest
from app.crawler import DefenseCrawler

@pytest.mark.parametrize("query,expected", [
    ("What are the program executive officers related to the Golden Dome effort?", True),
    ("What is the market size of the Golden Dome effort by mission system?", True),
    ("Explain the latest developments in missile defense technologies", True),
    ("What does Palantir do for the government?", True),
    ("Where is the best ice cream in Boston?", False),
    ("Who won the NBA finals?", False),
    ("How to get a security clearance?", True),
    ("What is the role of DARPA in defense innovation?", True),
    ("Best pizza in New York?", False),
])
def test_is_defense_related(query, expected):
    crawler = DefenseCrawler(api_key="dummy")
    assert crawler._is_defense_related(query) == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("query,should_run", [
    ("What is the market size of the Golden Dome effort by mission system?", True),
    ("Where is the best ice cream in Boston?", False),
])
async def test_deep_research_guardrail(monkeypatch, query, should_run):
    crawler = DefenseCrawler(api_key="dummy")
    if not should_run:
        result = await crawler.deep_research(query)
        assert result["summary"].startswith("Sorry, I can only assist")
    else:
        # Patch the API call to avoid real HTTP requests
        async def mock_post(*args, **kwargs):
            class MockResp:
                def json(self_inner):
                    return {"success": True, "id": "abc123"}
                def raise_for_status(self_inner):
                    pass
                text = "{\"success\": true, \"id\": \"abc123\"}"
            return MockResp()
        async def mock_get(*args, **kwargs):
            class MockResp:
                def json(self_inner):
                    return {"success": True, "data": {"status": "completed", "finalAnalysis": "Test analysis.", "sources": []}}
                def raise_for_status(self_inner):
                    pass
                text = "{\"success\": true, \"data\": {\"status\": \"completed\", \"finalAnalysis\": \"Test analysis.\", \"sources\": []}}"
            return MockResp()
        import httpx
        monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
        result = await crawler.deep_research(query)
        assert "Test analysis." in result["summary"]
        assert isinstance(result["sources"], list)

# Optionally, add more tests for _extract_key_findings
@pytest.mark.parametrize("analysis,expected", [
    ("1. First point\n2. Second point", ["First point", "Second point"]),
    ("- Bullet one\n- Bullet two", ["Bullet one", "Bullet two"]),
    ("This is a sentence. Another one. And one more.", ["This is a sentence", "Another one", "And one more"]),
    ("No findings here", ["No findings here"]),
])
def test_extract_key_findings(analysis, expected):
    crawler = DefenseCrawler(api_key="dummy")
    assert crawler._extract_key_findings(analysis) == expected
