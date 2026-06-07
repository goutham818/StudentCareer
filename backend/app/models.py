from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="student", nullable=False)  # 'admin' or 'student'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One-to-one relationship with Student (only for student role)
    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    students = relationship("Student", back_populates="department")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True)
    name = Column(String(100), nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    cgpa = Column(Float, nullable=False)
    attendance = Column(Float, nullable=False)
    skills = Column(Text, nullable=True)       # Comma-separated list of skills
    interests = Column(Text, nullable=True)    # Comma-separated list of interests

    # Relationships
    user = relationship("User", back_populates="student")
    department = relationship("Department", back_populates="students")
    performance_records = relationship("PerformanceRecord", back_populates="student", cascade="all, delete-orphan")
    career_recommendations = relationship("CareerRecommendation", back_populates="student", cascade="all, delete-orphan")


class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    attendance = Column(Float, nullable=False)
    internal_marks = Column(Float, nullable=False)
    assignment_score = Column(Float, nullable=False)
    previous_cgpa = Column(Float, nullable=False)
    predicted_category = Column(String(50), nullable=True)  # Excellent, Good, Average, Needs Improvement

    student = relationship("Student", back_populates="performance_records")


class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    career_path = Column(String(100), nullable=False)
    match_score = Column(Float, nullable=False)
    recommended_skills = Column(Text, nullable=True)
    roadmap = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="career_recommendations")
