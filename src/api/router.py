from fastapi import APIRouter

from api.routers import auth, events, storage, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(events.router)
api_router.include_router(users.router)
api_router.include_router(storage.router)
