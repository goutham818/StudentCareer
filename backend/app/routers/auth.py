from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import database, models, schemas, auth
from datetime import timedelta
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) | 
        (models.User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create user
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password_hash=auth.get_password_hash(user_data.password),
        role=user_data.role or "student"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # If it is a student role, check if a student profile with their username/email already exists
    # If not, let them fill it later or create a shell profile.
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(
    login_data: Optional[schemas.LoginRequest] = None,
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(None),
    db: Session = Depends(database.get_db)
):
    # Support both JSON payload and OAuth2 Form data for maximum compatibility
    username = None
    password = None

    if form_data:
        username = form_data.username
        password = form_data.password
    elif login_data:
        username = login_data.username
        password = login_data.password
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credentials must be provided in request body"
        )

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }

@router.get("/profile", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
