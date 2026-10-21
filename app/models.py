import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Enum, Float, ForeignKey, Index,
    Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DRIVER = "driver"
    PARENT = "parent"
    STUDENT = "student"

class TripStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED_LATE_BUS_DELAY = "excused_late_bus_delay"
    PENDING_REVIEW = "pending_review"

class School(Base):
    __tablename__ = "schools"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    timezone_name: Mapped[str] = mapped_column(String(80), default="America/New_York", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="school")
    students: Mapped[list["Student"]] = relationship(back_populates="school")
    buses: Mapped[list["Bus"]] = relationship(back_populates="school")
    routes: Mapped[list["Route"]] = relationship(back_populates="school")

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    school: Mapped["School"] = relationship(back_populates="users")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    student_number: Mapped[str] = mapped_column(String(40), nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    grade_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    school: Mapped["School"] = relationship(back_populates="students")
    parent_links: Mapped[list["ParentStudent"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    stop_assignments: Mapped[list["StudentStopAssignment"]] = relationship(back_populates="student")

    __table_args__ = (UniqueConstraint("school_id", "student_number", name="uq_student_school_number"),)

class ParentStudent(Base):
    __tablename__ = "parent_students"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    parent_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    relationship_label: Mapped[str] = mapped_column(String(40), default="parent", nullable=False)
    __table_args__ = (UniqueConstraint("parent_user_id", "student_id", name="uq_parent_student"),)
    student: Mapped["Student"] = relationship(back_populates="parent_links")

class Bus(Base):
    __tablename__ = "buses"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    bus_number: Mapped[str] = mapped_column(String(30), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    __table_args__ = (
        UniqueConstraint("school_id", "bus_number", name="uq_bus_school_number"),
        CheckConstraint("capacity > 0", name="ck_bus_capacity_positive"),
    )
    school: Mapped["School"] = relationship(back_populates="buses")

class Route(Base):
    __tablename__ = "routes"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), default="AM", nullable=False)
    scheduled_school_arrival: Mapped[str] = mapped_column(String(5), default="08:00", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    school: Mapped["School"] = relationship(back_populates="routes")
    stops: Mapped[list["RouteStop"]] = relationship(back_populates="route", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("school_id", "name", "direction", name="uq_route_name_direction"),)

class RouteStop(Base):
    __tablename__ = "route_stops"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), index=True)
    stop_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    scheduled_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    route: Mapped["Route"] = relationship(back_populates="stops")
    __table_args__ = (
        UniqueConstraint("route_id", "stop_order", name="uq_route_stop_order"),
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_stop_latitude"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_stop_longitude"),
    )

class StudentStopAssignment(Base):
    __tablename__ = "student_stop_assignments"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    route_stop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("route_stops.id", ondelete="CASCADE"), index=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    student: Mapped["Student"] = relationship(back_populates="stop_assignments")
    __table_args__ = (UniqueConstraint("student_id", "route_stop_id", "effective_from", name="uq_student_stop_effective"),)

class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id", ondelete="RESTRICT"), index=True)
    bus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buses.id", ondelete="RESTRICT"), index=True)
    driver_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    service_date: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[TripStatus] = mapped_column(Enum(TripStatus, native_enum=False), default=TripStatus.SCHEDULED, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (Index("ix_trip_date_status", "service_date", "status"),)

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus, native_enum=False), nullable=False)
    recorded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    __table_args__ = (UniqueConstraint("trip_id", "student_id", name="uq_attendance_trip_student"),)
