from fastapi import APIRouter, Query, Body, status
from python_backend.models.employee import EmployeeCreate, EmployeeUpdate
from python_backend.controllers.employee_controller import (
    get_all_employees,
    get_employee_by_id,
    create_employee,
    update_employee,
    delete_employee,
)

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.get("", status_code=status.HTTP_200_OK)
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    return await get_all_employees(page=page, limit=limit)

@router.post("", status_code=status.HTTP_201_CREATED)
async def post_employee(payload: EmployeeCreate):
    return await create_employee(payload)

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_employee(id: str):
    return await get_employee_by_id(id)

@router.put("/{id}", status_code=status.HTTP_200_OK)
async def put_employee(id: str, payload: EmployeeUpdate):
    return await update_employee(id, payload)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_emp(id: str):
    return await delete_employee(id)
