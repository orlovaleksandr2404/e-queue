from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api.v1.services import router as services_router
from src.api.v1.tickets import router as tickets_router
from src.api.v1.auth import router as auth_router
from src.api.v1.windows import router as windows_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(services_router, prefix="/api/v1")
app.include_router(windows_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok"}
