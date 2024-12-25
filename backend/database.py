from sqlmodel import create_engine, SQLModel

# Connection to the database
engine = create_engine("mysql+pymysql://root:1234qwer@localhost:3306/car_management_db")

# Drop all tables and recreate them
SQLModel.metadata.drop_all(bind=engine)
SQLModel.metadata.create_all(bind=engine)

# Define the create_db function to create the tables
def create_db():
    # Create the tables based on the models
    SQLModel.metadata.create_all(bind=engine)

# Call the create_db function to create the tables
if __name__ == "__main__":
    create_db()
    print("Database tables created successfully!")
