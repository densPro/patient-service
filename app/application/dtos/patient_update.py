"""DTO for updating an existing patient (partial update)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums.blood_type import BloodType
from app.domain.enums.gender import Gender
from app.domain.enums.marital_status import MaritalStatus
from app.domain.enums.patient_status import PatientStatus

from app.application.dtos.patient_create import (
    AddressDTO,
    ContactInfoDTO,
    EmergencyContactDTO,
    InsuranceInfoDTO,
)


class PatientUpdateDTO(BaseModel):
    """Input DTO for partially updating a patient.

    Every field is optional.  Only fields present in the request body
    will be applied to the existing patient record.
    """

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None

    ssn_last_four: str | None = Field(None, pattern=r"^\d{4}$")
    national_id: str | None = Field(None, max_length=50)

    blood_type: BloodType | None = None
    allergies: list[str] | None = None
    chronic_conditions: list[str] | None = None

    contact_info: ContactInfoDTO | None = None
    address: AddressDTO | None = None
    emergency_contact: EmergencyContactDTO | None = None
    insurance_info: InsuranceInfoDTO | None = None

    notes: str | None = Field(None, max_length=2000)
    status: PatientStatus | None = None
