import re
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, EmailStr

GenderEnum = Literal['Male', 'Female', 'Other', '']
DepartmentEnum = Literal['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales', 'Admin', 'Other', '']

class EmployeeBase(BaseModel):
    fullName: str = Field(..., max_length=100, description="Full name of employee")
    employeeId: str = Field(..., max_length=20, description="Employee ID")
    email: EmailStr = Field(..., max_length=150, description="Email address")
    phone: str = Field(..., max_length=10, description="Phone number")
    dateOfBirth: Optional[str] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = Field(None, max_length=500, description="Address")
    department: Optional[DepartmentEnum] = None
    position: Optional[str] = Field(None, max_length=100, description="Position")
    joinDate: Optional[str] = None

    @field_validator('fullName')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Full name is required')
        trimmed = v.strip()
        if not re.match(r'^[A-Za-z\s]+$', trimmed):
            raise ValueError('Full name must contain only letters and spaces (no numbers or special characters)')
        if len(trimmed) > 100:
            raise ValueError('Full name cannot exceed 100 characters')
        return trimmed

    @field_validator('employeeId')
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Employee ID is required')
        trimmed = v.strip()
        if not re.match(r'^EMP\d+$', trimmed):
            raise ValueError('Employee ID must start with EMP in capital letters followed by numbers (e.g. EMP001)')
        if len(trimmed) > 20:
            raise ValueError('Employee ID cannot exceed 20 characters')
        return trimmed

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Email is required')
        trimmed = v.strip().lower()
        if len(trimmed) > 150:
            raise ValueError('Email cannot exceed 150 characters')
        if not re.match(r'^[a-z0-9._%+-]+@snsgroups\.com$', trimmed):
            raise ValueError('Email must be in lowercase and end with @snsgroups.com domain')
        return trimmed

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Phone number is required')
        trimmed = v.strip()
        if not re.match(r'^\d{10}$', trimmed):
            raise ValueError('Phone number must be exactly 10 digits (numbers only)')
        return trimmed

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip()
            if len(trimmed) > 500:
                raise ValueError('Address cannot exceed 500 characters')
            return trimmed
        return v

    @field_validator('position')
    @classmethod
    def validate_position(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip()
            if len(trimmed) > 100:
                raise ValueError('Position cannot exceed 100 characters')
            return trimmed
        return v

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    fullName: Optional[str] = None
    employeeId: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dateOfBirth: Optional[str] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    department: Optional[DepartmentEnum] = None
    position: Optional[str] = None
    joinDate: Optional[str] = None

    @field_validator('fullName')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip()
            if not re.match(r'^[A-Za-z\s]+$', trimmed):
                raise ValueError('Full name must contain only letters and spaces (no numbers or special characters)')
            if len(trimmed) > 100:
                raise ValueError('Full name cannot exceed 100 characters')
            return trimmed
        return v

    @field_validator('employeeId')
    @classmethod
    def validate_employee_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip()
            if not re.match(r'^EMP\d+$', trimmed):
                raise ValueError('Employee ID must start with EMP in capital letters followed by numbers (e.g. EMP001)')
            if len(trimmed) > 20:
                raise ValueError('Employee ID cannot exceed 20 characters')
            return trimmed
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip().lower()
            if len(trimmed) > 150:
                raise ValueError('Email cannot exceed 150 characters')
            if not re.match(r'^[a-z0-9._%+-]+@snsgroups\.com$', trimmed):
                raise ValueError('Email must be in lowercase and end with @snsgroups.com domain')
            return trimmed
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip()
            if not re.match(r'^\d{10}$', trimmed):
                raise ValueError('Phone number must be exactly 10 digits (numbers only)')
            return trimmed
        return v

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip()
            if len(trimmed) > 500:
                raise ValueError('Address cannot exceed 500 characters')
            return trimmed
        return v

    @field_validator('position')
    @classmethod
    def validate_position(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != '':
            trimmed = v.strip()
            if len(trimmed) > 100:
                raise ValueError('Position cannot exceed 100 characters')
            return trimmed
        return v
