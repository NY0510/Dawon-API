from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from lib import DwClient
from models.device import DevicesResponse
from models.chart import ChartResponse
from models.current import CurrentDataResponse
from models.enums import Target, Metric

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = DwClient()
    await client.__aenter__()
    if not await client.login():
        await client.__aexit__(None, None, None)
        raise RuntimeError("Login failed")
    app.state.dwClient = client
    yield
    await client.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan, title="Dawon-API", description="Unofficial API for Dawon AIPM", version="1.0.0", license_info={"name": "GPL-3.0", "url": "https://www.gnu.org/licenses/gpl-3.0.en.html"})

def get_client(request: Request) -> DwClient:
    client = request.app.state.dwClient
    if client is None:
        raise HTTPException(500, "Client not initialized")
    return client

@app.get("/")
async def root():
    return {"message": "Dawon API is running"}

@app.get("/devices", response_model=DevicesResponse)
async def get_devices(dwClient: DwClient = Depends(get_client)):
    r = await dwClient.get_devices()
    if r is None:
        raise HTTPException(500, "Failed to retrieve devices")
    
    return JSONResponse(r)

@app.get("/devices/{device_id}/chart", response_model=ChartResponse)
async def get_chart_data(
    device_id: str,
    target: Target = Query(..., description="차트 데이터의 단위"),
    metric: Metric = Query(..., description="차트 데이터의 메트릭"),
    dwClient: DwClient = Depends(get_client),
):
    r = await dwClient.get_chart_data(device_id, target.value, metric.value)
    chart_data = r.get("statistic", {}).get("stat_info", [])
    chart_data_old = r.get("statistic", {}).get("stat_info_old", [])
    
    if chart_data is None:
        raise HTTPException(500, "Failed to retrieve chart data")
    
    key_mapping = {
        "n": "date",
        "sv": "value", 
        "unit": "unit"
    }
    
    def transform_chart_item(item):
        transformed = {key_mapping.get(key, key): value for key, value in item.items()}
        return transformed
      
    return ChartResponse(
        data=[transform_chart_item(item) for item in chart_data],
        old_data=[transform_chart_item(item) for item in chart_data_old]
    )

@app.get("/devices/{device_id}/current", response_model=CurrentDataResponse)
async def get_current_data(
  device_id: str,
  dwClient: DwClient = Depends(get_client),
):
    r = await dwClient.get_current_data(device_id)
    
    if r is None:
        raise HTTPException(500, "Failed to retrieve current data")
    
    return CurrentDataResponse(**r)