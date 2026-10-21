# users/models.py
"""Custom user model for BrightPath.

The model extends ``AbstractUser`` and adds a ``role`` field used for
role‑based authorisation throughout the platform.  A ``client`` foreign
key links a user to a client organisation when applicable.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("instructor", "Instructor"),
        ("learner", "Learner"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="learner")
    # ``null=True`` and ``blank=True`` allow users that are not tied to a client (e.g., superusers).
    client = models.ForeignKey(
        "clients.Client",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
