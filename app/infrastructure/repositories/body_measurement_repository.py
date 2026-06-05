"""Concrete body measurement repository using async SQLAlchemy."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.body_measurement_repository import IBodyMeasurementRepository
from app.domain.entities.body_measurement import BodyMeasurement
from app.infrastructure.database.models.body_measurement_model import BodyMeasurementModel


class BodyMeasurementRepository(IBodyMeasurementRepository):
    """SQLAlchemy implementation of ``IBodyMeasurementRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    async def get_latest_by_patient(self, patient_id: uuid.UUID) -> BodyMeasurement | None:
        stmt = (
            select(BodyMeasurementModel)
            .where(BodyMeasurementModel.patient_id == patient_id)
            .order_by(BodyMeasurementModel.measured_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_patient(
        self,
        patient_id: uuid.UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[BodyMeasurement], int]:
        from sqlalchemy import func

        count_stmt = (
            select(func.count())
            .select_from(BodyMeasurementModel)
            .where(BodyMeasurementModel.patient_id == patient_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(BodyMeasurementModel)
            .where(BodyMeasurementModel.patient_id == patient_id)
            .order_by(BodyMeasurementModel.measured_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    async def add(self, measurement: BodyMeasurement) -> BodyMeasurement:
        model = self._to_model(measurement)
        self._session.add(model)
        await self._session.flush()
        return measurement

    # ------------------------------------------------------------------
    # Mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_entity(model: BodyMeasurementModel) -> BodyMeasurement:
        """Map ORM model → domain entity."""
        return BodyMeasurement(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.created_at,  # measurements are immutable; no updated_at
            patient_id=model.patient_id,
            measured_at=model.measured_at,
            height_cm=model.height_cm,
            weight_kg=model.weight_kg,
            waist_cm=model.waist_cm,
            hip_cm=model.hip_cm,
        )

    @staticmethod
    def _to_model(measurement: BodyMeasurement) -> BodyMeasurementModel:
        """Map domain entity → ORM model."""
        return BodyMeasurementModel(
            id=measurement.id,
            patient_id=measurement.patient_id,
            measured_at=measurement.measured_at,
            height_cm=measurement.height_cm,
            weight_kg=measurement.weight_kg,
            waist_cm=measurement.waist_cm,
            hip_cm=measurement.hip_cm,
            created_at=measurement.created_at,
        )
