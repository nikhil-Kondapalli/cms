from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Content Service...")

    # Startup code goes here

    yield

    # Shutdown code goes here

    print("🛑 Stopping Content Service...")
