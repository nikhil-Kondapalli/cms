from collections.abc import Mapping
from dataclasses import dataclass

import httpx
from fastapi import HTTPException

from shared_contracts.auth.schemas import TokenClaims
from app.proxy.client import ProxyClient
from app.proxy.headers import filter_request_headers
from app.proxy.service_registry import Service


@dataclass
class ProxyRequest:
    method: str
    path: str
    headers: Mapping[str, str]
    query_params: Mapping[str, str]
    body: bytes
    request_id: str
    user: TokenClaims | None


async def forward_request(
    service: Service,
    req: ProxyRequest,
):
    url = f"{service.url}/{req.path}"

    headers = filter_request_headers(req.headers)
    headers["X-Request-ID"] = req.request_id
    if req.user is not None:
        headers["X-User-ID"] = str(req.user.sub)
        headers["X-User-Role"] = req.user.role

    try:
        client = ProxyClient.get_client()
        response = await client.request(
            method=req.method,
            url=url,
            headers=headers,
            params=req.query_params,
            content=req.body,
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway timeout")

    return response
