from fastapi import FastAPI
from matcher.api import router as matcher_router

app = FastAPI(
    title="Company Data API",
    version="0.1.0",
    description="Veridion tech challenge – company data matching API",
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(matcher_router, prefix="/api")

# Run with: uvicorn main:app --reload
