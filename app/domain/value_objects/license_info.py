"""LicenseInfo value object — physician license details."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LicenseInfo:
    """Immutable value object representing a medical license.

    Attributes:
        license_number: The official license number issued by the authority.
        issuing_body:   Name of the licensing board or authority.
        issue_date:     Date the license was issued.
        expiration_date: Date the license expires (None = no expiry / lifetime).
        state:          US state or jurisdiction code (e.g. "PR", "NY").
    """

    license_number: str
    issuing_body: str
    issue_date: date | None = None
    expiration_date: date | None = None
    state: str | None = None

    def is_valid(self) -> bool:
        """Return True if the license is currently valid (not expired)."""
        if self.expiration_date is None:
            return True
        return self.expiration_date >= date.today()

    def to_dict(self) -> dict:
        return {
            "license_number": self.license_number,
            "issuing_body": self.issuing_body,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "expiration_date": (
                self.expiration_date.isoformat() if self.expiration_date else None
            ),
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> LicenseInfo:
        return cls(
            license_number=data["license_number"],
            issuing_body=data["issuing_body"],
            issue_date=(
                date.fromisoformat(data["issue_date"]) if data.get("issue_date") else None
            ),
            expiration_date=(
                date.fromisoformat(data["expiration_date"])
                if data.get("expiration_date")
                else None
            ),
            state=data.get("state"),
        )
