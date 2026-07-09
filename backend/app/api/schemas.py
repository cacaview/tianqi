"""
请求/响应数据模型 (DTO)
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.constants import (
    MAX_CHAT_MESSAGE_LENGTH,
)

# ── 通用响应 ──


class ErrorResponse(BaseModel):
    """统一错误响应"""

    error: str
    detail: str | None = None
    code: str | None = None


# ── 天气 ──


class WeatherCurrentResponse(BaseModel):
    """当前天气响应"""

    temperature: float | None = None
    feels_like: float | None = None
    humidity: float | None = None
    precipitation: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    weather_code: int | None = None
    timezone: str | None = None
    latitude: float
    longitude: float


class ForecastDay(BaseModel):
    """单日预报"""

    date: str
    weather_code: int | None = None
    temp_max: float | None = None
    temp_min: float | None = None
    precipitation: float | None = None
    precipitation_probability: int | None = None
    wind_speed_max: float | None = None


class WeatherForecastResponse(BaseModel):
    """天气预报响应"""

    latitude: float
    longitude: float
    timezone: str | None = None
    forecast: list[ForecastDay] = []


class MinutelyPrecipitationPoint(BaseModel):
    """分钟级降水数据点"""

    time: str
    precipitation_mm: float


class MinutelyPrecipitationResponse(BaseModel):
    """分钟级降水预报响应"""

    latitude: float
    longitude: float
    timezone: str | None = None
    minutely_15: list[MinutelyPrecipitationPoint] = []


class LifestyleIndex(BaseModel):
    """生活指数项"""

    name: str
    name_zh: str
    level: str
    level_zh: str
    description: str
    icon: str | None = None


class LifestyleIndicesResponse(BaseModel):
    """生活指数响应"""

    latitude: float
    longitude: float
    timezone: str | None = None
    language: str = "zh"
    indices: list[LifestyleIndex] = []
    generated_by: str = "rules"


# ── 空气质量 ──


class AirQualityCurrent(BaseModel):
    """当前空气质量"""

    pm2_5: float | None = None
    pm10: float | None = None
    no2: float | None = None
    co: float | None = None
    so2: float | None = None
    o3: float | None = None
    us_aqi: float | None = None
    european_aqi: float | None = None


class AirQualityForecastDay(BaseModel):
    """空气质量预报单日"""

    date: str
    pm2_5: float | None = None
    pm10: float | None = None
    o3: float | None = None
    us_aqi: float | None = None


class AirQualityCurrentResponse(BaseModel):
    """当前空气质量响应"""

    latitude: float
    longitude: float
    timezone: str | None = None
    current: AirQualityCurrent


class AirQualityForecastResponse(BaseModel):
    """空气质量预报响应"""

    latitude: float
    longitude: float
    timezone: str | None = None
    forecast: list[AirQualityForecastDay] = []


# ── 对话 ──


class ChatRequest(BaseModel):
    """对话请求"""

    message: str = Field(
        ...,
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_LENGTH,
        description="用户消息",
    )
    language: str = Field(
        default="zh",
        description="语言代码",
        pattern="^(zh|en|vi|th|id|my|lo)$",
    )
    latitude: float | None = Field(None, ge=-90, le=90, description="纬度")
    longitude: float | None = Field(None, ge=-180, le=180, description="经度")
    session_id: str | None = Field(None, max_length=128, description="会话ID")


class ChatResponse(BaseModel):
    """对话响应"""

    reply: str
    language: str
    tools_used: list[str] = []


# ── 灾害预警 ──


class AlertResponse(BaseModel):
    """预警信息"""

    id: str
    type: str
    type_name: str
    level: str
    level_name: str
    title: str
    content: str
    start_time: str
    end_time: str
    affected_areas: list[str] = []
    recommendations: list[str] = []
    source: str


class AlertSummaryResponse(BaseModel):
    """预警汇总"""

    total: int
    by_level: dict[str, int] = {}
    by_type: dict[str, int] = {}
    alerts: list[AlertResponse] = []
    update_time: str


class TyphoonResponse(BaseModel):
    """台风信息"""

    id: str
    name: str
    code: str
    status: str
    position: dict
    intensity: str
    max_wind_speed: float
    pressure: float
    move_direction: str | None = None
    move_speed: float | None = None
    forecast_track: list[dict] = []
    impact_regions: list[str] = []
    source: str


class FourStageWarningResponse(BaseModel):
    """递进式四阶段预警"""

    disaster_id: str
    disaster_type: str
    disaster_name: str
    current_stage: str
    stages: dict
    update_time: str


# ── 地震预警 ──


class EarthquakeResponse(BaseModel):
    """地震信息"""

    id: str
    source: str
    hypocenter: str
    magnitude: float
    max_intensity: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    depth_km: float | None = None
    occurred_at: str | None = None
    url: str | None = None


class EarthquakeListResponse(BaseModel):
    """地震列表响应"""

    earthquakes: list[EarthquakeResponse] = []
    total: int = 0
    update_time: str = ""


class EEWAlertResponse(BaseModel):
    """地震预警 (EEW) 响应"""

    id: str
    source: str
    hypocenter: str
    magnitude: float
    expected_max_intensity: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    depth_km: float | None = None
    alert_time: str | None = None
    is_cancelled: bool = False


class WeatherReportResponse(BaseModel):
    """天气报告响应"""

    report: str
    language: str = "zh"
    location: str | None = None
    generated_by: str = "rules"


# ── 健康指数 ──


class HealthIndexComponent(BaseModel):
    """健康指数单项评分"""

    name: str
    name_zh: str
    score: float
    weight: float
    description: str


class HealthIndexResponse(BaseModel):
    """健康指数响应"""

    latitude: float
    longitude: float
    score: float
    level: str
    level_zh: str
    components: list[HealthIndexComponent] = []
    recommendation: str
    language: str = "zh"


# ── 建筑安全 ──


class SafetyFactor(BaseModel):
    """安全因子"""

    name: str
    name_zh: str
    status: str  # go / no_go / caution
    value: float | None = None
    threshold: float | None = None
    unit: str | None = None
    detail: str


class ConstructionSafetyResponse(BaseModel):
    """建筑安全评估响应"""

    latitude: float
    longitude: float
    overall_decision: str  # go / no_go / caution
    overall_decision_zh: str
    factors: list[SafetyFactor] = []
    description: str
    language: str = "zh"


# ── 气象日记 ──


class JournalCreateRequest(BaseModel):
    """创建日记请求"""

    user_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    feelings: str | None = None
    mood: str | None = None
    language: str = "zh"


class JournalEntryResponse(BaseModel):
    """日记条目响应"""

    id: int
    user_id: int
    latitude: float
    longitude: float
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    precipitation: float | None = None
    weather_code: int | None = None
    feelings: str | None = None
    mood: str | None = None
    language: str = "zh"
    created_at: str | None = None


class JournalListResponse(BaseModel):
    """日记列表响应"""

    entries: list[JournalEntryResponse] = []
    total: int = 0


class JournalReviewStats(BaseModel):
    """气候回顾统计"""

    total_entries: int
    avg_temperature: float
    max_temperature: float
    min_temperature: float
    total_precipitation: float


class JournalReviewResponse(BaseModel):
    """气候回顾响应"""

    user_id: int
    period: str
    review: str | None = None
    message: str | None = None
    stats: JournalReviewStats | None = None
    language: str = "zh"


# ── 天气播报 ──


class SubscriptionRequest(BaseModel):
    """订阅请求"""

    channel: str  # telegram/whatsapp/email
    recipient: str
    latitude: float | None = None
    longitude: float | None = None
    city_name: str | None = None
    language: str = "zh"
    broadcast_time: str = "07:00"


class SubscriptionResponse(BaseModel):
    """订阅响应"""

    channel: str
    recipient: str
    message: str


class BroadcastResponse(BaseModel):
    """播报响应"""

    message: str
    channels: list[str] = []
    language: str = "zh"


# ── 海事 ──


class RouteCheckpoint(BaseModel):
    """航线检查点"""

    name: str
    latitude: float | None = None
    longitude: float | None = None
    wave_height: float = 0
    decision: str


class RouteRiskResponse(BaseModel):
    """航线风险响应"""

    overall_decision: str
    origin: dict
    destination: dict
    checkpoints: list[RouteCheckpoint] = []
    language: str = "zh"


class MarineConditionResponse(BaseModel):
    """海况响应"""

    latitude: float
    longitude: float
    timezone: str | None = None
    wave_height: float | None = None
    wave_direction: float | None = None
    wave_period: float | None = None
    wind_wave_height: float | None = None
    wind_wave_direction: float | None = None
    wind_wave_period: float | None = None


# ── 能源预测 ──


class SolarForecastDay(BaseModel):
    """太阳能发电预测单日"""

    date: str
    estimated_radiation_wm2: float = 0
    temperature_factor: float = 1.0
    daily_output_kwh: float = 0
    weather_code: int | None = None


class SolarForecastResponse(BaseModel):
    """太阳能发电预测响应"""

    latitude: float
    longitude: float
    capacity_kw: float = 10.0
    efficiency: float = 0.17
    forecast: list[SolarForecastDay] = []


class WindPowerForecastDay(BaseModel):
    """风力发电预测单日"""

    date: str
    wind_speed_kmh: float = 0
    power_ratio: float = 0
    daily_output_kwh: float = 0


class WindPowerForecastResponse(BaseModel):
    """风力发电预测响应"""

    latitude: float
    longitude: float
    rated_power_kw: float = 100.0
    forecast: list[WindPowerForecastDay] = []


# ── 农业决策 ──


class AgroIrrigationResponse(BaseModel):
    """灌溉建议响应"""

    latitude: float
    longitude: float
    estimated_soil_moisture: float | None = None
    irrigation_needed: bool | None = None
    advice: str
    language: str = "zh"


class AgroPestRiskResponse(BaseModel):
    """病虫害风险响应"""

    latitude: float
    longitude: float
    temperature: float = 0
    humidity: float = 0
    risk_level: str = "low"
    language: str = "zh"


class AgroHarvestWindowResponse(BaseModel):
    """收获窗口响应"""

    latitude: float
    longitude: float
    best_window: list[str] = []
    dry_days: int = 0
    advice: str
    language: str = "zh"


# ── 众包观测 ──


class ObservationRequest(BaseModel):
    """观测提交请求"""

    user_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    weather_type: str
    description: str | None = None
    photo_url: str | None = None
    temperature: float | None = None
    language: str = "zh"


class ObservationResponse(BaseModel):
    """观测响应"""

    id: int
    user_id: int
    latitude: float
    longitude: float
    weather_type: str
    description: str | None = None
    photo_url: str | None = None
    temperature: float | None = None
    language: str = "zh"
    created_at: str | None = None


class ObservationListResponse(BaseModel):
    """观测列表响应"""

    observations: list[ObservationResponse] = []
    total: int = 0


# ── 保险指数 ──


class InsuranceTrigger(BaseModel):
    """保险触发条件"""

    type: str
    type_zh: str
    threshold: float
    metric: str
    operator: str
    description: str


class InsuranceTriggerResponse(BaseModel):
    """保险触发条件响应"""

    latitude: float
    longitude: float
    crop_type: str = "rice"
    policy_period_days: int = 90
    triggers: list[InsuranceTrigger] = []
    baseline: dict | None = None
    language: str = "zh"


class InsuranceRiskProfileResponse(BaseModel):
    """保险风险画像响应"""

    latitude: float
    longitude: float
    crop_type: str = "rice"
    risk_profile: dict | None = None
    language: str = "zh"


# ── 跨境灾害 ──


class CorrelationEvent(BaseModel):
    """关联事件"""

    type: str
    type_zh: str
    severity: str = "moderate"
    regions: list[str] = []
    magnitude: float | None = None
    location: str | None = None
    description: str | None = None


class CrossBorderCorrelateResponse(BaseModel):
    """跨境灾害关联响应"""

    time_window_hours: int = 48
    regions_with_alerts: list[str] = []
    total_alerts: int = 0
    correlations: list[CorrelationEvent] = []
    earthquake_count: int = 0
    language: str = "zh"


class ImpactChainStage(BaseModel):
    """影响链阶段"""

    stage: int
    event: str
    impact: str


class ImpactChainResponse(BaseModel):
    """灾害影响链响应"""

    disaster_type: str
    impact_chain: list[ImpactChainStage] = []
    language: str = "zh"


# ── 烟霾监测 ──


class FireHotspotResponse(BaseModel):
    """火点热点响应"""

    region: str
    data: str | None = None
    hotspots: list[dict] = []
    message: str | None = None
    mock: bool = True


class HazeLevelResponse(BaseModel):
    """烟霾等级响应"""

    latitude: float
    longitude: float
    us_aqi: float = 0
    haze_level: str = "good"
    haze_level_zh: str = "优"
    language: str = "zh"


# ── 照片墙 ──


class PhotoUploadResponse(BaseModel):
    """照片上传响应"""

    id: int
    user_id: int
    latitude: float
    longitude: float
    photo_url: str
    weather_type: str = "unknown"
    description: str | None = None
    language: str = "zh"


class PhotoListResponse(BaseModel):
    """照片列表响应"""

    photos: list[dict] = []
    total: int = 0
    latitude: float | None = None
    longitude: float | None = None


# ── 互助圈 ──


class MutualAidCreateRequest(BaseModel):
    """创建互助请求"""

    user_id: int
    request_type: str  # help/offer
    category: str  # food/water/shelter/medical/transport/other
    description: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    language: str = "zh"


class MutualAidResponse(BaseModel):
    """互助请求响应"""

    id: int
    user_id: int
    request_type: str
    category: str
    description: str
    latitude: float
    longitude: float
    status: str = "open"
    language: str = "zh"
    created_at: str | None = None


class MutualAidListResponse(BaseModel):
    """互助请求列表响应"""

    requests: list[MutualAidResponse] = []
    total: int = 0


class MutualAidMatchResponse(BaseModel):
    """互助匹配响应"""

    request_id: int
    status: str = "matched"
    responder_id: int


# ── 企业API ──


class V1WeatherResponse(BaseModel):
    """企业API天气响应"""

    data: dict | None = None
    error: str | None = None


class V1AirQualityResponse(BaseModel):
    """企业API空气质量响应"""

    data: dict | None = None
    error: str | None = None


class V1UsageResponse(BaseModel):
    """企业API使用量响应"""

    api_key_prefix: str
    requests_this_minute: int = 0
