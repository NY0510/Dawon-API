from pydantic import BaseModel, Field
from typing import Optional


class CurrentDataResponse(BaseModel):
    powered: bool = Field(..., description="Device power state")
    current_watt: Optional[float] = Field(None, description="Current power consumption in watts")
    monthly_kwh: Optional[float] = Field(
        None, description="Monthly cumulative power consumption in kWh"
    )
    temperature: Optional[float] = Field(None, description="Device temperature in Celsius")
