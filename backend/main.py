from fastapi import FastAPI
from backend.garage.garage import router as garage_router
from backend.maintenance.maintenance import router as maintenance_router
from backend.car.car import router as car_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(garage_router)
app.include_router(maintenance_router)
app.include_router(car_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Car Management API!"}