"""Doctor aggregate root — represents a physician in the healthcare system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.domain.entities.base import AggregateRoot
from app.domain.enums.doctor_status import DoctorStatus
from app.domain.enums.gender import Gender
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.license_info import LicenseInfo


@dataclass
class Doctor(AggregateRoot):
    """Doctor aggregate root.

    Represents a licensed physician registered in the system.  Doctors
    are linked to a single primary specialty and carry their own profile
    information (license, contact details, bio, etc.).

    Attributes:
        employee_id:         System-generated unique employee identifier
                             (format: ``EMP-XXXXXXXX``).
        first_name:          Legal first name.
        last_name:           Legal last name.
        date_of_birth:       Optional, for HR / identity purposes.
        gender:              Gender identity.
        specialty_id:        FK to the primary Specialty aggregate.
        license_info:        Medical license data (number, issuing board, expiry).
        contact_info:        Phone / email.
        address:             Work or home address.
        years_of_experience: Self-reported clinical experience in years.
        bio:                 Free-text professional biography.
        status:              Lifecycle status.
    """

    # --- Identity ---
    employee_id: str = ""
    first_name: str = ""
    last_name: str = ""
    date_of_birth: date | None = None
    gender: Gender = Gender.UNKNOWN

    # --- Specialty ---
    specialty_id: uuid.UUID = field(default_factory=uuid.uuid4)

    # --- Professional ---
    license_info: LicenseInfo | None = None
    years_of_experience: int | None = None
    bio: str | None = None

    # --- Contact ---
    contact_info: ContactInfo | None = None
    address: Address | None = None

    # --- Administrative ---
    status: DoctorStatus = DoctorStatus.ACTIVE

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        *,
        employee_id: str,
        first_name: str,
        last_name: str,
        specialty_id: uuid.UUID,
        gender: Gender = Gender.UNKNOWN,
        date_of_birth: date | None = None,
        license_info: LicenseInfo | None = None,
        contact_info: ContactInfo | None = None,
        address: Address | None = None,
        years_of_experience: int | None = None,
        bio: str | None = None,
    ) -> Doctor:
        """Create a new Doctor with invariant checks.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        if not employee_id or not employee_id.strip():
            raise ValueError("Employee ID is required.")
        if not first_name or not first_name.strip():
            raise ValueError("First name is required.")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required.")
        if date_of_birth is not None and date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        if years_of_experience is not None and years_of_experience < 0:
            raise ValueError("Years of experience cannot be negative.")

        now = datetime.now(timezone.utc)

        return cls(
            id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
            employee_id=employee_id.strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            date_of_birth=date_of_birth,
            gender=gender,
            specialty_id=specialty_id,
            license_info=license_info,
            contact_info=contact_info,
            address=address,
            years_of_experience=years_of_experience,
            bio=bio,
            status=DoctorStatus.ACTIVE,
        )

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def deactivate(self) -> None:
        """Mark the doctor as inactive (soft-delete)."""
        self.status = DoctorStatus.INACTIVE
        self.touch()

    def reactivate(self) -> None:
        """Re-activate a previously inactive doctor."""
        if self.status == DoctorStatus.RETIRED:
            raise ValueError("Cannot reactivate a retired doctor.")
        self.status = DoctorStatus.ACTIVE
        self.touch()

    def go_on_leave(self) -> None:
        """Set status to on-leave."""
        if self.status != DoctorStatus.ACTIVE:
            raise ValueError("Only active doctors can be placed on leave.")
        self.status = DoctorStatus.ON_LEAVE
        self.touch()

    def retire(self) -> None:
        """Mark the doctor as retired."""
        self.status = DoctorStatus.RETIRED
        self.touch()

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

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
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )
