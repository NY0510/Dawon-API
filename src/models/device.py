from pydantic import BaseModel, Field
from typing import Optional, List, Any


class DeviceSchedules(BaseModel):
    enable: str = Field(default="N", description="Schedule enable status")
    setting_id: Optional[str] = Field(default=None, description="Schedule setting ID")


class DeviceSunupDown(BaseModel):
    enable: str = Field(default="N", description="Sunup/down enable status")
    setting_id: Optional[str] = Field(default=None, description="Sunup/down setting ID")


class DeviceCaution(BaseModel):
    enable: str = Field(default="N", description="Caution enable status")
    setting_id: Optional[str] = Field(default=None, description="Caution setting ID")


class DeviceProfile(BaseModel):
    display_icon: str = Field(default="", description="Display icon path")
    display_name: str = Field(default="", description="Display name")
    display_icon_name: str = Field(default="", description="Display icon name")
    icon_use_premiere: str = Field(default="N", description="Use premiere icon")
    icon_use_care: str = Field(default="N", description="Use care icon")
    extra: str = Field(default="", description="Extra info")
    schedules: DeviceSchedules = Field(default_factory=DeviceSchedules)
    sunupdown: DeviceSunupDown = Field(default_factory=DeviceSunupDown)
    caution: DeviceCaution = Field(default_factory=DeviceCaution)
    power: str = Field(default="OFF", description="Power status")
    device_ip: str = Field(default="", description="Device IP address")
    timer_enable: str = Field(default="N", description="Timer enable status")
    alarm_enable: str = Field(default="N", description="Alarm enable status")
    wait_enable: str = Field(default="N", description="Wait enable status")
    echo_enable: str = Field(default="N", description="Echo enable status")
    fee_date: str = Field(default="", description="Fee date")
    fee_stand: str = Field(default="", description="Fee standard")
    fee_kwh: str = Field(default="", description="Fee per kWh")
    over_cnt: str = Field(default="0", description="Overload count")
    short_cnt: str = Field(default="0", description="Short circuit count")
    disconnect_cnt: str = Field(default="0", description="Disconnect count")
    ssid_info: str = Field(default="", description="SSID info")
    use_fee_base: str = Field(default="N", description="Use fee base")
    max_version: str = Field(default="", description="Max firmware version")
    device_version: str = Field(default="", description="Current device version")
    fac_count: int = Field(default=0, description="Factory count")
    connect_status_alarm: str = Field(default="N", description="Connection status alarm")
    user_group_id: Optional[str] = Field(default=None, description="User group ID")
    trespass_id: str = Field(default="", description="Trespass ID")
    ecs_status: str = Field(default="", description="ECS status")
    ecs_check_log: Optional[str] = Field(default=None, description="ECS check log")
    ecs_adjust: Optional[str] = Field(default=None, description="ECS adjustment")
    gateway_id: Optional[str] = Field(default=None, description="Gateway ID")
    gateway_display_name: str = Field(default="", description="Gateway display name")
    gateway_end_count: int = Field(default=0, description="Gateway end count")
    service_no: str = Field(default="", description="Service number")
    kt_related: Optional[str] = Field(default=None, description="KT related info")
    peak_use: Optional[str] = Field(default=None, description="Peak usage")
    peak_value: Optional[str] = Field(default=None, description="Peak value")
    peak_stand: Optional[str] = Field(default=None, description="Peak standard")
    gateway_conn_status: str = Field(default="", description="Gateway connection status")
    predicted_icon: Optional[str] = Field(default=None, description="Predicted icon")
    product_hold: Optional[str] = Field(default=None, description="Product hold status")
    ai_status: str = Field(default="", description="AI status")
    operate: Optional[str] = Field(default=None, description="Operation status")
    ecs_ai_check_log: Optional[str] = Field(default=None, description="ECS AI check log")
    status_type: Optional[str] = Field(default=None, description="Status type")


class UserProfile(BaseModel):
    push_alarm: str = Field(default="N", description="Push alarm status")
    overuse: str = Field(default="N", description="Overuse status")
    user_group_id: str = Field(default="", description="User group ID")
    control_fail_alarm: str = Field(default="N", description="Control fail alarm")


class ProdInfo(BaseModel):
    prod_manu_name: Optional[str] = Field(default=None, description="Manufacturer name")
    prod_year: Optional[str] = Field(default=None, description="Production year")
    prod_model_no: Optional[str] = Field(default=None, description="Model number")
    prod_power: Optional[str] = Field(default=None, description="Power rating")
    prod_name: str = Field(default="", description="Product name")
    prod_energy_grade: Optional[str] = Field(default=None, description="Energy grade")
    label_file_name: Optional[str] = Field(default=None, description="Label file name")
    label_datauri: Optional[str] = Field(default=None, description="Label data URI")
    energyInfo: Optional[str] = Field(default=None, description="Energy info")


class IRInfo(BaseModel):
    last_status: str = Field(default="", description="Last IR status")
    std_delay: str = Field(default="", description="Standard delay")


class Device(BaseModel):
    device_id: str = Field(..., description="Unique device ID")
    ir_device_id: Optional[str] = Field(default=None, description="IR device ID")
    ir_device_name: Optional[str] = Field(default=None, description="IR device name")
    registed_time: str = Field(default="", description="Registration time")
    system_id: str = Field(default="", description="System ID")
    model_id: str = Field(default="", description="Model ID")
    is_shared: str = Field(default="N", description="Is shared")
    conn_status: str = Field(default="", description="Connection status")
    group: str = Field(default="", description="Group")
    low_group_id: Optional[str] = Field(default=None, description="Low group ID")
    device_profile: DeviceProfile = Field(default_factory=DeviceProfile)
    user_profile: UserProfile = Field(default_factory=UserProfile)
    prod_info: ProdInfo = Field(default_factory=ProdInfo)
    ir_info: IRInfo = Field(default_factory=IRInfo)
    control_confirm: str = Field(default="", description="Control confirm")
    ai_active: Optional[str] = Field(default=None, description="AI active status")
    display_icon: Optional[str] = Field(default=None, description="Display icon")


class DevicesResponse(BaseModel):
    devices: List[Device] = Field(default_factory=list, description="List of devices")
