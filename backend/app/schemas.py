from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Token Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "student"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Department Schemas
class DepartmentCreate(BaseModel):
    name: str

class DepartmentResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

# Student Schemas
class StudentCreate(BaseModel):
    name: str
    roll_number: str
    department_id: int
    semester: int
    cgpa: float = Field(..., ge=0.0, le=10.0)
    attendance: float = Field(..., ge=0.0, le=100.0)
    skills: Optional[str] = ""
    interests: Optional[str] = ""

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    roll_number: Optional[str] = None
    department_id: Optional[int] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    attendance: Optional[float] = Field(None, ge=0.0, le=100.0)
    skills: Optional[str] = None
    interests: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    roll_number: str
    department_id: int
    department_name: Optional[str] = None  # Helper for flat display
    semester: int
    cgpa: float
    attendance: float
    skills: Optional[str] = ""
    interests: Optional[str] = ""

    class Config:
        orm_mode = True
        from_attributes = True

# Performance Record Schemas
class PerformanceRecordCreate(BaseModel):
    semester: int
    attendance: float = Field(..., ge=0.0, le=100.0)
    internal_marks: float = Field(..., ge=0.0, le=100.0)
    assignment_score: float = Field(..., ge=0.0, le=100.0)
    previous_cgpa: float = Field(..., ge=0.0, le=10.0)

class PerformanceRecordResponse(BaseModel):
    id: int
    student_id: int
    semester: int
    attendance: float
    internal_marks: float
    assignment_score: float
    previous_cgpa: float
    predicted_category: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

# ML Prediction Schemas
class PredictionRequest(BaseModel):
    attendance: float = Field(..., ge=0.0, le=100.0)
    internal_marks: float = Field(..., ge=0.0, le=100.0)
    previous_cgpa: float = Field(..., ge=0.0, le=10.0)
    assignment_score: float = Field(..., ge=0.0, le=100.0)

class PredictionResponse(BaseModel):
    predicted_category: str

# Career Recommendation Schemas
class CareerRecommendationResponse(BaseModel):
    career_path: str
    match_score: float
    recommended_skills: str
    roadmap: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Overall Analytics Summary
class OverviewStats(BaseModel):
    total_students: int
    average_cgpa: float
    average_attendance: float
    placement_readiness_score: float
