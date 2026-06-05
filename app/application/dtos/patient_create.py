"""DTO for creating a new patient."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums.blood_type import BloodType
from app.domain.enums.gender import Gender
from app.domain.enums.marital_status import MaritalStatus


class AddressDTO(BaseModel):
    """Nested address input."""

    street_line_1: str = Field(..., min_length=1, max_length=255)
    street_line_2: str | None = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field("US", max_length=3)


class ContactInfoDTO(BaseModel):
    """Nested contact information input."""

    phone_number: str = Field(..., min_length=7, max_length=20)
    email: str | None = Field(None, max_length=255)
    secondary_phone: str | None = Field(None, max_length=20)


class EmergencyContactDTO(BaseModel):
    """Nested emergency contact input."""

    full_name: str = Field(..., min_length=1, max_length=200)
    relationship: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=7, max_length=20)
    email: str | None = Field(None, max_length=255)


class InsuranceInfoDTO(BaseModel):
    """Nested insurance information input."""

    provider_name: str = Field(..., max_length=200)
    policy_number: str = Field(..., max_length=100)
    group_number: str | None = Field(None, max_length=100)
    subscriber_name: str | None = Field(None, max_length=200)
    subscriber_relationship: str | None = Field(None, max_length=100)
    effective_date: str | None = None
    expiration_date: str | None = None


class PatientCreateDTO(BaseModel):
    """Input DTO for creating a new patient.

    All required fields mirror the domain invariants enforced by
    ``Patient.create()``.
    """

    first_name: str = Field(..., min_length=1, max_length=100, examples=["María"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["García"])
    date_of_birth: date = Field(..., examples=["1990-05-15"])
    gender: Gender = Field(..., examples=[Gender.FEMALE])

    # Optional demographics
    marital_status: MaritalStatus = MaritalStatus.UNKNOWN
    ssn_last_four: str | None = Field(None, pattern=r"^\d{4}$", examples=["1234"])
    national_id: str | None = Field(None, max_length=50)
    age: int | None = Field(None, ge=0, examples=[30])
    height: float | None = Field(None, ge=0, examples=[175.5])
    weight: float | None = Field(None, ge=0, examples=[70.2])

    # Medical
    blood_type: BloodType = BloodType.UNKNOWN
    allergies: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)

    # Contact (required)
    contact_info: ContactInfoDTO

    # Optional nested objects
    address: AddressDTO | None = None
    emergency_contact: EmergencyContactDTO | None = None
    insurance_info: InsuranceInfoDTO | None = None

    # Notes
    notes: str | None = Field(None, max_length=2000)
