"""Specialty category enumeration."""

from __future__ import annotations

from enum import Enum


class SpecialtyCategory(str, Enum):
    """High-level grouping of medical specialties."""

    PRIMARY_CARE = "primary_care"
    SURGICAL = "surgical"
    DIAGNOSTIC = "diagnostic"
    THERAPEUTIC = "therapeutic"
    MENTAL_HEALTH = "mental_health"
    EMERGENCY = "emergency"
    OTHER = "other"
