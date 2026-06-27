"""DTOs for the Specialty bounded context."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums.specialty_category import SpecialtyCategory


# ---------------------------------------------------------------------------
# Create DTO
# ---------------------------------------------------------------------------


class SpecialtyCreateDTO(BaseModel):
    """Input schema for creating a new specialty."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        pattern=r"^[A-Z0-9_]+$",
        examples=["CARDIO"],
        description="Unique uppercase code (letters, digits, underscores only).",
    )
    name: str = Field(..., min_length=1, max_length=150, examples=["Cardiology"])
    category: SpecialtyCategory = Field(
        ..., examples=[SpecialtyCategory.THERAPEUTIC]
    )
    description: str | None = Field(None, max_length=1000)


# ---------------------------------------------------------------------------
# Update DTO
# ---------------------------------------------------------------------------


class SpecialtyUpdateDTO(BaseModel):
    """Input schema for partially updating a specialty."""

    name: str | None = Field(None, min_length=1, max_length=150)
    category: SpecialtyCategory | None = None
    description: str | None = Field(None, max_length=1000)


# ---------------------------------------------------------------------------
# Response DTO
# ---------------------------------------------------------------------------


class SpecialtyResponseDTO(BaseModel):
    """Output schema returned to API consumers."""

    id: uuid.UUID
    code: str
    name: str
    category: SpecialtyCategory
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
