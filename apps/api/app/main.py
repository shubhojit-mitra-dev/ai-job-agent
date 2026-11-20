from fastapi import FastAPI

app = FastAPI(
    title="Career Platform API",
    description="AI-powered career discovery platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
