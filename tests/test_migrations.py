# tests/test_migrations.py
"""Tests that verify the initial database schema after migrations.

The test suite runs against the SQLite fallback defined in
`brightpath.settings.DATABASES['default']['TEST']`. This avoids the need
for a running PostgreSQL server while still validating that the migration
files produce the expected tables and columns.
"""

import pytest
from django.db import connection

@pytest.mark.django_db
def test_user_and_client_tables_exist():
    # Get list of tables in the test DB
    tables = connection.introspection.table_names()
    assert "users_user" in tables, "users_user table missing"
    assert "clients_client" in tables, "clients_client table missing"

    # Verify columns on users_user table
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, "users_user")
    user_columns = {c.name for c in description}
    assert "role" in user_columns, "role column missing on users_user"
    assert "client_id" in user_columns, "client_id column missing on users_user"
