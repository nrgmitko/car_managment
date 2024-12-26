from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Date, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from sqlalchemy.orm import relationship

app = FastAPI(title="Car Management API", version="1.0.0")

# Database configuration
DATABASE_URL = "mysql+pymysql://root:1234qwer@localhost:3306/car_management_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Maintenance Model
class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), index=True)
    garage_id = Column(Integer, ForeignKey("garages.id"), index=True)
    service_type = Column(String(255), index=True)
    scheduled_date = Column(Date, index=True)

    # Relationships
    car = relationship("Car", back_populates="maintenances")
    garage = relationship("Garage", back_populates="maintenances")


# CarService Model
class CarService(Base):
    __tablename__ = "carservice"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    capacity = Column(Integer, nullable=False)

    # Relationships
    cars = relationship("CarServiceLink", back_populates="service")


# CarServiceLink Model
class CarServiceLink(Base):
    __tablename__ = "car_service_links"

    car_id = Column(Integer, ForeignKey("cars.id"), primary_key=True)
    service_id = Column(Integer, ForeignKey("carservice.id"), primary_key=True)

    # Relationships
    car = relationship("Car", back_populates="services")
    service = relationship("CarService", back_populates="cars")


# Car Model
class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)

    # Relationships
    maintenances = relationship("Maintenance", back_populates="car")
    services = relationship("CarServiceLink", back_populates="car")


# Garage Model
class Garage(Base):
    __tablename__ = "garages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    capacity = Column(Integer, nullable=False)

    # Relationships
    maintenances = relationship("Maintenance", back_populates="garage")


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DTO Models for Car
class CarCreateDTO(BaseModel):
    brand: str
    model: str
    year: int
    service_ids: List[int]  # List of service IDs to link cars with services

class CarUpdateDTO(BaseModel):
    brand: Optional[str]
    model: Optional[str]
    year: Optional[int]
    service_ids: Optional[List[int]]  # List of service IDs to link cars with services

class CarResponseDTO(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    services: List[int]  # List of associated service IDs

    class Config:
        orm_mode = True

# DTO Models for Garage
class GarageCreateDTO(BaseModel):
    name: str
    capacity: int

class GarageUpdateDTO(BaseModel):
    name: Optional[str]
    capacity: Optional[int]

class GarageResponseDTO(BaseModel):
    id: int
    name: str
    capacity: int

    class Config:
        orm_mode = True


# DTO Models
class ResponseMaintenanceDTO(BaseModel):
    id: int
    carId: int
    carName: str = ""  # Placeholder for car name
    serviceType: str
    scheduledDate: str
    garageId: int
    garageName: str = ""  # Placeholder for garage name

class UpdateMaintenanceDTO(BaseModel):
    carId: Optional[int]
    serviceType: Optional[str]
    scheduledDate: Optional[str]
    garageId: int

class CreateMaintenanceDTO(BaseModel):
    carId: int
    garageId: int
    serviceType: str
    scheduledDate: str

class MonthlyRequestsReportDTO(BaseModel):
    year: int
    month: int
    requestCount: int


# Car Routes
@app.post("/cars/", response_model=CarResponseDTO)
def create_car(car: CarCreateDTO, db: Session = Depends(get_db)):
    db_car = Car(**car.dict(exclude={"service_ids"}))
    db.add(db_car)
    db.commit()
    db.refresh(db_car)

    # Link services
    for service_id in car.service_ids:
        car_service_link = CarServiceLink(car_id=db_car.id, service_id=service_id)
        db.add(car_service_link)

    db.commit()
    db.refresh(db_car)

    return db_car


@app.put("/cars/{car_id}", response_model=CarResponseDTO)
def update_car(car_id: int, car: CarUpdateDTO, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    for key, value in car.dict(exclude_unset=True).items():
        setattr(db_car, key, value)

    # Update services if provided
    if car.service_ids:
        # Remove old service links
        db.query(CarServiceLink).filter(CarServiceLink.car_id == car_id).delete()
        # Add new service links
        for service_id in car.service_ids:
            car_service_link = CarServiceLink(car_id=db_car.id, service_id=service_id)
            db.add(car_service_link)

    db.commit()
    db.refresh(db_car)
    return db_car


@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Remove service links
    db.query(CarServiceLink).filter(CarServiceLink.car_id == car_id).delete()

    db.delete(db_car)
    db.commit()
    return {"message": "Car deleted successfully"}


@app.get("/cars/", response_model=List[CarResponseDTO])
def get_all_cars(brand: Optional[str] = None, service_id: Optional[int] = None, year_from: Optional[int] = None,
                 year_to: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Car)

    if brand:
        query = query.filter(Car.brand == brand)

    if service_id:
        query = query.join(CarServiceLink).filter(CarServiceLink.service_id == service_id)

    if year_from:
        query = query.filter(Car.year >= year_from)

    if year_to:
        query = query.filter(Car.year <= year_to)

    cars = query.all()
    return cars
#Garage routes
@app.post("/garages/", response_model=GarageResponseDTO)
def create_garage(garage: GarageCreateDTO, db: Session = Depends(get_db)):
    db_garage = Garage(**garage.dict())
    db.add(db_garage)
    db.commit()
    db.refresh(db_garage)
    return db_garage

@app.put("/garages/{garage_id}", response_model=GarageResponseDTO)
def update_garage(garage_id: int, garage: GarageUpdateDTO, db: Session = Depends(get_db)):
    db_garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not db_garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    for key, value in garage.dict(exclude_unset=True).items():
        setattr(db_garage, key, value)

    db.commit()
    db.refresh(db_garage)
    return db_garage


@app.delete("/garages/{garage_id}")
def delete_garage(garage_id: int, db: Session = Depends(get_db)):
    db_garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not db_garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    db.delete(db_garage)
    db.commit()
    return {"message": "Garage deleted successfully"}


@app.get("/garages/", response_model=List[GarageResponseDTO])
def get_all_garages(db: Session = Depends(get_db)):
    garages = db.query(Garage).all()
    return garages


@app.get("/garages/{garage_id}", response_model=GarageResponseDTO)
def get_garage_by_id(garage_id: int, db: Session = Depends(get_db)):
    db_garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not db_garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return db_garage


@app.get("/cars/{car_id}", response_model=CarResponseDTO)
def get_car_by_id(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car


# Maintenance routes
@app.get("/maintenance/{id}", response_model=ResponseMaintenanceDTO)
def get_maintenance_by_id(id: int = Path(..., description="The ID of the maintenance record to retrieve"), db: Session = Depends(get_db)):
    maintenance = db.query(Maintenance).filter(Maintenance.id == id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return maintenance

@app.put("/maintenance/{id}", response_model=ResponseMaintenanceDTO)
def update_maintenance(id: int, update: UpdateMaintenanceDTO, db: Session = Depends(get_db)):
    maintenance = db.query(Maintenance).filter(Maintenance.id == id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    # Check garage capacity for the new date
    if update.scheduledDate:
        date = datetime.strptime(update.scheduledDate, "%Y-%m-%d").date()
        garage_bookings = db.query(Maintenance).filter(Maintenance.garage_id == update.garageId, Maintenance.scheduled_date == date).count()
        garage = db.query(Garage).filter(Garage.id == update.garageId).first()
        if garage and garage_bookings >= garage.capacity:
            raise HTTPException(status_code=400, detail="No available capacity in the selected garage for the chosen date")

    for key, value in update.dict(exclude_unset=True).items():
        setattr(maintenance, key, value)
    db.commit()
    db.refresh(maintenance)
    return maintenance

@app.post("/maintenance", response_model=ResponseMaintenanceDTO)
def create_maintenance(new_maintenance: CreateMaintenanceDTO, db: Session = Depends(get_db)):
    date = datetime.strptime(new_maintenance.scheduledDate, "%Y-%m-%d").date()

    # Check garage capacity
    garage_bookings = db.query(Maintenance).filter(Maintenance.garage_id == new_maintenance.garageId, Maintenance.scheduled_date == date).count()
    garage = db.query(Garage).filter(Garage.id == new_maintenance.garageId).first()
    if garage and garage_bookings >= garage.capacity:
        raise HTTPException(status_code=400, detail="No available capacity in the selected garage for the chosen date")

    db_record = Maintenance(**new_maintenance.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.delete("/maintenance/{id}", response_model=dict)
def delete_maintenance(id: int, db: Session = Depends(get_db)):
    maintenance = db.query(Maintenance).filter(Maintenance.id == id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    db.delete(maintenance)
    db.commit()
    return {"success": True}

@app.get("/maintenance/monthlyRequestsReport", response_model=List[MonthlyRequestsReportDTO])
def monthly_requests_report(garage_id: int = Query(..., description="Garage ID to filter by"), start_month: str = Query(..., description="Start month in YYYY-MM format"), end_month: str = Query(..., description="End month in YYYY-MM format"), db: Session = Depends(get_db)):
    start_date = datetime.strptime(start_month + "-01", "%Y-%m-%d").date()
    end_date = datetime.strptime(end_month + "-01", "%Y-%m-%d").date()

    report = []
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month

        request_count = db.query(Maintenance).filter(
            Maintenance.garage_id == garage_id,
            func.extract("year", Maintenance.scheduled_date) == year,
            func.extract("month", Maintenance.scheduled_date) == month
        ).count()

        report.append(MonthlyRequestsReportDTO(year=year, month=month, requestCount=request_count))

        # Move to next month
        if month == 12:
            current_date = current_date.replace(year=year + 1, month=1)
        else:
            current_date = current_date.replace(month=month + 1)

    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8088)
