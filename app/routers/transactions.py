from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..deps import get_current_user
from ..database import get_db
from ..models import Transaction, Account, Category
from ..schemas import TransactionCreate, TransactionUpdate
from ..response import ok

router = APIRouter(prefix="/transactions", tags=["transactions"])

def apply_balance(db: Session, account_id: int, amount: float, ttype: str, reverse: bool = False):
    acc = db.query(Account).filter(Account.account_id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="account not found")
    delta = amount if ttype == "INCOME" else -amount
    if reverse:
        delta = -delta
    acc.balance = float(acc.balance) + delta

@router.post("/add")
def add_transaction(payload: TransactionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if payload.transaction_time is None:
        payload.transaction_time = datetime.utcnow()
    trx = Transaction(
        user_id=user.user_id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        amount=payload.amount,
        transaction_type=payload.type,
        transaction_time=payload.transaction_time,
        target_person=payload.target_person,
        summary=payload.summary,
        note=payload.note,
    )
    apply_balance(db, payload.account_id, payload.amount, payload.type, reverse=False)
    db.add(trx)
    db.commit()
    return ok(message="记账成功")

@router.get("/list")
def list_transactions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    start_date: str = Query(None),
    end_date: str = Query(None),
    type: str = Query(None),
    account_id: int = Query(None),
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(Transaction, Category.category_name, Account.account_name).join(Category, Transaction.category_id == Category.category_id).join(Account, Transaction.account_id == Account.account_id).filter(Transaction.user_id == user.user_id)
    if start_date:
        q = q.filter(Transaction.transaction_time >= f"{start_date} 00:00:00")
    if end_date:
        q = q.filter(Transaction.transaction_time <= f"{end_date} 23:59:59")
    if type:
        q = q.filter(Transaction.transaction_type == type)
    if account_id:
        q = q.filter(Transaction.account_id == account_id)
    total = q.count()
    rows = q.order_by(Transaction.transaction_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    data = {
        "list": [
            {
                "transaction_id": r.Transaction.transaction_id,
                "amount": float(r.Transaction.amount),
                "type": r.Transaction.transaction_type,
                "category_name": r[1],
                "account_name": r[2],
                "transaction_time": r.Transaction.transaction_time,
                "summary": r.Transaction.summary,
                "target_person": r.Transaction.target_person,
            }
            for r in rows
        ],
        "total": total,
        "current_page": page,
    }
    return ok(data)

@router.post("/update")
def update_transaction(payload: TransactionUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    trx = db.query(Transaction).filter(Transaction.transaction_id == payload.transaction_id, Transaction.user_id == user.user_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="transaction not found")
    # rollback old
    apply_balance(db, trx.account_id, float(trx.amount), trx.transaction_type, reverse=True)
    # apply changes
    if payload.amount is not None:
        trx.amount = payload.amount
    if payload.category_id is not None:
        trx.category_id = payload.category_id
    if payload.account_id is not None:
        trx.account_id = payload.account_id
    if payload.transaction_time is not None:
        trx.transaction_time = payload.transaction_time
    if payload.summary is not None:
        trx.summary = payload.summary
    if payload.target_person is not None:
        trx.target_person = payload.target_person
    if payload.note is not None:
        trx.note = payload.note
    # apply new
    apply_balance(db, trx.account_id, float(trx.amount), trx.transaction_type, reverse=False)
    db.commit()
    return ok(message="修改成功")

@router.post("/delete")
def delete_transaction(req: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    transaction_id = req.get("transaction_id")
    trx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id, Transaction.user_id == user.user_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="transaction not found")
    apply_balance(db, trx.account_id, float(trx.amount), trx.transaction_type, reverse=True)
    db.delete(trx)
    db.commit()
    return ok(message="删除成功")
