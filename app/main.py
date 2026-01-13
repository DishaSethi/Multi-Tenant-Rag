from fastapi import FastAPI
from app.api.endpoints import router as api_router

app=FastAPI(title="Multi-Tenant RAG API")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return{"message":"Multi-Tenant RAG API is running"}