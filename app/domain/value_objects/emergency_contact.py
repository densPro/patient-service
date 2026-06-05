"""Emergency contact value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmergencyContact:
    """Immutable emergency contact information.

    Healthcare facilities are required to maintain emergency contact
    details for every patient.
    """

    full_name: str
    relationship: str
    phone_number: str
    email: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "full_name": self.full_name,
            "relationship": self.relationship,
            "phone_number": self.phone_number,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> EmergencyContact:
        return cls(
            full_name=data.get("full_name", ""),
            relationship=data.get("relationship", ""),
            phone_number=data.get("phone_number", ""),
            email=data.get("email"),
        )
