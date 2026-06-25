from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.service import Service, ServiceCreate, ServiceUpdate, Lit, LitCreate, LitUpdate
from middleware.permissions import get_current_user, require_roles
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/services", tags=["Services et Lits"])

def get_db():
    from server import db
    return db

# Services
@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    service = Service(**service_data.model_dump())
    doc = service.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.services.insert_one(doc)
    return service

@router.get("/", response_model=List[Service])
async def get_services(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    services = await db.services.find({}, {"_id": 0}).to_list(1000)
    return services

# Lits (must come BEFORE /{service_id} to avoid route shadowing)
@router.post("/lits", response_model=Lit, status_code=status.HTTP_201_CREATED)
async def create_lit(
    lit_data: LitCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière"]))
):
    lit = Lit(**lit_data.model_dump())
    doc = lit.model_dump()
    if doc.get('date_admission'):
        doc['date_admission'] = doc['date_admission'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.lits.insert_one(doc)
    return lit

@router.get("/lits", response_model=List[Lit])
async def get_lits(
    service_id: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = {}
    if service_id:
        query["service_id"] = service_id
    if statut:
        query["statut"] = statut
    
    lits = await db.lits.find(query, {"_id": 0}).to_list(1000)
    return lits

@router.get("/lits/{lit_id}", response_model=Lit)
async def get_lit(
    lit_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    lit = await db.lits.find_one({"id": lit_id}, {"_id": 0})
    if not lit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lit non trouvé"
        )
    return lit

@router.put("/lits/{lit_id}", response_model=dict)
async def update_lit(
    lit_id: str,
    lit_data: LitUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "infirmière"]))
):
    update_dict = {k: v for k, v in lit_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    if 'date_admission' in update_dict and update_dict['date_admission']:
        update_dict['date_admission'] = update_dict['date_admission'].isoformat()
    
    update_dict["updated_at"] = datetime.now().isoformat()
    result = await db.lits.update_one({"id": lit_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lit non trouvé"
        )
    
    return {"message": "Lit mis à jour avec succès"}

# Services detail/update routes (declared AFTER /lits to avoid shadowing)
@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )
    return service

@router.put("/{service_id}", response_model=dict)
async def update_service(
    service_id: str,
    service_data: ServiceUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    update_dict = {k: v for k, v in service_data.model_dump(exclude_unset=True).items() if v is not None}

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )

    update_dict["updated_at"] = datetime.now().isoformat()
    result = await db.services.update_one({"id": service_id}, {"$set": update_dict})

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )

    return {"message": "Service mis à jour avec succès"}