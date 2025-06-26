"""
API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_authentication_required(client):
    """Test that protected endpoints require authentication"""
    response = client.post("/search/range", json={
        "bounds": {
            "min_lat": 40.0,
            "max_lat": 41.0,
            "min_lng": -75.0,
            "max_lng": -73.0
        }
    })
    # Should return 401 or 403 without authentication
    assert response.status_code in [401, 403]

def test_range_search_with_auth(client, test_database, sample_properties):
    """Test range search with authentication"""
    # First, get authentication token
    auth_response = client.post("/auth/token", json={"api_key": "test-api-key"})
    
    if auth_response.status_code == 200:
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Load sample data
        with test_database.get_connection() as conn:
            cursor = conn.cursor()
            for _, row in sample_properties.iterrows():
                cursor.execute("""
                    INSERT INTO core.properties (external_id, address, city, state, price, geom)
                    VALUES (%s, %s, %s, %s, %s, ST_Point(%s, %s))
                """, [
                    row['external_id'], row['address'], row['city'], 
                    row['state'], row['price'], row['longitude'], row['latitude']
                ])
            conn.commit()
        
        # Test range search
        response = client.post("/search/range", 
            json={
                "bounds": {
                    "min_lat": 40.0,
                    "max_lat": 42.0,
                    "min_lng": -75.0,
                    "max_lng": -73.0
                }
            },
            headers=headers
        )
        
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
