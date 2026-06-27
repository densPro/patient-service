"""Database seed script for patient-management-service.

Populates initial data for specialties, doctors, and patients.

Usage::

    # From the project root with the venv active:
    python -m app.infrastructure.seeds.seed

The script is idempotent: it checks for existing records by their unique
identifiers (specialty code, employee_id, MRN) before inserting.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.doctor import Doctor
from app.domain.entities.patient import Patient
from app.domain.entities.specialty import Specialty
from app.domain.enums.blood_type import BloodType
from app.domain.enums.doctor_status import DoctorStatus
from app.domain.enums.gender import Gender
from app.domain.enums.marital_status import MaritalStatus
from app.domain.enums.specialty_category import SpecialtyCategory
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.emergency_contact import EmergencyContact
from app.domain.value_objects.license_info import LicenseInfo
from app.infrastructure.database.session import async_session_factory
from app.infrastructure.repositories.doctor_repository import DoctorRepository
from app.infrastructure.repositories.patient_repository import PatientRepository
from app.infrastructure.repositories.specialty_repository import SpecialtyRepository


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

SPECIALTIES_DATA = [
    {
        "code": "CARDIO",
        "name": "Cardiology",
        "category": SpecialtyCategory.THERAPEUTIC,
        "description": "Diagnosis and treatment of heart and cardiovascular conditions.",
    },
    {
        "code": "DERM",
        "name": "Dermatology",
        "category": SpecialtyCategory.THERAPEUTIC,
        "description": "Diagnosis and treatment of skin, hair, and nail conditions.",
    },
    {
        "code": "PEDS",
        "name": "Pediatrics",
        "category": SpecialtyCategory.PRIMARY_CARE,
        "description": "Medical care for infants, children, and adolescents.",
    },
    {
        "code": "NEURO",
        "name": "Neurology",
        "category": SpecialtyCategory.DIAGNOSTIC,
        "description": "Diagnosis and treatment of nervous system disorders.",
    },
    {
        "code": "ORTHO",
        "name": "Orthopedics",
        "category": SpecialtyCategory.SURGICAL,
        "description": "Diagnosis and treatment of musculoskeletal conditions.",
    },
    {
        "code": "PSYCH",
        "name": "Psychiatry",
        "category": SpecialtyCategory.MENTAL_HEALTH,
        "description": "Diagnosis and treatment of mental, emotional, and behavioral disorders.",
    },
    {
        "code": "ONCO",
        "name": "Oncology",
        "category": SpecialtyCategory.THERAPEUTIC,
        "description": "Diagnosis and treatment of cancer.",
    },
    {
        "code": "RADIO",
        "name": "Radiology",
        "category": SpecialtyCategory.DIAGNOSTIC,
        "description": "Medical imaging used to diagnose and treat diseases.",
    },
    {
        "code": "GEN",
        "name": "General Practice",
        "category": SpecialtyCategory.PRIMARY_CARE,
        "description": "Primary care for patients of all ages.",
    },
    {
        "code": "EM",
        "name": "Emergency Medicine",
        "category": SpecialtyCategory.EMERGENCY,
        "description": "Immediate medical care for acute illness and injuries.",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_employee_id() -> str:
    return f"EMP-{uuid.uuid4().hex[:8].upper()}"


def _generate_mrn() -> str:
    return f"MRN-{uuid.uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

async def seed_specialties(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Seed specialties and return a code→id mapping."""
    repo = SpecialtyRepository(session)
    code_to_id: dict[str, uuid.UUID] = {}

    for data in SPECIALTIES_DATA:
        existing = await repo.get_by_code(data["code"])
        if existing:
            print(f"  [SKIP] Specialty '{data['code']}' already exists.")
            code_to_id[data["code"]] = existing.id
            continue

        specialty = Specialty.create(
            code=data["code"],
            name=data["name"],
            category=data["category"],
            description=data["description"],
        )
        await repo.add(specialty)
        code_to_id[specialty.code] = specialty.id
        print(f"  [OK]   Specialty '{specialty.code}' — {specialty.name}")

    await session.commit()
    return code_to_id


async def seed_doctors(
    session: AsyncSession, code_to_id: dict[str, uuid.UUID]
) -> None:
    """Seed sample doctors linked to specialties."""
    repo = DoctorRepository(session)

    doctors_data = [
        {
            "first_name": "Carlos",
            "last_name": "Rivera",
            "date_of_birth": date(1978, 3, 20),
            "gender": Gender.MALE,
            "specialty_code": "CARDIO",
            "license_number": "PR-12345",
            "issuing_body": "Puerto Rico Medical Licensing Board",
            "years_of_experience": 18,
            "bio": "Board-certified cardiologist specialising in interventional cardiology.",
            "phone": "+1-787-555-0101",
            "email": "c.rivera@chirimoya.health",
        },
        {
            "first_name": "Ana",
            "last_name": "Martínez",
            "date_of_birth": date(1985, 7, 14),
            "gender": Gender.FEMALE,
            "specialty_code": "PEDS",
            "license_number": "PR-67890",
            "issuing_body": "Puerto Rico Medical Licensing Board",
            "years_of_experience": 11,
            "bio": "Paediatric specialist focused on neonatal and developmental care.",
            "phone": "+1-787-555-0202",
            "email": "a.martinez@chirimoya.health",
        },
        {
            "first_name": "Luis",
            "last_name": "González",
            "date_of_birth": date(1970, 11, 5),
            "gender": Gender.MALE,
            "specialty_code": "ORTHO",
            "license_number": "PR-11111",
            "issuing_body": "Puerto Rico Medical Licensing Board",
            "years_of_experience": 25,
            "bio": "Orthopaedic surgeon specialising in joint replacement and sports medicine.",
            "phone": "+1-787-555-0303",
            "email": "l.gonzalez@chirimoya.health",
        },
        {
            "first_name": "Sofia",
            "last_name": "Torres",
            "date_of_birth": date(1990, 1, 30),
            "gender": Gender.FEMALE,
            "specialty_code": "DERM",
            "license_number": "PR-22222",
            "issuing_body": "Puerto Rico Medical Licensing Board",
            "years_of_experience": 6,
            "bio": "Dermatologist specialising in inflammatory skin diseases and cosmetic procedures.",
            "phone": "+1-787-555-0404",
            "email": "s.torres@chirimoya.health",
        },
        {
            "first_name": "Miguel",
            "last_name": "Rodríguez",
            "date_of_birth": date(1982, 9, 18),
            "gender": Gender.MALE,
            "specialty_code": "EM",
            "license_number": "PR-33333",
            "issuing_body": "Puerto Rico Medical Licensing Board",
            "years_of_experience": 14,
            "bio": "Emergency medicine physician with extensive trauma experience.",
            "phone": "+1-787-555-0505",
            "email": "m.rodriguez@chirimoya.health",
        },
    ]

    for data in doctors_data:
        employee_id = _generate_employee_id()
        specialty_id = code_to_id.get(data["specialty_code"])
        if specialty_id is None:
            print(f"  [WARN] Specialty '{data['specialty_code']}' not found — skipping doctor {data['last_name']}.")
            continue

        license_info = LicenseInfo(
            license_number=data["license_number"],
            issuing_body=data["issuing_body"],
        )
        contact_info = ContactInfo(
            phone_number=data["phone"],
            email=data["email"],
        )

        doctor = Doctor.create(
            employee_id=employee_id,
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["date_of_birth"],
            gender=data["gender"],
            specialty_id=specialty_id,
            license_info=license_info,
            contact_info=contact_info,
            years_of_experience=data["years_of_experience"],
            bio=data["bio"],
        )
        await repo.add(doctor)
        print(f"  [OK]   Doctor '{doctor.employee_id}' — {doctor.full_name}")

    await session.commit()


async def seed_patients(session: AsyncSession) -> None:
    """Seed sample patients."""
    repo = PatientRepository(session)

    patients_data = [
        {
            "first_name": "María",
            "last_name": "García",
            "dob": date(1990, 5, 15),
            "gender": Gender.FEMALE,
            "blood_type": BloodType.O_POSITIVE,
            "allergies": ["Penicillin"],
            "phone": "+1-787-555-1001",
            "email": "maria.garcia@email.com",
            "marital_status": MaritalStatus.SINGLE,
        },
        {
            "first_name": "Roberto",
            "last_name": "López",
            "dob": date(1975, 8, 22),
            "gender": Gender.MALE,
            "blood_type": BloodType.A_POSITIVE,
            "allergies": [],
            "chronic_conditions": ["Hypertension", "Type 2 Diabetes"],
            "phone": "+1-787-555-1002",
            "email": "roberto.lopez@email.com",
            "marital_status": MaritalStatus.MARRIED,
        },
        {
            "first_name": "Carmen",
            "last_name": "Reyes",
            "dob": date(1988, 12, 3),
            "gender": Gender.FEMALE,
            "blood_type": BloodType.B_POSITIVE,
            "allergies": ["Sulfa drugs", "Latex"],
            "phone": "+1-787-555-1003",
            "email": "carmen.reyes@email.com",
            "marital_status": MaritalStatus.DIVORCED,
        },
        {
            "first_name": "Javier",
            "last_name": "Morales",
            "dob": date(1962, 4, 10),
            "gender": Gender.MALE,
            "blood_type": BloodType.AB_POSITIVE,
            "allergies": ["Aspirin"],
            "chronic_conditions": ["Asthma"],
            "phone": "+1-787-555-1004",
            "email": "javier.morales@email.com",
            "marital_status": MaritalStatus.WIDOWED,
        },
        {
            "first_name": "Isabella",
            "last_name": "Vargas",
            "dob": date(2000, 7, 27),
            "gender": Gender.FEMALE,
            "blood_type": BloodType.O_NEGATIVE,
            "allergies": [],
            "phone": "+1-787-555-1005",
            "email": "isabella.vargas@email.com",
            "marital_status": MaritalStatus.SINGLE,
        },
    ]

    for data in patients_data:
        mrn = _generate_mrn()
        existing = await repo.get_by_mrn(mrn)
        if existing:
            continue  # Collision — skip (practically impossible)

        contact_info = ContactInfo(
            phone_number=data["phone"],
            email=data["email"],
        )

        patient = Patient.create(
            mrn=mrn,
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["dob"],
            gender=data["gender"],
            marital_status=data.get("marital_status", MaritalStatus.UNKNOWN),
            blood_type=data.get("blood_type", BloodType.UNKNOWN),
            allergies=data.get("allergies", []),
            chronic_conditions=data.get("chronic_conditions", []),
            contact_info=contact_info,
        )
        await repo.add(patient)
        print(f"  [OK]   Patient '{patient.mrn}' — {patient.full_name}")

    await session.commit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    print("\n🌱  Seeding patient-management-service database...\n")

    session: AsyncSession = async_session_factory()
    try:
        print("📋  Specialties:")
        code_to_id = await seed_specialties(session)

        print("\n👨‍⚕️  Doctors:")
        await seed_doctors(session, code_to_id)

        print("\n🧑  Patients:")
        await seed_patients(session)
    finally:
        await session.close()

    print("\n✅  Seeding complete.\n")


if __name__ == "__main__":
    asyncio.run(main())
