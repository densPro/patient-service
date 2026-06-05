"""Patient REST API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.commands.create_patient import CreatePatientCommand
from app.application.commands.update_patient import UpdatePatientCommand
from app.application.dtos.patient_create import PatientCreateDTO
from app.application.dtos.patient_response import (
    PaginatedPatientsResponseDTO,
    PatientResponseDTO,
)
from app.application.dtos.patient_search import PatientSearchDTO
from app.application.dtos.patient_update import PatientUpdateDTO
from app.application.queries.get_patient import GetPatientQuery
from app.application.queries.search_patients import SearchPatientsQuery
from app.dependencies import get_unit_of_work
from app.domain.enums.patient_status import PatientStatus
from app.domain.exceptions import (
    DuplicatePatientError,
    InvalidPatientDataError,
    PatientNotFoundError,
)

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])


# ------------------------------------------------------------------
# POST /api/v1/patients
# ------------------------------------------------------------------
@router.post(
    "",
    response_model=PatientResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient",
    description="Register a new patient in the system. A unique MRN is generated automatically.",
)
async def create_patient(
    dto: PatientCreateDTO,
    uow=Depends(get_unit_of_work),
) -> PatientResponseDTO:
    try:
        command = CreatePatientCommand(uow)
        return await command.execute(dto)
    except DuplicatePatientError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except InvalidPatientDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        )


# ------------------------------------------------------------------
# GET /api/v1/patients/{patient_id}
# ------------------------------------------------------------------
@router.get(
    "/{patient_id}",
    response_model=PatientResponseDTO,
    summary="Get patient by ID",
    description="Retrieve a single patient record by their unique identifier.",
)
async def get_patient_by_id(
    patient_id: uuid.UUID,
    uow=Depends(get_unit_of_work),
) -> PatientResponseDTO:
    try:
        query = GetPatientQuery(uow)
        return await query.by_id(patient_id)
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# ------------------------------------------------------------------
# GET /api/v1/patients/mrn/{mrn}
# ------------------------------------------------------------------
@router.get(
    "/mrn/{mrn}",
    response_model=PatientResponseDTO,
    summary="Get patient by MRN",
    description="Retrieve a single patient record by their Medical Record Number.",
)
async def get_patient_by_mrn(
    mrn: str,
    uow=Depends(get_unit_of_work),
) -> PatientResponseDTO:
    try:
        query = GetPatientQuery(uow)
        return await query.by_mrn(mrn)
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# ------------------------------------------------------------------
# PATCH /api/v1/patients/{patient_id}
# ------------------------------------------------------------------
@router.patch(
    "/{patient_id}",
    response_model=PatientResponseDTO,
    summary="Update a patient",
    description="Partially update a patient record. Only fields present in the request body are modified.",
)
async def update_patient(
    patient_id: uuid.UUID,
    dto: PatientUpdateDTO,
    uow=Depends(get_unit_of_work),
) -> PatientResponseDTO:
    try:
        command = UpdatePatientCommand(uow)
        return await command.execute(patient_id, dto)
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except InvalidPatientDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        )


# ------------------------------------------------------------------
# GET /api/v1/patients  (search)
# ------------------------------------------------------------------
@router.get(
    "",
    response_model=PaginatedPatientsResponseDTO,
    summary="Search patients",
    description="Search and filter patients with pagination. All filter parameters are optional.",
)
async def search_patients(
    first_name: str | None = Query(None, max_length=100),
    last_name: str | None = Query(None, max_length=100),
    date_of_birth: str | None = Query(None, examples=["1990-05-15"]),
    mrn: str | None = Query(None, max_length=50),
    patient_status: PatientStatus | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    uow=Depends(get_unit_of_work),
) -> PaginatedPatientsResponseDTO:
    search_dto = PatientSearchDTO(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        mrn=mrn,
        status=patient_status,
        limit=limit,
        offset=offset,
    )
    query = SearchPatientsQuery(uow)
    return await query.execute(search_dto)
