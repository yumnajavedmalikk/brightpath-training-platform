# clients/models.py
"""Minimal Client model for BrightPath.

This placeholder will later be expanded with additional fields (address,
contact info, etc.) but for now we only need an identifier that the
User model can reference.
"""

from django.db import models

class Client(models.Model):
    client_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "client"
        verbose_name_plural = "clients"

    def __str__(self):
        return self.name
