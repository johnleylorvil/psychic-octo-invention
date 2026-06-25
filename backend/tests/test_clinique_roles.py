"""
Backend regression tests for Clinique+ SGC.
Covers login for each role, role-filtered endpoints, doctor consultations/prescriptions,
nurse beds/blood bank, pharmacist medicaments, accountant billing/paiements,
patient self-data, and admin services/lits.
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cabinet-digital-2.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

CREDS = {
    "admin":      ("admin1@clinique.com",      "admin123"),
    "médecin":    ("medecin1@clinique.com",    "medecin123"),
    "infirmière": ("infirmiere1@clinique.com", "infirmiere123"),
    "pharmacien": ("pharmacien1@clinique.com", "pharmacien123"),
    "comptable":  ("comptable1@clinique.com",  "comptable123"),
    "patient":    ("patient1@email.com",       "patient123"),
}


def _login(email, password):
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=20)
    assert r.status_code == 200, f"Login failed for {email}: {r.status_code} {r.text}"
    return r.json()


@pytest.fixture(scope="session")
def tokens():
    out = {}
    for role, (email, pwd) in CREDS.items():
        data = _login(email, pwd)
        assert data["user"]["role"] == role, f"Role mismatch for {email}: got {data['user']['role']}"
        out[role] = {"token": data["access_token"], "user": data["user"]}
    return out


def h(tok):
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


# ---------- AUTH ----------
class TestAuth:
    def test_all_roles_login(self, tokens):
        assert set(tokens.keys()) == set(CREDS.keys())
        for role, info in tokens.items():
            assert info["token"]
            assert info["user"]["role"] == role

    def test_wrong_password(self):
        r = requests.post(f"{API}/auth/login", json={"email": "admin1@clinique.com", "password": "wrong"})
        assert r.status_code in (400, 401, 403)


# ---------- ADMIN ----------
class TestAdmin:
    def test_patients_list(self, tokens):
        r = requests.get(f"{API}/patients/", headers=h(tokens["admin"]["token"]))
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_users_list(self, tokens):
        r = requests.get(f"{API}/users/", headers=h(tokens["admin"]["token"]))
        assert r.status_code == 200

    def test_services_list(self, tokens):
        r = requests.get(f"{API}/services/", headers=h(tokens["admin"]["token"]))
        assert r.status_code == 200

    def test_create_service_and_lit(self, tokens):
        svc_name = f"TEST_Service_{uuid.uuid4().hex[:6]}"
        r = requests.post(f"{API}/services/",
                          headers=h(tokens["admin"]["token"]),
                          json={"nom": svc_name, "description": "Test", "capacite": 10})
        assert r.status_code in (200, 201), r.text
        service = r.json()
        svc_id = service.get("id")
        assert svc_id

        # Create lit
        lit_num = f"TEST_LIT_{uuid.uuid4().hex[:5]}"
        r2 = requests.post(f"{API}/services/lits",
                           headers=h(tokens["admin"]["token"]),
                           json={"service_id": svc_id, "numero": lit_num, "statut": "disponible"})
        assert r2.status_code in (200, 201), r2.text
        lit = r2.json()
        assert lit.get("numero") == lit_num
        pytest.lit_id = lit["id"]

    def test_patient_detail_get(self, tokens):
        r = requests.get(f"{API}/patients/", headers=h(tokens["admin"]["token"]))
        patients = r.json()
        if not patients:
            pytest.skip("No patients to detail")
        pid = patients[0]["id"]
        r2 = requests.get(f"{API}/patients/{pid}", headers=h(tokens["admin"]["token"]))
        assert r2.status_code == 200
        assert r2.json()["id"] == pid


# ---------- MEDECIN ----------
class TestMedecin:
    def test_patients_visible(self, tokens):
        r = requests.get(f"{API}/patients/", headers=h(tokens["médecin"]["token"]))
        assert r.status_code == 200

    def test_appointments_filtered(self, tokens):
        r = requests.get(f"{API}/appointments/", headers=h(tokens["médecin"]["token"]))
        assert r.status_code == 200
        med_id = tokens["médecin"]["user"]["id"]
        for a in r.json():
            assert a.get("medecin_id") == med_id, f"Doctor seeing other doctor's appointment: {a}"

    def test_consultations_and_prescription_flow(self, tokens):
        med_tok = tokens["médecin"]["token"]
        med_id = tokens["médecin"]["user"]["id"]

        # Pick a patient
        patients = requests.get(f"{API}/patients/", headers=h(med_tok)).json()
        if not patients:
            pytest.skip("No patients")
        patient_id = patients[0]["id"]

        # Create consultation
        cons_payload = {
            "patient_id": patient_id,
            "medecin_id": med_id,
            "motif": "TEST_motif",
            "diagnostic": "TEST_diag",
            "observations": "obs",
        }
        r = requests.post(f"{API}/consultations/", headers=h(med_tok), json=cons_payload)
        assert r.status_code == 201, r.text
        cons = r.json()
        assert cons["motif"] == "TEST_motif"
        cons_id = cons["id"]

        # List consultations -> should appear & only for this doctor
        rl = requests.get(f"{API}/consultations/", headers=h(med_tok))
        assert rl.status_code == 200
        all_cons = rl.json()
        assert any(c["id"] == cons_id for c in all_cons)
        for c in all_cons:
            assert c.get("medecin_id") == med_id

        # Create prescription
        presc_payload = {
            "consultation_id": cons_id,
            "patient_id": patient_id,
            "medecin_id": med_id,
            "medicaments": [
                {"medicament_id": "test-med-id", "nom": "TEST_paracetamol",
                 "dosage": "500mg", "frequence": "3x/j", "duree": "5j"}
            ],
            "instructions_generales": "Après repas",
        }
        rp = requests.post(f"{API}/consultations/prescriptions",
                           headers=h(med_tok), json=presc_payload)
        assert rp.status_code == 201, rp.text
        presc = rp.json()
        assert len(presc["medicaments"]) == 1

        # List prescriptions
        rpl = requests.get(f"{API}/consultations/prescriptions/", headers=h(med_tok))
        assert rpl.status_code == 200
        assert any(p["id"] == presc["id"] for p in rpl.json())


# ---------- INFIRMIERE ----------
class TestInfirmiere:
    def test_patients(self, tokens):
        r = requests.get(f"{API}/patients/", headers=h(tokens["infirmière"]["token"]))
        assert r.status_code == 200

    def test_lits_list_and_update(self, tokens):
        tok = tokens["infirmière"]["token"]
        r = requests.get(f"{API}/services/lits", headers=h(tok))
        assert r.status_code == 200, r.text
        lits = r.json()
        if not lits:
            pytest.skip("No beds")
        lit = lits[0]
        new_statut = "occupé" if lit["statut"] != "occupé" else "disponible"
        ru = requests.put(f"{API}/services/lits/{lit['id']}",
                          headers=h(tok), json={"statut": new_statut})
        assert ru.status_code in (200, 204), ru.text
        # verify
        verify = requests.get(f"{API}/services/lits", headers=h(tok)).json()
        updated = next((l for l in verify if l["id"] == lit["id"]), None)
        assert updated and updated["statut"] == new_statut

    def test_blood_bank_donneurs_and_stock(self, tokens):
        tok = tokens["infirmière"]["token"]
        rd = requests.get(f"{API}/blood-bank/donneurs", headers=h(tok))
        assert rd.status_code == 200
        rs = requests.get(f"{API}/blood-bank/stock", headers=h(tok))
        assert rs.status_code == 200

        # Create donneur
        donneur_payload = {
            "nom": "TEST_DONOR",
            "prenom": "X",
            "groupe_sanguin": "O+",
            "telephone": "+221 77 000 00 00",
            "date_naissance": "1990-01-01",
        }
        rc = requests.post(f"{API}/blood-bank/donneurs", headers=h(tok), json=donneur_payload)
        assert rc.status_code in (200, 201), rc.text


# ---------- PHARMACIEN ----------
class TestPharmacien:
    def test_medicaments_list_and_create(self, tokens):
        tok = tokens["pharmacien"]["token"]
        rl = requests.get(f"{API}/pharmacy/medicaments", headers=h(tok))
        assert rl.status_code == 200
        # Need a categorie - fetch or create
        rcat = requests.get(f"{API}/pharmacy/categories", headers=h(tok))
        if rcat.status_code == 200 and rcat.json():
            cat_id = rcat.json()[0]["id"]
        else:
            rcc = requests.post(f"{API}/pharmacy/categories", headers=h(tok),
                                json={"nom": f"TEST_CAT_{uuid.uuid4().hex[:5]}"})
            assert rcc.status_code in (200, 201), rcc.text
            cat_id = rcc.json()["id"]
        payload = {
            "nom": f"TEST_MED_{uuid.uuid4().hex[:5]}",
            "categorie_id": cat_id,
            "dosage": "500mg",
            "forme": "comprimé",
            "prix_unitaire": 100,
            "seuil_stock_min": 10,
        }
        rc = requests.post(f"{API}/pharmacy/medicaments", headers=h(tok), json=payload)
        assert rc.status_code in (200, 201), rc.text

    def test_stocks(self, tokens):
        tok = tokens["pharmacien"]["token"]
        r = requests.get(f"{API}/pharmacy/medicaments", headers=h(tok))
        assert r.status_code == 200

    def test_prescriptions_visible(self, tokens):
        tok = tokens["pharmacien"]["token"]
        r = requests.get(f"{API}/consultations/prescriptions/", headers=h(tok))
        assert r.status_code == 200


# ---------- COMPTABLE ----------
class TestComptable:
    def test_factures_list(self, tokens):
        tok = tokens["comptable"]["token"]
        r = requests.get(f"{API}/billing/factures", headers=h(tok))
        assert r.status_code == 200

    def test_stats(self, tokens):
        tok = tokens["comptable"]["token"]
        r = requests.get(f"{API}/billing/stats", headers=h(tok))
        assert r.status_code == 200
        data = r.json()
        for k in ["total_factures", "total_paye", "total_impaye"]:
            assert k in data

    def test_paiement_encaisser_flow(self, tokens):
        tok = tokens["comptable"]["token"]
        # Find or create a facture
        factures = requests.get(f"{API}/billing/factures", headers=h(tok)).json()
        patients = requests.get(f"{API}/patients/", headers=h(tokens["admin"]["token"])).json()
        if not patients:
            pytest.skip("No patients")
        # Create new facture
        fpayload = {
            "patient_id": patients[0]["id"],
            "montant_total": 5000,
            "items": [{"description": "TEST_consult", "quantite": 1, "prix_unitaire": 5000, "total": 5000}],
            "statut": "en_attente",
        }
        rc = requests.post(f"{API}/billing/factures", headers=h(tok), json=fpayload)
        assert rc.status_code in (200, 201), rc.text
        facture = rc.json()
        fid = facture["id"]

        # Encaisser
        ppayload = {
            "facture_id": fid,
            "montant": 5000,
            "methode": "espèces",
            "reference": "TEST_REF",
        }
        rp = requests.post(f"{API}/billing/paiements", headers=h(tok), json=ppayload)
        assert rp.status_code in (200, 201), rp.text

        # Verify facture marked payée
        rget = requests.get(f"{API}/billing/factures/{fid}", headers=h(tok))
        assert rget.status_code == 200
        assert rget.json()["statut"] == "payée"

        # List paiements
        rlp = requests.get(f"{API}/billing/paiements", headers=h(tok))
        assert rlp.status_code == 200


# ---------- PATIENT ----------
class TestPatient:
    def test_appointments_self(self, tokens):
        tok = tokens["patient"]["token"]
        r = requests.get(f"{API}/appointments/", headers=h(tok))
        assert r.status_code == 200

    def test_consultations_self(self, tokens):
        tok = tokens["patient"]["token"]
        r = requests.get(f"{API}/consultations/", headers=h(tok))
        assert r.status_code == 200

    def test_factures_self(self, tokens):
        tok = tokens["patient"]["token"]
        r = requests.get(f"{API}/billing/factures", headers=h(tok))
        assert r.status_code == 200


# ---------- RBAC ----------
class TestRBAC:
    def test_patient_cannot_access_users(self, tokens):
        r = requests.get(f"{API}/users/", headers=h(tokens["patient"]["token"]))
        assert r.status_code in (401, 403), f"Patient should not see users list, got {r.status_code}"

    def test_patient_cannot_create_facture(self, tokens):
        r = requests.post(f"{API}/billing/factures", headers=h(tokens["patient"]["token"]),
                          json={"patient_id": "x", "montant_total": 100, "items": []})
        assert r.status_code in (401, 403)

    def test_infirmiere_cannot_create_consultation(self, tokens):
        r = requests.post(f"{API}/consultations/", headers=h(tokens["infirmière"]["token"]),
                          json={"patient_id": "x", "medecin_id": "y", "motif": "x"})
        assert r.status_code in (401, 403)
