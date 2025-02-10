import httpx
from fastapi import HTTPException
from .schemas import APIResponse

async def proxy_request_to_service(service_id: int, processor_name: str, method: str, data: dict = None):
    """Proxy an API request to a processor running on an RTCVision instance."""
    try:
        # Validate the service instance
        service = ServiceInstance.objects.get(id=service_id)

        # Validate the processor API route
        processor_endpoint = ProcessorEndpoint.objects.filter(service_instance=service, route__contains=processor_name, is_active=True).first()
        if not processor_endpoint:
            raise HTTPException(status_code=404, detail="Processor endpoint not found.")

        url = f"{service.api_base_url}{processor_endpoint.route.replace('{processor_name}', processor_name)}"

        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            elif method == "DELETE":
                response = await client.delete(url)

        return APIResponse(status="success", message="Request forwarded successfully.", data=response.json())

    except ServiceInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
