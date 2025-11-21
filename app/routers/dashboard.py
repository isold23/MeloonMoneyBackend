from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..deps import get_current_user
from ..database import get_db
from ..models import Account, Transaction, Category
from ..response import ok

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user=Depends(get_current_user), month: str = Query(None)):
    total_balance = db.query(func.coalesce(func.sum(Account.balance), 0)).filter(Account.user_id == user.user_id).scalar() or 0
    if not month:
        month = datetime.utcnow().strftime("%Y-%m")
    start = f"{month}-01 00:00:00"
    # naive end: next month boundary by string compare; safer use date logic, but simplified
    month_year, month_num = month.split("-")
    mn = int(month_num)
    ny = int(month_year)
    if mn == 12:
        end = f"{ny+1}-01-01 00:00:00"
    else:
        end = f"{ny}-{mn+1:02d}-01 00:00:00"
    inc = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "INCOME", Transaction.transaction_time >= start, Transaction.transaction_time < end).scalar() or 0
    exp = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "EXPENSE", Transaction.transaction_time >= start, Transaction.transaction_time < end).scalar() or 0
    recent_q = db.query(Transaction, Category.category_name, Account.account_name).join(Category, Transaction.category_id == Category.category_id).join(Account, Transaction.account_id == Account.account_id).filter(Transaction.user_id == user.user_id).order_by(Transaction.transaction_time.desc()).limit(5)
    recent = [
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
        for r in recent_q
    ]
    return ok({
        "total_balance": float(total_balance),
        "month_income": float(inc),
        "month_expense": float(exp),
        "recent_transactions": recent,
    })
