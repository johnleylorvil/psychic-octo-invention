from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.patient import Patient, PatientCreate, PatientUpdate
from models.audit import AuditLogCreate, AuditLog
from middleware.permissions import get_current_user, require_roles
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["Patients"])

def get_db():
    from server import db
    return db

async def log_audit(db, user_id: str, user_role: str, action: str, patient_id: str, details: str = None):
    """Fonction helper pour logger les accès aux dossiers patients"""
    audit_log = AuditLog(
        user_id=user_id,
        user_role=user_role,
        action=action,
        ressource_type="patient",
        ressource_id=patient_id,
        details=details
    )
    doc = audit_log.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.audit_logs.insert_one(doc)

@router.post("/", response_model=Patient, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "médecin", "infirmière"]))
):
    """
    Créer un nouveau dossier patient.
    """
    # Vérifier si le numéro de dossier existe déjà
    existing = await db.patients.find_one({"numero_dossier": patient_data.numero_dossier}, {"_id": 0})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce numéro de dossier est déjà utilisé"
        )
    
    patient = Patient(**patient_data.model_dump())
    doc = patient.model_dump()
    doc['date_naissance'] = doc['date_naissance'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.patients.insert_one(doc)
    await log_audit(db, current_user["user_id"], current_user["role"], "création", patient.id, "Nouveau dossier patient créé")
    
    return patient

@router.get("/", response_model=List[Patient])
async def get_patients(
    search: Optional[str] = Query(None, description="Recherche par nom, prénom ou numéro de dossier"),
    groupe_sanguin: Optional[str] = Query(None),
    sexe: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer la liste des patients avec filtres optionnels.
    """
    # Les patients ne peuvent voir que leur propre dossier
    if current_user["role"] == "patient":
        patient = await db.patients.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
        return [patient] if patient else []
    
    query = {}
    if groupe_sanguin:
        query["groupe_sanguin"] = groupe_sanguin
    if sexe:
        query["sexe"] = sexe
    
    patients = await db.patients.find(query, {"_id": 0}).to_list(1000)
    
    # Filtre de recherche textuelle côté application
    if search:
        search_lower = search.lower()
        patients = [
            p for p in patients
            if search_lower in p.get("numero_dossier", "").lower()
        ]
    
    return patients

@router.get("/{patient_id}", response_model=Patient)
async def get_patient(
    patient_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer un patient par son ID.
    """
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Les patients ne peuvent voir que leur propre dossier
    if current_user["role"] == "patient" and patient["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    
    # Logger l'accès au dossier
    await log_audit(db, current_user["user_id"], current_user["role"], "lecture", patient_id, "Consultation du dossier")
    
    return patient

@router.put("/{patient_id}", response_model=dict)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "médecin", "infirmière"]))
):
    """
    Mettre à jour les informations d'un patient.
    """
    update_dict = {k: v for k, v in patient_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    # Convertir les dates en ISO string
    if 'date_naissance' in update_dict:
        update_dict['date_naissance'] = update_dict['date_naissance'].isoformat()
    
    update_dict["updated_at"] = datetime.now().isoformat()
    
    result = await db.patients.update_one({"id": patient_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    await log_audit(db, current_user["user_id"], current_user["role"], "modification", patient_id, f"Modification: {', '.join(update_dict.keys())}")
    
    return {"message": "Patient mis à jour avec succès"}

@router.delete("/{patient_id}", response_model=dict)
async def delete_patient(
    patient_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """
    Supprimer un patient (admin uniquement).
    """
    result = await db.patients.delete_one({"id": patient_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    await log_audit(db, current_user["user_id"], current_user["role"], "suppression", patient_id, "Dossier patient supprimé")
    
    return {"message": "Patient supprimé avec succès"}