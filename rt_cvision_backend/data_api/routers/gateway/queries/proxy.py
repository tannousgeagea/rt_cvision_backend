
import os
import time
import django
django.setup()
from typing import Callable
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.routing import APIRoute
from asgiref.sync import sync_to_async
from fastapi import FastAPI, Request, Depends, Response
import httpx

from instances.models import ServiceInstance
from upstreams.models import ServiceUpstream

class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler
    

router = APIRouter(
    route_class=TimedRoute,
)

@sync_to_async
def get_instance_and_upstream(service_instance_id: str, upstream_name: str) -> dict:
    """
    Retrieves the ServiceInstance and its associated ServiceUpstream configuration
    from the database.
    """
    try:
        service_instance = ServiceInstance.objects.get(pk=service_instance_id)
    except ServiceInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service instance not found")
    
    try:
        service_upstream = service_instance.upstreams.get(
            upstream_definition__name=upstream_name,
            is_active=True
        )
    except ServiceUpstream.DoesNotExist:
        raise HTTPException(status_code=404, detail="Upstream not found for the given service instance")
    
    route_path = service_upstream.custom_route or service_upstream.upstream_definition.route
    method = service_upstream.custom_method or service_upstream.upstream_definition.method
    api_base_url = service_instance.api_base_url

    return {
        "api_base_url": api_base_url,
        "default_route": route_path,
        "custom_route": None,
        "method": method
    }

@router.api_route(
    "/gateway/{service_instance_id}/{upstream_name}", methods=["GET", "POST", "PUT", "DELETE"], tags=['Gateway'])
async def proxy_request(service_instance_id: str, upstream_name: str, request: Request):
    try:
        config = await get_instance_and_upstream(service_instance_id, upstream_name)
    except HTTPException as e:
        raise e

    # Use the custom_route if defined, otherwise fallback to the default route.
    route_path = config.get("custom_route") or config.get("default_route")
    target_url = config["api_base_url"].rstrip("/") + route_path

    # Extract method, query parameters, headers, and body from the incoming request.

    print(request.method)

    method = request.method
    params = dict(request.query_params)
    headers = dict(request.headers)
    body = await request.body()


    print(body)
    # Forward the request using HTTPX.
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                params=params,
                content=body,
                timeout=10.0
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Error forwarding request: {exc}")

    return response.json()

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv('DATA_API_PORT')), log_level="debug", reload=True)