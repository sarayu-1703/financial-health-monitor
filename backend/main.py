from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.health import router as health_router
from backend.routes.agent import router as agent_router

app = FastAPI(
    title="Financial Health Monitor"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/api/v1"
)

app.include_router(
    agent_router,
    prefix="/api/v1"
)