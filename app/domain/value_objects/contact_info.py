"""Contact information value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContactInfo:
    """Immutable contact information for a patient.

    Stores the primary phone, secondary phone, and email.
    """

    phone_number: str
    email: str | None = None
    secondary_phone: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "phone_number": self.phone_number,
            "email": self.email,
            "secondary_phone": self.secondary_phone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> ContactInfo:
        return cls(
            phone_number=data.get("phone_number", ""),
            email=data.get("email"),
            secondary_phone=data.get("secondary_phone"),
        )
