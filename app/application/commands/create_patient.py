"""Command handler: create a new patient."""

from __future__ import annotations

import uuid

from app.application.dtos.body_measurement_dtos import BodyMeasurementResponseDTO
from app.application.dtos.patient_create import PatientCreateDTO
from app.application.dtos.patient_response import PatientResponseDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.patient import Patient
from app.domain.exceptions import DuplicatePatientError, InvalidPatientDataError
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.emergency_contact import EmergencyContact
from app.domain.value_objects.insurance_info import InsuranceInfo


def _generate_mrn() -> str:
    """Generate a unique Medical Record Number.

    Format: ``MRN-<8-hex-chars>`` (e.g. ``MRN-3a9f12bc``).
    In production this could be replaced with a sequential generator
    or an external MRN service.
    """
    return f"MRN-{uuid.uuid4().hex[:8].upper()}"


class CreatePatientCommand:
    """Creates a new patient aggregate and persists it."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: PatientCreateDTO) -> PatientResponseDTO:
        """Validate, build, and persist a new patient.

        Raises:
            DuplicatePatientError: If the generated MRN collides (unlikely).
            InvalidPatientDataError: If domain validation fails.
        """
        mrn = _generate_mrn()

        async with self._uow:
            # Check MRN uniqueness (extremely unlikely collision)
            existing = await self._uow.patients.get_by_mrn(mrn)
            if existing is not None:
                raise DuplicatePatientError(mrn)

            # Map nested DTOs → value objects
            contact_info = ContactInfo(
                phone_number=dto.contact_info.phone_number,
                email=dto.contact_info.email,
                secondary_phone=dto.contact_info.secondary_phone,
            )

            address = (
                Address(
                    street_line_1=dto.address.street_line_1,
                    street_line_2=dto.address.street_line_2,
                    city=dto.address.city,
                    state=dto.address.state,
                    postal_code=dto.address.postal_code,
                    country=dto.address.country,
                )
                if dto.address
                else None
            )

            emergency_contact = (
                EmergencyContact(
                    full_name=dto.emergency_contact.full_name,
                    relationship=dto.emergency_contact.relationship,
                    phone_number=dto.emergency_contact.phone_number,
                    email=dto.emergency_contact.email,
                )
                if dto.emergency_contact
                else None
            )

            insurance_info = (
                InsuranceInfo(
                    provider_name=dto.insurance_info.provider_name,
                    policy_number=dto.insurance_info.policy_number,
                    group_number=dto.insurance_info.group_number,
                    subscriber_name=dto.insurance_info.subscriber_name,
                    subscriber_relationship=dto.insurance_info.subscriber_relationship,
                    effective_date=dto.insurance_info.effective_date,
                    expiration_date=dto.insurance_info.expiration_date,
                )
                if dto.insurance_info
                else None
            )

            # Build domain entity via factory
            try:
                patient = Patient.create(
                    mrn=mrn,
                    first_name=dto.first_name,
                    last_name=dto.last_name,
                    date_of_birth=dto.date_of_birth,
                    gender=dto.gender,
                    marital_status=dto.marital_status,
                    ssn_last_four=dto.ssn_last_four,
                    national_id=dto.national_id,
                    blood_type=dto.blood_type,
                    allergies=dto.allergies,
                    chronic_conditions=dto.chronic_conditions,
                    contact_info=contact_info,
                    address=address,
                    emergency_contact=emergency_contact,
                    insurance_info=insurance_info,
                    notes=dto.notes,
                )
            except ValueError as exc:
                raise InvalidPatientDataError(str(exc)) from exc

            await self._uow.patients.add(patient)
            await self._uow.commit()

            return _to_response(patient)


def _measurement_to_dto(measurement, patient: Patient) -> BodyMeasurementResponseDTO | None:
    """Map an optional BodyMeasurement entity to a BodyMeasurementResponseDTO."""
    if measurement is None:
        return None
    return BodyMeasurementResponseDTO(
        id=measurement.id,
        patient_id=measurement.patient_id,
        measured_at=measurement.measured_at,
        height_cm=measurement.height_cm,
        height_m=measurement.height_m,
        weight_kg=measurement.weight_kg,
        waist_cm=measurement.waist_cm,
        hip_cm=measurement.hip_cm,
        bmi=measurement.bmi,
        bmi_category=measurement.bmi_category,
        healthy_weight=measurement.healthy_weight,
        minimum_weight=measurement.minimum_weight,
        maximum_weight=measurement.maximum_weight,
        bmr_harris_benedict=measurement.calculate_bmr_harris_benedict(patient.age, patient.gender.value) if patient.age is not None else None,
        bmr_mifflin_st_jeor=measurement.calculate_bmr_mifflin_st_jeor(patient.age, patient.gender.value) if patient.age is not None else None,
        created_at=measurement.created_at,
    )



def _to_response(patient: Patient) -> PatientResponseDTO:
    """Map domain entity → response DTO."""
    from app.application.dtos.patient_create import (
        AddressDTO,
        ContactInfoDTO,
        EmergencyContactDTO,
        InsuranceInfoDTO,
    )

    contact_dto = None
    if patient.contact_info:
        contact_dto = ContactInfoDTO(
            phone_number=patient.contact_info.phone_number,
            email=patient.contact_info.email,
            secondary_phone=patient.contact_info.secondary_phone,
        )

    address_dto = None
    if patient.address:
        address_dto = AddressDTO(
            street_line_1=patient.address.street_line_1,
            street_line_2=patient.address.street_line_2,
            city=patient.address.city,
            state=patient.address.state,
            postal_code=patient.address.postal_code,
            country=patient.address.country,
        )

    emergency_dto = None
    if patient.emergency_contact:
        emergency_dto = EmergencyContactDTO(
            full_name=patient.emergency_contact.full_name,
            relationship=patient.emergency_contact.relationship,
            phone_number=patient.emergency_contact.phone_number,
            email=patient.emergency_contact.email,
        )

    insurance_dto = None
    if patient.insurance_info:
        insurance_dto = InsuranceInfoDTO(
            provider_name=patient.insurance_info.provider_name,
            policy_number=patient.insurance_info.policy_number,
            group_number=patient.insurance_info.group_number,
            subscriber_name=patient.insurance_info.subscriber_name,
            subscriber_relationship=patient.insurance_info.subscriber_relationship,
            effective_date=patient.insurance_info.effective_date,
            expiration_date=patient.insurance_info.expiration_date,
        )

    return PatientResponseDTO(
        id=patient.id,
        mrn=patient.mrn,
        first_name=patient.first_name,
        last_name=patient.last_name,
        full_name=patient.full_name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        marital_status=patient.marital_status,
        ssn_last_four=patient.ssn_last_four,
        national_id=patient.national_id,
        age=patient.age,
        blood_type=patient.blood_type,
        allergies=patient.allergies,
        chronic_conditions=patient.chronic_conditions,
        contact_info=contact_dto,
        address=address_dto,
        emergency_contact=emergency_dto,
        insurance_info=insurance_dto,
        notes=patient.notes,
        status=patient.status,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
        latest_measurement=_measurement_to_dto(patient.latest_measurement, patient),
    )
