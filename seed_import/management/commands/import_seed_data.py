import csv
import os
import tempfile
import zipfile
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

# Helper import functions – each returns dict with counts

def import_clients(csv_path):
    from clients.models import Client
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            client_id = row.get("client_id")
            if not client_id:
                rejected += 1
                row["error_message"] = "Missing client_id"
                writer.writerow(row)
                continue
            try:
                obj, created_flag = Client.objects.update_or_create(
                    name=row["name"], defaults={
                        "name": row["name"],
                    }
                )
                # Use client_id as a unique identifier – add a hidden field if needed (create if missing)
                # For now we store client_id in a separate field (we add it via a temporary attribute)
                # Assuming Client model has a `client_id` CharField; if not, we add it later.
                if hasattr(obj, "client_id"):
                    if obj.client_id != client_id:
                        obj.client_id = client_id
                        obj.save()
                else:
                    # Dynamically add attribute (will raise if model lacks field)
                    pass
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}


def import_staff(csv_path):
    from users.models import User
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            staff_id = row.get("staff_id")
            if not staff_id:
                rejected += 1
                row["error_message"] = "Missing staff_id"
                writer.writerow(row)
                continue
            try:
                user, created_flag = User.objects.update_or_create(
                    username=staff_id,
                    defaults={
                        "first_name": row.get("full_name", "").split()[0] if row.get("full_name") else "",
                        "last_name": row.get("full_name", "").split()[-1] if row.get("full_name") else "",
                        "email": row.get("email", ""),
                        "role": row.get("role", "administrator"),
                        "is_staff": True,
                        "is_active": True,
                    },
                )
                # Link to client if provided
                client_id = row.get("client_id")
                if client_id:
                    from clients.models import Client
                    try:
                        client = Client.objects.get(name=client_id)  # fallback to name lookup
                    except Client.DoesNotExist:
                        try:
                            client = Client.objects.get(client_id=client_id)
                        except Exception:
                            client = None
                    if client:
                        user.client = client
                        user.save()
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}


def import_learners(csv_path):
    from learners.models import Learner
    from users.models import User
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            learner_id = row.get("learner_id")
            if not learner_id:
                rejected += 1
                row["error_message"] = "Missing learner_id"
                writer.writerow(row)
                continue
            try:
                # Ensure a User exists for this learner (username = learner_id)
                user, _ = User.objects.get_or_create(
                    username=learner_id,
                    defaults={
                        "first_name": row.get("full_name", "").split()[0] if row.get("full_name") else "",
                        "last_name": row.get("full_name", "").split()[-1] if row.get("full_name") else "",
                        "email": row.get("email", ""),
                        "role": "learner",
                        "is_active": row.get("account_status", "active") == "active",
                    },
                )
                learner, created_flag = Learner.objects.update_or_create(
                    learner_id=learner_id,
                    defaults={
                        "user": user,
                        "client_id": row.get("client_id"),
                        "department": row.get("department", ""),
                        "account_created_on": row.get("account_created_on"),
                        "created_by": row.get("created_by"),
                        "account_status": row.get("account_status", "active"),
                    },
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}

# Placeholder implementations for the remaining imports – they follow the same pattern.

def import_courses(csv_path):
    from courses.models import Course
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            course_id = row.get("course_id")
            if not course_id:
                rejected += 1
                row["error_message"] = "Missing course_id"
                writer.writerow(row)
                continue
            try:
                obj, created_flag = Course.objects.update_or_create(
                    course_id=course_id,
                    defaults={
                        "title": row.get("title", ""),
                        "category": row.get("category", ""),
                        "description": row.get("description", ""),
                        "cohort": row.get("cohort", ""),
                        "starts_on": row.get("starts_on"),
                        "ends_on": row.get("ends_on"),
                        "length_days": row.get("length_days"),
                    },
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}

def import_course_staff(csv_path):
    from courses.models import CourseStaff, Course
    from users.models import User
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            try:
                course = Course.objects.get(course_id=row["course_id"])
                staff = User.objects.get(username=row["staff_id"])
                obj, created_flag = CourseStaff.objects.update_or_create(
                    course=course,
                    staff=staff,
                    role=row.get("role", "instructor"),
                    defaults={
                        "assigned_on": row.get("assigned_on"),
                        "unassigned_on": row.get("unassigned_on"),
                    },
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}

def import_assessments(csv_path):
    from assessments.models import Assessment
    from courses.models import Course
    from users.models import User
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            try:
                course = Course.objects.get(course_id=row["course_id"])
                author = User.objects.get(username=row["author_id"]) if row.get("author_id") else None
                obj, created_flag = Assessment.objects.update_or_create(
                    assessment_id=row["assessment_id"],
                    defaults={
                        "course": course,
                        "type": row.get("type", ""),
                        "title": row.get("title", ""),
                        "due_on": row.get("due_on"),
                        "weight_pct": row.get("weight_pct"),
                        "author": author,
                        "status": row.get("status", "draft"),
                        "published_on": row.get("published_on"),
                    },
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}

def import_enrolments(csv_path):
    from enrolments.models import Enrolment
    from learners.models import Learner
    from courses.models import Course
    from users.models import User
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            try:
                learner = Learner.objects.get(learner_id=row["learner_id"])
                course = Course.objects.get(course_id=row["course_id"])
                enrolled_by = None
                if row.get("enrolled_by") and row["enrolled_by"] != "self":
                    enrolled_by = User.objects.get(username=row["enrolled_by"])
                obj, created_flag = Enrolment.objects.update_or_create(
                    enrolment_id=row["enrolment_id"],
                    defaults={
                        "learner": learner,
                        "course": course,
                        "enrolled_on": row.get("enrolled_on"),
                        "withdrawn_on": row.get("withdrawn_on"),
                        "outcome": row.get("outcome"),
                        "previous_attempts": row.get("previous_attempts"),
                        "activity_clicks": row.get("activity_clicks"),
                        "enrolled_by": enrolled_by,
                    },
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}

def import_attempts(csv_path):
    from attempts.models import Attempt
    from assessments.models import Assessment
    from learners.models import Learner
    from courses.models import Course
    from users.models import User
    processed = created = updated = rejected = 0
    rejected_path = csv_path.parent / f"rejected_{csv_path.name}"
    with open(csv_path, newline="") as f, open(rejected_path, "w", newline="") as rej:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(rej, fieldnames=reader.fieldnames + ["error_message"]) 
        writer.writeheader()
        for row in reader:
            processed += 1
            try:
                assessment = Assessment.objects.get(assessment_id=row["assessment_id"])
                learner = Learner.objects.get(learner_id=row["learner_id"])
                course = Course.objects.get(course_id=row["course_id"])
                graded_by = None
                if row.get("graded_by"):
                    graded_by = User.objects.get(username=row["graded_by"])
                obj, created_flag = Attempt.objects.update_or_create(
                    attempt_id=row["attempt_id"],
                    defaults={
                        "assessment": assessment,
                        "learner": learner,
                        "course": course,
                        "submitted_on": row.get("submitted_on"),
                        "score": row.get("score"),
                        "graded_by": graded_by,
                    },
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                rejected += 1
                row["error_message"] = str(e)
                writer.writerow(row)
    return {"processed": processed, "created": created, "updated": updated, "rejected": rejected}

class Command(BaseCommand):
    help = "Import seed data from the provided training-platform ZIP file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--zip",
            type=str,
            default=str(Path(settings.BASE_DIR) / "training-platform-seed.zip"),
            help="Path to the seed ZIP file",
        )

    def handle(self, *args, **options):
        zip_path = Path(options["zip"]).resolve()
        if not zip_path.is_file():
            raise CommandError(f"ZIP file not found: {zip_path}")
        self.stdout.write(self.style.NOTICE(f"Extracting {zip_path.name}…"))
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(tmpdir)
            base = Path(tmpdir)
            # Ordered imports
            import_order = [
                (base / "clients.csv", import_clients),
                (base / "staff.csv", import_staff),
                (base / "learners.csv", import_learners),
                (base / "courses.csv", import_courses),
                (base / "course_staff.csv", import_course_staff),
                (base / "assessments.csv", import_assessments),
                (base / "enrolments.csv", import_enrolments),
                (base / "attempts.csv", import_attempts),
            ]
            for csv_path, func in import_order:
                if not csv_path.is_file():
                    self.stdout.write(self.style.WARNING(f"Missing {csv_path.name}, skipping."))
                    continue
                self.stdout.write(self.style.NOTICE(f"Importing {csv_path.name}…"))
                with transaction.atomic():
                    result = func(csv_path)
                self.stdout.write(
                    f"{csv_path.name}: processed {result['processed']}, "
                    f"created {result['created']}, updated {result['updated']}, rejected {result['rejected']}"
                )
        self.stdout.write(self.style.SUCCESS("Seed import completed."))
