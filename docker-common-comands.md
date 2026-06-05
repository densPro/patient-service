# Rebuild the image
docker-compose build patient-service

# Run the migration
docker-compose run --rm patient-service alembic upgrade head

# Run the application
docker-compose up --build

# Run the database container
docker-compose up -d postgres
