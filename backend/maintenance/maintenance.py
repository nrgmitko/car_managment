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
    # Query the maintenance request by ID
    maintenance = (
        db.query(MaintenanceRequest)
        .filter(MaintenanceRequest.id == id)
        .first()
    )
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    # Fetch related car and garage details
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

    # Construct and return the response
    return ResponseMaintenanceDTO(
        id=maintenance.id,
        car_id=maintenance.car_id,
        carName=car.make,  # Using the `make` field from the Car model
        serviceType=maintenance.serviceType,
        scheduledDate=maintenance.scheduledDate,
        garage_id=maintenance.garage_id,
        garageName=garage.name,  # Using the `name` field from the Garage model
    )

@router.put("/maintenance/{id}", response_model=ResponseMaintenanceDTO, tags=["Maintenance Controller"])
def update_maintenance(id: int, update: UpdateMaintenanceDTO, db: Session = Depends(get_db)):
    # Fetch the maintenance record
    maintenance = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    # Fetch the related car and garage for response purposes
    car = db.query(Car).filter(Car.id == maintenance.car_id).first()
    garage = db.query(Garage).filter(Garage.id == maintenance.garage_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Update the maintenance record with the new data from the UpdateMaintenanceDTO
    for key, value in update.dict(exclude_unset=True).items():
        setattr(maintenance, key, value)

    # Commit the changes to the database
    db.commit()
    db.refresh(maintenance)

    # Construct and return the response
    return ResponseMaintenanceDTO(
        id=maintenance.id,
        car_id=maintenance.car_id,
        carName=car.make,  # Using the `make` field from the Car model
        serviceType=maintenance.serviceType,
        scheduledDate=maintenance.scheduledDate,
        garage_id=maintenance.garage_id,
        garageName=garage.name,  # Using the `name` field from the Garage model
    )



@router.post("/maintenance/", response_model=ResponseMaintenanceDTO, tags=["Maintenance Controller"])
def create_maintenance_request(
    maintenance: CreateMaintenanceDTO, db: Session = Depends(get_db)
):
    # Validate if the car exists
    car = db.query(Car).filter(Car.id == maintenance.carId).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Validate if the garage exists
    garage = db.query(Garage).filter(Garage.id == maintenance.garageId).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Ensure that maintenance fields are not None
    if not maintenance.serviceType or not maintenance.scheduledDate:
        raise HTTPException(status_code=400, detail="Service Type and Scheduled Date cannot be empty.")

    # Create the maintenance request in the database
    maintenance_request = MaintenanceRequest(
        car_id=maintenance.carId,
        serviceType=maintenance.serviceType,
        scheduledDate=maintenance.scheduledDate,
        garage_id=maintenance.garageId,
    )

        # Add to the DB session and commit
    db.add(maintenance_request)
    db.commit()
    db.refresh(maintenance_request)  # Refresh to get the ID and other auto-generated fields

    # Return the response with car and garage names
    # Construct the response object explicitly
    return ResponseMaintenanceDTO(
        id=maintenance_request.id,
        car_id=maintenance_request.car_id,
        carName=car.make,  # Using the `make` field from the Car model
        serviceType=maintenance_request.serviceType,
        scheduledDate=maintenance_request.scheduledDate,
        garage_id=maintenance_request.garage_id,
        garageName=garage.name,  # Using the `name` field from the Garage model
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
    # Start the query for maintenance records
    query = db.query(MaintenanceRequest)

    # Filter by carId if provided
    if carId:
        query = query.filter(MaintenanceRequest.car_id == carId)

    # Filter by garageId if provided
    if garageId:
        query = query.filter(MaintenanceRequest.garage_id == garageId)

    # Filter by startDate if provided
    if startDate:
        start_date = datetime.strptime(startDate, "%Y-%m-%d")
        query = query.filter(MaintenanceRequest.scheduledDate >= start_date)

    # Filter by endDate if provided
    if endDate:
        end_date = datetime.strptime(endDate, "%Y-%m-%d")
        query = query.filter(MaintenanceRequest.scheduledDate <= end_date)

    # Fetch maintenance records based on the filters
    maintenance_records = query.all()

    # If no records found, raise a 404 error
    if not maintenance_records:
        raise HTTPException(status_code=404, detail="No maintenance records found")

    # Create a list of ResponseMaintenanceDTOs for each maintenance record
    response_data = []
    for maintenance in maintenance_records:
        # Fetch related car and garage data
        car = db.query(Car).filter(Car.id == maintenance.car_id).first()  # Fetch the related car
        garage = db.query(Garage).filter(Garage.id == maintenance.garage_id).first()  # Fetch the related garage

        # Ensure car and garage are found
        if car is None or garage is None:
            raise HTTPException(status_code=404, detail="Related car or garage not found")

        # Construct the ResponseMaintenanceDTO object and append to the response list
        response_data.append(ResponseMaintenanceDTO(
            id=maintenance.id,
            car_id=maintenance.car_id,
            carName=car.make,  # Assuming the `Car` model has a `make` attribute
            serviceType=maintenance.serviceType,
            scheduledDate=maintenance.scheduledDate,
            garage_id=maintenance.garage_id,
            garageName=garage.name  # Assuming the `Garage` model has a `name` attribute
        ))

    return response_data  # Return the list of DTOs


@router.get("/maintenance/monthlyRequests/", response_model=List[MonthlyRequestsReportDTO], tags=["Maintenance Controller"])
def get_monthly_report(
    garage_id: int = Query(...),  # Garage ID (query parameter)
    start_month: str = Query(...),  # Start month in "YYYY-MM" format
    end_month: str = Query(...),  # End month in "YYYY-MM" format
    db: Session = Depends(get_db)
):
    print(f"Start date: {start_month}, End date: {end_month}")

    try:
        # Parse start and end months into datetime objects
        start_date = datetime.strptime(start_month, "%Y-%m")
        end_date = datetime.strptime(end_month, "%Y-%m")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM")

    # List to hold monthly report data
    monthly_report = []

    # Query the database for maintenance requests based on garage_id and month range
    while start_date <= end_date:
        # Format the current month in the desired "YYYY-MM" format
        current_month = start_date.strftime("%Y-%m")

        # Calculate the start and end date of the current month
        year = start_date.year
        month = start_date.month
        last_day = calendar.monthrange(year, month)[1]  # Get last day of the month

        # Create a datetime object for the last day of the month
        end_of_month = datetime(year, month, last_day)

        # Get the number of requests for the current month
        num_requests = db.query(MaintenanceRequest).filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduledDate >= start_date,  # Start of the month
            MaintenanceRequest.scheduledDate <= end_of_month  # End of the month
        ).count()

        # Append to the monthly_report list
        monthly_report.append(MonthlyRequestsReportDTO(month=current_month, requests=num_requests))

        # Move to the next month
        # This logic is for the date transition (next month)
        start_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    return monthly_report