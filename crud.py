# from sqlalchemy.orm import Session
# from models import Patient, Weight

# def create_patient(db: Session, name: str, age: int, barcode: str):
#     patient = Patient(name=name, age=age, barcode=barcode)
#     db.add(patient)
#     db.commit()
#     db.refresh(patient)
#     return patient

# def get_patient_by_barcode(db: Session, barcode: str):
#     return db.query(Patient).filter(Patient.barcode == barcode).first()

# def get_weights(db: Session, patient_id: int):
#     return db.query(Weight).filter(Weight.patient_id == patient_id).all()

# def add_weight(db: Session, patient_id: int, weight: float):
#     new_weight = Weight(patient_id=patient_id, weight=weight)
#     db.add(new_weight)
#     db.commit()
#     return new_weight
from sqlalchemy.orm import Session
from models import Patient, Weight

def create_patient(db: Session, name: str, age: int, barcode: str):
    patient = Patient(name=name, age=age, barcode=barcode)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient_by_barcode(db: Session, barcode: str):
    return db.query(Patient).filter(Patient.barcode == barcode).first()


def get_weights(db: Session, patient_id: int):
    return db.query(Weight).filter(Weight.patient_id == patient_id).order_by(Weight.timestamp.desc()).all()


def add_weight(db: Session, patient_id: int, weight: float):
    new_weight = Weight(patient_id=patient_id, weight=weight)
    db.add(new_weight)
    db.commit()
    db.refresh(new_weight)
    return new_weight