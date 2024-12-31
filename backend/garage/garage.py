from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from backend.models import Garage
from backend.dtos import (
    CreateGarageDTO,
    UpdateGarageDTO,
    ResponseGarageDTO,
    DailyAvailabilityReportDTO,
)
from backend.database import get_db

router = APIRouter()

# GET /garages/{id}
@router.get("/garages/{id}", response_model=ResponseGarageDTO, tags=["Garage Controller"])
def get_garage_by_id(id: int, db: Session = Depends(get_db)):
    garage = db.query(Garage).filter(Garage.id == id).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return garage


# PUT /garages/{id}
@router.put("/garages/{id}", response_model=ResponseGarageDTO, tags=["Garage Controller"])
def update_garage(id: int, update: UpdateGarageDTO, db: Session = Depends(get_db)):
    garage = db.query(Garage).filter(Garage.id == id).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Update garage record
    for key, value in update.dict(exclude_unset=True).items():
        setattr(garage, key, value)

    db.commit()
    db.refresh(garage)
    return garage


# DELETE /garages/{id}
@router.delete("/garages/{id}", response_model=dict, tags=["Garage Controller"])
def delete_garage(id: int, db: Session = Depends(get_db)):
    garage = db.query(Garage).filter(Garage.id == id).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    db.delete(garage)
    db.commit()
    return {"success": True}


# GET /garages
@router.get("/garages", response_model=List[ResponseGarageDTO], tags=["Garage Controller"])
def get_garages(city: str = None, db: Session = Depends(get_db)):
    query = db.query(Garage)

    if city:
        query = query.filter(Garage.city == city)

    garages = query.all()

    if not garages:
        raise HTTPException(status_code=404, detail="No garages found")

    return garages


# POST /garages
@router.post("/garages", response_model=ResponseGarageDTO, tags=["Garage Controller"])
def create_garage(new_garage: CreateGarageDTO, db: Session = Depends(get_db)):
    db_record = Garage(**new_garage.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


# GET /garages/dailyAvailabilityReport
@router.get("/garages/dailyAvailabilityReport", response_model=List[DailyAvailabilityReportDTO], tags=["Garage Controller"])
def daily_availability_report(
        garage_id: int,
        start_date: str,
        end_date: str,
        db: Session = Depends(get_db)
):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    report = []
    current_date = start_date
    while current_date <= end_date:
        available_capacity = db.query(Garage).filter(Garage.id == garage_id).first().capacity
        report.append(DailyAvailabilityReportDTO(date=current_date, availableCapacity=available_capacity))

        current_date += timedelta(days=1)

    return report
