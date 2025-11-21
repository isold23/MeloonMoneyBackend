from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import RegisterRequest, LoginRequest, TokenData
from ..models import User
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token
from ..response import ok

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existed = db.query(User).filter(User.email == payload.email).first()
    if existed:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(email=payload.email, password_hash=hash_password(payload.password), language=payload.language)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"user_id": user.user_id, "nickname": user.nickname})
    return ok({"user_id": user.user_id, "token": token}, "注册成功")

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"user_id": user.user_id, "nickname": user.nickname})
    return ok({"user_id": user.user_id, "nickname": user.nickname, "token": token})
