from enum import Enum

class Target(Enum):
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
class Metric(Enum):
    POWER = "power"
    FEE = "fee"
