# tests/test_main.py
"""
Integration and unit tests for FastAPI application endpoints.
Uses TestClient and patches external RAG pipelines.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test that the health endpoint returns status: ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("main.ask")
def test_chat_endpoint_success(mock_ask):
    """Test that the /chat endpoint returns valid responses and delegates to the RAG pipeline."""
    mock_ask.return_value = {
        "answer": "This is a mocked answer for test queries.",
        "sources": ["docs/court_bookings.md"]
    }
    
    payload = {"question": "What are your court booking prices?"}
    response = client.post("/chat", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"answer": "This is a mocked answer for test queries."}
    mock_ask.assert_called_once_with("What are your court booking prices?")

def test_chat_endpoint_invalid_payload():
    """Test that invalid request payloads are blocked with a 422 validation error."""
    payload = {"invalid_key": "What are your prices?"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 422
