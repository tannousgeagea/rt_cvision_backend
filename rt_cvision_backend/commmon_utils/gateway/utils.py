

from fastapi import HTTPException
from asgiref.sync import sync_to_async
from tenants.models import Tenant, Plant
from instances.models import ServiceInstance
from upstreams.models import ServiceUpstream

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
        raise HTTPException(
            status_code=404, 
            detail=f"Upstream not found for the given service instance: {service_instance}"
            )
    
    route_path = service_upstream.custom_route or service_upstream.upstream_definition.route
    method = service_upstream.custom_method or service_upstream.upstream_definition.method
    api_base_url = service_instance.api_base_url

    return {
        "api_base_url": api_base_url,
        "default_route": route_path,
        "custom_route": None,
        "method": method,
        "id": service_instance_id,
        "name": service_instance.instance_name,
        "status": "active" if service_instance.is_active else "inactive",
        "description": service_instance.description,
    }


@sync_to_async
def get_tenant(tenant_id):
    try:
        tenant = Tenant.objects.get(tenant_id=tenant_id)
    except Tenant.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Tenant {Tenant} not found ! Existing options: {[tenant.tenant_id for tenant in Tenant.objects.all()]}",)

    return {
        "id": tenant.pk,
        "tenant_id": tenant.tenant_id,
        "tenant_name": tenant.name,
        "location": tenant.location,
        "description": tenant.description,        
    }

@sync_to_async
def get_service_instance_per_tenant(tenant_id:str):
    try:
        tenant = Tenant.objects.get(tenant_id=tenant_id)
    except Tenant.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Tenant {Tenant} not found ! Existing options: {[tenant.tenant_id for tenant in Tenant.objects.all()]}",)

    services = ServiceInstance.objects.filter(
        tenant=tenant
    )

    data = []
    for srv in services:
        data.append(
            {
                "id": srv.pk,
                "service_name": srv.instance_name,
                "status": srv.status,
                "description": srv.description,
            }
        )
    
    return {
        "id": tenant.pk,
        "tenant_id": tenant.tenant_id,
        "tenant_name": tenant.name,
        "location": tenant.location,
        "description": tenant.description,
        "service_instances": data
    }