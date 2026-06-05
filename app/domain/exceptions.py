"""Domain-specific exceptions for the patient service."""


class PatientServiceError(Exception):
    """Base exception for all patient-service domain errors."""

    def __init__(self, message: str = "An error occurred in the patient service.") -> None:
        self.message = message
        super().__init__(self.message)


class PatientNotFoundError(PatientServiceError):
    """Raised when a patient cannot be found by ID or MRN."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Patient not found: {identifier}")
        self.identifier = identifier


class DuplicatePatientError(PatientServiceError):
    """Raised when attempting to create a patient with a duplicate MRN."""

    def __init__(self, mrn: str) -> None:
        super().__init__(f"A patient with MRN '{mrn}' already exists.")
        self.mrn = mrn


class InvalidPatientDataError(PatientServiceError):
    """Raised when patient data fails domain validation."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Invalid patient data: {detail}")
        self.detail = detail
