from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, time

# Auth
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    verification_code: Optional[str] = None
    language: Optional[str] = "zh-CN"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    user_id: int
    nickname: Optional[str]
    token: str

# Accounts
class AccountCreate(BaseModel):
    name: str
    type: str
    initial_balance: float = 0.0

class AccountUpdate(BaseModel):
    account_id: int
    name: Optional[str]
    balance: Optional[float]

class AccountItem(BaseModel):
    account_id: int
    name: str
    type: str
    balance: float

# Categories
class CategoryCreate(BaseModel):
    name: str
    type: str
    icon: Optional[str] = None

class CategoryUpdate(BaseModel):
    category_id: int
    name: Optional[str]
    icon: Optional[str]

class CategoryItem(BaseModel):
    category_id: int
    name: str
    type: str
    icon: Optional[str]

# Transactions
class TransactionCreate(BaseModel):
    amount: float
    type: str
    category_id: int
    account_id: int
    transaction_time: Optional[datetime]
    target_person: Optional[str]
    summary: Optional[str]
    note: Optional[str]

class TransactionUpdate(BaseModel):
    transaction_id: int
    amount: Optional[float]
    category_id: Optional[int]
    account_id: Optional[int]
    transaction_time: Optional[datetime]
    summary: Optional[str]
    target_person: Optional[str]
    note: Optional[str]

class TransactionBrief(BaseModel):
    transaction_id: int
    amount: float
    type: str
    category_name: str
    account_name: str
    transaction_time: datetime
    summary: Optional[str]
    target_person: Optional[str]

# Debts
class DebtCreate(BaseModel):
    type: str
    person_name: str
    amount: float
    action_time: datetime
    note: Optional[str]

class DebtUpdate(BaseModel):
    debt_id: int
    person_name: Optional[str]
    amount: Optional[float]
    note: Optional[str]

class DebtItem(BaseModel):
    debt_id: int
    type: str
    person_name: str
    amount: float
    action_time: datetime
    note: Optional[str]

# Reminders
class ReminderCreate(BaseModel):
    event_name: str
    reminder_time: time
    frequency: str
    note: Optional[str]

class ReminderUpdate(BaseModel):
    reminder_id: int
    event_name: Optional[str]
    reminder_time: Optional[time]
    frequency: Optional[str]
    note: Optional[str]
    is_active: Optional[bool]

class ReminderItem(BaseModel):
    reminder_id: int
    event_name: str
    reminder_time: time
    frequency: str
    is_active: bool
    note: Optional[str]

# Dashboard
class DashboardSummary(BaseModel):
    total_balance: float
    month_income: float
    month_expense: float
    recent_transactions: List[TransactionBrief]

# Stats
class StatsReportRequest(BaseModel):
    period_type: str
    date: str

class ExpenseByCategoryItem(BaseModel):
    category: str
    amount: float
    percent: float

class StatsReportResponse(BaseModel):
    income_total: float
    expense_total: float
    expense_by_category: List[ExpenseByCategoryItem]
    income_trend: List[float]

class AIAnalysisRequest(BaseModel):
    period: str

class AIAnalysisResponse(BaseModel):
    advice_text: str
    score: int
