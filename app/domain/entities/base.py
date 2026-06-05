"""Base entity and aggregate root classes for the domain layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class Entity:
    """Base class for all domain entities.

    Provides identity, creation/update timestamps, and equality by ID.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def touch(self) -> None:
        """Update the `updated_at` timestamp to the current UTC time."""
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class AggregateRoot(Entity):
    """Marker base class for aggregate roots.

    An aggregate root is the entry point for a cluster of domain objects
    that are treated as a single transactional unit.
    """

    pass
