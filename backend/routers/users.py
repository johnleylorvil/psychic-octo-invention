from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import User, UserCreate, UserUpdate
from services.auth_service import AuthService
from middleware.permissions import get_current_user, require_roles
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Utilisateurs"])

def get_db():
    from server import db
    return db

@router.post("/", response_model=dict, dependencies=[Depends(require_roles(["admin"]))])
async def create_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Créer un nouvel utilisateur (réservé aux admins).
    """
    auth_service = AuthService(db)
    user = await auth_service.create_user(user_data)
    return {"message": "Utilisateur créé avec succès", "user_id": user.id}

@router.get("/", response_model=List[User])
async def get_users(
    role: Optional[str] = Query(None),
    actif: Optional[bool] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin", "médecin", "infirmière"]))
):
    """
    Récupérer la liste des utilisateurs avec filtres optionnels.
    """
    query = {}
    if role:
        query["role"] = role
    if actif is not None:
        query["actif"] = actif
    
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).to_list(1000)
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupérer un utilisateur par son ID.
    """
    # Les patients ne peuvent voir que leur propre profil
    if current_user["role"] == "patient" and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user

@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """
    Mettre à jour un utilisateur (réservé aux admins).
    """
    update_dict = {k: v for k, v in user_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    update_dict["updated_at"] = datetime.now().isoformat()
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_dict})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return {"message": "Utilisateur mis à jour avec succès"}

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    """
    Supprimer un utilisateur (désactivation plutôt que suppression).
    """
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"actif": False, "updated_at": datetime.now().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return {"message": "Utilisateur désactivé avec succès"}