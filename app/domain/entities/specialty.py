"""Specialty aggregate root — represents a medical specialty in the system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.entities.base import AggregateRoot
from app.domain.enums.specialty_category import SpecialtyCategory


@dataclass
class Specialty(AggregateRoot):
    """Medical specialty aggregate root.

    Represents a recognised clinical specialisation (e.g. Cardiology,
    Dermatology). Specialties act as a reference catalogue that doctors
    are linked to.

    Attributes:
        code:        Short unique code used as a stable identifier
                     (e.g. ``"CARDIO"``, ``"DERM"``).
        name:        Human-readable full name (e.g. ``"Cardiology"``).
        category:    High-level grouping (primary care, surgical, etc.).
        description: Optional extended description.
        is_active:   Whether this specialty is currently in use.
    """

    code: str = ""
    name: str = ""
    category: SpecialtyCategory = SpecialtyCategory.OTHER
    description: str | None = None
    is_active: bool = True

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        *,
        code: str,
        name: str,
        category: SpecialtyCategory,
        description: str | None = None,
    ) -> Specialty:
        """Create a new Specialty with invariant checks.

        Raises:
            ValueError: If code or name are empty or invalid.
        """
        if not code or not code.strip():
            raise ValueError("Specialty code is required.")
        if len(code.strip()) > 20:
            raise ValueError("Specialty code must be at most 20 characters.")
        if not name or not name.strip():
            raise ValueError("Specialty name is required.")

        now = datetime.now(timezone.utc)

        return cls(
            id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
            code=code.strip().upper(),
            name=name.strip(),
            category=category,
            description=description,
            is_active=True,
        )

    # ------------------------------------------------------------------
    # Domain behaviour
    # ------------------------------------------------------------------

    def deactivate(self) -> None:
        """Mark this specialty as inactive (soft-delete)."""
        self.is_active = False
        self.touch()

    def reactivate(self) -> None:
        """Re-enable a previously deactivated specialty."""
        self.is_active = True
        self.touch()

    def update_details(
        self,
        *,
        name: str | None = None,
        category: SpecialtyCategory | None = None,
        description: str | None = None,
    ) -> None:
        """Apply partial updates to mutable fields."""
        if name is not None:
            if not name.strip():
                raise ValueError("Specialty name cannot be empty.")
            self.name = name.strip()
        if category is not None:
            self.category = category
        if description is not None:
            self.description = description
        self.touch()
