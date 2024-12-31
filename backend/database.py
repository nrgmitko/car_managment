
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.exc import OperationalError

# Define the database connection URL
DATABASE_URL = "mysql+pymysql://root:1234qwer@localhost:3306/car_management_db"

# Create the engine for the MySQL connection
engine = create_engine(DATABASE_URL, echo=True)  # echo=True will print SQL queries executed by SQLAlchemy

def get_db():
    with Session(engine) as db:
        yield db
# Function to drop and recreate all tables
def create_db():
    try:
        print("Dropping all tables if they exist...")
        SQLModel.metadata.drop_all(bind=engine)  # Drop tables if they exist
        print("Creating all tables...")
        SQLModel.metadata.create_all(bind=engine)  # Create tables based on your models
        print("Database tables created successfully!")
    except OperationalError as e:
        print(f"Error occurred while interacting with the database: {e}")

# Main block to create the database
if __name__ == "__main__":
    create_db()
