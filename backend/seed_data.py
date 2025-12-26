"""
Script pour générer des données de démonstration pour le Système de Gestion de Clinique.
Génère 5-10 utilisateurs par rôle avec des données réalistes.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta, date
import random

# Import des modèles
from models.user import User, UserInDB
from models.patient import Patient
from models.appointment import RendezVous
from models.consultation import Consultation, Prescription, MedicamentPrescrit
from models.pharmacy import CategorieMedicament, Medicament, StockPharmacie
from models.blood_bank import DonneurSang, StockSang
from models.billing import Facture, Paiement, ItemFacture
from models.service import Service, Lit
from utils.security import get_password_hash

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Données de base
SPECIALITES = ["Cardiologie", "Pédiatrie", "Chirurgie", "Médecine générale", "Gynécologie", "Dermatologie", "Neurologie"]
MOTIFS_RDV = ["Consultation générale", "Suivi", "Douleur abdominale", "Fièvre", "Check-up annuel", "Vaccination", "Contrôle"]
DIAGNOSTICS = ["Grippe", "Hypertension", "Diabète type 2", "Gastrite", "Migraine", "Dermatite", "Anxiété"]

async def clear_database():
    """Nettoyer la base de données avant d'ajouter les nouvelles données."""
    collections = [
        'users', 'patients', 'appointments', 'consultations', 'prescriptions',
        'drug_categories', 'medicaments', 'pharmacy_stock',
        'blood_donors', 'blood_stock', 'factures', 'paiements',
        'services', 'lits', 'audit_logs'
    ]
    for coll in collections:
        await db[coll].delete_many({})
    print("✓ Base de données nettoyée")

async def create_users():
    """Créer les utilisateurs avec différents rôles."""
    users = []
    
    # 2 Admins
    for i in range(1, 3):
        user = UserInDB(
            email=f"admin{i}@clinique.com",
            nom=f"Admin{i}",
            prenom="Système",
            role="admin",
            telephone=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            password_hash=get_password_hash("admin123"),
            actif=True
        )
        users.append(user)
    
    # 5 Médecins
    noms_medecins = ["Diop", "Ndiaye", "Fall", "Sow", "Sy"]
    prenoms = ["Amadou", "Fatou", "Mamadou", "Aïssatou", "Omar"]
    for i, (nom, prenom) in enumerate(zip(noms_medecins, prenoms), 1):
        user = UserInDB(
            email=f"medecin{i}@clinique.com",
            nom=nom,
            prenom=prenom,
            role="médecin",
            specialite=random.choice(SPECIALITES),
            telephone=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            password_hash=get_password_hash("medecin123"),
            actif=True
        )
        users.append(user)
    
    # 5 Infirmières
    noms_infirmieres = ["Sarr", "Kane", "Gueye", "Diouf", "Ba"]
    for i, nom in enumerate(noms_infirmieres, 1):
        user = UserInDB(
            email=f"infirmiere{i}@clinique.com",
            nom=nom,
            prenom=f"Marie" if i % 2 == 0 else "Khady",
            role="infirmière",
            telephone=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            password_hash=get_password_hash("infirmiere123"),
            actif=True
        )
        users.append(user)
    
    # 3 Pharmaciens
    for i in range(1, 4):
        user = UserInDB(
            email=f"pharmacien{i}@clinique.com",
            nom=f"Pharmacien{i}",
            prenom="Abdoulaye" if i % 2 == 0 else "Bineta",
            role="pharmacien",
            telephone=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            password_hash=get_password_hash("pharmacien123"),
            actif=True
        )
        users.append(user)
    
    # 2 Comptables
    for i in range(1, 3):
        user = UserInDB(
            email=f"comptable{i}@clinique.com",
            nom=f"Comptable{i}",
            prenom="Moussa" if i == 1 else "Awa",
            role="comptable",
            telephone=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            password_hash=get_password_hash("comptable123"),
            actif=True
        )
        users.append(user)
    
    # 10 Patients
    noms_patients = ["Diallo", "Thiam", "Cisse", "Ndao", "Toure", "Ly", "Faye", "Mbengue", "Drame", "Seck"]
    prenoms_patients = ["Ibrahima", "Mariama", "Cheikh", "Astou", "Ousmane", "Coumba", "Aliou", "Daba", "Modou", "Ndeye"]
    for i, (nom, prenom) in enumerate(zip(noms_patients, prenoms_patients), 1):
        user = UserInDB(
            email=f"patient{i}@email.com",
            nom=nom,
            prenom=prenom,
            role="patient",
            telephone=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            password_hash=get_password_hash("patient123"),
            actif=True
        )
        users.append(user)
    
    # Sauvegarder dans la base
    for user in users:
        doc = user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.users.insert_one(doc)
    
    print(f"✓ {len(users)} utilisateurs créés")
    return users

async def create_patients(users):
    """Créer les dossiers patients."""
    patient_users = [u for u in users if u.role == "patient"]
    patients = []
    groupes_sanguins = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    for i, user in enumerate(patient_users, 1):
        patient = Patient(
            user_id=user.id,
            numero_dossier=f"P-2025-{str(i).zfill(4)}",
            date_naissance=date(random.randint(1950, 2010), random.randint(1, 12), random.randint(1, 28)),
            sexe="M" if i % 2 == 0 else "F",
            groupe_sanguin=random.choice(groupes_sanguins),
            adresse=f"Quartier {random.choice(['Plateau', 'Mermoz', 'Sacré-Coeur', 'Almadies', 'Ouakam'])}, Dakar",
            contact_urgence_nom=f"Contact{i}",
            contact_urgence_tel=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            historique_medical=f"Historique médical du patient {i}",
            allergies="Aucune allergie connue" if i % 3 != 0 else "Allergie à la pénicilline"
        )
        patients.append(patient)
        
        doc = patient.model_dump()
        doc['date_naissance'] = doc['date_naissance'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.patients.insert_one(doc)
    
    print(f"✓ {len(patients)} dossiers patients créés")
    return patients

async def create_services():
    """Créer les services de la clinique."""
    services_data = [
        {"nom": "Cardiologie", "description": "Service de cardiologie", "nombre_lits": 15, "etage": "2"},
        {"nom": "Pédiatrie", "description": "Service de pédiatrie", "nombre_lits": 20, "etage": "1"},
        {"nom": "Chirurgie", "description": "Bloc opératoire et chirurgie", "nombre_lits": 12, "etage": "3"},
        {"nom": "Urgences", "description": "Service des urgences", "nombre_lits": 10, "etage": "RDC"},
        {"nom": "Maternité", "description": "Service de maternité", "nombre_lits": 18, "etage": "1"}
    ]
    
    services = []
    for data in services_data:
        service = Service(**data)
        doc = service.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.services.insert_one(doc)
        services.append(service)
    
    print(f"✓ {len(services)} services créés")
    return services

async def create_lits(services, patients):
    """Créer les lits dans les services."""
    lits = []
    statuts = ["disponible", "occupé", "disponible", "disponible"]
    
    for service in services:
        for i in range(1, min(service.nombre_lits, 8) + 1):
            statut = random.choice(statuts)
            lit = Lit(
                numero=f"{service.nom[:3].upper()}-{str(i).zfill(2)}",
                service_id=service.id,
                statut=statut,
                patient_id=random.choice(patients).id if statut == "occupé" and patients else None,
                date_admission=datetime.now() - timedelta(days=random.randint(1, 5)) if statut == "occupé" else None
            )
            lits.append(lit)
            
            doc = lit.model_dump()
            if doc.get('date_admission'):
                doc['date_admission'] = doc['date_admission'].isoformat()
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            await db.lits.insert_one(doc)
    
    print(f"✓ {len(lits)} lits créés")
    return lits

async def create_appointments(medecins, patients):
    """Créer des rendez-vous."""
    appointments = []
    
    for i in range(20):
        rdv = RendezVous(
            patient_id=random.choice(patients).id,
            medecin_id=random.choice(medecins).id,
            date_rdv=datetime.now() + timedelta(days=random.randint(-5, 15), hours=random.randint(8, 17)),
            type_rdv=random.choice(["présentiel", "présentiel", "présentiel", "en_ligne"]),
            motif=random.choice(MOTIFS_RDV),
            online_meeting_url="https://zoom.us/j/123456789" if random.random() < 0.2 else None,
            statut=random.choice(["planifié", "confirmé", "terminé"])
        )
        appointments.append(rdv)
        
        doc = rdv.model_dump()
        doc['date_rdv'] = doc['date_rdv'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.appointments.insert_one(doc)
    
    print(f"✓ {len(appointments)} rendez-vous créés")
    return appointments

async def create_pharmacy():
    """Créer les catégories et médicaments."""
    # Catégories
    categories_data = [
        {"nom": "Antibiotiques", "description": "Médicaments antibactériens"},
        {"nom": "Antalgiques", "description": "Médicaments contre la douleur"},
        {"nom": "Anti-inflammatoires", "description": "Médicaments anti-inflammatoires"},
        {"nom": "Antihypertenseurs", "description": "Traitement de l'hypertension"},
        {"nom": "Vitamines", "description": "Compléments vitaminiques"}
    ]
    
    categories = []
    for data in categories_data:
        cat = CategorieMedicament(**data)
        doc = cat.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.drug_categories.insert_one(doc)
        categories.append(cat)
    
    # Médicaments
    medicaments_data = [
        {"nom": "Amoxicilline 500mg", "forme": "comprimé", "dosage": "500mg", "prix_unitaire": 500},
        {"nom": "Paracétamol 1000mg", "forme": "comprimé", "dosage": "1000mg", "prix_unitaire": 200},
        {"nom": "Ibuprofène 400mg", "forme": "comprimé", "dosage": "400mg", "prix_unitaire": 300},
        {"nom": "Enalapril 10mg", "forme": "comprimé", "dosage": "10mg", "prix_unitaire": 800},
        {"nom": "Vitamine C 500mg", "forme": "comprimé", "dosage": "500mg", "prix_unitaire": 250},
        {"nom": "Azithromycine 250mg", "forme": "comprimé", "dosage": "250mg", "prix_unitaire": 1200},
        {"nom": "Aspirine 100mg", "forme": "comprimé", "dosage": "100mg", "prix_unitaire": 150},
        {"nom": "Metformine 850mg", "forme": "comprimé", "dosage": "850mg", "prix_unitaire": 600}
    ]
    
    medicaments = []
    for data in medicaments_data:
        cat = random.choice(categories)
        med = Medicament(
            categorie_id=cat.id,
            fabricant=random.choice(["Pfizer", "Sanofi", "GSK", "Novartis"]),
            seuil_stock_min=random.randint(10, 30),
            **data
        )
        medicaments.append(med)
        
        doc = med.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.medicaments.insert_one(doc)
    
    # Stocks
    for med in medicaments:
        for _ in range(random.randint(1, 3)):
            stock = StockPharmacie(
                medicament_id=med.id,
                quantite=random.randint(20, 200),
                date_peremption=date.today() + timedelta(days=random.randint(30, 730)),
                numero_lot=f"LOT-{random.randint(1000, 9999)}",
                emplacement=f"Étagère {random.choice(['A', 'B', 'C'])}-{random.randint(1, 10)}"
            )
            
            doc = stock.model_dump()
            doc['date_peremption'] = doc['date_peremption'].isoformat()
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            await db.pharmacy_stock.insert_one(doc)
    
    print(f"✓ {len(categories)} catégories et {len(medicaments)} médicaments créés")
    return categories, medicaments

async def create_blood_bank():
    """Créer la banque de sang."""
    groupes_sanguins = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    # Donneurs
    donneurs = []
    for i in range(15):
        donneur = DonneurSang(
            nom=f"Donneur{i}",
            prenom=f"Prenom{i}",
            groupe_sanguin=random.choice(groupes_sanguins),
            telephone=f"+221 77 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
            email=f"donneur{i}@email.com",
            date_derniere_donation=date.today() - timedelta(days=random.randint(30, 180)),
            eligible=random.choice([True, True, True, False])
        )
        donneurs.append(donneur)
        
        doc = donneur.model_dump()
        if doc.get('date_derniere_donation'):
            doc['date_derniere_donation'] = doc['date_derniere_donation'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.blood_donors.insert_one(doc)
    
    # Stocks de sang
    for _ in range(25):
        stock = StockSang(
            groupe_sanguin=random.choice(groupes_sanguins),
            quantite_ml=450,
            numero_poche=f"POCHE-{random.randint(10000, 99999)}",
            date_collecte=date.today() - timedelta(days=random.randint(1, 20)),
            date_expiration=date.today() + timedelta(days=random.randint(15, 35)),
            donneur_id=random.choice(donneurs).id if random.random() < 0.7 else None,
            statut=random.choice(["disponible", "disponible", "disponible", "réservé"])
        )
        
        doc = stock.model_dump()
        doc['date_collecte'] = doc['date_collecte'].isoformat()
        doc['date_expiration'] = doc['date_expiration'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.blood_stock.insert_one(doc)
    
    print(f"✓ {len(donneurs)} donneurs et 25 poches de sang créés")

async def create_billing(patients):
    """Créer des factures et paiements."""
    actes = [
        {"description": "Consultation générale", "prix": 15000},
        {"description": "Échographie", "prix": 25000},
        {"description": "Radiographie", "prix": 20000},
        {"description": "Analyse sanguine", "prix": 18000},
        {"description": "Hospitalisation (jour)", "prix": 35000}
    ]
    
    for i in range(15):
        patient = random.choice(patients)
        items = [
            ItemFacture(
                description=random.choice(actes)["description"],
                quantite=random.randint(1, 3),
                prix_unitaire=random.choice(actes)["prix"],
                total=0
            )
            for _ in range(random.randint(1, 3))
        ]
        
        # Calculer les totaux
        for item in items:
            item.total = item.quantite * item.prix_unitaire
        
        montant_total = sum(item.total for item in items)
        
        facture = Facture(
            patient_id=patient.id,
            montant_total=montant_total,
            statut=random.choice(["en_attente", "payée", "payée", "partiellement_payée"]),
            items=items,
            date_echeance=datetime.now() + timedelta(days=30)
        )
        
        doc = facture.model_dump()
        if doc.get('date_echeance'):
            doc['date_echeance'] = doc['date_echeance'].isoformat()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.factures.insert_one(doc)
        
        # Créer des paiements pour les factures payées
        if facture.statut in ["payée", "partiellement_payée"]:
            montant_paye = montant_total if facture.statut == "payée" else montant_total * 0.5
            paiement = Paiement(
                facture_id=facture.id,
                montant=montant_paye,
                methode=random.choice(["espèces", "carte", "virement", "mobile_money"]),
                reference=f"PAY-{random.randint(10000, 99999)}"
            )
            
            doc = paiement.model_dump()
            doc['date_paiement'] = doc['date_paiement'].isoformat()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.paiements.insert_one(doc)
    
    print("✓ 15 factures et paiements créés")

async def main():
    """Fonction principale pour générer toutes les données."""
    print("\n🏥 Génération des données de démonstration...\n")
    
    await clear_database()
    
    users = await create_users()
    
    # Séparer les utilisateurs par rôle
    medecins = [u for u in users if u.role == "médecin"]
    
    patients = await create_patients(users)
    services = await create_services()
    lits = await create_lits(services, patients)
    appointments = await create_appointments(medecins, patients)
    await create_pharmacy()
    await create_blood_bank()
    await create_billing(patients)
    
    print("\n✅ Données de démonstration générées avec succès!")
    print("\n📋 Informations de connexion:")
    print("   Admin:      admin1@clinique.com / admin123")
    print("   Médecin:    medecin1@clinique.com / medecin123")
    print("   Infirmière: infirmiere1@clinique.com / infirmiere123")
    print("   Pharmacien: pharmacien1@clinique.com / pharmacien123")
    print("   Comptable:  comptable1@clinique.com / comptable123")
    print("   Patient:    patient1@email.com / patient123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
