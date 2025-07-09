import os
import time
import math
import django
import httpx
from django.db import connection
from django.db.models import Q
from fastapi import status
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Callable
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.routing import APIRoute
from pydantic import BaseModel
from commmon_utils.gateway.utils import get_instance_and_upstream, get_service_instance_per_tenant

django.setup()
from django.core.exceptions import ObjectDoesNotExist
from tenants.models import Tenant, Plant
from instances.models import ServiceInstance

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

description = """

    URL Path: /instances

    TO DO
"""

@router.api_route(
    "/instances/{tenant_id}", methods=["GET"], tags=["Instances"], description=description,
)
async def get_services(
    response: Response,
    tenant_id: str, 
    request: Request
    ):
    results = {}
    try:
        data = []
        tenant = await get_service_instance_per_tenant(tenant_id=tenant_id)
        services = tenant['service_instances']

        for service in services:
            try:
                config = await get_instance_and_upstream(service['id'], "metadata")
            except HTTPException as e:
                continue

            # Use the custom_route if defined, otherwise fallback to the default route.
            route_path = config.get("custom_route") or config.get("default_route")
            target_url = config["api_base_url"].rstrip("/") + route_path

            method = request.method
            params = dict(request.query_params)
            headers = dict(request.headers)
            body = await request.body()

            # Forward the request using HTTPX.
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.request(
                        method=method,
                        url=target_url,
                        headers=headers,
                        params=params,
                        content=body,
                        timeout=20.0
                    )
                    response.raise_for_status()

                    print(response.text)
                except httpx.HTTPError as exc:
                    raise HTTPException(status_code=502, detail=f"Error forwarding request: {exc}")

            data.append(
                {
                    **response.json(),
                    "id": service["id"],
                    "name": service['service_name'],
                    "description": service['description'],
                }
            )
                
                
        results = {
            "status_code": "ok",
            "detail": "data retrieved successfully",
            "status_description": "OK",
            "data": data
        }
        
    except ObjectDoesNotExist as e:
        results['error'] = {
            'status_code': "non-matching-query",
            'status_description': f'Matching query was not found',
            'detail': f"matching query does not exist. {e}"
        }

        response.status_code = status.HTTP_404_NOT_FOUND
        
    except HTTPException as e:
        results['error'] = {
            "status_code": "not found",
            "status_description": "Request not Found",
            "detail": f"{e}",
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
    
    except Exception as e:
        results['error'] = {
            'status_code': 'server-error',
            "status_description": "Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return results