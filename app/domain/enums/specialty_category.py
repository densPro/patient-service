"""Specialty category enumeration."""

from __future__ import annotations

from enum import Enum


class SpecialtyCategory(str, Enum):
    """High-level grouping of medical specialties."""

    PRIMARY_CARE = "atencion_primaria"
    SURGICAL = "quirurgica"
    DIAGNOSTIC = "diagnostica"
    THERAPEUTIC = "terapeutica"
    MENTAL_HEALTH = "salud_mental"
    EMERGENCY = "emergencia"
    OTHER = "otra"
