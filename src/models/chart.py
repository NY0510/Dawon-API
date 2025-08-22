from pydantic import BaseModel
from typing import List
from datetime import datetime

class ChartDataPoint(BaseModel):
  date: datetime
  value: float
  unit: str

class ChartResponse(BaseModel):
  data: List[ChartDataPoint]
  old_data: List[ChartDataPoint]