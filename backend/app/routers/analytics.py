from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app import database, models, schemas, auth

router = APIRouter(tags=["Analytics"])

@router.get("/api/departments", response_model=List[schemas.DepartmentResponse])
def get_departments(
    db: Session = Depends(database.get_db)
):
    """Get list of all departments."""
    return db.query(models.Department).all()

@router.get("/api/analytics/overview", response_model=schemas.OverviewStats)
def get_overview_stats(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Retrieve key metrics cards (Total Students, Avg CGPA, Avg Attendance, Placement Readiness)."""
    students = db.query(models.Student).all()
    if not students:
        return {
            "total_students": 0,
            "average_cgpa": 0.0,
            "average_attendance": 0.0,
            "placement_readiness_score": 0.0
        }
    
    total_students = len(students)
    avg_cgpa = sum(s.cgpa for s in students) / total_students
    avg_attendance = sum(s.attendance for s in students) / total_students
    
    # Calculate Placement Readiness Score for each student
    # Formula: CGPA (40%), Attendance (30%), Skills count (30%)
    readiness_scores = []
    for s in students:
        cgpa_score = s.cgpa * 10  # Scale 0-10 to 0-100
        att_score = s.attendance
        
        # Skill rating out of 100 based on count of skills
        skills_list = [sk.strip() for sk in s.skills.split(",") if sk.strip()] if s.skills else []
        skills_score = min(len(skills_list) * 20, 100) # 5+ skills gets 100%
        
        student_readiness = (cgpa_score * 0.40) + (att_score * 0.30) + (skills_score * 0.30)
        readiness_scores.append(student_readiness)
        
    avg_readiness = sum(readiness_scores) / total_students
    
    return {
        "total_students": total_students,
        "average_cgpa": round(avg_cgpa, 2),
        "average_attendance": round(avg_attendance, 2),
        "placement_readiness_score": round(avg_readiness, 2)
    }

@router.get("/api/analytics/performance")
def get_performance_analytics(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Retrieve structured data for Chart.js dashboards."""
    students = db.query(models.Student).all()
    if not students:
        return {
            "cgpa_distribution": {},
            "attendance_distribution": {},
            "department_analytics": [],
            "semester_analytics": [],
            "top_performers": [],
            "at_risk_students": []
        }
        
    # 1. CGPA Distribution
    cgpa_ranges = {
        "< 6.0": 0,
        "6.0 - 7.0": 0,
        "7.0 - 8.0": 0,
        "8.0 - 9.0": 0,
        "9.0 - 10.0": 0
    }
    for s in students:
        if s.cgpa < 6.0:
            cgpa_ranges["< 6.0"] += 1
        elif s.cgpa < 7.0:
            cgpa_ranges["6.0 - 7.0"] += 1
        elif s.cgpa < 8.0:
            cgpa_ranges["7.0 - 8.0"] += 1
        elif s.cgpa < 9.0:
            cgpa_ranges["8.0 - 9.0"] += 1
        else:
            cgpa_ranges["9.0 - 10.0"] += 1
            
    # 2. Attendance Distribution
    attendance_ranges = {
        "< 75%": 0,
        "75% - 85%": 0,
        "85% - 95%": 0,
        "> 95%": 0
    }
    for s in students:
        if s.attendance < 75.0:
            attendance_ranges["< 75%"] += 1
        elif s.attendance < 85.0:
            attendance_ranges["75% - 85%"] += 1
        elif s.attendance < 95.0:
            attendance_ranges["85% - 95%"] += 1
        else:
            attendance_ranges["> 95%"] += 1

    # 3. Department-wise Performance
    depts = db.query(models.Department).all()
    dept_analytics = []
    for d in depts:
        dept_students = [s for s in students if s.department_id == d.id]
        if dept_students:
            avg_cgpa = sum(s.cgpa for s in dept_students) / len(dept_students)
            avg_att = sum(s.attendance for s in dept_students) / len(dept_students)
            dept_analytics.append({
                "department_name": d.name,
                "student_count": len(dept_students),
                "average_cgpa": round(avg_cgpa, 2),
                "average_attendance": round(avg_att, 2)
            })
        else:
            dept_analytics.append({
                "department_name": d.name,
                "student_count": 0,
                "average_cgpa": 0.0,
                "average_attendance": 0.0
            })

    # 4. Semester-wise Performance
    semesters = sorted(list(set(s.semester for s in students)))
    semester_analytics = []
    for sem in semesters:
        sem_students = [s for s in students if s.semester == sem]
        avg_cgpa = sum(s.cgpa for s in sem_students) / len(sem_students)
        avg_att = sum(s.attendance for s in sem_students) / len(sem_students)
        semester_analytics.append({
            "semester": sem,
            "student_count": len(sem_students),
            "average_cgpa": round(avg_cgpa, 2),
            "average_attendance": round(avg_att, 2)
        })

    # 5. Top Performers (Top 5 by CGPA)
    top_performers_query = db.query(models.Student).order_by(models.Student.cgpa.desc()).limit(5).all()
    top_performers = []
    for s in top_performers_query:
        top_performers.append({
            "id": s.id,
            "name": s.name,
            "roll_number": s.roll_number,
            "department_name": s.department.name if s.department else "N/A",
            "cgpa": s.cgpa,
            "attendance": s.attendance
        })

    # 6. At-Risk Students (CGPA < 6.0 OR Attendance < 75%)
    at_risk_query = db.query(models.Student).filter(
        (models.Student.cgpa < 6.0) | (models.Student.attendance < 75.0)
    ).all()
    at_risk_students = []
    for s in at_risk_query:
        reasons = []
        if s.cgpa < 6.0:
            reasons.append("Low CGPA")
        if s.attendance < 75.0:
            reasons.append("Low Attendance")
        
        at_risk_students.append({
            "id": s.id,
            "name": s.name,
            "roll_number": s.roll_number,
            "department_name": s.department.name if s.department else "N/A",
            "cgpa": s.cgpa,
            "attendance": s.attendance,
            "risk_factors": ", ".join(reasons)
        })

    return {
        "cgpa_distribution": cgpa_ranges,
        "attendance_distribution": attendance_ranges,
        "department_analytics": dept_analytics,
        "semester_analytics": semester_analytics,
        "top_performers": top_performers,
        "at_risk_students": at_risk_students
    }
