"""Gender enumeration for patient demographics."""

from enum import StrEnum


class Gender(StrEnum):
    """Biological sex / gender identity used for clinical purposes."""

    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    UNKNOWN = "unknown"
