from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.api.docs import router as docs_router
from app.api.history import router as history_router
from app.api.external import router as external_router
from fastapi.middleware.cors import CORSMiddleware



app=FastAPI(title="Multi-Tenant RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
app.include_router(docs_router, prefix="/api/docs")
app.include_router(history_router, prefix="/api/history")

app.include_router(external_router,prefix="/api/v1/external",tags=["Universal API"])
@app.get("/")
async def root():
    return{"message":"Multi-Tenant RAG API is running"}