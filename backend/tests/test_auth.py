"""Authentication and User isolation tests."""
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.database import SessionLocal, init_db
from app.models.user import User
from app.models.project import Project

def setup_module():
    init_db()

def test_password_hashing_and_verification():
    raw = "ResearchPassword!2026"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation_and_decoding():
    user_id = "test-user-uuid-12345"
    token = create_access_token(user_id)
    assert token is not None
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == user_id

def test_user_creation_and_isolation():
    db = SessionLocal()
    try:
        # Create user A
        user_a = User(email="user_a@test.com", hashed_password=hash_password("passA"), full_name="User A")
        # Create user B
        user_b = User(email="user_b@test.com", hashed_password=hash_password("passB"), full_name="User B")
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        # Projects for User A
        proj_a = Project(user_id=user_a.id, title="User A Private Research")
        # Projects for User B
        proj_b = Project(user_id=user_b.id, title="User B Private Research")
        db.add_all([proj_a, proj_b])
        db.commit()

        # Verify User A cannot access User B's project
        user_a_projects = db.query(Project).filter(Project.user_id == user_a.id).all()
        assert len(user_a_projects) == 1
        assert user_a_projects[0].title == "User A Private Research"

        # Cleanup
        db.delete(proj_a)
        db.delete(proj_b)
        db.delete(user_a)
        db.delete(user_b)
        db.commit()
    finally:
        db.close()
