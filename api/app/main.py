from fastapi import FastAPI
from app.routers import swarm
from app.websocket import dashboard_ws

from app.routers.auth_routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CircuitSaver API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(swarm.router)
app.include_router(dashboard_ws.router)

app.include_router(auth_router)