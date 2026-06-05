"""create_patient_body_measurements_and_migrate_data

Revision ID: f3a1b2c4d5e6
Revises: e6a89442c56d
Create Date: 2026-06-05 17:48:00.000000

This migration:
1. Creates the patient_body_measurements table
2. Migrates existing age/height/weight data from patients → one measurement row per patient
3. Drops age, height, weight columns from patients
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f3a1b2c4d5e6'
down_revision: Union[str, None] = 'e6a89442c56d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Step 1: Create patient_body_measurements table ────────────────
    op.create_table(
        'patient_body_measurements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'patient_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('patients.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'measured_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column('height_cm', sa.Float(), nullable=True),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('waist_cm', sa.Float(), nullable=True),
        sa.Column('hip_cm', sa.Float(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    op.create_index('ix_body_measurements_patient_id', 'patient_body_measurements', ['patient_id'])
    op.create_index('ix_body_measurements_measured_at', 'patient_body_measurements', ['measured_at'])
    op.create_index(
        'ix_body_measurements_patient_measured',
        'patient_body_measurements',
        ['patient_id', 'measured_at'],
    )

    # ── Step 2: Migrate existing height/weight data from patients ─────
    # For each patient that has height or weight recorded, create one
    # measurement row with measured_at = patient's created_at timestamp.
    connection = op.get_bind()
    import uuid

    rows = connection.execute(
        sa.text(
            "SELECT id, height, weight, created_at FROM patients "
            "WHERE height IS NOT NULL OR weight IS NOT NULL"
        )
    ).fetchall()

    if rows:
        measurements = []
        for row in rows:
            measurements.append({
                "id": str(uuid.uuid4()),
                "patient_id": str(row[0]),
                "height_cm": row[1],
                "weight_kg": row[2],
                "measured_at": row[3],
                "created_at": row[3],
            })

        connection.execute(
            sa.text(
                "INSERT INTO patient_body_measurements "
                "(id, patient_id, height_cm, weight_kg, measured_at, created_at) "
                "VALUES (:id, :patient_id, :height_cm, :weight_kg, :measured_at, :created_at)"
            ),
            measurements,
        )

    # ── Step 3: Drop age, height, weight columns from patients ────────
    op.drop_column('patients', 'age')
    op.drop_column('patients', 'height')
    op.drop_column('patients', 'weight')


def downgrade() -> None:
    # ── Step 1: Restore age, height, weight columns ───────────────────
    op.add_column('patients', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('patients', sa.Column('height', sa.Float(), nullable=True))
    op.add_column('patients', sa.Column('weight', sa.Float(), nullable=True))

    # ── Step 2: Restore latest measurement values back to patients ────
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE patients p
            SET
                height = m.height_cm,
                weight = m.weight_kg
            FROM (
                SELECT DISTINCT ON (patient_id)
                    patient_id, height_cm, weight_kg
                FROM patient_body_measurements
                ORDER BY patient_id, measured_at DESC
            ) m
            WHERE p.id = m.patient_id
        """)
    )

    # ── Step 3: Drop measurements table ──────────────────────────────
    op.drop_index('ix_body_measurements_patient_measured', table_name='patient_body_measurements')
    op.drop_index('ix_body_measurements_measured_at', table_name='patient_body_measurements')
    op.drop_index('ix_body_measurements_patient_id', table_name='patient_body_measurements')
    op.drop_table('patient_body_measurements')
