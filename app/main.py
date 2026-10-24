from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app import models, schemas
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title=settings.app_name, version="0.1.0", description="BusSync Phase 1 development API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:19006",
        "http://127.0.0.1:19006",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/schools", response_model=schemas.SchoolOut, status_code=201)
def create_school(payload: schemas.SchoolCreate, db: Session =  Depends(get_db)):
    row =  models.School(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@app.get("/schools", response_model=list[schemas.SchoolOut])
def list_schools(db: Session =  Depends(get_db)):
    return db.query(models.School).order_by(models.School.name).all()

@app.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if not db.get(models.School, payload.school_id):
        raise HTTPException(404, "School not found")
    row = models.User(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "A user with this email already exists")
    db.refresh(row)
    return row

@app.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.full_name).all()

@app.post("/students", response_model=schemas.StudentOut, status_code=201)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    if not db.get(models.School, payload.school_id):
        raise HTTPException(404, "School not found")
    row = models.Student(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Student number already exists for this school")
    db.refresh(row)
    return row

@app.get("/students", response_model=list[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).filter(models.Student.is_active.is_(True)).order_by(models.Student.last_name).all()

@app.post("/buses", response_model=schemas.BusOut, status_code=201)
def create_bus(payload: schemas.BusCreate, db: Session = Depends(get_db)):
    if not db.get(models.School, payload.school_id):
        raise HTTPException(404, "School not found")
    row = models.Bus(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Bus number already exists for this school")
    db.refresh(row)
    return row

@app.get("/buses", response_model=list[schemas.BusOut])
def list_buses(db: Session = Depends(get_db)):
    return db.query(models.Bus).filter(models.Bus.active.is_(True)).order_by(models.Bus.bus_number).all()

@app.post("/routes", response_model=schemas.RouteOut, status_code=201)
def create_route(payload: schemas.RouteCreate, db: Session = Depends(get_db)):
    if not db.get(models.School, payload.school_id):
        raise HTTPException(404, "School not found")
    row = models.Route(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Route name/direction already exists for this school")
    db.refresh(row)
    return row

@app.get("/routes", response_model=list[schemas.RouteOut])
def list_routes(db: Session = Depends(get_db)):
    return db.query(models.Route).filter(models.Route.active.is_(True)).order_by(models.Route.name).all()

@app.post("/stops", response_model=schemas.RouteStopOut, status_code=201)
def create_stop(payload: schemas.RouteStopCreate, db: Session = Depends(get_db)):
    if not db.get(models.Route, payload.route_id):
        raise HTTPException(404, "Route not found")
    row = models.RouteStop(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Stop order already exists for this route")
    db.refresh(row)
    return row

@app.get("/stops", response_model=list[schemas.RouteStopOut])
def list_stops(db: Session = Depends(get_db)):
    return db.query(models.RouteStop).order_by(models.RouteStop.route_id, models.RouteStop.stop_order).all()

@app.post("/trips", response_model=schemas.TripOut, status_code=201)
def create_trip(payload: schemas.TripCreate, db: Session = Depends(get_db)):
    if not db.get(models.Route, payload.route_id):
        raise HTTPException(404, "Route not found")
    if not db.get(models.Bus, payload.bus_id):
        raise HTTPException(404, "Bus not found")
    if payload.driver_user_id and not db.get(models.User, payload.driver_user_id):
        raise HTTPException(404, "Driver user not found")
    row = models.Trip(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@app.get("/trips", response_model=list[schemas.TripOut])
def list_trips(db: Session = Depends(get_db)):
    return db.query(models.Trip).order_by(models.Trip.service_date.desc()).all()

@app.post("/attendance", response_model=schemas.AttendanceOut, status_code=201)
def create_attendance(payload: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    if not db.get(models.Trip, payload.trip_id):
        raise HTTPException(404, "Trip not found")
    if not db.get(models.Student, payload.student_id):
        raise HTTPException(404, "Student not found")
    row = models.AttendanceRecord(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Attendance already exists for this student and trip")
    db.refresh(row)
    return row

@app.get("/attendance", response_model=list[schemas.AttendanceOut])
def list_attendance(trip_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.AttendanceRecord)
    if trip_id:
        query = query.filter(models.AttendanceRecord.trip_id == trip_id)
    return query.order_by(models.AttendanceRecord.recorded_at.desc()).all()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")
