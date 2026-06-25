from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.appointment import RendezVous, RendezVousCreate, RendezVousUpdate
from middleware.permissions import get_current_user, require_roles
from services.notification_service import NotificationService
from typing import List, Optional
from datetime import datetime, date

router = APIRouter(prefix="/appointments", tags=["Rendez-vous"])

def get_db():
    from server import db
    return db

@router.post("/", response_model=RendezVous, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    rdv_data: RendezVousCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Créer un nouveau rendez-vous.
    """
    rdv = RendezVous(**rdv_data.model_dump())

    # Un patient ne peut créer un RDV que pour lui-même
    if current_user["role"] == "patient":
        patient = await db.patients.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
        if not patient:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dossier patient introuvable")
        rdv.patient_id = patient["id"]
        rdv.statut = "en_attente"

    doc = rdv.model_dump()
    doc['date_rdv'] = doc['date_rdv'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.appointments.insert_one(doc)
    
    # Envoyer notification de rappel (log uniquement)
    patient = await db.patients.find_one({"id": rdv.patient_id}, {"_id": 0})
    medecin = await db.users.find_one({"id": rdv.medecin_id}, {"_id": 0})
    
    if patient and medecin:
        patient_info = await db.users.find_one({"id": patient["user_id"]}, {"_id": 0})
        NotificationService.send_appointment_reminder(
            patient_data={
                "nom": patient_info.get("nom"),
                "prenom": patient_info.get("prenom"),
                "email": patient_info.get("email"),
                "telephone": patient_info.get("telephone")
            },
            appointment_data={
                "date_rdv": rdv_data.date_rdv,
                "medecin_nom": f"{medecin.get('nom')} {medecin.get('prenom')}",
                "type_rdv": rdv.type_rdv,
                "motif": rdv.motif
            }
        )
    
    return rdv

@router.get("/", response_model=List[RendezVous])
async def get_appointments(
    patient_id: Optional[str] = Query(None),
    medecin_id: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    date_debut: Optional[str] = Query(None),
    date_fin: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer la liste des rendez-vous avec filtres.
    """
    query = {}
    
    # Les patients ne voient que leurs rendez-vous
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
    
    if statut:
        query["statut"] = statut
    
    appointments = await db.appointments.find(query, {"_id": 0}).to_list(1000)
    return appointments

@router.get("/{appointment_id}", response_model=RendezVous)
async def get_appointment(
    appointment_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer un rendez-vous par son ID.
    """
    appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous non trouvé"
        )
    
    # Vérifier les permissions
    if current_user["role"] == "patient":
        patient = await db.patients.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
        if not patient or appointment["patient_id"] != patient["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
    
    return appointment

@router.put("/{appointment_id}", response_model=dict)
async def update_appointment(
    appointment_id: str,
    rdv_data: RendezVousUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mettre à jour un rendez-vous.
    """
    update_dict = {k: v for k, v in rdv_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    if 'date_rdv' in update_dict:
        update_dict['date_rdv'] = update_dict['date_rdv'].isoformat()
    
    update_dict["updated_at"] = datetime.now().isoformat()
    
    result = await db.appointments.update_one({"id": appointment_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous non trouvé"
        )
    
    return {"message": "Rendez-vous mis à jour avec succès"}

@router.delete("/{appointment_id}", response_model=dict)
async def cancel_appointment(
    appointment_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Annuler un rendez-vous (changement de statut plutôt que suppression).
    """
    result = await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": {"statut": "annulé", "updated_at": datetime.now().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rendez-vous non trouvé"
        )
    
    return {"message": "Rendez-vous annulé avec succès"}