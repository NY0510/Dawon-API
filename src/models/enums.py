from enum import Enum

class Target(Enum):
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    
class Metric(Enum):
    POWER = "power"
    FEE = "fee"
