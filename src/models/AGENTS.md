# MODELS MODULE

**Generated:** 2025-04-02

## OVERVIEW
Pydantic schemas for API responses - device info, chart data, current status, enums.

## STRUCTURE
```
models/
├── device.py       # DeviceSchedules, DeviceProfile, Device, DevicesResponse
├── chart.py        # ChartDataPoint (with date validator), ChartResponse
├── current.py      # CurrentDataResponse (powered, current_watt, monthly_kwh, temperature)
└── enums.py        # Target (HOUR/DAY/MONTH/YEAR), Metric (POWER/FEE)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Device schema | device.py | Nested models: DeviceProfile, UserProfile, ProdInfo, IRInfo |
| Chart data | chart.py | date field_validator handles YYYY, YYYY-MM, ISO formats |
| Current status | current.py | All fields optional except powered |
| Query params | enums.py | Target/Metric for /chart endpoint |

## CONVENTIONS
- All Pydantic BaseModel
- Optional[str] for nullable fields
- List[Device] in DevicesResponse
- Field validation for date parsing in ChartDataPoint

## ANTI-PATTERNS
- No __init__.py
- device.py has many Optional[str] fields without defaults (API design)

## NOTES
- Chart date validator: adds "-01-01" for YYYY, "-01" for YYYY-MM
- All fields in CurrentDataResponse are strings (not int/float)
