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

### 2. Build & start all containers

```bash
docker-compose up --build -d
```

The API will be available at `http://localhost:8001`.  
The `-d` flag runs everything in the background (detached mode).

### 3. Run Alembic migrations inside the container

Once the containers are running, apply all migrations (creates tables + seeds all data):

```bash
docker-compose exec patient-management-service alembic upgrade head
```

This runs every migration in order:
- Creates the `patients`, `specialties`, `doctors`, and `body_measurements` tables
- Seeds 100 patients with Venezuelan data
- Seeds 10 medical specialties and 30 doctors in Spanish

---

## 🔄 Re-running Migrations from Scratch

Use this when you have updated migration files and need a completely clean slate (drops all data).

### Step 1 — Tear down containers and delete the database volume

```bash
docker-compose down -v
```

> ⚠️ The `-v` flag **deletes all database data permanently**. Only use this when you want a full reset.

### Step 2 — Rebuild and start containers

```bash
docker-compose up --build -d
```

### Step 3 — Apply all migrations

```bash
docker-compose exec patient-management-service alembic upgrade head
```

You should see output like:

```
INFO  Running upgrade  -> a71bef42bd17, create patients table
INFO  Running upgrade a71bef42bd17 -> d61dc0437346, seed 100 patients
INFO  Running upgrade d61dc0437346 -> e6a89442c56d, add_age_height_weight_to_patients
INFO  Running upgrade e6a89442c56d -> f3a1b2c4d5e6, create_patient_body_measurements_and_migrate_data
INFO  Running upgrade f3a1b2c4d5e6 -> a9b8c7d6e5f4, seed_body_measurements_history
INFO  Running upgrade a9b8c7d6e5f4 -> ad8a1e4a0e0d, create specialties and doctors tables
INFO  Running upgrade ad8a1e4a0e0d -> e7c4b56af4a1, seed specialties and doctors
```

---

## Other Useful Docker Commands

```bash
# Check running containers
docker-compose ps

# View live logs from the API service
docker-compose logs -f patient-management-service

# View live logs from the database
docker-compose logs -f postgres

# Stop containers (keeps data volume intact)
docker-compose down

# Open a shell inside the API container
docker-compose exec patient-management-service bash

# Check current Alembic migration state
docker-compose exec patient-management-service alembic current

# Roll back the last migration
docker-compose exec patient-management-service alembic downgrade -1
```

### Run locally (without Docker)

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
