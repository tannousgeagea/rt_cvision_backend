from pydantic import BaseModel
from typing import Optional, Dict

class ProcessorRequest(BaseModel):
    """Defines API request structure for processor endpoints."""
    method: str 
    processor_name: str
    data: Optional[Dict] = None

class ServiceControlRequest(BaseModel):
    """Defines API request structure for controlling services (start, stop, restart)."""
    action: str

class APIResponse(BaseModel):
    """Standardized API response structure."""
    status: str
    message: str
    data: Optional[Dict] = None
