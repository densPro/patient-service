"""Concrete Unit of Work using async SQLAlchemy sessions."""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.unit_of_work import IUnitOfWork
from app.infrastructure.repositories.body_measurement_repository import BodyMeasurementRepository
from app.infrastructure.repositories.patient_repository import PatientRepository
from app.infrastructure.repositories.specialty_repository import SpecialtyRepository
from app.infrastructure.repositories.doctor_repository import DoctorRepository


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Manages a single database transaction via an async session.

    Usage::

        async with SqlAlchemyUnitOfWork(session_factory) as uow:
            patient = await uow.patients.get_by_id(patient_id)
            ...
            await uow.commit()
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def patients(self) -> PatientRepository:
        """Access the patient repository for this unit of work."""
        if self._session is None:
            raise RuntimeError("UnitOfWork is not in an active context.")
        if not hasattr(self, "_patients"):
            self._patients = PatientRepository(self._session)
        return self._patients

    @property
    def measurements(self) -> BodyMeasurementRepository:
        """Access the body measurement repository for this unit of work."""
        if self._session is None:
            raise RuntimeError("UnitOfWork is not in an active context.")
        if not hasattr(self, "_measurements"):
            self._measurements = BodyMeasurementRepository(self._session)
        return self._measurements

    @property
    def specialties(self) -> SpecialtyRepository:
        """Access the specialty repository for this unit of work."""
        if self._session is None:
            raise RuntimeError("UnitOfWork is not in an active context.")
        if not hasattr(self, "_specialties"):
            self._specialties = SpecialtyRepository(self._session)
        return self._specialties

    @property
    def doctors(self) -> DoctorRepository:
        """Access the doctor repository for this unit of work."""
        if self._session is None:
            raise RuntimeError("UnitOfWork is not in an active context.")
        if not hasattr(self, "_doctors"):
            self._doctors = DoctorRepository(self._session)
        return self._doctors

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._session_factory()
        self._patients = PatientRepository(self._session)
        self._measurements = BodyMeasurementRepository(self._session)
        self._specialties = SpecialtyRepository(self._session)
        self._doctors = DoctorRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        if self._session:
            await self._session.close()
        self._session = None
