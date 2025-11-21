from sqlalchemy import Column, BigInteger, String, Enum, DECIMAL, DateTime, Text, TIMESTAMP, ForeignKey, TIME, Integer, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), default="蜜瓜用户")
    avatar_url = Column(String(255))
    language = Column(String(10), default="zh-CN")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    accounts = relationship("Account", back_populates="user", cascade="all, delete")

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    account_name = Column(String(50), nullable=False)
    account_type = Column(String(20), nullable=False)
    balance = Column(DECIMAL(15, 2), default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("User", back_populates="accounts")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    category_name = Column(String(50), nullable=False)
    category_type = Column(Enum("EXPENSE", "INCOME"), nullable=False)
    icon = Column(String(100))
    is_system = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    account_id = Column(BigInteger, ForeignKey("accounts.account_id", ondelete="RESTRICT"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.category_id", ondelete="RESTRICT"), nullable=False)

    amount = Column(DECIMAL(15, 2), nullable=False)
    transaction_type = Column(Enum("EXPENSE", "INCOME"), nullable=False)
    transaction_time = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    target_person = Column(String(50))
    summary = Column(String(100))
    note = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class Debt(Base):
    __tablename__ = "debts"
    debt_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    debt_type = Column(Enum("BORROW", "LEND"), nullable=False)
    person_name = Column(String(50), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    action_time = Column(DateTime, nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class Reminder(Base):
    __tablename__ = "reminders"
    reminder_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    event_name = Column(String(100), nullable=False)
    reminder_time = Column(TIME, nullable=False)
    frequency = Column(Enum("ONCE", "DAILY", "WEEKLY", "MONTHLY"), nullable=False, server_default="ONCE")
    note = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
