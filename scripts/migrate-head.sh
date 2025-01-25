set -ex
docker-compose exec api alembic upgrade "head"

