from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ..database import get_db
from ..models import Reminder
from ..schemas import ReminderCreate, ReminderUpdate
from ..response import ok

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.get("/list")
def list_reminders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Reminder).filter(Reminder.user_id == user.user_id).order_by(Reminder.reminder_id.desc()).all()
    data = [
        {
            "reminder_id": r.reminder_id,
            "event_name": r.event_name,
            "reminder_time": r.reminder_time,
            "frequency": r.frequency,
            "is_active": bool(r.is_active),
            "note": r.note,
        }
        for r in rows
    ]
    return ok(data)

@router.post("/add")
def add_reminder(payload: ReminderCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = Reminder(user_id=user.user_id, event_name=payload.event_name, reminder_time=payload.reminder_time, frequency=payload.frequency, note=payload.note)
    db.add(row)
    db.commit()
    return ok(message="设置成功")

@router.post("/update")
def update_reminder(payload: ReminderUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.query(Reminder).filter(Reminder.reminder_id == payload.reminder_id, Reminder.user_id == user.user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="reminder not found")
    if payload.event_name is not None:
        row.event_name = payload.event_name
    if payload.reminder_time is not None:
        row.reminder_time = payload.reminder_time
    if payload.frequency is not None:
        row.frequency = payload.frequency
    if payload.note is not None:
        row.note = payload.note
    if payload.is_active is not None:
        row.is_active = 1 if payload.is_active else 0
    db.commit()
    return ok(message="更新成功")

@router.post("/delete")
def delete_reminder(req: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    reminder_id = req.get("reminder_id")
    row = db.query(Reminder).filter(Reminder.reminder_id == reminder_id, Reminder.user_id == user.user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="reminder not found")
    db.delete(row)
    db.commit()
    return ok(message="删除成功")
