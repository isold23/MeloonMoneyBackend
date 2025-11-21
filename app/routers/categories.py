from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ..database import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryUpdate
from ..response import ok

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/list")
def list_categories(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Category).filter(Category.user_id == user.user_id).all()
    data = [
        {
            "category_id": r.category_id,
            "name": r.category_name,
            "type": r.category_type,
            "icon": r.icon,
        }
        for r in rows
    ]
    return ok(data)

@router.post("/add")
def add_category(payload: CategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = Category(user_id=user.user_id, category_name=payload.name, category_type=payload.type, icon=payload.icon, is_system=0)
    db.add(row)
    db.commit()
    return ok(message="添加成功")

@router.post("/update")
def update_category(payload: CategoryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.query(Category).filter(Category.category_id == payload.category_id, Category.user_id == user.user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="category not found")
    if payload.name is not None:
        row.category_name = payload.name
    if payload.icon is not None:
        row.icon = payload.icon
    db.commit()
    return ok(message="更新成功")

@router.post("/delete")
def delete_category(req: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    category_id = req.get("category_id")
    row = db.query(Category).filter(Category.category_id == category_id, Category.user_id == user.user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="category not found")
    db.delete(row)
    db.commit()
    return ok(message="删除成功")
