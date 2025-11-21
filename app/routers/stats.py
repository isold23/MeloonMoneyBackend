from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..deps import get_current_user
from ..database import get_db
from ..models import Transaction, Category
from ..response import ok

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/report")
def report(db: Session = Depends(get_db), user=Depends(get_current_user), period_type: str = Query("MONTH"), date: str = Query(None)):
    now = datetime.utcnow()
    if period_type == "YEAR":
        year = int(date or now.strftime("%Y"))
        start = f"{year}-01-01 00:00:00"
        end = f"{year+1}-01-01 00:00:00"
        months = [f"{year}-{m:02d}" for m in range(1, 13)]
    else:
        month = date or now.strftime("%Y-%m")
        y, m = month.split("-")
        y = int(y)
        m = int(m)
        start = f"{y}-{m:02d}-01 00:00:00"
        end = f"{y+1}-01-01 00:00:00" if m == 12 else f"{y}-{m+1:02d}-01 00:00:00"
        months = [month]

    inc_total = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "INCOME", Transaction.transaction_time >= start, Transaction.transaction_time < end).scalar() or 0
    exp_total = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "EXPENSE", Transaction.transaction_time >= start, Transaction.transaction_time < end).scalar() or 0

    exp_rows = db.query(Category.category_name, func.coalesce(func.sum(Transaction.amount), 0)).join(Transaction, Transaction.category_id == Category.category_id).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "EXPENSE", Transaction.transaction_time >= start, Transaction.transaction_time < end).group_by(Category.category_name).all()
    expense_by_category = []
    for name, amount in exp_rows:
        expense_by_category.append({"category": name, "amount": float(amount), "percent": float(amount) / float(exp_total) if exp_total else 0})

    trend = []
    if period_type == "YEAR":
        for mstr in months:
            y, m = mstr.split("-")
            y = int(y)
            m = int(m)
            ms = f"{y}-{m:02d}-01 00:00:00"
            me = f"{y+1}-01-01 00:00:00" if m == 12 else f"{y}-{m+1:02d}-01 00:00:00"
            it = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "INCOME", Transaction.transaction_time >= ms, Transaction.transaction_time < me).scalar() or 0
            trend.append(float(it))
    else:
        trend = [float(inc_total)]

    return ok({
        "income_total": float(inc_total),
        "expense_total": float(exp_total),
        "expense_by_category": expense_by_category,
        "income_trend": trend,
    })

@router.post("/ai_analysis")
def ai_analysis(req: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    period = req.get("period")
    y, m = (period or datetime.utcnow().strftime("%Y-%m")).split("-")
    y = int(y); m = int(m)
    start = f"{y}-{m:02d}-01 00:00:00"
    end = f"{y+1}-01-01 00:00:00" if m == 12 else f"{y}-{m+1:02d}-01 00:00:00"
    exp_total = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "EXPENSE", Transaction.transaction_time >= start, Transaction.transaction_time < end).scalar() or 0
    rows = db.query(Category.category_name, func.coalesce(func.sum(Transaction.amount), 0)).join(Transaction, Transaction.category_id == Category.category_id).filter(Transaction.user_id == user.user_id, Transaction.transaction_type == "EXPENSE", Transaction.transaction_time >= start, Transaction.transaction_time < end).group_by(Category.category_name).order_by(func.sum(Transaction.amount).desc()).all()
    advice = ""
    if rows:
        top_cat, top_amt = rows[0]
        advice = f"本月在{top_cat}的支出最高，建议适当控制。"
    else:
        advice = "本月支出较少，保持良好习惯。"
    score = 100
    if float(exp_total) > 0:
        score = max(60, 100 - int(float(exp_total) / 1000))
    return ok({"advice_text": advice, "score": score})
