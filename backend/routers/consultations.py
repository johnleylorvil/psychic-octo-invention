from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.consultation import Consultation, ConsultationCreate, ConsultationUpdate, Prescription, PrescriptionCreate
from middleware.permissions import get_current_user, require_roles
from services.notification_service import NotificationService
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/consultations", tags=["Consultations"])

def get_db():
    from server import db
    return db

@router.post("/", response_model=Consultation, status_code=status.HTTP_201_CREATED)
async def create_consultation(
    consultation_data: ConsultationCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["médecin"]))
):
    """
    Créer une nouvelle consultation (médecins uniquement).
    """
    consultation = Consultation(**consultation_data.model_dump())
    doc = consultation.model_dump()
    doc['date_consultation'] = doc['date_consultation'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.consultations.insert_one(doc)
    return consultation

@router.get("/", response_model=List[Consultation])
async def get_consultations(
    patient_id: Optional[str] = Query(None),
    medecin_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer les consultations avec filtres.
    """
    query = {}
    
    if current_user["role"] == "patient":
        patient = await db.patients.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
        if patient:
            query["patient_id"] = patient["id"]
        else:
            return []
    elif current_user["role"] == "médecin":
        query["medecin_id"] = current_user["user_id"]
    else:
        if patient_id:
            query["patient_id"] = patient_id
        if medecin_id:
            query["medecin_id"] = medecin_id
    
    consultations = await db.consultations.find(query, {"_id": 0}).to_list(1000)
    return consultations

@router.get("/{consultation_id}", response_model=Consultation)
async def get_consultation(
    consultation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer une consultation par son ID.
    """
    consultation = await db.consultations.find_one({"id": consultation_id}, {"_id": 0})
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée"
        )
    
    return consultation

@router.put("/{consultation_id}", response_model=dict)
async def update_consultation(
    consultation_id: str,
    consultation_data: ConsultationUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["médecin"]))
):
    """
    Mettre à jour une consultation.
    """
    update_dict = {k: v for k, v in consultation_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    update_dict["updated_at"] = datetime.now().isoformat()
    
    result = await db.consultations.update_one({"id": consultation_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée"
        )
    
    return {"message": "Consultation mise à jour avec succès"}

@router.post("/prescriptions", response_model=Prescription, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    prescription_data: PrescriptionCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["médecin"]))
):
    """
    Créer une nouvelle prescription.
    """
    prescription = Prescription(**prescription_data.model_dump())
    doc = prescription.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('date_validite'):
        doc['date_validite'] = doc['date_validite'].isoformat()
    
    await db.prescriptions.insert_one(doc)
    
    # Notification au patient
    patient = await db.patients.find_one({"id": prescription_data.patient_id}, {"_id": 0})
    medecin = await db.users.find_one({"id": prescription_data.medecin_id}, {"_id": 0})
    
    if patient and medecin:
        patient_info = await db.users.find_one({"id": patient["user_id"]}, {"_id": 0})
        NotificationService.send_prescription_notification(
            patient_data={
                "nom": patient_info.get("nom"),
                "prenom": patient_info.get("prenom"),
                "email": patient_info.get("email")
            },
            prescription_data={
                "medecin_nom": f"{medecin.get('nom')} {medecin.get('prenom')}"
            }
        )
    
    return prescription

@router.get("/prescriptions/", response_model=List[Prescription])
async def get_prescriptions(
    patient_id: Optional[str] = Query(None),
    medecin_id: Optional[str] = Query(None),
    consultation_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer les prescriptions avec filtres.
    """
    query = {}
    
    if current_user["role"] == "patient":
        patient = await db.patients.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
        if patient:
            query["patient_id"] = patient["id"]
        else:
            return []
    elif current_user["role"] == "médecin":
        query["medecin_id"] = current_user["user_id"]
    else:
        if patient_id:
            query["patient_id"] = patient_id
        if medecin_id:
            query["medecin_id"] = medecin_id
        if consultation_id:
            query["consultation_id"] = consultation_id
    
    prescriptions = await db.prescriptions.find(query, {"_id": 0}).to_list(1000)
    return prescriptions