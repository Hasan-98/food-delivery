from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from services.auth_service import AuthService
from utils.database import get_db
from app.schemas import UserCreate, User as UserSchema, Token
from app.dependencies import get_current_user, require_role
from models.user import User

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    auth_service = AuthService()
    # Check if user already exists
    print("user-----", user)
    db_user = auth_service.get_user_by_email(db, user.email)
    print("db_user", db_user)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    # Create new user
    db_user = auth_service.create_user(
        db=db,
        email=user.email,
        name=user.name,
        password=user.password,
        role=user.role
    )
    
    return db_user

@router.post("/login", response_model=Token)
async def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    auth_service = AuthService()
    
    user = auth_service.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users", response_model=list[UserSchema])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/health/db")
async def health_check_db(db: Session = Depends(get_db)):
    """Check database connection health"""
    try:
        # Test database connection by executing a simple query
        from sqlalchemy import text
        result = db.execute(text("SELECT 1")).fetchone()
        if result:
            return {
                "status": "healthy",
                "database": "connected",
                "message": "Database connection successful"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "message": "Database connection failed"
        }