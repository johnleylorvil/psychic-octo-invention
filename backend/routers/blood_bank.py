from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.blood_bank import DonneurSang, DonneurSangCreate, DonneurSangUpdate, StockSang, StockSangCreate, StockSangUpdate
from middleware.permissions import get_current_user, require_roles
from services.notification_service import NotificationService
from typing import List, Optional
from datetime import datetime, date

router = APIRouter(prefix="/blood-bank", tags=["Banque de Sang"])

def get_db():
    from server import db
    return db

# Donneurs
@router.post("/donneurs", response_model=DonneurSang, status_code=status.HTTP_201_CREATED)
async def create_donneur(
    donneur_data: DonneurSangCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière"]))
):
    donneur = DonneurSang(**donneur_data.model_dump())
    doc = donneur.model_dump()
    if doc.get('date_derniere_donation'):
        doc['date_derniere_donation'] = doc['date_derniere_donation'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.blood_donors.insert_one(doc)
    return donneur

@router.get("/donneurs", response_model=List[DonneurSang])
async def get_donneurs(
    groupe_sanguin: Optional[str] = Query(None),
    eligible: Optional[bool] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière", "médecin"]))
):
    query = {}
    if groupe_sanguin:
        query["groupe_sanguin"] = groupe_sanguin
    if eligible is not None:
        query["eligible"] = eligible
    
    donneurs = await db.blood_donors.find(query, {"_id": 0}).to_list(1000)
    return donneurs

@router.get("/donneurs/{donneur_id}", response_model=DonneurSang)
async def get_donneur(
    donneur_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière", "médecin"]))
):
    donneur = await db.blood_donors.find_one({"id": donneur_id}, {"_id": 0})
    if not donneur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donneur non trouvé"
        )
    return donneur

@router.put("/donneurs/{donneur_id}", response_model=dict)
async def update_donneur(
    donneur_id: str,
    donneur_data: DonneurSangUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière"]))
):
    update_dict = {k: v for k, v in donneur_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    if 'date_derniere_donation' in update_dict:
        update_dict['date_derniere_donation'] = update_dict['date_derniere_donation'].isoformat()
    
    update_dict["updated_at"] = datetime.now().isoformat()
    result = await db.blood_donors.update_one({"id": donneur_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donneur non trouvé"
        )
    
    return {"message": "Donneur mis à jour avec succès"}

# Stock de sang
@router.post("/stock", response_model=StockSang, status_code=status.HTTP_201_CREATED)
async def create_stock_sang(
    stock_data: StockSangCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière"]))
):
    stock = StockSang(**stock_data.model_dump())
    doc = stock.model_dump()
    doc['date_collecte'] = doc['date_collecte'].isoformat()
    doc['date_expiration'] = doc['date_expiration'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.blood_stock.insert_one(doc)
    return stock

@router.get("/stock", response_model=List[StockSang])
async def get_stock_sang(
    groupe_sanguin: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière", "médecin"]))
):
    query = {}
    if groupe_sanguin:
        query["groupe_sanguin"] = groupe_sanguin
    if statut:
        query["statut"] = statut
    
    stocks = await db.blood_stock.find(query, {"_id": 0}).to_list(1000)
    return stocks

@router.get("/stock/summary", response_model=dict)
async def get_stock_summary(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière", "médecin"]))
):
    """
    Résumé des stocks par groupe sanguin.
    """
    stocks = await db.blood_stock.find({"statut": "disponible"}, {"_id": 0}).to_list(1000)
    
    summary = {}
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    for bt in blood_types:
        blood_stocks = [s for s in stocks if s.get("groupe_sanguin") == bt]
        total_ml = sum(s.get("quantite_ml", 0) for s in blood_stocks)
        summary[bt] = {
            "groupe_sanguin": bt,
            "quantite_ml": total_ml,
            "nombre_poches": len(blood_stocks),
            "statut": "critique" if total_ml < 2000 else "faible" if total_ml < 5000 else "ok"
        }
        
        # Alerte si stock critique
        if total_ml < 3000:
            NotificationService.send_blood_stock_alert(bt, total_ml)
    
    return summary

@router.put("/stock/{stock_id}", response_model=dict)
async def update_stock_sang(
    stock_id: str,
    stock_data: StockSangUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière"]))
):
    update_dict = {k: v for k, v in stock_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    update_dict["updated_at"] = datetime.now().isoformat()
    result = await db.blood_stock.update_one({"id": stock_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock non trouvé"
        )
    
    return {"message": "Stock mis à jour avec succès"}