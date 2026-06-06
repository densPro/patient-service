"""BodyMeasurement entity — represents a single body measurement snapshot for a patient."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.entities.base import AggregateRoot


_ACTIVITY_FACTORS: dict[str, float] = {
    "sedentary": 1.0,
    "lightly_active": 1.12,
    "moderately_active": 1.29,
    "very_active": 1.59,
}

_STRESS_FACTORS: dict[str, float] = {
    "major_surgery": 1.2,
    "minor_surgery": 1.1,
    "mild_infection": 1.1,
    "moderate_infection": 1.5,
    "severe_infection": 1.8,
    "trauma_with_impaired_consciousness": 1.35,
    "burns_40_tbsa": 1.5,
    "burns_100_tbsa": 1.95,
    "cancer": 1.2, 
    "malnutrition": 0.7,
    "traumatic_brain_injury": 1.6
}



@dataclass
class BodyMeasurement(AggregateRoot):
    """A time-stamped body measurement record linked to a patient.

    Each instance represents one clinical measurement event.
    Patients can accumulate many measurements over time, enabling
    trend analysis (weight loss, BMI evolution, etc.).

    Attributes:
        patient_id:  The owning patient's UUID.
        measured_at: When the measurement was taken (defaults to now).
        height_cm:   Height in centimetres (nullable — may be absent in partial measurements).
        weight_kg:   Weight in kilograms (nullable).
        waist_cm:    Waist circumference in centimetres (nullable).
        hip_cm:      Hip circumference in centimetres (nullable).
    """

    patient_id: uuid.UUID = field(default_factory=uuid.uuid4)
    measured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    height_cm: float | None = None
    weight_kg: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        *,
        patient_id: uuid.UUID,
        height_cm: float | None = None,
        weight_kg: float | None = None,
        waist_cm: float | None = None,
        hip_cm: float | None = None,
        measured_at: datetime | None = None,
    ) -> BodyMeasurement:
        """Create a new BodyMeasurement with invariant checks.

        Raises:
            ValueError: If all measurement values are None, or if any
                        provided value is out of a clinically plausible range.
        """
        if all(v is None for v in (height_cm, weight_kg, waist_cm, hip_cm)):
            raise ValueError(
                "At least one measurement value (height, weight, waist, hip) is required."
            )

        if height_cm is not None and not (50.0 <= height_cm <= 300.0):
            raise ValueError("height_cm must be between 50 and 300 cm.")
        if weight_kg is not None and not (1.0 <= weight_kg <= 700.0):
            raise ValueError("weight_kg must be between 1 and 700 kg.")
        if waist_cm is not None and not (20.0 <= waist_cm <= 300.0):
            raise ValueError("waist_cm must be between 20 and 300 cm.")
        if hip_cm is not None and not (20.0 <= hip_cm <= 300.0):
            raise ValueError("hip_cm must be between 20 and 300 cm.")

        now = datetime.now(timezone.utc)

        return cls(
            id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
            patient_id=patient_id,
            measured_at=measured_at or now,
            height_cm=height_cm,
            weight_kg=weight_kg,
            waist_cm=waist_cm,
            hip_cm=hip_cm,
        )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def bmi(self) -> float | None:
        """Body Mass Index — kg / m².

        Returns None if either height or weight is unavailable.
        """
        if self.height_m and self.weight_kg:
            return round(self.weight_kg / (self.height_m ** 2), 2)
        return None


    @property
    def bmi_category(self) -> str | None:
        """WHO BMI classification string, or None if BMI cannot be computed."""
        bmi = self.bmi
        if bmi is None:
            return None
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25.0:
            return "Normal weight"
        if bmi < 30.0:
            return "Overweight"
        return "Obese"

    @property
    def height_m(self) -> float | None:
        """Height in metres."""
        if self.height_cm is not None:
            return round(self.height_cm / 100.0, 2)
        return None

    @property
    def healthy_weight(self) -> float | None:
        """Healthy reference weight in kilograms based on height (BMI = 22.0)."""
        if self.height_m:
            return round((self.height_m ** 2) * 22.0, 1)
        return None

    @property
    def minimum_weight(self) -> float | None:
        """Minimum healthy weight in kilograms based on height (BMI = 18.5)."""
        if self.height_m:
            return round((self.height_m ** 2) * 18.5, 1)
        return None

    @property
    def maximum_weight(self) -> float | None:
        """Maximum healthy weight in kilograms based on height (BMI = 24.9)."""
        if self.height_m:
            return round((self.height_m ** 2) * 24.9, 1)
        return None

    def calculate_bmr_harris_benedict(self, age: int, gender: str) -> float | None:
        """Calculate BMR using the revised Harris-Benedict equation (1984)."""
        if not (self.height_cm and self.weight_kg):
            return None
        
        gender_val = gender.lower().strip()
        if gender_val == "male":
            return round(66 + (13.7 * self.weight_kg) + (5 * self.height_cm) - (6.8 * age), 2)
        elif gender_val == "female":
            return round(655 + (9.7 * self.weight_kg) + (1.8 * self.height_cm) - (4.7 * age), 2)
        return None
       
    def calculate_bmr_mifflin_st_jeor(self, age: int, gender: str) -> float | None:
        """Calculate BMR using the Mifflin-St Jeor equation."""
        if not (self.height_cm and self.weight_kg):
            return None
        
        gender_val = gender.lower().strip()
        if gender_val == "male":
            return round((10.0 * self.weight_kg) + (6.25 * self.height_cm) - (5.0 * age) + 5.0, 2)
        elif gender_val == "female":
            return round((10.0 * self.weight_kg) + (6.25 * self.height_cm) - (5.0 * age) - 161.0, 2)
        return None

    def calculate_tdee_harris_benedict(self, age: int, gender: str) -> dict[str, float] | None:
        """Calculate TDEE for standard activity levels using Harris-Benedict BMR."""
        bmr = self.calculate_bmr_harris_benedict(age, gender)
        if bmr is None:
            return None
        return {
            "sedentary": round(bmr * 1, 2),
            "lightly_active": round(bmr * 1.12, 2),
            "moderately_active": round(bmr * 1.29, 2),
            "very_active": round(bmr * 1.59, 2)
        }

    def calculate_tdee_mifflin_st_jeor(self, age: int, gender: str) -> dict[str, float] | None:
        """Calculate TDEE for standard activity levels using Mifflin-St Jeor BMR."""
        bmr = self.calculate_bmr_mifflin_st_jeor(age, gender)
        if bmr is None:
            return None
        return {
            "sedentary": round(bmr * 1, 2),
            "lightly_active": round(bmr * 1.12, 2),
            "moderately_active": round(bmr * 1.29, 2),
            "very_active": round(bmr * 1.59, 2)
        }


    def _build_total_calories(self, bmr: float) -> dict[str, dict[str, float]]:
        """Return BMR × Activity Factor × Stress Factor for every combination."""
        return {
            stress_label: {
                activity_label: round(bmr * af * sf, 2)
                for activity_label, af in _ACTIVITY_FACTORS.items()
            }
            for stress_label, sf in _STRESS_FACTORS.items()
        }


    def calculate_total_calories_harris_benedict(
        self, age: int, gender: str
    ) -> dict[str, dict[str, float]] | None:
        """Total Calories = BMR × Activity Factor × Stress Factor (Harris-Benedict)."""
        bmr = self.calculate_bmr_harris_benedict(age, gender)
        return self._build_total_calories(bmr) if bmr is not None else None

    def calculate_total_calories_mifflin_st_jeor(
        self, age: int, gender: str
    ) -> dict[str, dict[str, float]] | None:
        """Total Calories = BMR × Activity Factor × Stress Factor (Mifflin-St Jeor)."""
        bmr = self.calculate_bmr_mifflin_st_jeor(age, gender)
        return self._build_total_calories(bmr) if bmr is not None else None



