"""Abstract Unit of Work interface (port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from app.application.interfaces.body_measurement_repository import IBodyMeasurementRepository
from app.application.interfaces.patient_repository import IPatientRepository
from app.application.interfaces.specialty_repository import ISpecialtyRepository
from app.application.interfaces.doctor_repository import IDoctorRepository


class IUnitOfWork(ABC):
    """Port defining the contract for a transactional unit of work.

    Usage::

        async with uow:
            patient = await uow.patients.get_by_id(patient_id)
            patient.deactivate()
            await uow.patients.update(patient)
            await uow.commit()
    """

    patients: IPatientRepository
    measurements: IBodyMeasurementRepository
    specialties: ISpecialtyRepository
    doctors: IDoctorRepository

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back the current transaction."""
        ...

    @abstractmethod
    async def __aenter__(self) -> IUnitOfWork:
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        ...
