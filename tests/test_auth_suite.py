import sys
import os
import uuid
from typing import Dict, Any
from fastapi.testclient import TestClient

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.database.db import init_db, get_db_connection
from backend.app.auth.security import hash_password, verify_password, create_access_token

client = TestClient(app)

def setup_test_db():
    init_db()

# 1. Valid Signup Test
def test_valid_signup():
    email = f"student_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/signup", json={
        "name": "Arun Kumar",
        "email": email,
        "password": "Password123",
        "confirm_password": "Password123"
    })
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["name"] == "Arun Kumar"
    assert data["user"]["email"] == email.lower()
    return data

# 2. Invalid Email Test
def test_invalid_email_signup():
    resp = client.post("/api/auth/signup", json={
        "name": "Invalid User",
        "email": "not-an-email",
        "password": "Password123",
        "confirm_password": "Password123"
    })
    assert resp.status_code == 400
    assert "valid email" in resp.json()["detail"].lower()

# 3. Empty Email Test
def test_empty_email_signup():
    resp = client.post("/api/auth/signup", json={
        "name": "Empty Email",
        "email": "",
        "password": "Password123",
        "confirm_password": "Password123"
    })
    assert resp.status_code == 400
    assert "required" in resp.json()["detail"].lower()

# 4. Short Password Test (< 6 chars)
def test_short_password_signup():
    resp = client.post("/api/auth/signup", json={
        "name": "Short Pass",
        "email": f"short_{uuid.uuid4().hex[:6]}@example.com",
        "password": "123",
        "confirm_password": "123"
    })
    assert resp.status_code == 400
    assert "at least 6 characters" in resp.json()["detail"].lower()

# 5. Password Mismatch Test
def test_password_mismatch_signup():
    resp = client.post("/api/auth/signup", json={
        "name": "Mismatch User",
        "email": f"mismatch_{uuid.uuid4().hex[:6]}@example.com",
        "password": "Password123",
        "confirm_password": "DifferentPassword123"
    })
    assert resp.status_code == 400
    assert "match" in resp.json()["detail"].lower()

# 6. Valid Login Test
def test_valid_login():
    email = f"login_user_{uuid.uuid4().hex[:8]}@example.com"
    # Create account first
    client.post("/api/auth/signup", json={
        "name": "Login Test User",
        "email": email,
        "password": "ValidPassword999",
        "confirm_password": "ValidPassword999"
    })
    
    # Login
    resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "ValidPassword999"
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == email.lower()

# 7. Wrong Password Test
def test_wrong_password_login():
    email = f"wp_user_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/signup", json={
        "name": "WP User",
        "email": email,
        "password": "CorrectPassword123",
        "confirm_password": "CorrectPassword123"
    })
    
    resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "WrongPassword456"
    })
    assert resp.status_code == 401
    assert "invalid email or password" in resp.json()["detail"].lower()

# 8. Unknown Account Test
def test_unknown_account_login():
    resp = client.post("/api/auth/login", json={
        "email": f"nonexistent_{uuid.uuid4().hex[:8]}@example.com",
        "password": "SomePassword123"
    })
    assert resp.status_code == 401
    assert "invalid email or password" in resp.json()["detail"].lower()

# 9. Password Hashing Security Test (Plaintext not stored)
def test_password_never_stored_plaintext():
    email = f"security_{uuid.uuid4().hex[:8]}@example.com"
    pw = "SuperSecretPassword2026!"
    client.post("/api/auth/signup", json={
        "name": "Security Check",
        "email": email,
        "password": pw,
        "confirm_password": pw
    })
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
        assert row is not None
        pw_hash = row["password_hash"]
        assert pw_hash != pw
        assert pw not in pw_hash
        assert pw_hash.startswith("$2b$") or pw_hash.startswith("$2a$")

# 10. Guest Access Test (Public endpoints accessible without auth)
def test_guest_access_public_endpoints():
    # Health check
    resp = client.get("/api/health")
    assert resp.status_code == 200

    # Pulse
    resp = client.get("/api/pulse")
    assert resp.status_code == 200

    # Opportunities
    resp = client.get("/api/opportunities")
    assert resp.status_code == 200

    # Locations
    resp = client.get("/api/locations")
    assert resp.status_code == 200

# 11. Protected Endpoints Reject Unauthenticated Guests with 401
def test_protected_endpoints_reject_unauthenticated():
    # Saved Answers without token
    resp = client.get("/api/saved")
    assert resp.status_code == 401

    resp = client.post("/api/saved", json={
        "question": "What is the mess menu?",
        "answer": "Idli and chutney"
    })
    assert resp.status_code == 401

    # Personal Vault without token
    resp = client.get("/api/vault/documents")
    assert resp.status_code == 401

    resp = client.post("/api/vault/query", json={
        "query": "What is my syllabus?"
    })
    assert resp.status_code == 401

# 12. Refresh while logged in (/api/auth/me)
def test_me_endpoint_with_valid_token():
    auth_data = test_valid_signup()
    token = auth_data["access_token"]
    user_id = auth_data["user"]["id"]

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["id"] == user_id

# 13. Profile Preferences Update
def test_profile_preferences_update():
    auth_data = test_valid_signup()
    token = auth_data["access_token"]

    resp = client.put(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "role": "current_student",
            "department": "Artificial Intelligence & Data Science (AI&DS)",
            "year": "3rd Year",
            "semester": "Semester 6",
            "interests": ["Machine Learning", "Autonomous Drones"]
        }
    )
    assert resp.status_code == 200
    prof = resp.json()["profile"]
    assert prof["department"] == "Artificial Intelligence & Data Science (AI&DS)"
    assert "Autonomous Drones" in prof["interests"]

# 14. Saved Answers Belongs Strictly to Authenticated User
def test_saved_answers_user_association():
    auth_data = test_valid_signup()
    token = auth_data["access_token"]
    user_id = auth_data["user"]["id"]

    # Save an answer
    resp = client.post(
        "/api/saved",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "question": "What is the dress code on Wednesday?",
            "answer": "Formal attire is mandatory from Monday to Wednesday.",
            "sources": [{"title": "dress_code.txt"}]
        }
    )
    assert resp.status_code == 200
    saved_item = resp.json()
    assert saved_item["user_id"] == user_id

    # Retrieve saved answers
    resp = client.get("/api/saved", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert any(i["id"] == saved_item["id"] for i in items)

# 15. User A Cannot Access User B's Private Data (Saved Answers & Vault)
def test_user_a_cannot_access_user_b_data():
    # User A (Alice)
    alice = test_valid_signup()
    alice_token = alice["access_token"]
    alice_id = alice["user"]["id"]

    # User B (Bob)
    bob = test_valid_signup()
    bob_token = bob["access_token"]
    bob_id = bob["user"]["id"]

    # Alice saves an answer
    resp_a = client.post(
        "/api/saved",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={
            "question": "Alice's Secret Academic Question",
            "answer": "Alice's Private Grounded Answer",
            "sources": []
        }
    )
    alice_saved_id = resp_a.json()["id"]

    # Bob retrieves his saved answers; Alice's answer must NOT be present
    resp_b = client.get("/api/saved", headers={"Authorization": f"Bearer {bob_token}"})
    assert resp_b.status_code == 200
    bob_items = resp_b.json()
    assert not any(i["id"] == alice_saved_id for i in bob_items)

    # Bob tries to delete Alice's saved answer; must return 404/unauthorized
    resp_del = client.delete(
        f"/api/saved/{alice_saved_id}",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert resp_del.status_code == 404

    # Bob tries to spoof Alice's user_id in query; server ignores client user_id and uses Bob's token
    resp_spoof = client.get(
        f"/api/saved?user_id={alice_id}",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert resp_spoof.status_code == 200
    spoofed_items = resp_spoof.json()
    assert not any(i["id"] == alice_saved_id for i in spoofed_items)

# 16. Personal Vault Document Isolation (User A vs User B)
def test_vault_user_isolation_via_api():
    alice = test_valid_signup()
    alice_token = alice["access_token"]

    bob = test_valid_signup()
    bob_token = bob["access_token"]

    # Alice uploads a private notes file
    alice_file_content = b"ALICE PRIVATE PROJECT PROPOSAL: SECURE RAG AGENT 2026"
    resp_upload = client.post(
        "/api/vault/upload",
        headers={"Authorization": f"Bearer {alice_token}"},
        files={"file": ("alice_notes.txt", alice_file_content, "text/plain")}
    )
    assert resp_upload.status_code == 200
    doc_id = resp_upload.json()["id"]

    # Bob queries his vault documents; Alice's document must NOT be returned
    resp_bob_docs = client.get(
        "/api/vault/documents",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert resp_bob_docs.status_code == 200
    bob_docs = resp_bob_docs.json()
    assert not any(d["id"] == doc_id for d in bob_docs)

    # Bob queries his vault for Alice's secret; cannot retrieve it
    resp_bob_query = client.post(
        "/api/vault/query",
        headers={"Authorization": f"Bearer {bob_token}"},
        json={"query": "What is the project proposal?"}
    )
    assert resp_bob_query.status_code == 200
    assert "SECURE RAG AGENT" not in resp_bob_query.json()["answer"]

    # Alice queries her own vault; she CAN retrieve it
    resp_alice_query = client.post(
        "/api/vault/query",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"query": "What is the project proposal?"}
    )
    assert resp_alice_query.status_code == 200
    assert "SECURE RAG AGENT" in resp_alice_query.json()["answer"]

# 17. Forgot Password Recovery Guidance Test
def test_forgot_password_guidance():
    resp = client.post("/api/auth/forgot-password", json={
        "email": "student@example.com"
    })
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert "instructions have been dispatched" in resp.json()["message"].lower()

def run_auth_suite():
    print("=" * 70)
    print("CAMPUSIQ — OPTIONAL AUTHENTICATION & TENANT ISOLATION TEST SUITE")
    print("=" * 70)

    setup_test_db()

    tests = [
        ("1. Valid Signup", test_valid_signup),
        ("2. Invalid Email Format Rejection", test_invalid_email_signup),
        ("3. Empty Email Rejection", test_empty_email_signup),
        ("4. Short Password Rejection (<6 chars)", test_short_password_signup),
        ("5. Password Mismatch Rejection", test_password_mismatch_signup),
        ("6. Valid Login & Token Issuance", test_valid_login),
        ("7. Wrong Password Rejection (401)", test_wrong_password_login),
        ("8. Unknown Account Rejection (401)", test_unknown_account_login),
        ("9. Password Hashing Security (bcrypt)", test_password_never_stored_plaintext),
        ("10. Guest Access to Public College Information", test_guest_access_public_endpoints),
        ("11. Protected Features Reject Unauthenticated Guests (401)", test_protected_endpoints_reject_unauthenticated),
        ("12. Refresh While Logged In (/api/auth/me)", test_me_endpoint_with_valid_token),
        ("13. User Profile Preferences Update", test_profile_preferences_update),
        ("14. Saved Answers User Association", test_saved_answers_user_association),
        ("15. Saved Answers Isolation (User A vs User B)", test_user_a_cannot_access_user_b_data),
        ("16. Personal Vault Document Isolation (User A vs User B)", test_vault_user_isolation_via_api),
        ("17. Forgot Password Guidance", test_forgot_password_guidance)
    ]

    passed = 0
    failed = 0

    for name, func in tests:
        print(f"Running: {name} ... ", end="", flush=True)
        try:
            func()
            print("[PASS]")
            passed += 1
        except Exception as e:
            print(f"[FAIL]: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 70)
    print(f"AUTH TEST SUMMARY: {passed} PASSED, {failed} FAILED (TOTAL {len(tests)})")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_auth_suite()
