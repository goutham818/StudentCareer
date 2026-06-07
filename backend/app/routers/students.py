from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import database, models, schemas, auth

router = APIRouter(prefix="/api/students", tags=["Students"])

@router.get("", response_model=List[schemas.StudentResponse])
def get_students(
    department_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(database.get_db)
):
    """Retrieve all students (Admin only). Optional filtering by department."""
    query = db.query(models.Student)
    if department_id:
        query = query.filter(models.Student.department_id == department_id)
    
    students = query.all()
    
    # Flatten responses to include department name
    results = []
    for s in students:
        s_resp = schemas.StudentResponse.from_orm(s)
        s_resp.department_name = s.department.name if s.department else "N/A"
        results.append(s_resp)
        
    return results

@router.get("/me", response_model=schemas.StudentResponse)
def get_my_profile(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Retrieve current logged-in student's profile."""
    student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please create or link your profile."
        )
    resp = schemas.StudentResponse.from_orm(student)
    resp.department_name = student.department.name if student.department else "N/A"
    return resp

@router.post("/me", response_model=schemas.StudentResponse)
def create_my_profile(
    student_data: schemas.StudentCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Create or link a student profile for the current logged-in user."""
    # Check if user already has a student profile
    existing_profile = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile already exists for this user."
        )
        
    # Check if roll number already exists
    existing_roll = db.query(models.Student).filter(models.Student.roll_number == student_data.roll_number).first()
    if existing_roll:
        # If it exists but has no user_id, link it!
        if existing_roll.user_id is None:
            existing_roll.user_id = current_user.id
            # Also update name if needed
            existing_roll.name = student_data.name
            db.commit()
            db.refresh(existing_roll)
            resp = schemas.StudentResponse.from_orm(existing_roll)
            resp.department_name = existing_roll.department.name if existing_roll.department else "N/A"
            return resp
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Roll number is already linked to another user account."
            )

    # If it doesn't exist, create a fresh profile
    new_student = models.Student(
        user_id=current_user.id,
        name=student_data.name,
        roll_number=student_data.roll_number,
        department_id=student_data.department_id,
        semester=student_data.semester,
        cgpa=student_data.cgpa,
        attendance=student_data.attendance,
        skills=student_data.skills,
        interests=student_data.interests
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    resp = schemas.StudentResponse.from_orm(new_student)
    resp.department_name = new_student.department.name if new_student.department else "N/A"
    return resp

@router.post("", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: schemas.StudentCreate,
    current_user: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(database.get_db)
):
    """Add a new student (Admin only)."""
    existing_roll = db.query(models.Student).filter(models.Student.roll_number == student_data.roll_number).first()
    if existing_roll:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this roll number already exists"
        )
    
    # Create the student profile
    new_student = models.Student(
        name=student_data.name,
        roll_number=student_data.roll_number,
        department_id=student_data.department_id,
        semester=student_data.semester,
        cgpa=student_data.cgpa,
        attendance=student_data.attendance,
        skills=student_data.skills,
        interests=student_data.interests
    )
    
    # Automatically create a corresponding Student user account if not exists
    # Default username will be roll number (lowercase), password will be roll_number + "123"
    username = student_data.roll_number.lower()
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if not existing_user:
        hashed_pw = auth.get_password_hash(f"{student_data.roll_number.lower()}123")
        student_user = models.User(
            username=username,
            email=f"{username}@college.edu",
            password_hash=hashed_pw,
            role="student"
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)
        new_student.user_id = student_user.id
        
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    resp = schemas.StudentResponse.from_orm(new_student)
    resp.department_name = new_student.department.name if new_student.department else "N/A"
    return resp

@router.get("/{id}", response_model=schemas.StudentResponse)
def get_student(
    id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """View details of a specific student (Admin or the student themselves)."""
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check permissions: Admin can view all; student can only view their own profile
    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this student profile"
        )
        
    resp = schemas.StudentResponse.from_orm(student)
    resp.department_name = student.department.name if student.department else "N/A"
    return resp

@router.put("/{id}", response_model=schemas.StudentResponse)
def update_student(
    id: int,
    student_data: schemas.StudentUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Update student profile (Admin or the student themselves)."""
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
        
    # Check permissions
    if current_user.role != "admin" and student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this student profile"
        )
    
    # Exclude roll number update for normal students to maintain integrity
    update_dict = student_data.dict(exclude_unset=True)
    if current_user.role != "admin" and "roll_number" in update_dict:
        del update_dict["roll_number"]
        
    for key, value in update_dict.items():
        setattr(student, key, value)
        
    db.commit()
    db.refresh(student)
    
    resp = schemas.StudentResponse.from_orm(student)
    resp.department_name = student.department.name if student.department else "N/A"
    return resp

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    id: int,
    current_user: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(database.get_db)
):
    """Delete a student and their linked user account (Admin only)."""
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
        
    # Delete student (associated user account will be deleted if we want, or just delete user.
    # Since we set ondelete="CASCADE" on student.user_id, deleting student does NOT delete user.
    # Let's delete user as well to clean up.
    if student.user_id:
        user = db.query(models.User).filter(models.User.id == student.user_id).first()
        if user:
            db.delete(user)
    
    db.delete(student)
    db.commit()
    return None
