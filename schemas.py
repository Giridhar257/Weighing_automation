from pydantic import BaseModel
from typing import List
import datetime

class PatientCreate(BaseModel):
    name: str
    age: int

class WeightResponse(BaseModel):
    weight: float
    timestamp: datetime.datetime

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    barcode: str
    weights: List[WeightResponse]
    
class WeightCreate(BaseModel):
    weight: float

    class Config:
        orm_mode = True

class ScanCreate(BaseModel):
    barcode: str