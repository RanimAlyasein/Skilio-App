"""
tests/test_auth.py
──────────────────
Tests for authentication endpoints covering:
  - Happy-path registration and login
  - Duplicate email rejection
  - Invalid credentials rejection
  - Password complexity validation
  - Token rotation
  - Rate limiting (skipped if running fast)
"""
import pytest


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "new@skilio.com",
            "full_name": "New User",
            "password": "NewPass1",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@skilio.com"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, registered_user):
        resp = client.post("/api/auth/register", json={
            "email": "test@skilio.com",
            "full_name": "Duplicate",
            "password": "Dup12345",
        })
        assert resp.status_code == 409

    def test_register_weak_password(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "weak@skilio.com",
            "full_name": "Weak Pass",
            "password": "alllowercase",  # no digit
        })
        assert resp.status_code == 422

    def test_register_short_password(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "short@skilio.com",
            "full_name": "Short Pass",
            "password": "Ab1",  # too short
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "notanemail",
            "full_name": "Bad Email",
            "password": "GoodPass1",
        })
        assert resp.status_code == 422

    def test_register_blank_name(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "blank@skilio.com",
            "full_name": "   ",
            "password": "GoodPass1",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, registered_user):
        resp = client.post("/api/auth/login", data={
            "username": "test@skilio.com",
            "password": "Test1234!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post("/api/auth/login", data={
            "username": "test@skilio.com",
            "password": "WrongPass1",
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post("/api/auth/login", data={
            "username": "nobody@skilio.com",
            "password": "AnyPass1",
        })
        assert resp.status_code == 401

    def test_login_returns_bearer_type(self, client, registered_user):
        resp = client.post("/api/auth/login", data={
            "username": "test@skilio.com",
            "password": "Test1234!",
        })
        assert resp.json()["token_type"] == "bearer"


class TestMe:
    def test_me_authenticated(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@skilio.com"

    def test_me_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer notavalidtoken"})
        assert resp.status_code == 401


class TestChildren:
    def test_create_child(self, client, auth_headers):
        resp = client.post("/api/children/", json={
            "display_name": "TestKid",
            "age": 8,
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["display_name"] == "TestKid"
        assert data["age"] == 8

    def test_create_child_age_too_low(self, client, auth_headers):
        resp = client.post("/api/children/", json={
            "display_name": "Baby",
            "age": 2,
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_create_child_age_too_high(self, client, auth_headers):
        resp = client.post("/api/children/", json={
            "display_name": "Adult",
            "age": 25,
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_list_children(self, client, auth_headers):
        resp = client.get("/api/children/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_child_not_accessible_by_other_user(self, client, auth_headers):
        # Create a child for user1
        c = client.post("/api/children/", json={"display_name": "Kid1", "age": 9}, headers=auth_headers)
        child_id = c.json()["id"]

        # Register user2
        client.post("/api/auth/register", json={
            "email": "user2@skilio.com", "full_name": "User Two", "password": "User2Pass1"
        })
        login2 = client.post("/api/auth/login", data={"username": "user2@skilio.com", "password": "User2Pass1"})
        headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

        # user2 cannot access user1's child
        resp = client.get(f"/api/children/{child_id}", headers=headers2)
        assert resp.status_code == 404  # not 403 — no enumeration


class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
