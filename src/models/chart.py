from pydantic import BaseModel, field_validator
from typing import List
from datetime import datetime

class ChartDataPoint(BaseModel):
  date: datetime
  value: float
  unit: str
  
  @field_validator('date', mode='before')
  @classmethod
  def parse_date(cls, v):
    if isinstance(v, str):
      # Handle "YYYY" format (year only) by adding "-01-01" to make it a valid date
      if len(v) == 4 and v.isdigit():  # "YYYY" format
        return datetime.strptime(f"{v}-01-01", "%Y-%m-%d")
      # Handle "YYYY-MM" format by adding "-01" to make it a valid date
      elif len(v) == 7 and v.count('-') == 1:  # "YYYY-MM" format
        return datetime.strptime(f"{v}-01", "%Y-%m-%d")
      # Handle other string formats
      else:
        return datetime.fromisoformat(v)
    return v

class ChartResponse(BaseModel):
  data: List[ChartDataPoint]
  old_data: List[ChartDataPoint]