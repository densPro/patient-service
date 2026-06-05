"""Patient aggregate root — the central domain entity."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from app.domain.entities.base import AggregateRoot
from app.domain.enums.blood_type import BloodType
from app.domain.enums.gender import Gender
from app.domain.enums.marital_status import MaritalStatus
from app.domain.enums.patient_status import PatientStatus
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.emergency_contact import EmergencyContact
from app.domain.value_objects.insurance_info import InsuranceInfo

if TYPE_CHECKING:
    from app.domain.entities.body_measurement import BodyMeasurement


@dataclass
class Patient(AggregateRoot):
    """Patient aggregate root.

    Represents a patient registered in the healthcare system.  This is
    the transactional boundary for all patient-related data.

    Attributes:
        mrn: Medical Record Number — unique, system-generated identifier
             used across the organization.
        first_name / last_name: Legal name.
        date_of_birth: Used for identity verification and age-based
                       clinical decisions.
        gender: Biological sex / gender identity.
        marital_status: Civil status.
        ssn_last_four: Last four digits of SSN (stored for identity
                       verification; full SSN must never be persisted).
        national_id: Government-issued ID number (passport, DNI, etc.).
        blood_type: ABO-Rh blood group.
        allergies: Free-text list of known allergies.
        chronic_conditions: Free-text list of chronic conditions.
        contact_info: Phone / email.
        address: Residential address.
        emergency_contact: Required by healthcare regulations.
        insurance_info: Primary insurance coverage.
        notes: General clinical or administrative notes.
        status: Lifecycle status (active / inactive / deceased).
    """

    # --- Demographics ---
    mrn: str = ""
    first_name: str = ""
    last_name: str = ""
    date_of_birth: date | None = None
    gender: Gender = Gender.UNKNOWN
    marital_status: MaritalStatus = MaritalStatus.UNKNOWN

    # --- Body Measurements (denormalized — populated on read, not persisted here) ---
    latest_measurement: BodyMeasurement | None = field(default=None, compare=False)

    # --- Identifiers ---
    ssn_last_four: str | None = None
    national_id: str | None = None

    # --- Medical ---
    blood_type: BloodType = BloodType.UNKNOWN
    allergies: list[str] = field(default_factory=list)
    chronic_conditions: list[str] = field(default_factory=list)

    # --- Contact ---
    contact_info: ContactInfo | None = None
    address: Address | None = None
    emergency_contact: EmergencyContact | None = None

    # --- Insurance ---
    insurance_info: InsuranceInfo | None = None

    # --- Administrative ---
    notes: str | None = None
    status: PatientStatus = PatientStatus.ACTIVE

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        *,
        mrn: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        gender: Gender,
        contact_info: ContactInfo,
        marital_status: MaritalStatus = MaritalStatus.UNKNOWN,
        ssn_last_four: str | None = None,
        national_id: str | None = None,
        blood_type: BloodType = BloodType.UNKNOWN,
        allergies: list[str] | None = None,
        chronic_conditions: list[str] | None = None,
        address: Address | None = None,
        emergency_contact: EmergencyContact | None = None,
        insurance_info: InsuranceInfo | None = None,
        notes: str | None = None,
    ) -> Patient:
        """Create a new Patient with invariant checks.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        if not mrn or not mrn.strip():
            raise ValueError("Medical Record Number (MRN) is required.")
        if not first_name or not first_name.strip():
            raise ValueError("First name is required.")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required.")
        if date_of_birth is None:
            raise ValueError("Date of birth is required.")
        if date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        if ssn_last_four is not None and len(ssn_last_four) != 4:
            raise ValueError("SSN last four must be exactly 4 digits.")

        now = datetime.now(timezone.utc)

        return cls(
            id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
            mrn=mrn.strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            date_of_birth=date_of_birth,
            gender=gender,
            marital_status=marital_status,
            ssn_last_four=ssn_last_four,
            national_id=national_id,
            blood_type=blood_type,
            allergies=allergies or [],
            chronic_conditions=chronic_conditions or [],
            contact_info=contact_info,
            address=address,
            emergency_contact=emergency_contact,
            insurance_info=insurance_info,
            notes=notes,
            status=PatientStatus.ACTIVE,
        )

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def deactivate(self) -> None:
        """Mark the patient as inactive (soft-delete)."""
        self.status = PatientStatus.INACTIVE
        self.touch()

    def mark_deceased(self) -> None:
        """Mark the patient as deceased."""
        self.status = PatientStatus.DECEASED
        self.touch()

    def reactivate(self) -> None:
        """Re-activate a previously inactive patient."""
        if self.status == PatientStatus.DECEASED:
            raise ValueError("Cannot reactivate a deceased patient.")
        self.status = PatientStatus.ACTIVE
        self.touch()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int | None:
        """Compute age dynamically from date_of_birth."""
        if self.date_of_birth is None:
            return None
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )
