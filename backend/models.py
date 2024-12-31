from sqlmodel import Field, SQLModel, Relationship
from typing import List
from datetime import date
from enum import Enum

from typing_extensions import Optional


# Link model for the many-to-many relationship between Car and Garage
class CarGarage(SQLModel, table=True):
    car_id: int = Field(foreign_key="car.id", primary_key=True)
    garage_id: int = Field(foreign_key="garage.id", primary_key=True)


# Enum for Maintenance Request Status
class Car(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    make: str
    model: str
    productionYear: int
    licensePlate: str

    # Many-to-many relationship with Garage
    garages: List["Garage"] = Relationship(back_populates="cars", link_model=CarGarage)

    # One-to-many relationship with MaintenanceRequest
    maintenance_requests: List["MaintenanceRequest"] = Relationship(back_populates="car")


class Garage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    location: str
    city: str
    capacity: int

    # Many-to-many relationship with Car
    cars: List["Car"] = Relationship(back_populates="garages", link_model=CarGarage)

    # One-to-many relationship with MaintenanceRequest
    maintenance_requests: List["MaintenanceRequest"] = Relationship(back_populates="garage")


class MaintenanceRequest(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    car_id: int = Field(foreign_key="car.id")
    garage_id: int = Field(foreign_key="garage.id")
    serviceType: str
    scheduledDate: date

    # One-to-many relationship with Car
    car: Car = Relationship(back_populates="maintenance_requests")

    # One-to-many relationship with Garage
    garage: Garage = Relationship(back_populates="maintenance_requests")
