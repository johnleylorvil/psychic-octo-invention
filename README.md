# Système de Gestion de Clinique en Ligne

## 📋 Vue d'ensemble

Application web complète de gestion de clinique développée avec **React** (frontend) et **FastAPI** (backend), utilisant **MongoDB** comme base de données.

## ✨ Fonctionnalités principales

### Gestion multi-rôles
- **Administrateur** : Configuration système, gestion des utilisateurs, supervision globale
- **Médecin** : Consultations, prescriptions, suivi des patients
- **Infirmière** : Admissions, gestion des lits, banque de sang
- **Pharmacien** : Gestion des médicaments et stocks
- **Comptable** : Facturation et suivi des paiements
- **Patient** : Portail personnel, rendez-vous, consultations en ligne

### Modules implémentés

#### 1. Gestion des Patients
- Dossiers médicaux numériques complets
- Historique médical
- Informations administratives et biométriques
- Gestion des admissions et allocation des lits

#### 2. Gestion des Rendez-vous
- Planification intuitive
- Rendez-vous présentiels et en ligne
- Système de rappels automatiques (logs)
- Gestion des statuts (planifié, confirmé, terminé, annulé)

#### 3. Consultations & Prescriptions
- Enregistrement des consultations
- Notes médicales et diagnostics
- Prescriptions numériques sécurisées
- Transmission automatique à la pharmacie

#### 4. Gestion de la Pharmacie
- Catalogue de médicaments par catégories
- Gestion des stocks en temps réel
- Alertes de stock faible
- Surveillance des dates de péremption

#### 5. Banque de Sang
- Base de données des donneurs
- Classification par groupes sanguins
- Suivi des stocks disponibles
- Alertes de stock critique

#### 6. Facturation
- Génération automatique des factures
- Suivi des paiements
- Historique financier par patient
- Rapports financiers détaillés

#### 7. Tableaux de Bord
- Indicateurs clés de performance (KPIs)
- Statistiques en temps réel
- Alertes intelligentes
- Rapports d'activité

#### 8. Consultation à Distance
- Lien URL pour visioconférence (Zoom, Google Meet)
- Gestion des rendez-vous en ligne

## 🚀 Démarrage rapide

### Comptes de test

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Admin | admin1@clinique.com | admin123 |
| Médecin | medecin1@clinique.com | medecin123 |
| Infirmière | infirmiere1@clinique.com | infirmiere123 |
| Pharmacien | pharmacien1@clinique.com | pharmacien123 |
| Comptable | comptable1@clinique.com | comptable123 |
| Patient | patient1@email.com | patient123 |

## 🔒 Sécurité

- **Authentification JWT** : Tokens sécurisés
- **Contrôle d'accès par rôles** : Permissions granulaires
- **Hash des mots de passe** : Bcrypt
- **Audit logging** : Traçabilité complète

## 🎨 Design

- **Thème médical professionnel** : Tons bleu et vert
- **Police moderne** : Inter
- **Interface responsive** : Compatible tous appareils

---

**Développé avec FastAPI + React + MongoDB**  
*Version 1.0.0*
