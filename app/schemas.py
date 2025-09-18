from pydantic import BaseModel, Field
from typing import Literal

class IngestEvent(BaseModel):
    camera_id: str = Field(..., examples=["porch_cam"])
    dst_ip: str
    dst_port: int = Field(..., ge=0, le=65535)
    protocol: Literal["tcp","udp","icmp","other"] = "tcp"
    timestamp: str = Field(..., description="ISO8601 string")
