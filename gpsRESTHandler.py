from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# We are running on localhost, so allow everything
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gps_coordinates = {
    "default": {"lat": 0,
                "lon": 0}
}

class GpsInfo(BaseModel):
    lat: float
    lon: float
    
@app.get("/gps/get")
def index():
    if 'septentrio' in gps_coordinates.keys():
        return gps_coordinates['septentrio']
    else:
        return gps_coordinates['default']

@app.post("/gps/post/{name_gps}")
def post_gps(name_gps: str, gps: GpsInfo):
    gps_coordinates[name_gps] = gps
    
    return gps_coordinates

@app.put("/gps/update/{name_gps}")
def update_gps(name_gps: str, gps: GpsInfo):
    if name_gps != "septentrio":
        return {"Error"}
    else:
        gps_coordinates[name_gps]= gps
    
    return gps_coordinates