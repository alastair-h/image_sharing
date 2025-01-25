docker-compose -f docker-compose.yaml run --rm api black . --check
docker-compose -f docker-compose.yaml run --rm api isort .  --check-only --diff
