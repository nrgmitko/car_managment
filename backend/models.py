from sqlmodel import Field, SQLModel, Relationship
from typing import List
from datetime import date

# CarService Model
class CarService(SQLModel, table=True):
    __tablename__ = "carservice"
    id: int = Field(default=None, primary_key=True)
    name: str
    city: str
    capacity: int
    requests: List["MaintenanceRequest"] = Relationship(back_populates="service")
    cars: List["CarServiceLink"] = Relationship(back_populates="service")

# Car Model
class Car(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    brand: str
    model: str
    year: int
    services: List["CarServiceLink"] = Relationship(back_populates="car")
    requests: List["MaintenanceRequest"] = Relationship(back_populates="car")

# CarServiceLink Model (junction table)
class CarServiceLink(SQLModel, table=True):
    car_id: int = Field(foreign_key="car.id", primary_key=True)
    service_id: int = Field(foreign_key="carservice.id", primary_key=True)  # Corrected foreign key (reference to CarService)

    car: Car = Relationship(back_populates="services")
    service: CarService = Relationship(back_populates="cars")

# MaintenanceRequest Model
class MaintenanceRequest(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    service_id: int = Field(foreign_key="carservice.id")  # Corrected foreign key (reference to CarService)
    car_id: int = Field(foreign_key="car.id")
    date: date
    status: str

    service: CarService = Relationship(back_populates="requests")
    car: Car = Relationship(back_populates="requests")
