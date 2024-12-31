from pydantic import BaseModel
from typing import List, Optional
from datetime import date


#Garages Dtos
class CreateGarageDTO(BaseModel):
    name: str
    location: str
    city: str
    capacity: int

    class Config:
        from_attributes = True

class UpdateGarageDTO(BaseModel):
    name: str
    location: str
    city: str
    capacity: int

    class Config:
        from_attributes = True

class ResponseGarageDTO(BaseModel):
    name: str
    location: str
    capacity: int
    city: str

    class Config:
        from_attributes = True

#CarDtos
class CreateCarDTO(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garageIds: List[int]  # Expecting garageIds for association

    class Config:
        from_attributes = True

class UpdateCarDTO(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garageIds: List[int]  # Expecting garageIds for association

    class Config:
        from_attributes = True

class ResponseCarDTO(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garages: List[ResponseGarageDTO]  # List of garage objects (not just ids)

    class Config:
        from_attributes = True



#Maintinance Dtos
class CreateMaintenanceDTO(BaseModel):
    garage_id: int  # Required: ID of the garage
    car_id: int  # Required: ID of the car
    serviceType: str  # Required: Type of service (e.g., Oil Change)
    scheduledDate: date  # Required: Scheduled date of the service

    class Config:
        from_attributes = True

class UpdateMaintenanceDTO(BaseModel):
    garage_id: int  # Required: ID of the garage
    car_id: int  # Required: ID of the car
    serviceType: str  # Required: Type of service (e.g., Oil Change)
    scheduledDate: date  # Required: Scheduled date of the service

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True

class ResponseMaintenanceDTO(BaseModel):
    id: int  # ID of the maintenance request
    car_id: int  # Required: ID of the car
    carName: str  # Name of the car (optional, included in the response for context)
    serviceType: str  # Type of service (e.g., Oil Change)
    scheduledDate: date  # Scheduled date of the maintenance
    garage_id: int  # Required: ID of the garage

    garageName: str  # Name of the garage (optional, included in the response for context)

    class Config:
        from_attributes = True


class MonthlyRequestsReportDTO(BaseModel):
    month: str  # The specific month (e.g., '2024-12')
    requests: int  # The number of maintenance requests in this month

    class Config:
        from_attributes = True

class DailyAvailabilityReportDTO(BaseModel):
    date: date
    availableCapacity: int

    class Config:
        from_attributes = True