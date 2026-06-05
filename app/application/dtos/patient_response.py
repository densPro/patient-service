"""DTO for patient API responses."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums.blood_type import BloodType
from app.domain.enums.gender import Gender
from app.domain.enums.marital_status import MaritalStatus
from app.domain.enums.patient_status import PatientStatus

from app.application.dtos.body_measurement_dtos import BodyMeasurementResponseDTO
from app.application.dtos.patient_create import (
    AddressDTO,
    ContactInfoDTO,
    EmergencyContactDTO,
    InsuranceInfoDTO,
)


class PatientResponseDTO(BaseModel):
    """Output DTO returned by patient API endpoints.

    Maps 1:1 from the ``Patient`` domain entity, but uses Pydantic
    serialization rather than exposing the domain object directly.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mrn: str
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: date
    gender: Gender
    marital_status: MaritalStatus

    ssn_last_four: str | None = None
    national_id: str | None = None
    age: int | None = None

    # Latest measurement (denormalized for convenience)
    latest_measurement: BodyMeasurementResponseDTO | None = None

    blood_type: BloodType
    allergies: list[str]
    chronic_conditions: list[str]

    contact_info: ContactInfoDTO | None = None
    address: AddressDTO | None = None
    emergency_contact: EmergencyContactDTO | None = None
    insurance_info: InsuranceInfoDTO | None = None

    notes: str | None = None
    status: PatientStatus

    created_at: datetime
    updated_at: datetime


class PaginatedPatientsResponseDTO(BaseModel):
    """Paginated list response for patient search."""

    items: list[PatientResponseDTO]
    total: int
    limit: int
    offset: int
