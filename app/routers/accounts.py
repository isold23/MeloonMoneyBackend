from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ..database import get_db
from ..models import Account
from ..schemas import AccountCreate, AccountUpdate, AccountItem
from ..response import ok

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/list")
def list_accounts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Account).filter(Account.user_id == user.user_id).all()
    data = [
        {"account_id": r.account_id, "name": r.account_name, "type": r.account_type, "balance": float(r.balance)}
        for r in rows
    ]
    return ok(data)

@router.post("/add")
def add_account(payload: AccountCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    acc = Account(user_id=user.user_id, account_name=payload.name, account_type=payload.type, balance=payload.initial_balance)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return ok({"account_id": acc.account_id}, "添加成功")

@router.post("/update")
def update_account(payload: AccountUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    acc = db.query(Account).filter(Account.account_id == payload.account_id, Account.user_id == user.user_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="account not found")
    if payload.name is not None:
        acc.account_name = payload.name
    if payload.balance is not None:
        acc.balance = payload.balance
    db.commit()
    return ok(message="更新成功")

@router.post("/delete")
def delete_account(req: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    account_id = req.get("account_id")
    acc = db.query(Account).filter(Account.account_id == account_id, Account.user_id == user.user_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="account not found")
    # naive check: allow delete; in production ensure no transactions exist
    db.delete(acc)
    db.commit()
    return ok(message="删除成功")
