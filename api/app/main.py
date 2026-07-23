from fastapi import FastAPI
from app.routers import swarm

app = FastAPI(title="CircuitSaver API")

app.include_router(swarm.router)