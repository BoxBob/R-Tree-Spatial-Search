# tests/test_advanced_features.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class TestAdvancedSpatialFeatures:
    def setup_method(self):
        # Get authentication token
        response = client.post("/auth/token", json={"api_key": "your-api-key-here"})
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_polygon_search(self):
        """Test custom polygon search"""
        polygon_coords = [
            [-74.0060, 40.7128],  # NYC coordinates
            [-74.0060, 40.7589],
            [-73.9352, 40.7589],
            [-73.9352, 40.7128],
            [-74.0060, 40.7128]   # Close the polygon
        ]
        
        query_data = {
            "polygon_coordinates": polygon_coords,
            "max_price": 1000000
        }
        
        response = client.post("/api/v1/advanced/search/polygon", 
                             json=query_data, headers=self.headers)
        assert response.status_code == 200
        
        results = response.json()
        assert isinstance(results, list)
    
    def test_proximity_search(self):
        """Test amenity proximity search"""
        query_data = {
            "amenity_type": "school",
            "distance_km": 2.0,
            "max_price": 800000
        }
        
        response = client.post("/api/v1/advanced/search/proximity",
                             json=query_data, headers=self.headers)
        assert response.status_code == 200
        
        results = response.json()
        assert isinstance(results, list)
        
        # Verify distance constraint
        for result in results:
            assert result['distance_km'] <= 2.0
    
    def test_district_analysis(self):
        """Test district-based property analysis"""
        response = client.get("/api/v1/advanced/search/districts", 
                            headers=self.headers)
        assert response.status_code == 200
        
        results = response.json()
        assert isinstance(results, dict)
        
        # Verify structure
        for district_name, stats in results.items():
            assert 'count' in stats
            assert 'avg_price' in stats
            assert 'properties' in stats
