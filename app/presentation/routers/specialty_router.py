"""Specialty REST API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.commands.create_specialty import CreateSpecialtyCommand
from app.application.commands.update_specialty import UpdateSpecialtyCommand
from app.application.commands.deactivate_specialty import DeactivateSpecialtyCommand
from app.application.dtos.specialty_dtos import (
    SpecialtyCreateDTO,
    SpecialtyResponseDTO,
    SpecialtyUpdateDTO,
)
from app.application.queries.get_specialty import GetSpecialtyQuery
from app.dependencies import get_unit_of_work
from app.domain.exceptions import (
    DuplicateSpecialtyError,
    InvalidSpecialtyDataError,
    SpecialtyNotFoundError,
)

router = APIRouter(prefix="/api/v1/specialties", tags=["Specialties"])


# ------------------------------------------------------------------
# POST /api/v1/specialties
# ------------------------------------------------------------------
@router.post(
    "",
    response_model=SpecialtyResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new specialty",
    description="Add a new medical specialty to the catalogue. The code must be unique.",
)
async def create_specialty(
    dto: SpecialtyCreateDTO,
    uow=Depends(get_unit_of_work),
) -> SpecialtyResponseDTO:
    try:
        command = CreateSpecialtyCommand(uow)
        return await command.execute(dto)
    except DuplicateSpecialtyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except InvalidSpecialtyDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        )


# ------------------------------------------------------------------
# GET /api/v1/specialties
# ------------------------------------------------------------------
@router.get(
    "",
    response_model=list[SpecialtyResponseDTO],
    summary="List all specialties",
    description="Return all specialties. Use `active_only=true` to filter to active specialties only.",
)
async def list_specialties(
    active_only: bool = Query(False, description="If true, only return active specialties."),
    uow=Depends(get_unit_of_work),
) -> list[SpecialtyResponseDTO]:
    query = GetSpecialtyQuery(uow)
    return await query.list_all(active_only=active_only)


# ------------------------------------------------------------------
# GET /api/v1/specialties/{specialty_id}
# ------------------------------------------------------------------
@router.get(
    "/{specialty_id}",
    response_model=SpecialtyResponseDTO,
    summary="Get specialty by ID",
    description="Retrieve a single specialty by its unique UUID.",
)
async def get_specialty_by_id(
    specialty_id: uuid.UUID,
    uow=Depends(get_unit_of_work),
) -> SpecialtyResponseDTO:
    try:
        query = GetSpecialtyQuery(uow)
        return await query.by_id(specialty_id)
    except SpecialtyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# ------------------------------------------------------------------
# GET /api/v1/specialties/code/{code}
# ------------------------------------------------------------------
@router.get(
    "/code/{code}",
    response_model=SpecialtyResponseDTO,
    summary="Get specialty by code",
    description="Retrieve a single specialty by its unique code (e.g. CARDIO).",
)
async def get_specialty_by_code(
    code: str,
    uow=Depends(get_unit_of_work),
) -> SpecialtyResponseDTO:
    try:
        query = GetSpecialtyQuery(uow)
        return await query.by_code(code)
    except SpecialtyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# ------------------------------------------------------------------
# PATCH /api/v1/specialties/{specialty_id}
# ------------------------------------------------------------------
@router.patch(
    "/{specialty_id}",
    response_model=SpecialtyResponseDTO,
    summary="Update a specialty",
    description="Partially update a specialty. Only supplied fields are modified.",
)
async def update_specialty(
    specialty_id: uuid.UUID,
    dto: SpecialtyUpdateDTO,
    uow=Depends(get_unit_of_work),
) -> SpecialtyResponseDTO:
    try:
        command = UpdateSpecialtyCommand(uow)
        return await command.execute(specialty_id, dto)
    except SpecialtyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except InvalidSpecialtyDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        )


# ------------------------------------------------------------------
# DELETE /api/v1/specialties/{specialty_id}  (soft-delete)
# ------------------------------------------------------------------
@router.delete(
    "/{specialty_id}",
    response_model=SpecialtyResponseDTO,
    summary="Deactivate a specialty",
    description="Soft-delete a specialty (sets is_active=false). The record is preserved.",
)
async def deactivate_specialty(
    specialty_id: uuid.UUID,
    uow=Depends(get_unit_of_work),
) -> SpecialtyResponseDTO:
    try:
        command = DeactivateSpecialtyCommand(uow)
        return await command.execute(specialty_id)
    except SpecialtyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
