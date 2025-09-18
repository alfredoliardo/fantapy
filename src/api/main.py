import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routers import auctions
# Path assoluto basato sulla posizione di questo file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if not os.path.exists(FRONTEND_DIR):
    raise RuntimeError(f"Frontend directory not found: {FRONTEND_DIR}")

app = FastAPI()

# Routers
app.include_router(auctions.router, prefix="/auctions", tags=["auctions"])

# Static frontend
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")