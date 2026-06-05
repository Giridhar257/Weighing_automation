# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# import models, database, crud
# import barcode_generator as bc
# from schemas import PatientCreate
# from schemas import WeightCreate
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# models.Base.metadata.create_all(bind=database.engine)

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# app.mount("/barcodes", StaticFiles(directory="barcodes"), name="barcodes")
# def get_db():
#     db = database.SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # Register patient
# @app.post("/register")
# def register(patient: PatientCreate, db: Session = Depends(get_db)):
#     code, img = bc.generate_barcode()
#     new_patient = crud.create_patient(db, patient.name, patient.age, code)

#     return {
#         "name": new_patient.name,
#         "age": new_patient.age,
#         "barcode": code,
#         "barcode_image": f"http://10.65.139.44:8000/{img}.png"
#     }


# # Get patient details by barcode
# @app.get("/patient/{barcode}")
# def get_patient(barcode: str, db: Session = Depends(get_db)):

#     patient = crud.get_patient_by_barcode(db, barcode)

#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")

#     weights = crud.get_weights(db, patient.id)

#     return {
#         "name": patient.name,
#         "age": patient.age,
#         "barcode": patient.barcode,
#         "weights": [
#             {
#                 "weight": w.weight,
#                 "timestamp": w.timestamp
#             } for w in weights
#         ]
#     }


# # Receive weight (barcode + weight)
# @app.post("/weight")
# def receive_weight(data: WeightCreate, db: Session = Depends(get_db)):

#     barcode = data.barcode
#     weight = data.weight

#     patient = crud.get_patient_by_barcode(db, barcode)

#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")

#     new_weight = crud.add_weight(db, patient.id, weight)

#     return {
#         "message": "Weight added",
#         "weight": new_weight.weight,
#         "timestamp": new_weight.timestamp
#     }

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database, crud
import barcode_generator as bc
from schemas import PatientCreate
from schemas import WeightCreate
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from schemas import ScanCreate
import hid
import threading

last_scanned_barcode = None
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/barcodes", StaticFiles(directory="barcodes"), name="barcodes")

# NEW: Store last scanned barcode
last_scanned_barcode = None
current_live_weight = 0
stable_weight = 0
is_stable = False

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register patient
@app.post("/register")
def register(patient: PatientCreate, db: Session = Depends(get_db)):
    code, img = bc.generate_barcode()
    new_patient = crud.create_patient(db, patient.name, patient.age, code)

    return {
        "name": new_patient.name,
        "age": new_patient.age,
        "barcode": code,
        # 🔧 FIX: use your real IP instead of 192.168.56.1
        "barcode_image": f"http://10.65.139.44:8000/{img}.png"
    }



#  NEW: Scan barcode from PC
@app.post("/scan")
def scan_barcode(data: ScanCreate):
    global last_scanned_barcode

    barcode = data.barcode

    if not barcode:
        raise HTTPException(status_code=400, detail="Barcode missing")

    last_scanned_barcode = barcode

    return {
        "message": "Barcode stored",
        "barcode": barcode
    }


# Get patient details by barcode
@app.get("/patient/{barcode}")
def get_patient(barcode: str, db: Session = Depends(get_db)):

    patient = crud.get_patient_by_barcode(db, barcode)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    weights = crud.get_weights(db, patient.id)

    return {
        "name": patient.name,
        "age": patient.age,
        "barcode": patient.barcode,
        "weights": [
            {
                "weight": w.weight,
                "timestamp": w.timestamp
            } for w in weights
        ]
    }


#  MODIFIED: Receive weight (NO barcode from ESP)
@app.post("/weight")
def receive_weight(data: WeightCreate, db: Session = Depends(get_db)):

    global last_scanned_barcode

    if not last_scanned_barcode:
        raise HTTPException(status_code=400, detail="No barcode scanned")

    weight = data.weight

    patient = crud.get_patient_by_barcode(db, last_scanned_barcode)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_weight = crud.add_weight(db, patient.id, weight)

    last_scanned_barcode = None

    return {
        "message": "Weight added",
        "barcode": patient.barcode,
        "weight": new_weight.weight,
        "timestamp": new_weight.timestamp
    }

@app.get("/status")
def status():
    global last_scanned_barcode
    return {"ready": last_scanned_barcode is not None}


def scanner_listener():
    global last_scanned_barcode

    try:
        device = hid.device()
        
        # You must replace these with your scanner values
        VENDOR_ID = 1504
        PRODUCT_ID = 4608

        device.open(VENDOR_ID, PRODUCT_ID)

        print("Scanner connected")

        barcode = ""

        while True:
            data = device.read(64)

            if data:
                for d in data:
                    if d == 40:  # ENTER key
                        if barcode:
                            last_scanned_barcode = barcode
                            print("Scanned:", barcode)
                            barcode = ""
                    elif d > 0:
                        barcode += chr(d)

    except Exception as e:
        print("Scanner error:", e)

@app.post("/live-weight")
def live_weight(data: dict):

    global current_live_weight
    global stable_weight
    global is_stable

    current_live_weight = data.get("weight", 0)
    is_stable = data.get("stable", False)

    if is_stable:
        stable_weight = current_live_weight

    return {"message": "updated"}

@app.get("/live-weight")
def get_live_weight():

    return {
        "live_weight": current_live_weight,
        "stable_weight": stable_weight,
        "stable": is_stable
    }