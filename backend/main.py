from fastapi import FastAPI

app = FastAPI(
    title="RouteQ API",
    description="Backend API for the RouteQ logistics prototype",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": "RouteQ"
    }
