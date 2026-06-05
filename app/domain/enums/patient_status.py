"""Patient lifecycle status enumeration."""

from enum import StrEnum


class PatientStatus(StrEnum):
    """Lifecycle status of a patient record.

    Healthcare regulations typically require soft-deletes rather than
    hard-deletes, so patients transition between these statuses instead
    of being removed from the database.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"
