"""
tests/conftest.py
─────────────────
Shared fixtures for the test suite.
Uses an in-memory SQLite database — no external services required.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.dependencies import get_db
from app.main import app

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(setup_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    resp = client.post("/api/auth/register", json={
        "email": "test@skilio.com",
        "full_name": "Test Parent",
        "password": "Test1234!",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def auth_headers(client, registered_user):
    resp = client.post("/api/auth/login", data={
        "username": "test@skilio.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
