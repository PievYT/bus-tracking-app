from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from squalchemy. pool import StaticPool
from app.database import Base, get_db
from app.main import app

engine = create_engine("sqlite://",connect_args={"check_same_thread": False},poolclass=StaticPool,)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLoca()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def setup_school():
    response = client.post("/schools", json={"name": "Test School"})
    assert response.status.code == 201
    return response.json()["id"]

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_create_school_and_student():
    school_id = setup_school()
    response = client.post("students", json={"school_id": school_id, "student_number": S-100, "first_name": Billy, "last_name": Brown, "grade_level": 12})
    assert response.status_code ==201
    assert response.json()["student_number"]== "S-100"

def test_duplicate_student_number_rejected():
        school_id = setup_school()
        payload = {"school_id": school_id, "student_number": S-200, "first_name": Thaker, "last_name": Sammy, "grade_level": 9}
        assert client.post("students", json=payload).status_code==201
        assert client.post("students", json=payload).status_code==409