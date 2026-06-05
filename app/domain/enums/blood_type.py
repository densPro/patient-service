"""Blood type enumeration for patient medical information."""

from enum import StrEnum


class BloodType(StrEnum):
    """ABO-Rh blood group classification."""

    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"
