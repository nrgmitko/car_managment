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
    garageIds: List[int]

    class Config:
        from_attributes = True

class UpdateCarDTO(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garageIds: List[int]

    class Config:
        from_attributes = True

class ResponseCarDTO(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garages: List[ResponseGarageDTO]

    class Config:
        from_attributes = True



#Maintinance Dtos
class CreateMaintenanceDTO(BaseModel):
    garage_id: int
    car_id: int
    serviceType: str
    scheduledDate: date

    class Config:
        from_attributes = True

class UpdateMaintenanceDTO(BaseModel):
    garage_id: int
    car_id: int
    serviceType: str
    scheduledDate: date

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True

class ResponseMaintenanceDTO(BaseModel):
    id: int
    car_id: int
    carName: str
    serviceType: str
    scheduledDate: date
    garage_id: int

    garageName: str

    class Config:
        from_attributes = True


class MonthlyRequestsReportDTO(BaseModel):
    month: str
    requests: int

    class Config:
        from_attributes = True

class DailyAvailabilityReportDTO(BaseModel):
    date: date
    availableCapacity: int

    class Config:
        from_attributes = True