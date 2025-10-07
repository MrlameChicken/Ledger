from fastapi import APIRouter

from app.api.v1.endpoints import auth, expenses, ledgers, settlements, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(ledgers.router)
api_router.include_router(expenses.router)
api_router.include_router(settlements.router)
