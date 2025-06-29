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
from django.db.models import Prefetch
from django.utils.timesince import timesince

django.setup()
from django.core.exceptions import ObjectDoesNotExist
from tenants.models import Tenant
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

    URL Path: /tenants

    TO DO
"""

@router.api_route(
    "/tenants", methods=["GET"], tags=["Tenants"], description=description,
)
def get_tenants(
    response: Response, 
    ):
    results = {}
    try:
        data = []
        tenants = Tenant.objects.prefetch_related(
            Prefetch('services', queryset=ServiceInstance.objects.all())
        ).filter(is_active=True)
        for tenant in tenants:
            data.append(
                {
                    "id": tenant.id,
                    "tenant_id": tenant.tenant_id,
                    "name": tenant.name,
                    "location": tenant.location,
                    "logo": tenant.logo_url,
                    "activeServices": tenant.services.filter(is_active=True).count(),
                    "totalServices": tenant.services.count(),
                    "status": "active" if tenant.is_active else "inactive",
                    "lastActivity": timesince(tenant.last_activity) + " ago" if tenant.last_activity else None,
                    "description": tenant.description,
                    "region": tenant.region,
                    "plan": tenant.plan,
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