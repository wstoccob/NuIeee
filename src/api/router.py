from fastapi import APIRouter

from api.routers import admin_hackathon, auth, big_events, events, storage, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(events.router)
api_router.include_router(big_events.router)
api_router.include_router(admin_hackathon.router)
api_router.include_router(users.router)
api_router.include_router(storage.router)
