
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.exc import OperationalError

DATABASE_URL = "mysql+pymysql://root:1234qwer@localhost:3306/car_management_db"

engine = create_engine(DATABASE_URL, echo=True)

def get_db():
    with Session(engine) as db:
        yield db
def create_db():
    try:
        print("Dropping all tables if they exist...")
        SQLModel.metadata.drop_all(bind=engine)
        print("Creating all tables...")
        SQLModel.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except OperationalError as e:
        print(f"Error occurred while interacting with the database: {e}")

if __name__ == "__main__":
    create_db()
