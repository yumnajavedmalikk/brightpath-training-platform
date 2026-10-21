# tests/test_admin_registration.py
"""Verify that custom User and Client models are registered in Django admin.

This avoids rendering admin templates (which can trigger Django's template
context copy bug in certain versions). Instead we inspect the admin site
registry directly.
"""

import pytest
from django.contrib import admin
from users.models import User
from clients.models import Client
from users.admin import UserAdmin
from clients.admin import ClientAdmin

def test_user_admin_registered():
    assert User in admin.site._registry, "User model not registered in admin"
    assert isinstance(admin.site._registry[User], UserAdmin), "UserAdmin not correctly registered"

def test_client_admin_registered():
    assert Client in admin.site._registry, "Client model not registered in admin"
    assert isinstance(admin.site._registry[Client], ClientAdmin), "ClientAdmin not correctly registered"
