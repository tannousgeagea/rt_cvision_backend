from pydantic import BaseModel
from typing import Optional, Dict

class ProcessorRequest(BaseModel):
    """Defines API request structure for processor endpoints."""
    method: str  # HTTP method (GET, POST, etc.)
    processor_name: str  # Name of the processor
    data: Optional[Dict] = None  # Optional JSON payload for the request

class ServiceControlRequest(BaseModel):
    """Defines API request structure for controlling services (start, stop, restart)."""
    action: str  # Example: "start", "stop", "restart"

class APIResponse(BaseModel):
    """Standardized API response structure."""
    status: str
    message: str
    data: Optional[Dict] = None
