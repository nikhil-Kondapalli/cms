from fastapi import APIRouter, HTTPException, Request, Response

from app.proxy.headers import filter_request_headers, filter_response_headers
from app.proxy.router import ProxyRequest, forward_request
from app.utils.helpers import get_service

router = APIRouter()


from app.gateway.route_matcher import get_route

@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy(
    path: str,
    request: Request,
):
    route = get_route(request.method, request.url.path)
    if not route:
        raise HTTPException(
            status_code=404,
            detail="Route not found",
        )
    
    try:
        service_info = get_service(route.service)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Unknown service",
        )

    req = ProxyRequest(
        method=request.method,
        path=path,
        headers=filter_request_headers(request.headers),
        query_params=request.query_params,
        body=await request.body(),
        request_id=request.state.request_id,
        user=getattr(request.state, "user", None),
    )

    response = await forward_request(
        service=service_info,
        req=req,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=filter_response_headers(response.headers),
    )
