
import httpx
import time
import django
from fastapi import status
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

@router.api_route(
    "/service/{service_id}/control", methods=["POST"], tags=["Instances"]
)
async def control_service(service_id: int, action: str):
    """Control a service instance (start, stop, restart)."""
    try:
        service = ServiceInstance.objects.get(id=service_id)
        url = f"{service.api_base_url}/{action}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
        
        if response.status_code == 200:
            return {"message": f"Service {action} executed successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to execute action.")
    
    except ServiceInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service not found.")