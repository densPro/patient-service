# ORM models — import all so SQLAlchemy metadata / Alembic can detect them

from app.infrastructure.database.models.patient_model import PatientModel
from app.infrastructure.database.models.body_measurement_model import BodyMeasurementModel
from app.infrastructure.database.models.specialty_model import SpecialtyModel
from app.infrastructure.database.models.doctor_model import DoctorModel

__all__ = ["PatientModel", "BodyMeasurementModel", "SpecialtyModel", "DoctorModel"]
