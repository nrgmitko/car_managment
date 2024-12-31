from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from backend.garage import garage
from backend.models import Car, Garage, CarGarage, MaintenanceRequest
from backend.dtos import (
    CreateCarDTO,
    UpdateCarDTO,
    ResponseCarDTO,
    DailyAvailabilityReportDTO, ResponseGarageDTO,
)
from backend.database import get_db

router = APIRouter()

# GET /cars/{id}
@router.get("/cars/{id}", response_model=ResponseCarDTO, tags=["Car Controller"])
def get_car_by_id(id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.put("/cars/{id}", response_model=ResponseCarDTO, tags=["Car Controller"])
def update_car(id: int, update: UpdateCarDTO, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    for key, value in update.dict(exclude_unset=True, exclude={"garageIds"}).items():
        setattr(car, key, value)

    if update.garageIds is not None:
        existing_garages = db.query(CarGarage).filter(CarGarage.car_id == car.id).all()
        for car_garage in existing_garages:
            db.delete(car_garage)

        for garage_id in update.garageIds:
            garage = db.get(Garage, garage_id)
            if not garage:
                raise HTTPException(status_code=404, detail=f"Garage with id {garage_id} not found")
            car_garage = CarGarage(car_id=car.id, garage_id=garage_id)
            db.add(car_garage)

    db.commit()
    db.refresh(car)

    garages = db.query(Garage).filter(Garage.id.in_(update.garageIds)).all() if update.garageIds else []

    garage_dtos = [ResponseGarageDTO.from_orm(garage) for garage in garages]

    response_data = ResponseCarDTO(
        make=car.make,
        model=car.model,
        productionYear=car.productionYear,
        licensePlate=car.licensePlate,
        garages=garage_dtos
    )

    return response_data


# DELETE /cars/{id}
@router.delete("/cars/{id}", response_model=ResponseCarDTO, tags=["Car Controller"])
def delete_car(id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    db.query(CarGarage).filter(CarGarage.car_id == id).delete()
    db.query(MaintenanceRequest).filter(MaintenanceRequest.car_id == id).delete()

    car_dto = ResponseCarDTO.from_orm(car)

    db.delete(car)
    db.commit()

    return car_dto

# GET /cars
@router.get("/cars", response_model=List[ResponseCarDTO], tags=["Car Controller"])
def get_cars(
        car_make: str = None,
        garage_id: int = None,
        from_year: int = None,
        to_year: int = None,
        db: Session = Depends(get_db)
):
    query = db.query(Car)

    if car_make:
        query = query.filter(Car.make == car_make)

    if garage_id:
        query = query.join(Car.garages).filter(Garage.id == garage_id)

    if from_year:
        query = query.filter(Car.production_year >= from_year)

    if to_year:
        query = query.filter(Car.production_year <= to_year)

    cars = query.all()

    if not cars:
        raise HTTPException(status_code=404, detail="No cars found")

    return cars


@router.post("/cars/", response_model=None, tags=["Car Controller"])
def create_car(car: CreateCarDTO, session: Session = Depends(get_db)):
    car_obj = Car(**car.dict(exclude={"garageIds"}))
    session.add(car_obj)
    session.commit()
    session.refresh(car_obj)

    for garage_id in car.garageIds:
        garage = session.get(Garage, garage_id)
        if not garage:
            raise HTTPException(status_code=404, detail=f"Garage with id {garage_id} not found")

        car_garage = CarGarage(car_id=car_obj.id, garage_id=garage_id)
        session.add(car_garage)

    session.commit()

    garages = session.query(Garage).filter(Garage.id.in_(car.garageIds)).all()

    garage_dtos = [ResponseGarageDTO.from_orm(garage) for garage in garages]

    response_data = ResponseCarDTO(
        make=car_obj.make,
        model=car_obj.model,
        productionYear=car_obj.productionYear,
        licensePlate=car_obj.licensePlate,
        garages=garage_dtos
    )

    return response_data

