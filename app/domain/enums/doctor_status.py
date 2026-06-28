"""Doctor status enumeration."""

from __future__ import annotations

from enum import Enum


class DoctorStatus(str, Enum):
    """Lifecycle status of a doctor in the system."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    RETIRED = "retired"
