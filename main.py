# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("- Server Start -")
    
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    
    print("- DB Connection Success -")
    
    yield
    
    await engine.dispose()
    print("- Server Close-")


app = FastAPI(
    title="Popkorn API",
    description="AI 스포일러 방지 영화 실시간 토론 플랫폼",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "popkorn-be"}