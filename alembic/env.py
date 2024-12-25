from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from backend.models import SQLModel  # Ensure this is the correct path to your SQLModel models
import os

# Configuration setup from alembic.ini
config = context.config
fileConfig(config.config_file_name)

# Set the target metadata to SQLModel's metadata
target_metadata = SQLModel.metadata

# Set the DATABASE_URL directly in the code (no need for alembic.ini)
DATABASE_URL = "mysql+pymysql://root:1234qwer@localhost:3306/car_management_db"

def run_migrations_online():
    # Connect to the database using the DATABASE_URL defined directly in the code
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool
    )

    # Contextualize the connection and run the migrations
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Compare column types to ensure accurate migration
        )

        # Begin a transaction for the migration
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
