import pytest
from httpx import AsyncClient, ASGITransport
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

@pytest.fixture
def mock_db():
    with patch("routes.employee_routes.get_database") as mock_get_db:
        db = MagicMock()
        mock_get_db.return_value = db
        yield db

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "running" in data["message"]

@pytest.mark.asyncio
async def test_get_all_employees_empty(mock_db):
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[])
    
    mock_collection.find.return_value = mock_cursor
    mock_collection.count_documents = AsyncMock(return_value=0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/employees")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 0
    assert data["total"] == 0
    assert data["data"] == []

@pytest.mark.asyncio
async def test_create_employee_success(mock_db):
    mock_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection
    
    mock_collection.find_one = AsyncMock(side_effect=[None, None, {"_id": "507f1f77bcf86cd799439011", "fullName": "Jane Doe", "employeeId": "EMP001", "email": "jane.doe@snsgroups.com", "phone": "9876543210"}])
    mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="507f1f77bcf86cd799439011"))

    payload = {
        "fullName": "Jane Doe",
        "employeeId": "EMP001",
        "email": "jane.doe@snsgroups.com",
        "phone": "9876543210",
        "department": "IT",
        "position": "Developer",
        "gender": "Female",
        "dateOfBirth": "1998-01-15",
        "joinDate": "2024-06-01",
        "address": "Coimbatore"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/employees", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Employee created successfully"
    assert data["data"]["employeeId"] == "EMP001"
    assert data["data"]["email"] == "jane.doe@snsgroups.com"

@pytest.mark.asyncio
async def test_create_employee_validation_error():
    payload = {
        "fullName": "Jane123",
        "employeeId": "INVALID",
        "email": "jane@gmail.com",
        "phone": "12345"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/employees", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "message" in data

@pytest.mark.asyncio
async def test_get_employee_by_id_invalid_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/employees/invalid-object-id")

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "Invalid employee ID format" in data["message"]
