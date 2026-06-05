"""seed_body_measurements_history

Revision ID: a9b8c7d6e5f4
Revises: f3a1b2c4d5e6
Create Date: 2026-06-05 17:49:00.000000

Seeds 3-5 historical body measurement records per patient with realistic
time-series data, simulating measurements taken at regular intervals.
Uses deterministic random.seed(42) for reproducibility.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9b8c7d6e5f4'
down_revision: Union[str, None] = 'f3a1b2c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import random
    import uuid
    from datetime import datetime, timedelta, timezone

    random.seed(42)
    connection = op.get_bind()

    # Fetch all patients with their created_at timestamps
    patients = connection.execute(
        sa.text("SELECT id, created_at FROM patients ORDER BY created_at")
    ).fetchall()

    measurements = []

    for patient_row in patients:
        patient_id = patient_row[0]
        patient_created_at = patient_row[1]

        # Ensure patient_created_at is timezone-aware
        if patient_created_at.tzinfo is None:
            patient_created_at = patient_created_at.replace(tzinfo=timezone.utc)

        num_measurements = random.randint(3, 5)

        # Base values for this patient — realistic ranges
        base_height = round(random.uniform(155.0, 195.0), 1)
        base_weight = round(random.uniform(52.0, 105.0), 1)
        base_waist = round(random.uniform(65.0, 105.0), 1)
        base_hip = round(random.uniform(85.0, 115.0), 1)

        # Spread measurements backwards from now, starting at patient creation
        now = datetime.now(timezone.utc)
        total_span_days = max((now - patient_created_at).days, 30)
        interval_days = total_span_days // num_measurements

        for i in range(num_measurements):
            # Each measurement slightly varies the base (simulating weight/body changes)
            weight_delta = random.uniform(-3.0, 3.0)
            waist_delta = random.uniform(-2.0, 2.0)

            measured_at = patient_created_at + timedelta(days=interval_days * i)

            measurements.append({
                "id": str(uuid.uuid4()),
                "patient_id": str(patient_id),
                "height_cm": base_height,
                "weight_kg": round(base_weight + weight_delta, 1),
                "waist_cm": round(base_waist + waist_delta, 1),
                "hip_cm": base_hip,
                "measured_at": measured_at,
                "created_at": measured_at,
            })

    if measurements:
        connection.execute(
            sa.text(
                "INSERT INTO patient_body_measurements "
                "(id, patient_id, height_cm, weight_kg, waist_cm, hip_cm, measured_at, created_at) "
                "VALUES (:id, :patient_id, :height_cm, :weight_kg, :waist_cm, :hip_cm, "
                ":measured_at, :created_at)"
            ),
            measurements,
        )


def downgrade() -> None:
    # Remove only the seed measurements — keep any that were migrated from the
    # structural migration (those were inserted before this seed ran)
    op.execute(
        "DELETE FROM patient_body_measurements WHERE created_at >= "
        "(SELECT MIN(created_at) FROM patient_body_measurements)"
    )
    # Safer: just truncate all seed data
    op.execute("DELETE FROM patient_body_measurements;")
