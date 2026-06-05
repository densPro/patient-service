"""Marital status enumeration for patient demographics."""

from enum import StrEnum


class MaritalStatus(StrEnum):
    """Marital / civil status of a patient."""

    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"
    DOMESTIC_PARTNER = "domestic_partner"
    UNKNOWN = "unknown"
