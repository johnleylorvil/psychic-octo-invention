# Clinique+ — Système de Gestion de Clinique (SGC)

## Problème / Objectif
Application full-stack de gestion de clinique avec contrôle d'accès par rôle (RBAC).
Rôles : Admin, Médecin, Infirmière, Pharmacien, Comptable, Patient.
Modules : patients, rendez-vous (avec lien visio URL), consultations/prescriptions,
pharmacie (stock/péremption), banque de sang, lits/services, facturation, dashboards par rôle.
Exigence forte : AUCUNE page placeholder « En développement ». Langue : français.

## Stack
FastAPI + React + MongoDB + JWT. Shadcn/UI + Tailwind. Universal Emergent LLM key (non utilisé pour l'instant).

## Architecture
- backend/: models/, routers/ (auth, users, patients, appointments, consultations, pharmacy, blood_bank, billing, services, dashboard), services/notification_service.py (log SMS/email), middleware/permissions.py (require_roles).
- frontend/src/pages/: admin, doctor, nurse, pharmacist, accountant, patient. utils/pdfExport.js (export PDF via impression navigateur).

## Implémenté (à jour — Juin 2026)
- Backend complet : 9 domaines, filtrage par rôle (patient/médecin voient leurs données), RBAC sur endpoints sensibles. 25/25 tests backend OK.
- Service de notifications (rappel RDV, prescription, alertes stock/sang) — LOG uniquement (simulation).
- Frontend : toutes les routes câblées, ZÉRO placeholder « En développement ».
  - Admin : dashboard, patients (liste/form/détail), RDV, pharmacie, banque sang (+donneur), services/lits (+form service, +form lit), users, facturation (+PDF).
  - Médecin : dashboard, patients, RDV, consultations (+création), prescriptions (+création, +PDF).
  - Infirmière : dashboard, patients, RDV, lits (changement statut), banque sang (+ajout donneur).
  - Pharmacien : dashboard, médicaments (+ajout avec catégorie), stocks+alertes, prescriptions (+PDF).
  - Comptable : dashboard, factures (stats, encaisser, PDF), paiements.
  - Patient : dashboard, RDV, consultations, factures (+PDF).
- Export PDF : via window.print (utils/pdfExport.js) sur factures et ordonnances. Architecture prête pour un service serveur.

## Corrections notables (fork actuel)
- FIX backend : ordre des routes /services (/{service_id} masquait /lits) — réordonné.
- FIX backend : ProxyHeadersMiddleware ajouté (Mixed Content sur redirections 307 derrière ingress https).
- FIX frontend : formulaire médicament inclut categorie_id (requis) ; page prescriptions pharmacien ne dépend plus de /users (403 pharmacien).

## Identifiants de test
Voir /app/memory/test_credentials.md.

## Backlog / Améliorations futures (P1/P2)
- P1 : Export PDF côté serveur (ReportLab) pour factures/ordonnances officielles.
- P1 : Notifications réelles (Twilio SMS / Resend email) au lieu de log.
- P2 : Téléconsultation intégrée (au lieu d'un simple lien URL).
- P2 : Recherche/pagination avancée, audit log UI.
- P2 : Édition/suppression médicaments, gestion lots de stock côté pharmacien.
