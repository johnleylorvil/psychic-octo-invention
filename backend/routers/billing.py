from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.billing import Facture, FactureCreate, FactureUpdate, Paiement, PaiementCreate
from middleware.permissions import get_current_user, require_roles
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/billing", tags=["Facturation"])

def get_db():
    from server import db
    return db

# Factures
@router.post("/factures", response_model=Facture, status_code=status.HTTP_201_CREATED)
async def create_facture(
    facture_data: FactureCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "comptable"]))
):
    facture = Facture(**facture_data.model_dump())
    # Sécurité : recalculer le total à partir des lignes (ne pas faire confiance au client)
    computed_total = sum((it.total if it.total else it.quantite * it.prix_unitaire) for it in facture.items)
    facture.montant_total = computed_total
    doc = facture.model_dump()
    if doc.get('date_echeance'):
        doc['date_echeance'] = doc['date_echeance'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.factures.insert_one(doc)
    return facture

@router.get("/factures", response_model=List[Facture])
async def get_factures(
    patient_id: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = {}
    
    # Les patients ne voient que leurs factures
    if current_user["role"] == "patient":
        patient = await db.patients.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
        if patient:
            query["patient_id"] = patient["id"]
        else:
            return []
    else:
        if patient_id:
            query["patient_id"] = patient_id
    
    if statut:
        query["statut"] = statut
    
    factures = await db.factures.find(query, {"_id": 0}).to_list(1000)
    return factures

@router.get("/factures/{facture_id}", response_model=Facture)
async def get_facture(
    facture_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    facture = await db.factures.find_one({"id": facture_id}, {"_id": 0})
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )
    
    # Vérifier les permissions pour les patients
    if current_user["role"] == "patient":
        patient = await db.patients.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
        if not patient or facture["patient_id"] != patient["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
    
    return facture

@router.put("/factures/{facture_id}", response_model=dict)
async def update_facture(
    facture_id: str,
    facture_data: FactureUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "comptable"]))
):
    update_dict = {k: v for k, v in facture_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    if 'date_echeance' in update_dict:
        update_dict['date_echeance'] = update_dict['date_echeance'].isoformat()
    
    update_dict["updated_at"] = datetime.now().isoformat()
    result = await db.factures.update_one({"id": facture_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )
    
    return {"message": "Facture mise à jour avec succès"}

# Paiements
@router.post("/paiements", response_model=Paiement, status_code=status.HTTP_201_CREATED)
async def create_paiement(
    paiement_data: PaiementCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "comptable"]))
):
    # Vérifier que la facture existe
    facture = await db.factures.find_one({"id": paiement_data.facture_id}, {"_id": 0})
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )
    
    paiement = Paiement(**paiement_data.model_dump())
    doc = paiement.model_dump()
    doc['date_paiement'] = doc['date_paiement'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.paiements.insert_one(doc)
    
    # Mettre à jour le statut de la facture
    paiements = await db.paiements.find({"facture_id": paiement_data.facture_id}, {"_id": 0}).to_list(1000)
    total_paye = sum(p.get("montant", 0) for p in paiements)
    
    nouveau_statut = "payée" if total_paye >= facture["montant_total"] else "partiellement_payée"
    await db.factures.update_one(
        {"id": paiement_data.facture_id},
        {"$set": {"statut": nouveau_statut, "updated_at": datetime.now().isoformat()}}
    )
    
    return paiement

@router.get("/paiements", response_model=List[Paiement])
async def get_paiements(
    facture_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "comptable"]))
):
    query = {}
    if facture_id:
        query["facture_id"] = facture_id
    
    paiements = await db.paiements.find(query, {"_id": 0}).to_list(1000)
    return paiements

@router.get("/stats", response_model=dict)
async def get_billing_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "comptable"]))
):
    """
    Statistiques financières.
    """
    factures = await db.factures.find({}, {"_id": 0}).to_list(10000)
    paiements = await db.paiements.find({}, {"_id": 0}).to_list(10000)
    
    total_factures = sum(f.get("montant_total", 0) for f in factures)
    total_paye = sum(p.get("montant", 0) for p in paiements)
    total_impaye = total_factures - total_paye
    
    factures_en_attente = len([f for f in factures if f.get("statut") == "en_attente"])
    factures_payees = len([f for f in factures if f.get("statut") == "payée"])
    
    return {
        "total_factures": total_factures,
        "total_paye": total_paye,
        "total_impaye": total_impaye,
        "nombre_factures": len(factures),
        "factures_en_attente": factures_en_attente,
        "factures_payees": factures_payees,
        "nombre_paiements": len(paiements)
    }