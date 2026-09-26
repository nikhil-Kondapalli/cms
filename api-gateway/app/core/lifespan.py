from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.proxy.client import ProxyClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the shared HTTP client and attach it to the client
    # singleton so that it can be accessed by all other parts of
    # the application (e.g., ProxyClient)
    ProxyClient.client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=5,
            read=30,
            write=30,
            pool=30,
        )
    )

    yield

    await ProxyClient.client.aclose()
