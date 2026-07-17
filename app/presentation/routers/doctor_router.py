"""Doctor REST API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.commands.create_doctor import CreateDoctorCommand
from app.application.commands.update_doctor import UpdateDoctorCommand
from app.application.commands.deactivate_doctor import DeactivateDoctorCommand
from app.application.dtos.doctor_dtos import (
    DoctorCreateDTO,
    DoctorResponseDTO,
    DoctorUpdateDTO,
    PaginatedDoctorsResponseDTO,
)
from app.application.queries.get_doctor import GetDoctorQuery
from app.application.queries.search_doctors import SearchDoctorsQuery
from app.application.dtos.doctor_dtos import DoctorSearchDTO
from app.core.logging import get_logger
from app.dependencies import get_unit_of_work
from app.domain.enums.doctor_status import DoctorStatus
from app.domain.exceptions import (
    DoctorNotFoundError,
    DuplicateDoctorError,
    InvalidDoctorDataError,
    SpecialtyNotFoundError,
)

router = APIRouter(prefix="/api/v1/doctors", tags=["Doctors"])
logger = get_logger(__name__)


# ------------------------------------------------------------------
# POST /api/v1/doctors
# ------------------------------------------------------------------
@router.post(
    "",
    response_model=DoctorResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new doctor",
    description=(
        "Create a new doctor profile. A unique employee ID is generated automatically. "
        "The specialty_id must reference an existing, active specialty."
    ),
)
async def create_doctor(
    dto: DoctorCreateDTO,
    uow=Depends(get_unit_of_work),
) -> DoctorResponseDTO:
    logger.debug(
        "create_doctor request received",
        extra={"name": f"{dto.first_name} {dto.last_name}", "specialty_id": str(dto.specialty_id)},
    )
    try:
        command = CreateDoctorCommand(uow)
        result = await command.execute(dto)
        logger.info(
            "Doctor created",
            extra={"doctor_id": str(result.id), "employee_id": result.employee_id},
        )
        return result
    except SpecialtyNotFoundError as exc:
        logger.warning("Specialty not found when creating doctor", extra={"detail": exc.message})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except DuplicateDoctorError as exc:
        logger.warning("Duplicate doctor rejected", extra={"detail": exc.message})
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except InvalidDoctorDataError as exc:
        logger.warning("Invalid doctor data", extra={"detail": exc.message})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        )


# ------------------------------------------------------------------
# GET /api/v1/doctors  (search / list)
# ------------------------------------------------------------------
@router.get(
    "",
    response_model=PaginatedDoctorsResponseDTO,
    summary="Search doctors",
    description="Search and filter doctors with pagination. All filter parameters are optional.",
)
async def search_doctors(
    first_name: str | None = Query(None, max_length=100),
    last_name: str | None = Query(None, max_length=100),
    specialty_id: uuid.UUID | None = Query(None),
    doctor_status: DoctorStatus | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    uow=Depends(get_unit_of_work),
) -> PaginatedDoctorsResponseDTO:
    search_dto = DoctorSearchDTO(
        first_name=first_name,
        last_name=last_name,
        specialty_id=specialty_id,
        status=doctor_status,
        limit=limit,
        offset=offset,
    )
    query = SearchDoctorsQuery(uow)
    result = await query.execute(search_dto)
    logger.debug(
        "Doctor search returned %d/%d results",
        len(result.items),
        result.total,
        extra={"limit": limit, "offset": offset},
    )
    return result


# ------------------------------------------------------------------
# GET /api/v1/doctors/{doctor_id}
# ------------------------------------------------------------------
@router.get(
    "/{doctor_id}",
    response_model=DoctorResponseDTO,
    summary="Get doctor by ID",
    description="Retrieve a single doctor record by their unique UUID.",
)
async def get_doctor_by_id(
    doctor_id: uuid.UUID,
    uow=Depends(get_unit_of_work),
) -> DoctorResponseDTO:
    try:
        query = GetDoctorQuery(uow)
        return await query.by_id(doctor_id)
    except DoctorNotFoundError as exc:
        logger.info("Doctor not found", extra={"doctor_id": str(doctor_id)})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# ------------------------------------------------------------------
# GET /api/v1/doctors/emp/{employee_id}
# ------------------------------------------------------------------
@router.get(
    "/emp/{employee_id}",
    response_model=DoctorResponseDTO,
    summary="Get doctor by employee ID",
    description="Retrieve a single doctor record by their system-generated employee ID.",
)
async def get_doctor_by_employee_id(
    employee_id: str,
    uow=Depends(get_unit_of_work),
) -> DoctorResponseDTO:
    try:
        query = GetDoctorQuery(uow)
        return await query.by_employee_id(employee_id)
    except DoctorNotFoundError as exc:
        logger.info("Doctor not found by employee ID", extra={"employee_id": employee_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# ------------------------------------------------------------------
# PATCH /api/v1/doctors/{doctor_id}
# ------------------------------------------------------------------
@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponseDTO,
    summary="Update a doctor",
    description=(
        "Partially update a doctor record. Only fields present in the request body "
        "are modified. Status changes are routed through domain lifecycle methods."
    ),
)
async def update_doctor(
    doctor_id: uuid.UUID,
    dto: DoctorUpdateDTO,
    uow=Depends(get_unit_of_work),
) -> DoctorResponseDTO:
    logger.debug("update_doctor request", extra={"doctor_id": str(doctor_id)})
    try:
        command = UpdateDoctorCommand(uow)
        result = await command.execute(doctor_id, dto)
        logger.info("Doctor updated", extra={"doctor_id": str(doctor_id)})
        return result
    except DoctorNotFoundError as exc:
        logger.info("Doctor not found for update", extra={"doctor_id": str(doctor_id)})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SpecialtyNotFoundError as exc:
        logger.warning(
            "Specialty not found during doctor update",
            extra={"doctor_id": str(doctor_id), "detail": exc.message},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except InvalidDoctorDataError as exc:
        logger.warning(
            "Invalid update data for doctor",
            extra={"doctor_id": str(doctor_id), "detail": exc.message},
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        )


# ------------------------------------------------------------------
# DELETE /api/v1/doctors/{doctor_id}  (soft-delete)
# ------------------------------------------------------------------
@router.delete(
    "/{doctor_id}",
    response_model=DoctorResponseDTO,
    summary="Deactivate a doctor",
    description="Soft-deactivate a doctor (sets status=inactive). The record is preserved.",
)
async def deactivate_doctor(
    doctor_id: uuid.UUID,
    uow=Depends(get_unit_of_work),
) -> DoctorResponseDTO:
    logger.debug("deactivate_doctor request", extra={"doctor_id": str(doctor_id)})
    try:
        command = DeactivateDoctorCommand(uow)
        result = await command.execute(doctor_id)
        logger.info("Doctor deactivated", extra={"doctor_id": str(doctor_id)})
        return result
    except DoctorNotFoundError as exc:
        logger.info("Doctor not found for deactivation", extra={"doctor_id": str(doctor_id)})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
