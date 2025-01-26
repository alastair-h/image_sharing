curl -X 'POST' \
  'http://localhost:9000/caption' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "image_url": "https://hedgehoglab.com/wp-content/uploads/2024/07/hhl-logo.png"
}'
