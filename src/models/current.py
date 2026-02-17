from pydantic import BaseModel


class CurrentDataResponse(BaseModel):
    powered: str
    current_watt: str | None = None
    monthly_kwh: str | None = None
    temperature: str | None = None
