from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..deps import get_current_user
from ..database import get_db
from ..models import Debt
from ..schemas import DebtCreate, DebtUpdate
from ..response import ok

router = APIRouter(prefix="/debts", tags=["debts"])

@router.get("/summary")
def debts_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    borrow_sum = db.query(func.coalesce(func.sum(Debt.amount), 0)).filter(Debt.user_id == user.user_id, Debt.debt_type == "BORROW").scalar()
    lend_sum = db.query(func.coalesce(func.sum(Debt.amount), 0)).filter(Debt.user_id == user.user_id, Debt.debt_type == "LEND").scalar()
    data = {
        "total_borrow_in": float(borrow_sum or 0),
        "total_lend_out": float(lend_sum or 0),
        "net_debt": float((lend_sum or 0) - (borrow_sum or 0)),
    }
    return ok(data)

@router.get("/list")
def list_debts(db: Session = Depends(get_db), user=Depends(get_current_user), type: str = Query(None), page: int = 1, page_size: int = 20):
    q = db.query(Debt).filter(Debt.user_id == user.user_id)
    if type:
        q = q.filter(Debt.debt_type == type)
    total = q.count()
    rows = q.order_by(Debt.action_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    data = {
        "list": [
            {
                "debt_id": r.debt_id,
                "type": r.debt_type,
                "person_name": r.person_name,
                "amount": float(r.amount),
                "action_time": r.action_time,
                "note": r.note,
            }
            for r in rows
        ],
        "total": total,
    }
    return ok(data)

@router.post("/add")
def add_debt(payload: DebtCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = Debt(user_id=user.user_id, debt_type=payload.type, person_name=payload.person_name, amount=payload.amount, action_time=payload.action_time, note=payload.note)
    db.add(row)
    db.commit()
    return ok(message="添加成功")

@router.post("/update")
def update_debt(payload: DebtUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.query(Debt).filter(Debt.debt_id == payload.debt_id, Debt.user_id == user.user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="debt not found")
    if payload.person_name is not None:
        row.person_name = payload.person_name
    if payload.amount is not None:
        row.amount = payload.amount
    if payload.note is not None:
        row.note = payload.note
    db.commit()
    return ok(message="修改成功")

@router.post("/delete")
def delete_debt(req: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    debt_id = req.get("debt_id")
    row = db.query(Debt).filter(Debt.debt_id == debt_id, Debt.user_id == user.user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="debt not found")
    db.delete(row)
    db.commit()
    return ok(message="删除成功")
