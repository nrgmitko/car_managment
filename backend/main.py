from fastapi import FastAPI
from backend.garage.garage import router as garage_router
from backend.maintenance.maintenance import router as maintenance_router
from backend.car.car import router as car_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; restrict this to specific domains for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Registering the routers for Garage, Maintenance, and Car resources
app.include_router(garage_router)
app.include_router(maintenance_router)
app.include_router(car_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Car Management API!"}