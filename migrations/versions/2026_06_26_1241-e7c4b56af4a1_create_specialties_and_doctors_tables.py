"""seed specialties and doctors

Revision ID: e7c4b56af4a1
Revises: ad8a1e4a0e0d
Create Date: 2026-06-26 12:41:07.386259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e7c4b56af4a1'
down_revision: Union[str, None] = 'ad8a1e4a0e0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import uuid
    import random
    from datetime import date, datetime, timezone

    random.seed(42)
    now = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Specialties seed data (Venezuelan medical specialties in Spanish)
    # ------------------------------------------------------------------
    specialties_table = sa.table(
        'specialties',
        sa.column('id', sa.UUID()),
        sa.column('code', sa.String()),
        sa.column('name', sa.String()),
        sa.column('category', sa.String()),
        sa.column('description', sa.Text()),
        sa.column('is_active', sa.Boolean()),
        sa.column('created_at', sa.DateTime(timezone=True)),
        sa.column('updated_at', sa.DateTime(timezone=True)),
    )

    specialties_data = [
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000001"),
            "code": "CARD",
            "name": "Cardiología",
            "category": "terapeutica",
            "description": "Diagnóstico y tratamiento de enfermedades del corazón y del sistema cardiovascular.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000002"),
            "code": "NEUR",
            "name": "Neurología",
            "category": "terapeutica",
            "description": "Diagnóstico y tratamiento de trastornos del sistema nervioso central y periférico.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000003"),
            "code": "PEDI",
            "name": "Pediatría",
            "category": "atencion_primaria",
            "description": "Atención médica integral para niños y adolescentes.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000004"),
            "code": "GINE",
            "name": "Ginecología y Obstetricia",
            "category": "quirurgica",
            "description": "Salud reproductiva de la mujer, embarazo y parto.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000005"),
            "code": "ORTO",
            "name": "Traumatología y Ortopedia",
            "category": "quirurgica",
            "description": "Diagnóstico y tratamiento de lesiones y enfermedades del aparato locomotor.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000006"),
            "code": "DERM",
            "name": "Dermatología",
            "category": "terapeutica",
            "description": "Diagnóstico y tratamiento de enfermedades de la piel, cabello y uñas.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000007"),
            "code": "OFTA",
            "name": "Oftalmología",
            "category": "quirurgica",
            "description": "Diagnóstico y tratamiento de enfermedades oculares y de la visión.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000008"),
            "code": "PSIQ",
            "name": "Psiquiatría",
            "category": "salud_mental",
            "description": "Diagnóstico y tratamiento de trastornos mentales, emocionales y de conducta.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000009"),
            "code": "ENDO",
            "name": "Endocrinología",
            "category": "terapeutica",
            "description": "Diagnóstico y tratamiento de trastornos hormonales y metabólicos.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": uuid.UUID("11111111-0001-0001-0001-000000000010"),
            "code": "GAST",
            "name": "Gastroenterología",
            "category": "terapeutica",
            "description": "Diagnóstico y tratamiento de enfermedades del sistema digestivo.",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
    ]

    op.bulk_insert(specialties_table, specialties_data)

    # ------------------------------------------------------------------
    # Doctors seed data
    # ------------------------------------------------------------------
    doctors_table = sa.table(
        'doctors',
        sa.column('id', sa.UUID()),
        sa.column('employee_id', sa.String()),
        sa.column('first_name', sa.String()),
        sa.column('last_name', sa.String()),
        sa.column('date_of_birth', sa.Date()),
        sa.column('gender', sa.String()),
        sa.column('specialty_id', sa.UUID()),
        sa.column('license_info', postgresql.JSON()),
        sa.column('years_of_experience', sa.Integer()),
        sa.column('bio', sa.Text()),
        sa.column('contact_info', postgresql.JSON()),
        sa.column('address', postgresql.JSON()),
        sa.column('status', sa.String()),
        sa.column('created_at', sa.DateTime(timezone=True)),
        sa.column('updated_at', sa.DateTime(timezone=True)),
    )

    first_names_male = ["Carlos", "José", "Luis", "Miguel", "Juan", "Andrés", "Diego", "Manuel", "Pedro", "Alejandro"]
    first_names_female = ["María", "Luisa", "Ana", "Carmen", "Gabriela", "Sofía", "Valentina", "Isabel", "Patricia", "Daniela"]
    last_names = ["González", "Rodríguez", "Pérez", "García", "Martínez", "López", "Hernández", "Díaz", "Morales", "Torres",
                  "Ramírez", "Flores", "Castro", "Vargas", "Romero", "Jiménez", "Salazar", "Medina", "Reyes", "Gutiérrez"]
    cities = ["Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Maturín", "Barcelona"]
    states = ["Distrito Capital", "Zulia", "Carabobo", "Lara", "Monagas", "Anzoátegui"]
    specialty_ids = [uuid.UUID(f"11111111-0001-0001-0001-{str(i).zfill(12)}") for i in range(1, 11)]

    doctors_data = []
    for i in range(30):
        gender = random.choice(["male", "female"])
        first_name = random.choice(first_names_male if gender == "male" else first_names_female)
        last_name = random.choice(last_names)
        specialty_id = random.choice(specialty_ids)
        birth_year = random.randint(1965, 1990)
        dob = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        years_exp = 2025 - birth_year - 26  # rough estimate after 6y med school + residency
        years_exp = max(1, min(years_exp, 35))
        city = random.choice(cities)
        state = states[cities.index(city)]

        doctors_data.append({
            "id": uuid.uuid4(),
            "employee_id": f"EMP-{str(i + 1).zfill(4)}",
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "gender": gender,
            "specialty_id": specialty_id,
            "license_info": {
                "license_number": f"MSDS-{random.randint(10000, 99999)}",
                "issuing_body": "Ministerio del Poder Popular para la Salud",
                "issue_date": f"{random.randint(2000, 2015)}-{str(random.randint(1, 12)).zfill(2)}-01",
            },
            "years_of_experience": years_exp,
            "bio": (
                f"Dr. {first_name} {last_name} es especialista con {years_exp} años de experiencia. "
                f"Egresado de una universidad venezolana, comprometido con la salud de sus pacientes."
            ),
            "contact_info": {
                "phone_number": f"+58-412-{random.randint(1000000, 9999999)}",
                "email": f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}@clinica.com.ve",
            },
            "address": {
                "street_line_1": f"Av. Principal, Consultorio {random.randint(1, 20)}, Piso {random.randint(1, 8)}",
                "city": city,
                "state": state,
                "postal_code": f"{random.randint(1000, 9999)}",
                "country": "VE",
            },
            "status": "active" if random.random() > 0.1 else "inactive",
            "created_at": now,
            "updated_at": now,
        })

    op.bulk_insert(doctors_table, doctors_data)


def downgrade() -> None:
    op.execute("DELETE FROM doctors;")
    op.execute("DELETE FROM specialties;")
