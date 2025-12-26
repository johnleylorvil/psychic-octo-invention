from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.pharmacy import (
    CategorieMedicament, CategorieMedicamentCreate,
    Medicament, MedicamentCreate, MedicamentUpdate,
    StockPharmacie, StockPharmacieCreate, StockPharmacieUpdate
)
from middleware.permissions import get_current_user, require_roles
from services.notification_service import NotificationService
from typing import List, Optional
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/pharmacy", tags=["Pharmacie"])

def get_db():
    from server import db
    return db

# Catégories de médicaments
@router.post("/categories", response_model=CategorieMedicament, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategorieMedicamentCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "pharmacien"]))
):
    category = CategorieMedicament(**category_data.model_dump())
    doc = category.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.drug_categories.insert_one(doc)
    return category

@router.get("/categories", response_model=List[CategorieMedicament])
async def get_categories(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    categories = await db.drug_categories.find({}, {"_id": 0}).to_list(1000)
    return categories

# Médicaments
@router.post("/medicaments", response_model=Medicament, status_code=status.HTTP_201_CREATED)
async def create_medicament(
    med_data: MedicamentCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "pharmacien"]))
):
    medicament = Medicament(**med_data.model_dump())
    doc = medicament.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.medicaments.insert_one(doc)
    return medicament

@router.get("/medicaments", response_model=List[Medicament])
async def get_medicaments(
    categorie_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = {}
    if categorie_id:
        query["categorie_id"] = categorie_id
    
    medicaments = await db.medicaments.find(query, {"_id": 0}).to_list(1000)
    
    if search:
        search_lower = search.lower()
        medicaments = [m for m in medicaments if search_lower in m.get("nom", "").lower()]
    
    return medicaments

@router.get("/medicaments/{medicament_id}", response_model=Medicament)
async def get_medicament(
    medicament_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    medicament = await db.medicaments.find_one({"id": medicament_id}, {"_id": 0})
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médicament non trouvé"
        )
    return medicament

@router.put("/medicaments/{medicament_id}", response_model=dict)
async def update_medicament(
    medicament_id: str,
    med_data: MedicamentUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "pharmacien"]))
):
    update_dict = {k: v for k, v in med_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    update_dict["updated_at"] = datetime.now().isoformat()
    result = await db.medicaments.update_one({"id": medicament_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médicament non trouvé"
        )
    
    return {"message": "Médicament mis à jour avec succès"}

# Stocks
@router.post("/stock", response_model=StockPharmacie, status_code=status.HTTP_201_CREATED)
async def create_stock(
    stock_data: StockPharmacieCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "pharmacien"]))
):
    stock = StockPharmacie(**stock_data.model_dump())
    doc = stock.model_dump()
    doc['date_peremption'] = doc['date_peremption'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.pharmacy_stock.insert_one(doc)
    return stock

@router.get("/stock", response_model=List[StockPharmacie])
async def get_stock(
    medicament_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "pharmacien", "médecin"]))
):
    query = {}
    if medicament_id:
        query["medicament_id"] = medicament_id
    
    stocks = await db.pharmacy_stock.find(query, {"_id": 0}).to_list(1000)
    return stocks

@router.put("/stock/{stock_id}", response_model=dict)
async def update_stock(
    stock_id: str,
    stock_data: StockPharmacieUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "pharmacien"]))
):
    update_dict = {k: v for k, v in stock_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    if 'date_peremption' in update_dict:
        update_dict['date_peremption'] = update_dict['date_peremption'].isoformat()
    
    update_dict["updated_at"] = datetime.now().isoformat()
    result = await db.pharmacy_stock.update_one({"id": stock_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock non trouvé"
        )
    
    return {"message": "Stock mis à jour avec succès"}

# Alertes
@router.get("/alerts", response_model=dict)
async def get_pharmacy_alerts(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "pharmacien"]))
):
    """
    Récupérer les alertes de stock faible et de péremption.
    """
    # Alertes de stock faible
    medicaments = await db.medicaments.find({}, {"_id": 0}).to_list(1000)
    low_stock_alerts = []
    
    for med in medicaments:
        stocks = await db.pharmacy_stock.find({"medicament_id": med["id"]}, {"_id": 0}).to_list(1000)
        total_quantity = sum(s.get("quantite", 0) for s in stocks)
        
        if total_quantity < med.get("seuil_stock_min", 10):
            low_stock_alerts.append({
                "medicament_id": med["id"],
                "nom": med["nom"],
                "quantite_actuelle": total_quantity,
                "seuil_min": med.get("seuil_stock_min", 10),
                "type": "stock_faible"
            })
            
            # Envoyer notification
            NotificationService.send_stock_alert({
                "nom": med["nom"],
                "type_alerte": "Stock faible",
                "quantite": total_quantity
            })
    
    # Alertes de péremption (30 jours)
    expiry_date_limit = (datetime.now().date() + timedelta(days=30)).isoformat()
    stocks = await db.pharmacy_stock.find({}, {"_id": 0}).to_list(1000)
    
    expiry_alerts = []
    for stock in stocks:
        if stock.get("date_peremption") and stock["date_peremption"] <= expiry_date_limit:
            med = await db.medicaments.find_one({"id": stock["medicament_id"]}, {"_id": 0})
            if med:
                expiry_alerts.append({
                    "stock_id": stock["id"],
                    "medicament_nom": med["nom"],
                    "quantite": stock["quantite"],
                    "date_peremption": stock["date_peremption"],
                    "numero_lot": stock["numero_lot"],
                    "type": "peremption_proche"
                })
                
                # Envoyer notification
                NotificationService.send_stock_alert({
                    "nom": med["nom"],
                    "type_alerte": "Péremption proche",
                    "date_peremption": stock["date_peremption"],
                    "quantite": stock["quantite"]
                })
    
    return {
        "stock_faible": low_stock_alerts,
        "peremption_proche": expiry_alerts,
        "total_alertes": len(low_stock_alerts) + len(expiry_alerts)
    }