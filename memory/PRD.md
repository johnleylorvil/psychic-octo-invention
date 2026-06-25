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

## Audit & compléments (Juin 2026 — itération 2)
Audit des fonctionnalités manquantes (endpoints backend existants sans UI) → implémentées et testées (6/6 OK) :
- Création de facture : formulaire avec lignes + calcul auto du total (Admin /admin/billing/new + Comptable /comptable/factures/new).
- RDV admin : actions Éditer + Annuler (DELETE) directement depuis la liste.
- Pharmacie : ajout de lots de stock (numéro lot, quantité, péremption, emplacement).
- Banque de sang : ajout de poches de sang (groupe, n° poche, ml, dates, donneur) côté infirmière.

## Itération 3 (Juin 2026) — Prise de RDV patient + sécurité/UX
- Prise de rendez-vous en libre-service par le patient : page /patient/appointments/new, endpoint GET /users/medecins (accessible aux patients), le backend force le patient_id du demandeur et met le statut à « en_attente ». Testé 100%.
- Sécurité : POST /billing/factures recalcule montant_total à partir des lignes (anti-falsification client). Vérifié.
- UX : confirmation avant annulation de RDV et avant encaissement ; quantités min=1 sur les formulaires.
- FIX CRITIQUE : les pages patient (RDV, consultations) appelaient /users?role=médecin (403 patient) → le Promise.all échouait et le patient ne voyait jamais ses données. Corrigé via /users/medecins. Testé 100%, zéro 403.

## Backlog / Améliorations futures (P1/P2)
- P1 : Export PDF côté serveur (ReportLab) pour factures/ordonnances officielles.
- P1 : Notifications réelles (Twilio SMS / Resend email) au lieu de log.
- P2 : Téléconsultation intégrée (au lieu d'un simple lien URL).
- P2 : Recherche/pagination avancée, audit log UI.
- P2 : Édition/suppression médicaments, gestion lots de stock côté pharmacien.
