"""seed 100 patients

Revision ID: d61dc0437346
Revises: a71bef42bd17
Create Date: 2026-05-30 18:25:40.195293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd61dc0437346'
down_revision: Union[str, None] = 'a71bef42bd17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Seeder: Populate 100 realistic patients ---
    import random
    import uuid
    from datetime import date, datetime, timezone

    patients_table = sa.table(
        'patients',
        sa.column('id', sa.UUID()),
        sa.column('mrn', sa.String()),
        sa.column('first_name', sa.String()),
        sa.column('last_name', sa.String()),
        sa.column('date_of_birth', sa.Date()),
        sa.column('gender', sa.String()),
        sa.column('marital_status', sa.String()),
        sa.column('ssn_last_four', sa.String()),
        sa.column('national_id', sa.String()),
        sa.column('blood_type', sa.String()),
        sa.column('allergies', postgresql.ARRAY(sa.String())),
        sa.column('chronic_conditions', postgresql.ARRAY(sa.String())),
        sa.column('contact_info', postgresql.JSON()),
        sa.column('address', postgresql.JSON()),
        sa.column('emergency_contact', postgresql.JSON()),
        sa.column('insurance_info', postgresql.JSON()),
        sa.column('notes', sa.Text()),
        sa.column('status', sa.String()),
        sa.column('created_at', sa.DateTime(timezone=True)),
        sa.column('updated_at', sa.DateTime(timezone=True))
    )

    random.seed(42)  # Deterministic seed so the exact same patients are created every time

    first_names_male = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark"]
    first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Sandra", "Margaret"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    genders = ["male", "female"]
    marital_statuses = ["single", "married", "divorced", "widowed"]
    blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    all_allergies = ["Penicillin", "Sulfa drugs", "Peanuts", "Shellfish", "Latex", "Aspirin", "Tree nuts"]
    all_conditions = ["Hypertension", "Type 2 Diabetes", "Asthma", "Hyperlipidemia", "Hypothyroidism", "Arthritis", "Anxiety"]
    providers = ["Blue Cross Blue Shield", "UnitedHealthcare", "Aetna", "Cigna", "Humana"]
    relationships = ["spouse", "parent", "sibling", "child", "friend"]

    patients_data = []
    for i in range(100):
        p_id = uuid.uuid4()
        gender = random.choice(genders)
        if gender == "male":
            first_name = random.choice(first_names_male)
        else:
            first_name = random.choice(first_names_female)
        last_name = random.choice(last_names)

        # Random date of birth between 1940 and 2015
        year = random.randint(1940, 2015)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        dob = date(year, month, day)

        mrn = f"MRN-{dob.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        ssn_last_four = f"{random.randint(1000, 9999)}"

        # Allergies and conditions (0 to 2 random selections)
        allergies = random.sample(all_allergies, random.randint(0, 2))
        conditions = random.sample(all_conditions, random.randint(0, 2))

        # Random contact info
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}@example.com"
        phone = f"+1-555-01{random.randint(10, 99)}"
        contact_info = {"phone_number": phone, "email": email}

        # Random address
        address = {
            "street_line_1": f"{random.randint(100, 999)} Main St",
            "city": random.choice(["Boston", "New York", "Chicago", "Seattle", "Austin", "Denver"]),
            "state": random.choice(["MA", "NY", "IL", "WA", "TX", "CO"]),
            "postal_code": f"{random.randint(10000, 99999)}",
            "country": "US"
        }

        # Emergency contact
        emergency_contact = {
            "full_name": f"{random.choice(first_names_male if gender == 'female' else first_names_female)} {last_name}",
            "relationship": random.choice(relationships),
            "phone_number": f"+1-555-02{random.randint(10, 99)}"
        }

        # Insurance info
        insurance_info = {
            "provider_name": random.choice(providers),
            "policy_number": f"POL{random.randint(10000000, 99999999)}",
            "group_number": f"GRP{random.randint(10000, 99999)}"
        } if random.random() > 0.1 else None

        patients_data.append({
            "id": p_id,
            "mrn": mrn,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "gender": gender,
            "marital_status": random.choice(marital_statuses),
            "ssn_last_four": ssn_last_four,
            "national_id": f"ID-{random.randint(100000, 999999)}",
            "blood_type": random.choice(blood_types),
            "allergies": allergies,
            "chronic_conditions": conditions,
            "contact_info": contact_info,
            "address": address,
            "emergency_contact": emergency_contact,
            "insurance_info": insurance_info,
            "notes": f"Simulated seed data for testing. Patient number {i+1}.",
            "status": "active" if random.random() > 0.1 else "inactive",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })

    op.bulk_insert(patients_table, patients_data)


def downgrade() -> None:
    op.execute("DELETE FROM patients;")
