"""Address value object for patient residence and mailing addresses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """Immutable postal address.

    Used for patient residence, mailing, and billing addresses.
    """

    street_line_1: str
    street_line_2: str | None = None
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = "US"

    def to_dict(self) -> dict[str, str | None]:
        return {
            "street_line_1": self.street_line_1,
            "street_line_2": self.street_line_2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> Address:
        return cls(
            street_line_1=data.get("street_line_1", ""),
            street_line_2=data.get("street_line_2"),
            city=data.get("city", ""),
            state=data.get("state", ""),
            postal_code=data.get("postal_code", ""),
            country=data.get("country", "US"),
        )
