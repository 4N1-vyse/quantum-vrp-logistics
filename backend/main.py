from sqlalchemy import text
from backend.app.core.database import engine
from fastapi import FastAPI

from backend.app.api.health import router as health_router
from backend.app.api.scenarios import router as scenarios_router

app = FastAPI(
    title="RouteQ API",
    description="Backend API for the RouteQ logistics prototype",
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(scenarios_router)

@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "database": str(error)
        }
