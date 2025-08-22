from pydantic import BaseModel

class CurrentDataResponse(BaseModel):
  powered: str
  current_watt: str
  monthly_kwh: str
  temperature: str