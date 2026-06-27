# Patient Management Service

> Unified patient management microservice for the **Chirimoya** healthcare platform.

## Tech Stack

| Layer            | Technology                           |
|------------------|--------------------------------------|
| Language         | Python 3.12                          |
| Framework        | FastAPI                              |
| ORM              | SQLAlchemy 2.0 (async)               |
| Database         | PostgreSQL 16                        |
| Migrations       | Alembic                              |
| Containerization | Docker + Docker Compose              |
| Architecture     | DDD / Clean Architecture / CQRS-lite |

---

## Modules

| Module          | Description                                         |
|-----------------|-----------------------------------------------------|
| **patients**    | Patient aggregate — demographics, insurance, medical history |
| **doctors**     | Doctor profiles — license, specialty link, contact  |
| **specialties** | Medical specialty catalogue                         |
| **measurements**| Body measurement snapshots (BMI, BMR, TDEE)         |

---

## Architecture

```
app/
├── domain/           # Entities, value objects, enums, exceptions
├── application/      # Use cases (commands & queries), DTOs, interfaces
├── infrastructure/   # SQLAlchemy models, repositories, UoW, seeds
└── presentation/     # FastAPI routers (REST endpoints)
```

### Domain entities

| Entity         | Aggregate Root | Key identifiers      |
|----------------|----------------|----------------------|
| Patient        | ✅             | `mrn` (MRN-XXXXXXXX) |
| Doctor         | ✅             | `employee_id` (EMP-XXXXXXXX) |
| Specialty      | ✅             | `code` (e.g. CARDIO)  |
| BodyMeasurement| ✅             | `id` + `patient_id`  |

---

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
# Edit DATABASE_URL if needed
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8001`.

### 3. Run Alembic migrations

```bash
# Auto-generate migration (includes specialties, doctors, patients, measurements)
alembic revision --autogenerate -m "initial patient management schema"

# Apply migrations
alembic upgrade head
```

### 4. Seed the database

```bash
python -m app.infrastructure.seeds.seed
```

Populates 10 specialties, 5 doctors, and 5 patients.

### 5. Run locally (without Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

---

## API Endpoints

### Health

| Method | Endpoint  | Description      |
|--------|-----------|------------------|
| `GET`  | `/health` | Liveness probe   |
| `GET`  | `/ready`  | Readiness probe  |

### Patients

| Method  | Endpoint                              | Description                  |
|---------|---------------------------------------|------------------------------|
| `POST`  | `/api/v1/patients`                    | Create a new patient         |
| `GET`   | `/api/v1/patients`                    | Search patients (paginated)  |
| `GET`   | `/api/v1/patients/{patient_id}`       | Get patient by ID            |
| `GET`   | `/api/v1/patients/mrn/{mrn}`          | Get patient by MRN           |
| `PATCH` | `/api/v1/patients/{patient_id}`       | Update patient               |
| `POST`  | `/api/v1/patients/{patient_id}/measurements` | Add body measurement |
| `GET`   | `/api/v1/patients/{patient_id}/measurements` | List measurements     |

### Specialties

| Method   | Endpoint                              | Description                    |
|----------|---------------------------------------|--------------------------------|
| `POST`   | `/api/v1/specialties`                 | Create a specialty             |
| `GET`    | `/api/v1/specialties`                 | List all specialties           |
| `GET`    | `/api/v1/specialties/{id}`            | Get specialty by ID            |
| `GET`    | `/api/v1/specialties/code/{code}`     | Get specialty by code          |
| `PATCH`  | `/api/v1/specialties/{id}`            | Update specialty               |
| `DELETE` | `/api/v1/specialties/{id}`            | Soft-deactivate specialty      |

### Doctors

| Method   | Endpoint                              | Description                    |
|----------|---------------------------------------|--------------------------------|
| `POST`   | `/api/v1/doctors`                     | Register a new doctor          |
| `GET`    | `/api/v1/doctors`                     | Search doctors (paginated)     |
| `GET`    | `/api/v1/doctors/{id}`                | Get doctor by ID               |
| `GET`    | `/api/v1/doctors/emp/{employee_id}`   | Get doctor by employee ID      |
| `PATCH`  | `/api/v1/doctors/{id}`                | Update doctor                  |
| `DELETE` | `/api/v1/doctors/{id}`                | Soft-deactivate doctor         |

### Interactive docs

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## Environment Variables

| Variable        | Default                                                              | Description           |
|-----------------|----------------------------------------------------------------------|-----------------------|
| `APP_NAME`      | `Patient Management Service`                                         | Application name      |
| `DEBUG`         | `false`                                                              | Debug mode            |
| `DATABASE_URL`  | `postgresql+asyncpg://postgres:postgres@localhost:5432/patient_management_db` | Async DB connection |
| `CORS_ORIGINS`  | `["*"]`                                                              | Allowed CORS origins  |

---

## Project Structure

```
patient-management-service/
├── app/
│   ├── config.py                   # Settings (pydantic-settings)
│   ├── dependencies.py             # DI wiring
│   ├── main.py                     # FastAPI app factory
│   ├── domain/
│   │   ├── entities/               # Patient, Doctor, Specialty, BodyMeasurement
│   │   ├── value_objects/          # Address, ContactInfo, EmergencyContact, InsuranceInfo, LicenseInfo
│   │   ├── enums/                  # Gender, BloodType, MaritalStatus, PatientStatus, DoctorStatus, SpecialtyCategory
│   │   └── exceptions.py           # Domain exceptions
│   ├── application/
│   │   ├── interfaces/             # IPatientRepository, IDoctorRepository, ISpecialtyRepository, IUnitOfWork
│   │   ├── dtos/                   # Patient, Doctor, Specialty, BodyMeasurement DTOs
│   │   ├── commands/               # CreatePatient, UpdatePatient, CreateDoctor, UpdateDoctor, CreateSpecialty, ...
│   │   └── queries/                # GetPatient, SearchPatients, GetDoctor, SearchDoctors, GetSpecialty
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── session.py          # Async engine & session factory
│   │   │   └── models/             # PatientModel, DoctorModel, SpecialtyModel, BodyMeasurementModel
│   │   ├── repositories/           # Concrete implementations
│   │   ├── unit_of_work.py         # SqlAlchemyUnitOfWork
│   │   └── seeds/
│   │       └── seed.py             # Database seeder
│   └── presentation/
│       └── routers/                # patient, doctor, specialty, body_measurement, health routers
├── migrations/                     # Alembic
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Example: Create a Specialty

```bash
curl -X POST http://localhost:8001/api/v1/specialties \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CARDIO",
    "name": "Cardiology",
    "category": "therapeutic",
    "description": "Diagnosis and treatment of heart conditions."
  }'
```

## Example: Create a Doctor

```bash
curl -X POST http://localhost:8001/api/v1/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Carlos",
    "last_name": "Rivera",
    "date_of_birth": "1978-03-20",
    "gender": "male",
    "specialty_id": "<specialty-uuid>",
    "license_info": {
      "license_number": "PR-12345",
      "issuing_body": "Puerto Rico Medical Licensing Board"
    },
    "years_of_experience": 18,
    "bio": "Board-certified cardiologist."
  }'
```
