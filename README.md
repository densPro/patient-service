# Patient Service

> Patient management microservice for the **Chirimoya** healthcare platform.

## Tech Stack

| Layer            | Technology                        |
|------------------|-----------------------------------|
| Language         | Python 3.12                       |
| Framework        | FastAPI                           |
| ORM              | SQLAlchemy 2.0 (async)            |
| Database         | PostgreSQL 16                     |
| Migrations       | Alembic                           |
| Containerization | Docker + Docker Compose           |
| Architecture     | DDD / Clean Architecture / CQRS-lite |

## Architecture

```
app/
├── domain/           # Enterprise business rules (entities, value objects, enums)
├── application/      # Use cases, DTOs, commands, queries, interfaces
├── infrastructure/   # SQLAlchemy models, repositories, unit of work, DB session
└── presentation/     # FastAPI routers (REST endpoints)
```

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env if needed
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### 3. Run Alembic migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "create patients table"

# Apply migrations
alembic upgrade head
```

### 4. Run locally (without Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method  | Endpoint                          | Description              |
|---------|-----------------------------------|--------------------------|
| `GET`   | `/health`                         | Liveness probe           |
| `GET`   | `/ready`                          | Readiness probe          |
| `POST`  | `/api/v1/patients`                | Create a new patient     |
| `GET`   | `/api/v1/patients`                | Search patients          |
| `GET`   | `/api/v1/patients/{patient_id}`   | Get patient by ID        |
| `GET`   | `/api/v1/patients/mrn/{mrn}`      | Get patient by MRN       |
| `PATCH` | `/api/v1/patients/{patient_id}`   | Update patient           |

### Interactive docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example: Create a Patient

```bash
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "María",
    "last_name": "García",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "contact_info": {
      "phone_number": "+1-555-0123",
      "email": "maria.garcia@email.com"
    },
    "blood_type": "O+",
    "allergies": ["Penicillin"],
    "address": {
      "street_line_1": "123 Main St",
      "city": "San Juan",
      "state": "PR",
      "postal_code": "00901",
      "country": "US"
    },
    "emergency_contact": {
      "full_name": "Carlos García",
      "relationship": "spouse",
      "phone_number": "+1-555-0456"
    }
  }'
```

## Environment Variables

| Variable        | Default                                                        | Description           |
|-----------------|----------------------------------------------------------------|-----------------------|
| `APP_NAME`      | `Patient Service`                                              | Application name      |
| `DEBUG`         | `false`                                                        | Debug mode            |
| `DATABASE_URL`  | `postgresql+asyncpg://postgres:postgres@localhost:5432/patient_db` | Async DB connection   |
| `CORS_ORIGINS`  | `["*"]`                                                        | Allowed CORS origins  |

## Project Structure

```
patient-service/
├── app/
│   ├── config.py                 # Settings (pydantic-settings)
│   ├── dependencies.py           # DI wiring
│   ├── main.py                   # FastAPI app factory
│   ├── domain/
│   │   ├── entities/             # Entity & AggregateRoot base, Patient
│   │   ├── value_objects/        # Address, ContactInfo, EmergencyContact, InsuranceInfo
│   │   ├── enums/                # Gender, BloodType, MaritalStatus, PatientStatus
│   │   └── exceptions.py        # Domain exceptions
│   ├── application/
│   │   ├── interfaces/           # IPatientRepository, IUnitOfWork
│   │   ├── dtos/                 # Create, Update, Response, Search DTOs
│   │   ├── commands/             # CreatePatient, UpdatePatient
│   │   └── queries/              # GetPatient, SearchPatients
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── session.py        # Async engine & session factory
│   │   │   └── models/           # SQLAlchemy ORM models
│   │   ├── repositories/         # Concrete PatientRepository
│   │   └── unit_of_work.py       # SqlAlchemyUnitOfWork
│   └── presentation/
│       └── routers/              # patient_router, health_router
├── migrations/                   # Alembic
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
