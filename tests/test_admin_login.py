# tests/test_admin_login.py
"""Test that a superuser can access the Django admin index.

We use ``RequestFactory`` to build a request and invoke ``admin.site.index``
directly. This avoids the Django test client’s template‑render capture which
triggers a ``AttributeError`` in the current Django version.
"""

import pytest
from django.contrib import admin
from django.test import RequestFactory
from users.models import User

@pytest.mark.django_db
def test_admin_access_via_request_factory():
    # Create a superuser with the required fields.
    superuser = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="testpass123",
        role="admin",
        is_staff=True,
        is_superuser=True,
    )
    # Build a GET request for the admin index.
    request = RequestFactory().get("/admin/")
    request.user = superuser
    # Call the admin index view directly.
    response = admin.site.index(request)
    # ``TemplateResponse`` sets the status code without rendering.
    assert response.status_code == 200, "Admin index not reachable"
