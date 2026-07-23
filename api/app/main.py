from fastapi import FastAPI
from app.routers import swarm
from app.websocket import dashboard_ws

app = FastAPI(title="CircuitSaver API")

app.include_router(swarm.router)
app.include_router(dashboard_ws.router)