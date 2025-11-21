from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import API_PREFIX
from .models import Base
from .database import engine
from .routers import auth, accounts, transactions, debts, reminders, categories, dashboard, stats, export_import

app = FastAPI(title="MeloonMoney API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create tables if not exist (will not drop)
Base.metadata.create_all(bind=engine)

api = FastAPI()

api.include_router(auth.router)
api.include_router(dashboard.router)
api.include_router(accounts.router)
api.include_router(categories.router)
api.include_router(transactions.router)
api.include_router(debts.router)
api.include_router(stats.router)
api.include_router(export_import.router)
api.include_router(reminders.router)

app.mount(API_PREFIX, api)

@app.get("/")
def root():
    return {"service": "MeloonMoney", "version": "1.0"}
