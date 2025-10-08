from pydantic import BaseModel
from typing import List, Optional

class WeeklyVolume(BaseModel):
    week_start: str
    runs: int
    distance_km: float
    time_minutes: float

class MonthlyVolume(BaseModel):
    month: str
    runs: int
    distance_km: float
    time_minutes: float

class CalendarDay(BaseModel):
    day: str
    date: str
    workout: str
    reason: str

class TrainingCalendar(BaseModel):
    week_of: str
    days: List[CalendarDay]

class TrainingVolumeResponse(BaseModel):
    total_activities: int
    weekly_volume: List[WeeklyVolume]
    monthly_volume: List[MonthlyVolume]
    calendar: Optional[TrainingCalendar] = None
