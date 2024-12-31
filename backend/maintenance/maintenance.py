import calendar

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from backend.models import MaintenanceRequest, Car, Garage
from backend.dtos import (
    CreateMaintenanceDTO,
    UpdateMaintenanceDTO,
    ResponseMaintenanceDTO,
MonthlyRequestsReportDTO
)
from backend.database import get_db


router = APIRouter()


@router.get("/maintenance/{id}", response_model=ResponseMaintenanceDTO, tags=["Maintenance Controller"])
def get_maintenance_by_id(id: int, db: Session = Depends(get_db)):
    maintenance = (
        db.query(MaintenanceRequest)
        .filter(MaintenanceRequest.id == id)
        .first()
    )
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    car = db.query(Car).filter(Car.id == maintenance.car_id).first()
    if not car:
        raise HTTPException(
            status_code=500,
            detail=f"Associated car (ID: {maintenance.car_id}) not found.",
        )

    garage = db.query(Garage).filter(Garage.id == maintenance.garage_id).first()
    if not garage:
        raise HTTPException(
            status_code=500,
            detail=f"Associated garage (ID: {maintenance.garage_id}) not found.",
        )

    return ResponseMaintenanceDTO(
        id=maintenance.id,
        car_id=maintenance.car_id,
        carName=car.make,
        serviceType=maintenance.serviceType,
        scheduledDate=maintenance.scheduledDate,
        garage_id=maintenance.garage_id,
        garageName=garage.name,
    )

@router.put("/maintenance/{id}", response_model=ResponseMaintenanceDTO, tags=["Maintenance Controller"])
def update_maintenance(id: int, update: UpdateMaintenanceDTO, db: Session = Depends(get_db)):
    maintenance = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    car = db.query(Car).filter(Car.id == maintenance.car_id).first()
    garage = db.query(Garage).filter(Garage.id == maintenance.garage_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    for key, value in update.dict(exclude_unset=True).items():
        setattr(maintenance, key, value)

    db.commit()
    db.refresh(maintenance)

    return ResponseMaintenanceDTO(
        id=maintenance.id,
        car_id=maintenance.car_id,
        carName=car.make,
        serviceType=maintenance.serviceType,
        scheduledDate=maintenance.scheduledDate,
        garage_id=maintenance.garage_id,
        garageName=garage.name,
    )



@router.post("/maintenance/", response_model=ResponseMaintenanceDTO, tags=["Maintenance Controller"])
def create_maintenance_request(
    maintenance: CreateMaintenanceDTO, db: Session = Depends(get_db)
):
    car = db.query(Car).filter(Car.id == maintenance.carId).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    garage = db.query(Garage).filter(Garage.id == maintenance.garageId).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    if not maintenance.serviceType or not maintenance.scheduledDate:
        raise HTTPException(status_code=400, detail="Service Type and Scheduled Date cannot be empty.")

    # Create the maintenance request in the database
    maintenance_request = MaintenanceRequest(
        car_id=maintenance.carId,
        serviceType=maintenance.serviceType,
        scheduledDate=maintenance.scheduledDate,
        garage_id=maintenance.garageId,
    )

    db.add(maintenance_request)
    db.commit()
    db.refresh(maintenance_request)

    return ResponseMaintenanceDTO(
        id=maintenance_request.id,
        car_id=maintenance_request.car_id,
        carName=car.make,
        serviceType=maintenance_request.serviceType,
        scheduledDate=maintenance_request.scheduledDate,
        garage_id=maintenance_request.garage_id,
        garageName=garage.name,
    )

# DELETE /maintenance/{id}
@router.delete("/maintenance/{id}", response_model=dict, tags=["Maintenance Controller"])
def delete_maintenance(id: int, db: Session = Depends(get_db)):
    maintenance = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    db.delete(maintenance)
    db.commit()
    return {"success": True}


@router.get("/maintenance", response_model=List[ResponseMaintenanceDTO], tags=["Maintenance Controller"])
def get_maintenance_list(
        carId: int = None,
        garageId: int = None,
        startDate: str = None,
        endDate: str = None,
        db: Session = Depends(get_db)
):

    query = db.query(MaintenanceRequest)

    if carId:
        query = query.filter(MaintenanceRequest.car_id == carId)

    if garageId:
        query = query.filter(MaintenanceRequest.garage_id == garageId)

    if startDate:
        start_date = datetime.strptime(startDate, "%Y-%m-%d")
        query = query.filter(MaintenanceRequest.scheduledDate >= start_date)

    if endDate:
        end_date = datetime.strptime(endDate, "%Y-%m-%d")
        query = query.filter(MaintenanceRequest.scheduledDate <= end_date)

    maintenance_records = query.all()

    if not maintenance_records:
        raise HTTPException(status_code=404, detail="No maintenance records found")

    response_data = []
    for maintenance in maintenance_records:
        car = db.query(Car).filter(Car.id == maintenance.car_id).first()
        garage = db.query(Garage).filter(Garage.id == maintenance.garage_id).first()

        if car is None or garage is None:
            raise HTTPException(status_code=404, detail="Related car or garage not found")

        response_data.append(ResponseMaintenanceDTO(
            id=maintenance.id,
            car_id=maintenance.car_id,
            carName=car.make,
            serviceType=maintenance.serviceType,
            scheduledDate=maintenance.scheduledDate,
            garage_id=maintenance.garage_id,
            garageName=garage.name
        ))

    return response_data


@router.get("/maintenance/monthlyRequestsReport/", response_model=List[MonthlyRequestsReportDTO], tags=["Maintenance Controller"])
def get_monthly_report(
    garage_id: int = Query(...),
    start_month: str = Query(...),
    end_month: str = Query(...),
    db: Session = Depends(get_db)
):

    try:
        start_date = datetime.strptime(start_month, "%Y-%m")
        end_date = datetime.strptime(end_month, "%Y-%m")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM")

    monthly_report = []

    while start_date <= end_date:
        current_month = start_date.strftime("%Y-%m")

        year = start_date.year
        month = start_date.month
        last_day = calendar.monthrange(year, month)[1]

        end_of_month = datetime(year, month, last_day)

        num_requests = db.query(MaintenanceRequest).filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduledDate >= start_date,
            MaintenanceRequest.scheduledDate <= end_of_month
        ).count()

        # Append to the monthly_report list
        monthly_report.append(MonthlyRequestsReportDTO(month=current_month, requests=num_requests))

        start_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    return monthly_report