from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.connection import DatabaseConnection
from app.db.schema import metadata, engine
from app.api.apollo import apollo

db = DatabaseConnection()
@asynccontextmanager
async def lifespan(app: FastAPI):
    metadata.create_all(engine)
    
    await db.connect()
    yield
    await db.disconnect()

app = FastAPI(app=lifespan)
app.include_router(apollo)