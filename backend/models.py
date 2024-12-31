from sqlmodel import Field, SQLModel, Relationship
from typing import List
from datetime import date
from enum import Enum

from typing_extensions import Optional


class CarGarage(SQLModel, table=True):
    car_id: int = Field(foreign_key="car.id", primary_key=True)
    garage_id: int = Field(foreign_key="garage.id", primary_key=True)


class Car(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    make: str
    model: str
    productionYear: int
    licensePlate: str

    garages: List["Garage"] = Relationship(back_populates="cars", link_model=CarGarage)

    maintenance_requests: List["MaintenanceRequest"] = Relationship(back_populates="car")


class Garage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    location: str
    city: str
    capacity: int

    cars: List["Car"] = Relationship(back_populates="garages", link_model=CarGarage)

    maintenance_requests: List["MaintenanceRequest"] = Relationship(back_populates="garage")


class MaintenanceRequest(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    car_id: int = Field(foreign_key="car.id")
    garage_id: int = Field(foreign_key="garage.id")
    serviceType: str
    scheduledDate: date

    car: Car = Relationship(back_populates="maintenance_requests")

    garage: Garage = Relationship(back_populates="maintenance_requests")
