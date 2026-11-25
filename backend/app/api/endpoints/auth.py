"""Auth endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User
from app.core.security import verify_password, create_access_token, get_current_user, get_password_hash
from app.schemas import LoginRequest, TokenResponse, UserOut, UserCreate
from app.models import AuditLog

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(form_data: LoginRequest, db: Session = Depends(get_db), request: Request = None):
    email = form_data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    token = create_access_token({"sub": str(user.id), "role": user.role})

    # Audit log
    db.add(AuditLog(user_id=user.id, action="login", resource="auth"))
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
        }
    }


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserOut)
async def register(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Admin only - register new user"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can register users")
    
    email = payload.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Password changed successfully"}
