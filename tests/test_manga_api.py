from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from fastapi_pagination import Page

from main import app
from config.db import get_db

client = TestClient(app)

@pytest.fixture
def override_get_db():
    """Overrides the database dependency to return a mock DB session."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides.clear()


@patch("routes.manga.sqlalchemy_paginate")
@patch("routes.manga.get_manga_listing", new_callable=AsyncMock)
def test_manga_list_endpoint(mock_get_manga_listing, mock_sqlalchemy_paginate, override_get_db):
    """Test the paginated manga listing endpoint with optional filters and sorting."""
    mock_get_manga_listing.return_value = MagicMock()
    
    # Mock fastapi-pagination's sqlalchemy_paginate return value
    mock_sqlalchemy_paginate.return_value = Page(
        items=[
            {
                "mal_id": 1,
                "title": "Berserk",
                "genres": "Action, Fantasy",
                "chapters": 365,
                "volumes": 41,
                "score": 9.47
            }
        ],
        total=1,
        page=1,
        size=20,
        pages=1
    )

    response = client.get("/api/manga/?page=1&size=20&genre=Fantasy&sort_by=popularity")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Berserk"
    mock_get_manga_listing.assert_awaited_once()


@patch("routes.manga.search_manga_by_vibe", new_callable=AsyncMock)
def test_manga_vibe_search_endpoint(mock_search_manga_by_vibe, override_get_db):
    """Test the natural language manga vibe-search endpoint."""
    mock_search_manga_by_vibe.return_value = [
        {"mal_id": 2, "title": "Vagabond", "similarity_score": 0.91}
    ]

    response = client.get("/api/manga/vibe-search?q=philosophical%20samurai%20journey&limit=5")

    assert response.status_code == 200
    json_data = response.json()
    assert "results" in json_data
    assert len(json_data["results"]) == 1
    assert json_data["results"][0]["title"] == "Vagabond"
    mock_search_manga_by_vibe.assert_awaited_once_with("philosophical samurai journey", top_k=5)


@patch("routes.manga.get_manga_by_id", new_callable=AsyncMock)
def test_get_manga_detail_endpoint(mock_get_manga_by_id, override_get_db):
    """Test fetching details for a specific manga by mal_id along with similar manga."""
    mock_get_manga_by_id.return_value = {
        "mal_id": 1,
        "title": "Berserk",
        "chapters": 365,
        "score": 9.47,
        "similar_manga": [
            {
                "rank": 1,
                "similarity_score": 0.88,
                "mal_id": 13,
                "title": "Vinland Saga"
            }
        ]
    }

    response = client.get("/api/manga/1")

    assert response.status_code == 200
    data = response.json()
    assert data["mal_id"] == 1
    assert data["title"] == "Berserk"
    assert len(data["similar_manga"]) == 1
    assert data["similar_manga"][0]["title"] == "Vinland Saga"
    mock_get_manga_by_id.assert_awaited_once()