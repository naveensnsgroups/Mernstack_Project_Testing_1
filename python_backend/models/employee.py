from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
import re

GenderEnum = Literal['Male', 'Female', 'Other', '']
DepartmentEnum = Literal['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales', 'Admin', 'Other', '']

class EmployeeCreate(BaseModel):
    fullName: str = Field(..., min_length=1, max_length=100)
    employeeId: str = Field(..., min_length=1, max_length=20)
    email: EmailStr = Field(..., max_length=150)
    phone: str = Field(..., min_length=10, max_length=10)
    dateOfBirth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = Field(None, max_length=500)
    department: Optional[DepartmentEnum] = None
    position: Optional[str] = Field(None, max_length=100)
    joinDate: Optional[date] = None

    @field_validator('fullName')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v_trimmed = v.strip()
        if not v_trimmed:
            raise ValueError('Full name is required')
        if len(v_trimmed) > 100:
            raise ValueError('Full name cannot exceed 100 characters')
        if not re.match(r'^[A-Za-z\s]+$', v_trimmed):
            raise ValueError('Full name must contain only letters and spaces (no numbers or special characters)')
        return v_trimmed

    @field_validator('employeeId')
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        v_trimmed = v.strip()
        if not v_trimmed:
            raise ValueError('Employee ID is required')
        if len(v_trimmed) > 20:
            raise ValueError('Employee ID cannot exceed 20 characters')
        if not re.match(r'^EMP\d+$', v_trimmed):
            raise ValueError('Employee ID must start with EMP in capital letters followed by numbers (e.g. EMP001)')
        return v_trimmed

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        v_trimmed = v.strip().lower()
        if not v_trimmed:
            raise ValueError('Email is required')
        if len(v_trimmed) > 150:
            raise ValueError('Email cannot exceed 150 characters')
        if not re.match(r'^[a-z0-9._%+-]+@snsgroups\.com$', v_trimmed):
            raise ValueError('Email must be in lowercase and end with @snsgroups.com domain')
        return v_trimmed

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v_trimmed = v.strip()
        if not v_trimmed:
            raise ValueError('Phone number is required')
        if not re.match(r'^\d{10}$', v_trimmed):
            raise ValueError('Phone number must be exactly 10 digits (numbers only)')
        return v_trimmed

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip()
        if len(v_trimmed) > 500:
            raise ValueError('Address cannot exceed 500 characters')
        return v_trimmed if v_trimmed else None

    @field_validator('position')
    @classmethod
    def validate_position(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip()
        if len(v_trimmed) > 100:
            raise ValueError('Position cannot exceed 100 characters')
        return v_trimmed if v_trimmed else None


class EmployeeUpdate(BaseModel):
    fullName: Optional[str] = Field(None, max_length=100)
    employeeId: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, min_length=10, max_length=10)
    dateOfBirth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = Field(None, max_length=500)
    department: Optional[DepartmentEnum] = None
    position: Optional[str] = Field(None, max_length=100)
    joinDate: Optional[date] = None

    @field_validator('fullName')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip()
        if not v_trimmed:
            raise ValueError('Full name cannot be empty')
        if len(v_trimmed) > 100:
            raise ValueError('Full name cannot exceed 100 characters')
        if not re.match(r'^[A-Za-z\s]+$', v_trimmed):
            raise ValueError('Full name must contain only letters and spaces (no numbers or special characters)')
        return v_trimmed

    @field_validator('employeeId')
    @classmethod
    def validate_employee_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip()
        if not v_trimmed:
            raise ValueError('Employee ID cannot be empty')
        if len(v_trimmed) > 20:
            raise ValueError('Employee ID cannot exceed 20 characters')
        if not re.match(r'^EMP\d+$', v_trimmed):
            raise ValueError('Employee ID must start with EMP in capital letters followed by numbers (e.g. EMP001)')
        return v_trimmed

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip().lower()
        if not v_trimmed:
            raise ValueError('Email cannot be empty')
        if len(v_trimmed) > 150:
            raise ValueError('Email cannot exceed 150 characters')
        if not re.match(r'^[a-z0-9._%+-]+@snsgroups\.com$', v_trimmed):
            raise ValueError('Email must be in lowercase and end with @snsgroups.com domain')
        return v_trimmed

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip()
        if not v_trimmed:
            raise ValueError('Phone number cannot be empty')
        if not re.match(r'^\d{10}$', v_trimmed):
            raise ValueError('Phone number must be exactly 10 digits (numbers only)')
        return v_trimmed

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip()
        if len(v_trimmed) > 500:
            raise ValueError('Address cannot exceed 500 characters')
        return v_trimmed if v_trimmed else None

    @field_validator('position')
    @classmethod
    def validate_position(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_trimmed = v.strip()
        if len(v_trimmed) > 100:
            raise ValueError('Position cannot exceed 100 characters')
        return v_trimmed if v_trimmed else None
