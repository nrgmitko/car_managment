from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from backend.models import Garage, MaintenanceRequest
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


@router.get("/garages/dailyAvailabilityReport/", response_model=List[DailyAvailabilityReportDTO],
            tags=["Garage Controller"])
def daily_availability_report(
        garage_id: int,
        start_date: str,
        end_date: str,
        db: Session = Depends(get_db)
):
    # Parse the start and end dates
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")

    # Fetch the garage and its capacity
    garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Start with the static available capacity (before maintenance requests)
    available_capacity = garage.capacity

    # Generate the report
    report = []
    current_date = start_date
    while current_date <= end_date:
        # Query the number of maintenance requests for this specific day
        maintenance_requests_count = db.query(MaintenanceRequest).filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduledDate == current_date  # Match the date exactly
        ).count()

        # Adjust the available capacity based on the number of requests for this day
        daily_available_capacity = available_capacity - maintenance_requests_count

        # Append the report entry for this day
        report.append(DailyAvailabilityReportDTO(
            date=current_date,
            availableCapacity=daily_available_capacity
        ))

        # Move to the next day
        current_date += timedelta(days=1)

    return report