import os
import time
import math
import django
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
def get_services(
    response: Response,
    tenant_id: str, 
    ):
    results = {}
    try:
        data = []
         
        if not Tenant.objects.filter(tenant_id=tenant_id).exists():
            results = {
                "error": {
                    "status_code": "not found",
                    "status_description": f"Tenant {tenant_id} not found",
                    "detail": f"Tenant {Tenant} not found ! Existing options: {[tenant.tenant_id for tenant in Tenant.objects.all()]}",
                }
            }
            
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
        
        if not Plant.objects.filter(tenant__tenant_id=tenant_id).exists():
            results = {
                "error": {
                    "status_code": "not found",
                    "status_description": f"Plant for {tenant_id} not found",
                    "detail":f"Plant for {tenant_id} not found",
                }
            }
            
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
        
        
        plant = Plant.objects.get(
            tenant=Tenant.objects.get(
                tenant_id=tenant_id
            )
        )

        services = ServiceInstance.objects.filter(
            plant=plant
        )
        for service in services:
            data.append(
                {
                    "id": service.id,
                    "name": service.instance_name,
                    "status": "active" if service.is_active else "inactive",
                    "description": service.description,
                    "is_active": service.is_active, 
                }
            )
                
                
        results = {
            "data": data
        }
        
        results['status_code'] = "ok"
        results["detail"] = "data retrieved successfully"
        results["status_description"] = "OK"
    
        
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