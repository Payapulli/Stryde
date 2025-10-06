import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import main

@pytest.fixture
def client():
    return TestClient(main.app)

@pytest.fixture
def mock_strava_response():
    return {
        "id": 12345,
        "username": "testuser",
        "firstname": "Test",
        "lastname": "User",
        "profile_medium": "https://example.com/profile.jpg"
    }

@pytest.fixture
def mock_activities_response():
    return [
        {
            "id": 1,
            "type": "Run",
            "distance": 5000,
            "moving_time": 1800,
            "start_date": "2024-01-01T10:00:00Z"
        },
        {
            "id": 2,
            "type": "Run", 
            "distance": 10000,
            "moving_time": 3600,
            "start_date": "2024-01-02T10:00:00Z"
        }
    ]

class TestPingEndpoint:
    def test_ping_returns_pong(self, client):
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"message": "pong"}

class TestStravaAuth:
    def test_strava_auth_returns_auth_url(self, client):
        response = client.get("/auth/strava")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "state" in data
        assert "strava.com/oauth/authorize" in data["auth_url"]

    def test_strava_callback_with_invalid_state(self, client):
        response = client.get("/auth/callback?code=test_code&state=invalid_state")
        assert response.status_code == 400
        assert "Invalid state" in response.json()["detail"]

class TestTrainingVolume:
    def test_training_volume_requires_authentication(self, client):
        response = client.get("/training/volume?state=invalid_state")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @patch('main.fetch_user_activities')
    def test_training_volume_with_valid_session(self, mock_fetch, client, mock_activities_response):
        # Mock user session
        main.user_sessions["test_state"] = {
            "authenticated": True,
            "access_token": "test_token",
            "athlete": {"id": 12345}
        }
        
        # Mock activities response
        mock_fetch.return_value = mock_activities_response
        
        response = client.get("/training/volume?state=test_state")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_activities" in data
        assert "weekly_volume" in data
        assert "monthly_volume" in data
        assert data["total_activities"] == 2

class TestUserProfile:
    def test_user_profile_requires_authentication(self, client):
        response = client.get("/user/profile?state=invalid_state")
        assert response.status_code == 401

    def test_user_profile_with_valid_session(self, client, mock_strava_response):
        # Mock user session with athlete data
        main.user_sessions["test_state"] = {
            "authenticated": True,
            "access_token": "test_token",
            "athlete": mock_strava_response
        }
        
        response = client.get("/user/profile?state=test_state")
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["firstname"] == "Test"
