from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes_chat import router as chat_router
from api.routes_simulate import router as simulate_router
from api.routes_venue import router as venue_router
from worker.telemetry_subscriber import start_subscriber_worker
from typing import Dict

app = FastAPI(title="EventFlow AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(simulate_router, prefix="/api/v1")
app.include_router(venue_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event() -> None:
    start_subscriber_worker()

@app.get("/api/v1/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
