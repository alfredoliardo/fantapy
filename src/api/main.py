from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routers import auctions, participants
from api.ws import manager

app = FastAPI()

# Routers REST
app.include_router(auctions.router, prefix="/auctions", tags=["auctions"])
app.include_router(participants.router, prefix="/participants", tags=["participants"])

# Static frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# WebSocket router
app.include_router(manager.router, prefix="/ws", tags=["ws"])
