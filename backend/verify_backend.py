"""Smoke test end-to-end : login admin -> teachers -> courses -> activity -> exports.

Utilise le compte admin seedé automatiquement (admin@uvci.ci / admin123).
À lancer avec : python verify_backend.py
"""

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_workflow():
    print("--- Verification backend UVCI ---")

    # 1. Login admin (compte seedé)
    print("1. Login admin...")
    r = client.post("/auth/login", json={"email": "admin@uvci.ci", "password": "admin123"})
    assert r.status_code == 200, f"Login admin échoué : {r.status_code} {r.text}"
    token = r.json()["access_token"]
    print(f"   ok (role={r.json()['role']})")

    headers = _auth_headers(token)

    # 2. /auth/me
    print("2. /auth/me...")
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200 and r.json()["role"] == "admin"
    print("   ok")

    # 3. Liste enseignants
    print("3. Liste enseignants...")
    r = client.get("/teachers/", headers=headers)
    assert r.status_code == 200, r.text
    teachers = r.json()
    assert len(teachers) >= 1
    teacher_id = teachers[0]["id"]
    print(f"   ok ({len(teachers)} enseignants, id pris = {teacher_id})")

    # 4. Liste cours
    print("4. Liste cours...")
    r = client.get("/courses/", headers=headers)
    assert r.status_code == 200, r.text
    courses = r.json()
    assert len(courses) >= 1
    course_id = courses[0]["id"]
    print(f"   ok ({len(courses)} cours, id pris = {course_id})")

    # 5. Création activité (Niveau 2 création, 1 séquence → attendu 0.75 h)
    print("5. Création activité (Niveau 2 / création / 1 séquence)...")
    r = client.post(
        "/activities/",
        headers=headers,
        json={
            "teacher_id": teacher_id,
            "course_id": course_id,
            "type_activite": "creation",
            "niveau_complexite": 2,
            "nb_sequences": 1,
        },
    )
    assert r.status_code == 200, r.text
    activity = r.json()
    assert activity["volume_horaire_calcule"] == 0.75, (
        f"Volume attendu 0.75 h, obtenu {activity['volume_horaire_calcule']}"
    )
    print(f"   ok (volume = {activity['volume_horaire_calcule']} h, conforme au barème)")

    # 6. Volume total enseignant
    print("6. Volume total enseignant...")
    r = client.get(f"/activities/volume/{teacher_id}", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    print(f"   ok (volume_total = {body['volume_total']} h, validé = {body['volume_valide']} h)")

    # 7. Dashboard stats (admin)
    print("7. Dashboard stats...")
    r = client.get("/dashboard/stats", headers=headers)
    assert r.status_code == 200, r.text
    stats = r.json()
    print(f"   ok ({stats['total_teachers']} enseignants, {stats['volume_total']} h cumulées)")

    # 8. Export PDF
    print("8. Export PDF...")
    r = client.get(f"/exports/pdf/{teacher_id}", headers=headers)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/pdf"
    print(f"   ok ({len(r.content)} octets)")

    # 9. Export Excel
    print("9. Export Excel...")
    r = client.get("/exports/excel", headers=headers)
    assert r.status_code == 200, r.text
    assert "spreadsheet" in r.headers["content-type"]
    print(f"   ok ({len(r.content)} octets)")

    # 10. Garde-fou sécurité : accès non authentifié refusé
    print("10. Garde-fou : /dashboard/stats sans token doit refuser...")
    r = client.get("/dashboard/stats")
    assert r.status_code in (401, 403), f"Sécurité cassée : status {r.status_code}"
    print(f"   ok (refus avec {r.status_code})")

    print("--- Verification reussie ---")


if __name__ == "__main__":
    test_workflow()
