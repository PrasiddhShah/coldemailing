from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.connection import DatabaseConnection
from app.db.schema import metadata, engine

db = DatabaseConnection()
@asynccontextmanager
async def lifespan(app: FastAPI):
    metadata.create_all(engine)
    
    await db.connect()
    yield
    await db.disconnect()

app = FastAPI(app=lifespan)