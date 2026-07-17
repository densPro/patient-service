"""Body measurement REST API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.commands.add_body_measurement import AddBodyMeasurementCommand
from app.application.dtos.body_measurement_dtos import (
    BodyMeasurementCreateDTO,
    BodyMeasurementResponseDTO,
    PaginatedMeasurementsResponseDTO,
)
from app.application.queries.get_body_measurements import GetBodyMeasurementsQuery
from app.core.logging import get_logger
from app.dependencies import get_unit_of_work
from app.domain.exceptions import InvalidPatientDataError, PatientNotFoundError

router = APIRouter(prefix="/api/v1/patients", tags=["Body Measurements"])
logger = get_logger(__name__)


# ------------------------------------------------------------------
# POST /api/v1/patients/{patient_id}/measurements
# ------------------------------------------------------------------
@router.post(
    "/{patient_id}/measurements",
    response_model=BodyMeasurementResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Record a body measurement",
    description=(
        "Record a new body measurement snapshot for a patient. "
        "At least one measurement value (height, weight, waist, or hip) must be provided."
    ),
)
async def add_body_measurement(
    patient_id: uuid.UUID,
    dto: BodyMeasurementCreateDTO,
    uow=Depends(get_unit_of_work),
) -> BodyMeasurementResponseDTO:
    logger.debug("add_body_measurement request", extra={"patient_id": str(patient_id)})
    try:
        command = AddBodyMeasurementCommand(uow)
        result = await command.execute(patient_id, dto)
        logger.info(
            "Body measurement recorded",
            extra={"patient_id": str(patient_id), "measurement_id": str(result.id)},
        )
        return result
    except PatientNotFoundError as exc:
        logger.info("Patient not found for measurement", extra={"patient_id": str(patient_id)})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except InvalidPatientDataError as exc:
        logger.warning(
            "Invalid measurement data",
            extra={"patient_id": str(patient_id), "detail": exc.message},
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        )


# ------------------------------------------------------------------
# GET /api/v1/patients/{patient_id}/measurements/latest
# ------------------------------------------------------------------
@router.get(
    "/{patient_id}/measurements/latest",
    response_model=BodyMeasurementResponseDTO,
    summary="Get latest body measurement",
    description="Retrieve the most recent body measurement recorded for a patient.",
)
async def get_latest_measurement(
    patient_id: uuid.UUID,
    uow=Depends(get_unit_of_work),
) -> BodyMeasurementResponseDTO:
    try:
        query = GetBodyMeasurementsQuery(uow)
        return await query.latest(patient_id)
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# ------------------------------------------------------------------
# GET /api/v1/patients/{patient_id}/measurements
# ------------------------------------------------------------------
@router.get(
    "/{patient_id}/measurements",
    response_model=PaginatedMeasurementsResponseDTO,
    summary="List body measurements",
    description="Retrieve the full measurement history for a patient, newest first.",
)
async def list_measurements(
    patient_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    uow=Depends(get_unit_of_work),
) -> PaginatedMeasurementsResponseDTO:
    try:
        query = GetBodyMeasurementsQuery(uow)
        return await query.list_all(patient_id, limit=limit, offset=offset)
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
