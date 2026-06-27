# main.py
from fastapi import FastAPI

app = FastAPI(title="Popkorn API")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "popkorn-be"}