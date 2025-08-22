from pydantic import BaseModel
from typing import Optional, List

class DeviceSchedules(BaseModel):
    enable: str
    setting_id: Optional[str]

class DeviceSunupDown(BaseModel):
    enable: str
    setting_id: Optional[str]

class DeviceCaution(BaseModel):
    enable: str
    setting_id: Optional[str]

class DeviceProfile(BaseModel):
    display_icon: str
    display_name: str
    display_icon_name: str
    icon_use_premiere: str
    icon_use_care: str
    extra: str
    schedules: DeviceSchedules
    sunupdown: DeviceSunupDown
    caution: DeviceCaution
    power: str
    device_ip: str
    timer_enable: str
    alarm_enable: str
    wait_enable: str
    echo_enable: str
    fee_date: str
    fee_stand: str
    fee_kwh: str
    over_cnt: str
    short_cnt: str
    disconnect_cnt: str
    ssid_info: str
    use_fee_base: str
    max_version: str
    device_version: str
    fac_count: int
    connect_status_alarm: str
    user_group_id: Optional[str]
    trespass_id: str
    ecs_status: str
    ecs_check_log: Optional[str]
    ecs_adjust: Optional[str]
    gateway_id: Optional[str]
    gateway_display_name: str
    gateway_end_count: int
    service_no: str
    kt_related: Optional[str]
    peak_use: Optional[str]
    peak_value: Optional[str]
    peak_stand: Optional[str]
    gateway_conn_status: str
    predicted_icon: Optional[str]
    product_hold: Optional[str]
    ai_status: str
    operate: Optional[str]
    ecs_ai_check_log: Optional[str]
    status_type: Optional[str]

class UserProfile(BaseModel):
    push_alarm: str
    overuse: str
    user_group_id: str
    control_fail_alarm: str

class ProdInfo(BaseModel):
    prod_manu_name: Optional[str]
    prod_year: Optional[str]
    prod_model_no: Optional[str]
    prod_power: Optional[str]
    prod_name: str
    prod_energy_grade: Optional[str]
    label_file_name: Optional[str]
    label_datauri: Optional[str]
    energyInfo: Optional[str]

class IRInfo(BaseModel):
    last_status: str
    std_delay: str

class Device(BaseModel):
    device_id: str
    ir_device_id: Optional[str]
    ir_device_name: Optional[str]
    registed_time: str
    system_id: str
    model_id: str
    is_shared: str
    conn_status: str
    group: str
    low_group_id: Optional[str]
    device_profile: DeviceProfile
    user_profile: UserProfile
    prod_info: ProdInfo
    ir_info: IRInfo
    control_confirm: str
    ai_active: Optional[str]
    display_icon: Optional[str]

class DevicesResponse(BaseModel):
    devices: List[Device]