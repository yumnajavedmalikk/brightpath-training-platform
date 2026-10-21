# Makefile
# -------------------------------------------------
# Project-wide shortcuts for development, testing, Docker, etc.
# -------------------------------------------------

.PHONY: setup install migrate run test e2e lint import createsuperuser docker-up docker-down

# Install Python dependencies
install:
	pip install -r requirements.txt

# Apply database migrations
migrate:
	python manage.py migrate

# Full local setup (install + migrate + superuser creation)
setup: install migrate createsuperuser

# Run the development server
run:
	python manage.py runserver 0.0.0.0:8000

# Run unit / integration tests (pytest)
test:
	pytest

# End‑to‑end tests using Superpowers (if available)
# The script `scripts/run_e2e.sh` should invoke the Superpowers workflow.
e2e:
	./scripts/run_e2e.sh

# Lint / static analysis (Ponytail)
lint:
	make pylint  # Ponytail provides a pylintrc‑compatible target

# Import seed data (placeholder command)
import:
	python manage.py import_seed_data

# Create a superuser (non‑interactive fallback if environment vars are set)
createsuperuser:
	python manage.py createsuperuser --noinput || echo "Create superuser manually if needed"

# Docker compose helpers
docker-up:
	docker compose up --build

docker-down:
	docker compose down
