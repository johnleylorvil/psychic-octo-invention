from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from middleware.permissions import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["Tableau de Bord"])

def get_db():
    from server import db
    return db

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Statistiques du tableau de bord adaptées selon le rôle de l'utilisateur.
    """
    role = current_user["role"]
    user_id = current_user["user_id"]
    
    stats = {}
    
    # Statistiques communes
    if role in ["admin", "médecin", "infirmière"]:
        # Patients
        total_patients = await db.patients.count_documents({})
        stats["total_patients"] = total_patients
        
        # Rendez-vous du jour
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        rdv_today = await db.appointments.count_documents({
            "date_rdv": {"$gte": today, "$lt": tomorrow},
            "statut": {"$ne": "annulé"}
        })
        stats["rendez_vous_aujourdhui"] = rdv_today
    
    # Statistiques spécifiques par rôle
    if role == "admin":
        # Utilisateurs actifs
        total_users = await db.users.count_documents({"actif": True})
        stats["total_utilisateurs_actifs"] = total_users
        
        # Services
        total_services = await db.services.count_documents({})
        stats["total_services"] = total_services
        
        # Lits disponibles
        lits_disponibles = await db.lits.count_documents({"statut": "disponible"})
        lits_occupes = await db.lits.count_documents({"statut": "occupé"})
        stats["lits_disponibles"] = lits_disponibles
        stats["lits_occupes"] = lits_occupes
        
        # Alertes pharmacie
        medicaments = await db.medicaments.find({}, {"_id": 0}).to_list(1000)
        alertes_stock = 0
        for med in medicaments:
            stocks = await db.pharmacy_stock.find({"medicament_id": med["id"]}, {"_id": 0}).to_list(1000)
            total_quantity = sum(s.get("quantite", 0) for s in stocks)
            if total_quantity < med.get("seuil_stock_min", 10):
                alertes_stock += 1
        stats["alertes_pharmacie"] = alertes_stock
        
    elif role == "médecin":
        # Mes rendez-vous
        mes_rdv = await db.appointments.count_documents({
            "medecin_id": user_id,
            "statut": {"$in": ["planifié", "confirmé"]}
        })
        stats["mes_rendez_vous"] = mes_rdv
        
        # Mes consultations du mois
        debut_mois = datetime.now().replace(day=1).isoformat()
        mes_consultations = await db.consultations.count_documents({
            "medecin_id": user_id,
            "date_consultation": {"$gte": debut_mois}
        })
        stats["consultations_ce_mois"] = mes_consultations
        
        # Mes patients
        mes_patients = await db.patients.count_documents({})
        stats["mes_patients"] = mes_patients
        
    elif role == "infirmière":
        # Lits
        lits_disponibles = await db.lits.count_documents({"statut": "disponible"})
        lits_occupes = await db.lits.count_documents({"statut": "occupé"})
        stats["lits_disponibles"] = lits_disponibles
        stats["lits_occupes"] = lits_occupes
        
        # Stock sang critique
        blood_stocks = await db.blood_stock.find({"statut": "disponible"}, {"_id": 0}).to_list(1000)
        stock_critique = 0
        for bt in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            total_ml = sum(s.get("quantite_ml", 0) for s in blood_stocks if s.get("groupe_sanguin") == bt)
            if total_ml < 2000:
                stock_critique += 1
        stats["groupes_sanguins_critiques"] = stock_critique
        
    elif role == "pharmacien":
        # Médicaments
        total_medicaments = await db.medicaments.count_documents({})
        stats["total_medicaments"] = total_medicaments
        
        # Alertes stock faible
        medicaments = await db.medicaments.find({}, {"_id": 0}).to_list(1000)
        alertes_stock = 0
        for med in medicaments:
            stocks = await db.pharmacy_stock.find({"medicament_id": med["id"]}, {"_id": 0}).to_list(1000)
            total_quantity = sum(s.get("quantite", 0) for s in stocks)
            if total_quantity < med.get("seuil_stock_min", 10):
                alertes_stock += 1
        stats["alertes_stock_faible"] = alertes_stock
        
        # Péremption proche (30 jours)
        expiry_date_limit = (datetime.now().date() + timedelta(days=30)).isoformat()
        stocks_expiring = await db.pharmacy_stock.count_documents({
            "date_peremption": {"$lte": expiry_date_limit}
        })
        stats["alertes_peremption"] = stocks_expiring
        
    elif role == "comptable":
        # Factures
        total_factures = await db.factures.count_documents({})
        factures_impayees = await db.factures.count_documents({"statut": "en_attente"})
        stats["total_factures"] = total_factures
        stats["factures_impayees"] = factures_impayees
        
        # Montants
        factures = await db.factures.find({}, {"_id": 0}).to_list(10000)
        paiements = await db.paiements.find({}, {"_id": 0}).to_list(10000)
        
        total_a_payer = sum(f.get("montant_total", 0) for f in factures)
        total_paye = sum(p.get("montant", 0) for p in paiements)
        stats["montant_total"] = total_a_payer
        stats["montant_paye"] = total_paye
        stats["montant_impaye"] = total_a_payer - total_paye
        
    elif role == "patient":
        # Mes rendez-vous
        patient = await db.patients.find_one({"user_id": user_id}, {"_id": 0})
        if patient:
            mes_rdv = await db.appointments.count_documents({
                "patient_id": patient["id"],
                "statut": {"$ne": "annulé"}
            })
            stats["mes_rendez_vous"] = mes_rdv
            
            # Mes factures
            mes_factures = await db.factures.count_documents({"patient_id": patient["id"]})
            factures_impayees = await db.factures.count_documents({
                "patient_id": patient["id"],
                "statut": {"$in": ["en_attente", "partiellement_payée"]}
            })
            stats["mes_factures"] = mes_factures
            stats["factures_impayees"] = factures_impayees
            
            # Mes consultations
            mes_consultations = await db.consultations.count_documents({"patient_id": patient["id"]})
            stats["mes_consultations"] = mes_consultations
    
    return stats