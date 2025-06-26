import pytest
from fastapi.testclient import TestClient
from api.main import app  # Import your FastAPI app

# Create a client to interact with your app in tests
client = TestClient(app)

def test_health_check():
    """Tests if the health check endpoint is working."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "rtree-spatial-search"}

def test_range_search_success():
    """
    Tests a successful range search.
    Note: This will fail initially because the endpoint only returns a static mock.
    You will implement the logic in the next step to make this pass.
    """
    query = {
        "bounds": {
            "min_lng": -122.4,
            "min_lat": 37.7,
            "max_lng": -122.3,
            "max_lat": 37.8
        },
        "filters": {}
    }
    response = client.post("/search/range", json=query)
    assert response.status_code == 200
    
    # Assert that the response is a list (even if empty)
    assert isinstance(response.json(), list)

def test_range_search_invalid_input():
    """Tests the API's response to invalid or missing data."""
    # Missing 'bounds' key
    invalid_query = {
        "filters": {}
    }
    response = client.post("/search/range", json=invalid_query)
    # FastAPI should automatically return a 422 Unprocessable Entity for invalid models
    assert response.status_code == 422
