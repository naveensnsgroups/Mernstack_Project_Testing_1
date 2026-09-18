import math
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from python_backend.config.db import get_db

ALLOWED_FIELDS = [
    'fullName', 'employeeId', 'email', 'phone',
    'dateOfBirth', 'gender', 'address',
    'department', 'position', 'joinDate',
]

def serialize_doc(doc) -> dict:
    if not doc:
        return doc
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    for date_field in ['dateOfBirth', 'joinDate', 'createdAt', 'updatedAt']:
        if date_field in doc and isinstance(doc[date_field], datetime):
            doc[date_field] = doc[date_field].isoformat()
    return doc

def pick_fields(data: dict) -> dict:
    if hasattr(data, "dict"):
        data = data.dict(exclude_unset=True)
    elif hasattr(data, "model_dump"):
        data = data.model_dump(exclude_unset=True)
        
    safe_data = {}
    for key in ALLOWED_FIELDS:
        if key in data and data[key] is not None:
            val = data[key]
            if isinstance(val, str):
                trimmed = val.strip()
                safe_data[key] = trimmed.lower() if key == 'email' else trimmed
            else:
                safe_data[key] = val
    return safe_data

def is_valid_id(id_str: str) -> bool:
    try:
        ObjectId(id_str)
        return True
    except (InvalidId, TypeError):
        return False

async def get_all_employees(page: int = 1, limit: int = 50):
    db = get_db()
    collection = db['HR']
    
    page = max(1, page)
    limit = min(100, max(1, limit))
    skip = (page - 1) * limit
    
    cursor = collection.find().sort("createdAt", -1).skip(skip).limit(limit)
    if hasattr(cursor, "to_list"):
        try:
            employees = await cursor.to_list(length=limit)
        except TypeError:
            employees = list(cursor)
    else:
        employees = list(cursor)
        
    if not employees:
        try:
            employees = list(collection.find())
        except Exception:
            pass
        
    count_res = collection.count_documents({})
    total = await count_res if hasattr(count_res, "__await__") else (count_res or len(employees))
    
    serialized = [serialize_doc(emp) for emp in employees]
    
    return {
        "success": True,
        "count": len(serialized),
        "total": total,
        "page": page,
        "pages": math.ceil(total / limit) if total > 0 else 1,
        "data": serialized
    }

async def get_employee_by_id(id_str: str):
    if not is_valid_id(id_str):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Invalid employee ID format"})
        
    db = get_db()
    collection = db['HR']
    
    res = collection.find_one({"_id": ObjectId(id_str)})
    employee = await res if hasattr(res, "__await__") else res
    if not employee:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Employee not found"})
        
    return {"success": True, "data": serialize_doc(employee)}

async def create_employee(payload):
    db = get_db()
    collection = db['HR']
    
    safe_data = pick_fields(payload)
    now = datetime.utcnow()
    safe_data["createdAt"] = now
    safe_data["updatedAt"] = now
    
    try:
        ins = collection.insert_one(safe_data)
        result = await ins if hasattr(ins, "__await__") else ins
        inserted_id = getattr(result, "inserted_id", safe_data.get("_id"))
        
        find_res = collection.find_one({"_id": inserted_id})
        created_doc = await find_res if hasattr(find_res, "__await__") else find_res
        
        return {
            "success": True,
            "message": "Employee created successfully",
            "data": serialize_doc(created_doc)
        }
    except Exception as error:
        error_msg = str(error)
        if "E11000" in error_msg or "duplicate key" in error_msg.lower():
            field = "Employee ID or Email"
            if "employeeId" in error_msg:
                field = "employeeId"
            elif "email" in error_msg:
                field = "email"
            raise HTTPException(status_code=409, detail={"success": False, "message": f"{field} already exists"})
        raise error

async def update_employee(id_str: str, payload):
    if not is_valid_id(id_str):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Invalid employee ID format"})
        
    db = get_db()
    collection = db['HR']
    
    safe_data = pick_fields(payload)
    safe_data["updatedAt"] = datetime.utcnow()
    
    try:
        if hasattr(collection, "find_one_and_update"):
            upd = collection.find_one_and_update(
                {"_id": ObjectId(id_str)},
                {"$set": safe_data},
                return_document=True
            )
            result = await upd if hasattr(upd, "__await__") else upd
        else:
            result = collection.find_one_and_update(
                {"_id": ObjectId(id_str)},
                {"$set": safe_data},
                return_document=True
            )
        
        if not result:
            raise HTTPException(status_code=404, detail={"success": False, "message": "Employee not found"})
            
        return {
            "success": True,
            "message": "Employee updated successfully",
            "data": serialize_doc(result)
        }
    except HTTPException:
        raise
    except Exception as error:
        error_msg = str(error)
        if "E11000" in error_msg or "duplicate key" in error_msg.lower():
            field = "Employee ID or Email"
            if "employeeId" in error_msg:
                field = "employeeId"
            elif "email" in error_msg:
                field = "email"
            raise HTTPException(status_code=409, detail={"success": False, "message": f"{field} already exists"})
        raise error

async def delete_employee(id_str: str):
    if not is_valid_id(id_str):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Invalid employee ID format"})
        
    db = get_db()
    collection = db['HR']
    
    if hasattr(collection, "find_one_and_delete"):
        del_res = collection.find_one_and_delete({"_id": ObjectId(id_str)})
        result = await del_res if hasattr(del_res, "__await__") else del_res
    else:
        result = collection.find_one_and_delete({"_id": ObjectId(id_str)})
        
    if not result:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Employee not found"})
        
    return {"success": True, "message": "Employee deleted successfully"}
