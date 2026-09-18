import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

from python_backend.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Personal Details API is running."}

def test_not_found_endpoint():
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"success": False, "message": "Route not found"}

@patch("python_backend.controllers.employee_controller.get_db")
def test_get_all_employees_mock(mock_get_db):
    mock_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.__iter__.return_value = iter([
        {
            "_id": ObjectId(),
            "fullName": "John Doe",
            "employeeId": "EMP001",
            "email": "john.doe@snsgroups.com",
            "phone": "9876543210",
            "department": "IT",
            "createdAt": "2024-01-01T00:00:00"
        }
    ])
    mock_collection.find.return_value = mock_cursor
    mock_collection.count_documents = AsyncMock(return_value=1)
    
    mock_db = {"HR": mock_collection}
    mock_get_db.return_value = mock_db

    response = client.get("/api/employees")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 1
    assert data["total"] == 1
    assert data["data"][0]["fullName"] == "John Doe"

def test_create_employee_validation_error():
    payload = {
        "fullName": "Jane Smith",
        "employeeId": "EMP002",
        "email": "jane@gmail.com",
        "phone": "123",
        "department": "HR"
    }
    response = client.post("/api/employees", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "email" in data["message"].lower() or "phone" in data["message"].lower()
