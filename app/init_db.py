from app.database import Base, engine
from app import models  # noqa: F401

def main():
    Base.metadata.create_all(bind=engine)
    print("BusSync database tables created.")

if __name__ == "__main__":
    main()
