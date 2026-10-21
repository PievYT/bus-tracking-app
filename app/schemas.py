from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models import AttendanceStatus, TripStatus, UserRole

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes = True)


class SchoolCreate(BaseModel):
    name: str = Field(min_length=2, max_length= 160)
    timezone_name: str = "America/New_York"

class SchoolOut(ORMModel):
    id: UUID
    name: str
    timezone_name: str

class UserCreate(BaseModel):
    school_id: UUID
    full_name: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=3, max_length=255)
    role: UserRole

class UserOut(ORMModel):
    id: UUID
    school_id: UUID
    full_name: str
    email: str
    role: UserRole
    is_active: bool

class StudentCreate(BaseModel):
    school_id: UUID
    student_number: str = Field(min_length=1, max_length=40)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    grade_level: int | None = Field(default=None, ge=0, le=12)

class StudentOut(ORMModel):
    id: UUID
    school_id: UUID
    student_number: str
    first_name: str
    last_name: str
    grade_level: int | None
    is_active: bool

class BusCreate(BaseModel):
    school_id: UUID
    bus_number: str = Field(min_length=1, max_length=30)
    capacity: int = Field(default=60, ge=1, le=100)

class BusOut(ORMModel):
    id: UUID
    school_id: UUID
    bus_number: str
    capacity: int
    active: bool

class RouteCreate(BaseModel):
    school_id: UUID
    name: str = Field(min_length=1, max_length=120)
    direction: str = Field(default="AM", pattern="^(AM|PM)$")
    scheduled_school_arrival: str = Field(default="08:00", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")

class RouteOut(ORMModel):
    id: UUID
    school_id: UUID
    name: str
    direction: str
    scheduled_school_arrival: str
    active: bool

class RouteStopCreate(BaseModel):
    route_id: UUID
    stop_order: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    scheduled_time: str | None = None

class RouteStopOut(ORMModel):
    id: UUID
    route_id: UUID
    stop_order: int
    name: str
    latitude: float
    longitude: float
    scheduled_time: str | None

class TripCreate(BaseModel):
    route_id: UUID
    bus_id: UUID
    driver_user_id: UUID | None = None
    service_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")

class TripOut(ORMModel):
    id: UUID
    route_id: UUID
    bus_id: UUID
    driver_user_id: UUID | None
    service_date: str
    status: TripStatus

class AttendanceCreate(BaseModel):
    trip_id: UUID
    student_id: UUID
    status: AttendanceStatus
    recorded_by_user_id: UUID | None = None
    note: str | None = None

class AttendanceOut(ORMModel):
    id: UUID
    trip_id: UUID
    student_id: UUID
    status: AttendanceStatus
    recorded_by_user_id: UUID | None
    recorded_at: datetime
    note: str | None