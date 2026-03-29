from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_workflow():
    print("--- Starting Backend Verification ---")
    
    # 1. Register a user
    print("1. Registering user...")
    response = client.post("/auth/register", json={
        "email": "test@uvci.edu.ci",
        "password": "password123",
        "role": "admin"
    })
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    user_id = response.json()["id"]
    
    # 2. Login
    print("2. Logging in...")
    response = client.post("/auth/login", json={
        "email": "test@uvci.edu.ci",
        "password": "password123"
    })
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 3. Create a teacher
    print("3. Creating teacher...")
    response = client.post("/teachers/", json={
        "nom": "KOFFI",
        "prenom": "Jean",
        "grade": "Maitre-Assistant",
        "statut": "Permanent",
        "departement": "Informatique",
        "taux_horaire": 10000,
        "email": "koffi.jean@uvci.edu.ci",
        "telephone": "0102030405",
        "user_id": user_id
    })
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    teacher_id = response.json()["id"]
    
    # 4. Create a course
    print("4. Creating course...")
    response = client.post("/courses/", json={
        "intitule": "Base de donnees",
        "filiere": "Informatique",
        "niveau": "L2",
        "semestre": "S1",
        "nb_heures": 40,
        "nb_credits": 4
    })
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    course_id = response.json()["id"]
    
    # 5. Log activity
    # First, need a resource. We need to manually add it or have an endpoint. 
    # Let's assume we have a way to link it. In our models, Resource has course_id and level.
    # Note: I didn't create a POST /resources endpoint yet. I'll use the DB directly for test or add it.
    # Let's just create an activity and mock/ensure resource exists.
    from app.db.database import SessionLocal
    from app.models.models import Resource, AcademicYear
    db = SessionLocal()
    res = Resource(type="Video", niveau_complexite=2, course_id=course_id, teacher_id=teacher_id)
    ay = AcademicYear(libelle="2025-2026")
    db.add(res)
    db.add(ay)
    db.commit()
    db.refresh(res)
    db.refresh(ay)
    resource_id = res.id
    academic_year_id = ay.id
    db.close()
    
    print(f"5. Logging activity (1 sequence Level 2)...")
    response = client.post("/activities/", json={
        "type": "creation",
        "resource_id": resource_id,
        "teacher_id": teacher_id,
        "nb_sequences": 1,
        "academic_year_id": academic_year_id
    })
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    volume = response.json()["volume_horaire_calcule"]
    print(f"Calculated Volume: {volume} h (Expected: 0.75 h)")
    assert volume == 0.75
    
    # 6. Check total volume
    print("6. Checking total volume...")
    response = client.get(f"/activities/volume/{teacher_id}")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    print(f"Total Volume: {response.json()['total_volume_horaire']} h")
    
    # 7. Check Exports
    print("7. Testing PDF Export...")
    response = client.get(f"/exports/pdf/{teacher_id}")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    print("8. Testing Excel Export...")
    response = client.get("/exports/excel")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    assert "spreadsheet" in response.headers["content-type"]
    
    print("--- Verification Successful! ---")

if __name__ == "__main__":
    test_workflow()
