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


def test_health_check(override_get_db):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI Anime Recommendation API is healthy"}


@patch("routes.anime.sqlalchemy_paginate")
@patch("routes.anime.get_anime_listing", new_callable=AsyncMock)
def test_anime_list_endpoint(mock_get_listing, mock_sqlalchemy_paginate, override_get_db):
    """Test the paginated anime listing endpoint by mocking sqlalchemy_paginate."""
    mock_get_listing.return_value = MagicMock()
    
    # Mock fastapi-pagination's sqlalchemy_paginate return value directly 
    # to bypass live database execution queries during testing
    mock_sqlalchemy_paginate.return_value = Page(
        items=[
            {
                "mal_id": 1,
                "title": "Naruto",
                "genres": "Action",
                "episodes": 220
            }
        ],
        total=1,
        page=1,
        size=20,
        pages=1
    )

    response = client.get("/api/anime/?page=1&size=20&genre=Action")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Naruto"
    mock_get_listing.assert_awaited_once()


@patch("routes.anime.search_anime_by_vibe", new_callable=AsyncMock)
def test_vibe_search_endpoint(mock_vibe_search, override_get_db):
    """Test the natural language vibe-search endpoint."""
    mock_vibe_search.return_value = [
        {"mal_id": 1, "title": "Cyberpunk: Edgerunners", "similarity_score": 0.89}
    ]

    response = client.get("/api/anime/vibe-search?q=gritty%20cyberpunk%20action&limit=5")

    assert response.status_code == 200
    json_data = response.json()
    assert "results" in json_data
    assert len(json_data["results"]) == 1
    assert json_data["results"][0]["title"] == "Cyberpunk: Edgerunners"
    mock_vibe_search.assert_awaited_once_with(query_text="gritty cyberpunk action", top_k=5)


@patch("routes.anime.get_anime_by_id", new_callable=AsyncMock)
def test_get_anime_detail_endpoint(mock_get_by_id, override_get_db):
    """Test fetching details for a specific anime by mal_id."""
    mock_get_by_id.return_value = {
        "mal_id": 21,
        "title": "One Piece",
        "episodes": 1000,
        "score": 8.7,
        "similar_anime": []
    }

    response = client.get("/api/anime/21")

    assert response.status_code == 200
    data = response.json()
    assert data["mal_id"] == 21
    assert data["title"] == "One Piece"
    mock_get_by_id.assert_awaited_once()