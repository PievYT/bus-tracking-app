from datetime import date
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app import models

def main():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        school = db.query(models.School).filter_by(name="Demo High School").first()
        if not school:
            school = models.School(name="Demo High School", timezone_name="America/New_York")
            db.add(school)
            db.flush()

        admin = db.query(models.User).filter_by(email="admin@bussync.local").first()
        if not admin:
            admin = models.User(school_id=school.id, full_name="Demo Admin", email="admin@bussync.local", role=models.UserRole.ADMIN)
            db.add(admin)

        driver = db.query(models.User).filter_by(email="driver@bussync.local").first()
        if not driver:
            driver = models.User(school_id=school.id, full_name="Demo Driver", email="driver@bussync.local", role=models.UserRole.DRIVER)
            db.add(driver)
        db.flush()

        student = db.query(models.Student).filter_by(school_id=school.id, student_number="DEMO-001").first()
        if not student:
            student = models.Student(school_id=school.id, student_number="DEMO-001", first_name="Alex", last_name="Student", grade_level=10)
            db.add(student)

        bus = db.query(models.Bus).filter_by(school_id=school.id, bus_number="BUS-01").first()
        if not bus:
            bus = models.Bus(school_id=school.id, bus_number="BUS-01", capacity=60)
            db.add(bus)

        route = db.query(models.Route).filter_by(school_id=school.id, name="Route A", direction="AM").first()
        if not route:
            route = models.Route(school_id=school.id, name="Route A", direction="AM", scheduled_school_arrival="08:00")
            db.add(route)
        db.flush()

        stop = db.query(models.RouteStop).filter_by(route_id=route.id, stop_order=1).first()
        if not stop:
            stop = models.RouteStop(route_id=route.id, stop_order=1, name="Demo Stop", latitude=40.2300, longitude=-74.2800, scheduled_time="07:30")
            db.add(stop)
        db.flush()

        assignment = db.query(models.StudentStopAssignment).filter_by(student_id=student.id, route_stop_id=stop.id).first()
        if not assignment:
            db.add(models.StudentStopAssignment(student_id=student.id, route_stop_id=stop.id))

        trip = db.query(models.Trip).filter_by(route_id=route.id, bus_id=bus.id, service_date=date.today().isoformat()).first()
        if not trip:
            trip = models.Trip(route_id=route.id, bus_id=bus.id, driver_user_id=driver.id, service_date=date.today().isoformat(), status=models.TripStatus.SCHEDULED)
            db.add(trip)
        db.commit()
        print("Seed complete.")
        print("Demo school: Demo High School")
        print("Demo admin: admin@bussync.local (authentication not yet enabled)")
        print("Demo driver: driver@bussync.local (authentication not yet enabled)")
        print("Demo student number: DEMO-001")
    finally:
        db.close()

if __name__ == "__main__":
    main()
