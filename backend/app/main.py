from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import tasks, auth
from app.database import engine, Base
from app.config import settings

app = FastAPI(title="Busyness API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
