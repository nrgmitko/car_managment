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
    # Fetch the car to update
    car = db.query(Car).filter(Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Update car fields (excluding garageIds)
    for key, value in update.dict(exclude_unset=True, exclude={"garageIds"}).items():
        setattr(car, key, value)

    # Update the garages if garageIds are provided in the request
    if update.garageIds is not None:
        # Remove old associations (if any)
        existing_garages = db.query(CarGarage).filter(CarGarage.car_id == car.id).all()
        for car_garage in existing_garages:
            db.delete(car_garage)

        # Add new associations
        for garage_id in update.garageIds:
            garage = db.get(Garage, garage_id)
            if not garage:
                raise HTTPException(status_code=404, detail=f"Garage with id {garage_id} not found")
            # Create the association between the car and the garage
            car_garage = CarGarage(car_id=car.id, garage_id=garage_id)
            db.add(car_garage)

    # Commit the changes to the database
    db.commit()
    db.refresh(car)

    # Fetch the updated garages
    garages = db.query(Garage).filter(Garage.id.in_(update.garageIds)).all() if update.garageIds else []

    # Create the ResponseGarageDTO objects for the updated garages
    garage_dtos = [ResponseGarageDTO.from_orm(garage) for garage in garages]

    # Prepare the response data
    response_data = ResponseCarDTO(
        make=car.make,
        model=car.model,
        productionYear=car.productionYear,
        licensePlate=car.licensePlate,
        garages=garage_dtos  # Attach the garages as DTOs
    )

    # Return the updated car object with associated garages
    return response_data


# DELETE /cars/{id}
@router.delete("/cars/{id}", response_model=ResponseCarDTO, tags=["Car Controller"])
def delete_car(id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Optionally delete related entries (CarGarage, MaintenanceRequest)
    db.query(CarGarage).filter(CarGarage.car_id == id).delete()
    db.query(MaintenanceRequest).filter(MaintenanceRequest.car_id == id).delete()

    # Create a DTO response for the car before deletion
    car_dto = ResponseCarDTO.from_orm(car)

    db.delete(car)
    db.commit()

    # Return the car's information before it was deleted
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
    # Create the Car instance (without `garageIds`)
    car_obj = Car(**car.dict(exclude={"garageIds"}))  # Exclude garageIds while creating the car
    session.add(car_obj)
    session.commit()  # Commit to get the ID assigned
    session.refresh(car_obj)

    # Now associate the car with the garages based on garageIds
    for garage_id in car.garageIds:
        # Ensure the garage exists
        garage = session.get(Garage, garage_id)
        if not garage:
            raise HTTPException(status_code=404, detail=f"Garage with id {garage_id} not found")

        # Create the CarGarage entry to associate the car with the garage
        car_garage = CarGarage(car_id=car_obj.id, garage_id=garage_id)
        session.add(car_garage)

    session.commit()  # Commit the associations

    # Fetch the associated garages
    garages = session.query(Garage).filter(Garage.id.in_(car.garageIds)).all()

    # Create the ResponseGarageDTO objects
    garage_dtos = [ResponseGarageDTO.from_orm(garage) for garage in garages]

    # Ensure all fields in ResponseCarDTO are populated
    response_data = ResponseCarDTO(
        make=car_obj.make,
        model=car_obj.model,
        productionYear=car_obj.productionYear,
        licensePlate=car_obj.licensePlate,
        garages=garage_dtos  # Attach the garages as DTOs
    )

    # Return the car object with the associated garages
    return response_data

