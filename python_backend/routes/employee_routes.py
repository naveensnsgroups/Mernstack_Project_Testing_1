from fastapi import APIRouter, HTTPException, Query, status
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from config.db import get_database
from models.employee import EmployeeCreate, EmployeeUpdate

router = APIRouter(prefix="/api/employees", tags=["employees"])

ALLOWED_FIELDS = [
    'fullName', 'employeeId', 'email', 'phone',
    'dateOfBirth', 'gender', 'address',
    'department', 'position', 'joinDate',
]

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        doc["_id"] = str(doc["_id"])
    
    # Convert date / datetime objects to ISO strings or formatted strings matching mongoose behavior
    for key, value in list(doc.items()):
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, date):
            doc[key] = value.isoformat()
            
    # Also ensure createdAt / updatedAt are ISO strings if present
    if "createdAt" in doc and isinstance(doc["createdAt"], datetime):
        doc["createdAt"] = doc["createdAt"].isoformat()
    if "updatedAt" in doc and isinstance(doc["updatedAt"], datetime):
        doc["updatedAt"] = doc["updatedAt"].isoformat()
        
    return doc

@router.get("", status_code=status.HTTP_200_OK)
async def get_all_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    try:
        db = get_database()
        collection = db["HR"]
        skip = (page - 1) * limit

        cursor = collection.find().sort("createdAt", -1).skip(skip).limit(limit)
        employees_cursor = await cursor.to_list(length=limit)
        total = await collection.count_documents({})

        employees = [serialize_doc(emp) for emp in employees_cursor]

        pages = (total + limit - 1) // limit if limit > 0 else 0

        return {
            "success": True,
            "count": len(employees),
            "total": total,
            "page": page,
            "pages": pages,
            "data": employees,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_employee_by_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid employee ID format")
    try:
        db = get_database()
        collection = db["HR"]
        employee = await collection.find_one({"_id": ObjectId(id)})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {"success": True, "data": serialize_doc(employee)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate):
    try:
        db = get_database()
        collection = db["HR"]
        
        data = payload.model_dump(exclude_unset=True)
        
        # Convert date objects to datetime or strings if needed for MongoDB storage matching mongoose
        for k in ['dateOfBirth', 'joinDate']:
            if k in data and data[k]:
                if isinstance(data[k], date) and not isinstance(data[k], datetime):
                    data[k] = datetime.combine(data[k], datetime.min.time())

        # Check unique constraints manually to match mongoose E11000 duplicate key error handling
        if "employeeId" in data:
            existing_emp = await collection.find_one({"employeeId": data["employeeId"]})
            if existing_emp:
                raise HTTPException(status_code=409, detail="employeeId already exists")
        if "email" in data:
            existing_email = await collection.find_one({"email": data["email"]})
            if existing_email:
                raise HTTPException(status_code=409, detail="email already exists")

        now = datetime.utcnow()
        data["createdAt"] = now
        data["updatedAt"] = now

        result = await collection.insert_one(data)
        created_doc = await collection.find_one({"_id": result.inserted_id})

        return {
            "success": True,
            "message": "Employee created successfully",
            "data": serialize_doc(created_doc)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        if "duplicate key error" in str(e) or "E11000" in str(e):
            raise HTTPException(status_code=409, detail="Duplicate key error")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_employee(id: str, payload: EmployeeUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid employee ID format")
    try:
        db = get_database()
        collection = db["HR"]

        data = payload.model_dump(exclude_unset=True)
        if not data:
            employee = await collection.find_one({"_id": ObjectId(id)})
            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found")
            return {"success": True, "message": "Employee updated successfully", "data": serialize_doc(employee)}

        for k in ['dateOfBirth', 'joinDate']:
            if k in data and data[k]:
                if isinstance(data[k], date) and not isinstance(data[k], datetime):
                    data[k] = datetime.combine(data[k], datetime.min.time())

        # Check duplicate keys if updating employeeId or email
        if "employeeId" in data:
            existing = await collection.find_one({"employeeId": data["employeeId"], "_id": {"$ne": ObjectId(id)}})
            if existing:
                raise HTTPException(status_code=409, detail="employeeId already exists")
        if "email" in data:
            existing = await collection.find_one({"email": data["email"], "_id": {"$ne": ObjectId(id)}})
            if existing:
                raise HTTPException(status_code=409, detail="email already exists")

        data["updatedAt"] = datetime.utcnow()

        updated_doc = await collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True
        )

        if not updated_doc:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {
            "success": True,
            "message": "Employee updated successfully",
            "data": serialize_doc(updated_doc)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        if "duplicate key error" in str(e) or "E11000" in str(e):
            raise HTTPException(status_code=409, detail="Duplicate key error")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_employee(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid employee ID format")
    try:
        db = get_database()
        collection = db["HR"]

        deleted_doc = await collection.find_one_and_delete({"_id": ObjectId(id)})
        if not deleted_doc:
            raise HTTPException(status_code=404, detail="Employee not found")

        return {"success": True, "message": "Employee deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
