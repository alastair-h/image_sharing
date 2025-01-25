set -ex
docker-compose -f docker-compose.yaml run --rm api black . 
docker-compose -f docker-compose.yaml run --rm api isort .
