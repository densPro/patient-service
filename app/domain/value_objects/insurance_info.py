"""Insurance information value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InsuranceInfo:
    """Immutable insurance coverage information.

    Stores the patient's primary insurance details for billing
    and claims processing.
    """

    provider_name: str
    policy_number: str
    group_number: str | None = None
    subscriber_name: str | None = None
    subscriber_relationship: str | None = None
    effective_date: str | None = None
    expiration_date: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "provider_name": self.provider_name,
            "policy_number": self.policy_number,
            "group_number": self.group_number,
            "subscriber_name": self.subscriber_name,
            "subscriber_relationship": self.subscriber_relationship,
            "effective_date": self.effective_date,
            "expiration_date": self.expiration_date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> InsuranceInfo:
        return cls(
            provider_name=data.get("provider_name", ""),
            policy_number=data.get("policy_number", ""),
            group_number=data.get("group_number"),
            subscriber_name=data.get("subscriber_name"),
            subscriber_relationship=data.get("subscriber_relationship"),
            effective_date=data.get("effective_date"),
            expiration_date=data.get("expiration_date"),
        )
