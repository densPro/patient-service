"""Domain-specific exceptions for the patient-management service."""


class PatientManagementError(Exception):
    """Base exception for all patient-management-service domain errors."""

    def __init__(self, message: str = "An error occurred in the patient management service.") -> None:
        self.message = message
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Patient exceptions (kept for backward compatibility)
# ---------------------------------------------------------------------------

# Legacy alias so existing imports keep working
PatientServiceError = PatientManagementError


class PatientNotFoundError(PatientManagementError):
    """Raised when a patient cannot be found by ID or MRN."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Patient not found: {identifier}")
        self.identifier = identifier


class DuplicatePatientError(PatientManagementError):
    """Raised when attempting to create a patient with a duplicate MRN."""

    def __init__(self, mrn: str) -> None:
        super().__init__(f"A patient with MRN '{mrn}' already exists.")
        self.mrn = mrn


class InvalidPatientDataError(PatientManagementError):
    """Raised when patient data fails domain validation."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Invalid patient data: {detail}")
        self.detail = detail


# ---------------------------------------------------------------------------
# Specialty exceptions
# ---------------------------------------------------------------------------


class SpecialtyNotFoundError(PatientManagementError):
    """Raised when a specialty cannot be found by ID or code."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Specialty not found: {identifier}")
        self.identifier = identifier


class DuplicateSpecialtyError(PatientManagementError):
    """Raised when attempting to create a specialty with a duplicate code."""

    def __init__(self, code: str) -> None:
        super().__init__(f"A specialty with code '{code}' already exists.")
        self.code = code


class InvalidSpecialtyDataError(PatientManagementError):
    """Raised when specialty data fails domain validation."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Invalid specialty data: {detail}")
        self.detail = detail


# ---------------------------------------------------------------------------
# Doctor exceptions
# ---------------------------------------------------------------------------


class DoctorNotFoundError(PatientManagementError):
    """Raised when a doctor cannot be found by ID or employee ID."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Doctor not found: {identifier}")
        self.identifier = identifier


class DuplicateDoctorError(PatientManagementError):
    """Raised when attempting to create a doctor with a duplicate employee ID."""

    def __init__(self, employee_id: str) -> None:
        super().__init__(f"A doctor with employee ID '{employee_id}' already exists.")
        self.employee_id = employee_id


class InvalidDoctorDataError(PatientManagementError):
    """Raised when doctor data fails domain validation."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Invalid doctor data: {detail}")
        self.detail = detail


# ---------------------------------------------------------------------------
# Auth / Token exceptions
# ---------------------------------------------------------------------------


class TokenExpiredError(PatientManagementError):
    """Raised when a JWT access token has expired."""

    def __init__(self) -> None:
        super().__init__("Token has expired.")


class TokenInvalidError(PatientManagementError):
    """Raised when a JWT token cannot be decoded (bad signature, malformed, etc.)."""

    def __init__(self, detail: str = "Invalid token.") -> None:
        super().__init__(detail)
