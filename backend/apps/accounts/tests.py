import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User

PASSWORD = "StrongPass#2026"


@pytest.fixture
def api():
    return APIClient()


def make_user(role, email=None):
    email = email or f"{role.lower()}@example.com"
    return User.objects.create_user(email=email, password=PASSWORD, role=role)


# ---------------------------------------------------------- registration
@pytest.mark.django_db
def test_register_always_creates_a_patient(api):
    response = api.post(
        "/api/auth/register/",
        {"email": "p@example.com", "password": PASSWORD, "role": "ADMIN"},
        format="json",
    )
    assert response.status_code == 201
    assert "password" not in response.data
    assert User.objects.get(email="p@example.com").role == User.Role.PATIENT


@pytest.mark.django_db
def test_register_rejects_weak_password(api):
    response = api.post(
        "/api/auth/register/",
        {"email": "p@example.com", "password": "12345"},
        format="json",
    )
    assert response.status_code == 400


# ---------------------------------------------------------- login
@pytest.mark.django_db
def test_login_sets_httponly_cookies(api):
    make_user(User.Role.PATIENT)
    response = api.post(
        "/api/auth/login/",
        {"email": "patient@example.com", "password": PASSWORD},
        format="json",
    )
    assert response.status_code == 200
    assert response.cookies["hms_access"]["httponly"]
    assert response.cookies["hms_refresh"]["httponly"]
    assert "access" not in response.data


@pytest.mark.django_db
def test_login_wrong_password(api):
    make_user(User.Role.PATIENT)
    response = api.post(
        "/api/auth/login/",
        {"email": "patient@example.com", "password": "wrong-password"},
        format="json",
    )
    assert response.status_code == 401


# ---------------------------------------------------------- /me/
@pytest.mark.django_db
def test_me_requires_login(api):
    assert api.get("/api/auth/me/").status_code == 401


@pytest.mark.django_db
def test_user_cannot_change_own_role(api):
    user = make_user(User.Role.PATIENT)
    api.force_authenticate(user)
    api.patch("/api/auth/me/", {"role": "ADMIN"}, format="json")
    user.refresh_from_db()
    assert user.role == User.Role.PATIENT


# ---------------------------------------------------------- admin users API
@pytest.mark.django_db
def test_anonymous_cannot_list_users(api):
    assert api.get("/api/users/").status_code == 401


@pytest.mark.django_db
@pytest.mark.parametrize("role", [User.Role.PATIENT, User.Role.DOCTOR])
def test_non_admin_cannot_use_users_api(api, role):
    api.force_authenticate(make_user(role))
    assert api.get("/api/users/").status_code == 403
    response = api.post(
        "/api/users/",
        {"email": "x@example.com", "password": PASSWORD, "role": "ADMIN"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_create_doctor_who_can_then_log_in(api):
    api.force_authenticate(make_user(User.Role.ADMIN))
    response = api.post(
        "/api/users/",
        {
            "email": "doc@example.com",
            "first_name": "Asha",
            "password": PASSWORD,
            "role": "DOCTOR",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["role"] == "DOCTOR"
    assert "password" not in response.data

    fresh_client = APIClient()
    login = fresh_client.post(
        "/api/auth/login/",
        {"email": "doc@example.com", "password": PASSWORD},
        format="json",
    )
    assert login.status_code == 200


@pytest.mark.django_db
def test_admin_can_filter_by_role(api):
    make_user(User.Role.DOCTOR)
    make_user(User.Role.PATIENT)
    api.force_authenticate(make_user(User.Role.ADMIN))
    response = api.get("/api/users/?role=DOCTOR")
    assert response.status_code == 200
    roles = {item["role"] for item in response.data["results"]}
    assert roles == {"DOCTOR"}


@pytest.mark.django_db
def test_admin_cannot_deactivate_self(api):
    admin = make_user(User.Role.ADMIN)
    api.force_authenticate(admin)
    response = api.patch(f"/api/users/{admin.pk}/", {"is_active": False}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_admin_can_deactivate_another_user(api):
    patient = make_user(User.Role.PATIENT)
    api.force_authenticate(make_user(User.Role.ADMIN))
    response = api.patch(f"/api/users/{patient.pk}/", {"is_active": False}, format="json")
    assert response.status_code == 200
    patient.refresh_from_db()
    assert patient.is_active is False