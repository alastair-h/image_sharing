set -ex
docker-compose -f docker-compose.yaml run --rm api black .  --check 
