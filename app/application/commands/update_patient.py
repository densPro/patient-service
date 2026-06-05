"""Command handler: update an existing patient."""

from __future__ import annotations

import uuid

from app.application.commands.create_patient import _to_response
from app.application.dtos.patient_response import PatientResponseDTO
from app.application.dtos.patient_update import PatientUpdateDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.exceptions import InvalidPatientDataError, PatientNotFoundError
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.emergency_contact import EmergencyContact
from app.domain.value_objects.insurance_info import InsuranceInfo


class UpdatePatientCommand:
    """Applies a partial update to an existing patient aggregate."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, patient_id: uuid.UUID, dto: PatientUpdateDTO
    ) -> PatientResponseDTO:
        """Load, patch, and persist the patient.

        Raises:
            PatientNotFoundError: If no patient exists with the given ID.
            InvalidPatientDataError: If updated data violates domain rules.
        """
        async with self._uow:
            patient = await self._uow.patients.get_by_id(patient_id)
            if patient is None:
                raise PatientNotFoundError(str(patient_id))

            # Apply only the fields that were explicitly set in the request
            update_data = dto.model_dump(exclude_unset=True)

            for field_name, value in update_data.items():
                if field_name == "contact_info" and value is not None:
                    patient.contact_info = ContactInfo(
                        phone_number=value["phone_number"],
                        email=value.get("email"),
                        secondary_phone=value.get("secondary_phone"),
                    )
                elif field_name == "address" and value is not None:
                    patient.address = Address(
                        street_line_1=value["street_line_1"],
                        street_line_2=value.get("street_line_2"),
                        city=value.get("city", ""),
                        state=value.get("state", ""),
                        postal_code=value.get("postal_code", ""),
                        country=value.get("country", "US"),
                    )
                elif field_name == "emergency_contact" and value is not None:
                    patient.emergency_contact = EmergencyContact(
                        full_name=value["full_name"],
                        relationship=value["relationship"],
                        phone_number=value["phone_number"],
                        email=value.get("email"),
                    )
                elif field_name == "insurance_info" and value is not None:
                    patient.insurance_info = InsuranceInfo(
                        provider_name=value["provider_name"],
                        policy_number=value["policy_number"],
                        group_number=value.get("group_number"),
                        subscriber_name=value.get("subscriber_name"),
                        subscriber_relationship=value.get("subscriber_relationship"),
                        effective_date=value.get("effective_date"),
                        expiration_date=value.get("expiration_date"),
                    )
                elif field_name == "status" and value is not None:
                    # Use domain methods for status transitions
                    from app.domain.enums.patient_status import PatientStatus

                    try:
                        if value == PatientStatus.INACTIVE:
                            patient.deactivate()
                        elif value == PatientStatus.DECEASED:
                            patient.mark_deceased()
                        elif value == PatientStatus.ACTIVE:
                            patient.reactivate()
                    except ValueError as exc:
                        raise InvalidPatientDataError(str(exc)) from exc
                else:
                    setattr(patient, field_name, value)

            patient.touch()
            await self._uow.patients.update(patient)
            await self._uow.commit()

            return _to_response(patient)
