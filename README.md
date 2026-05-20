# hairdresser
django_project

server :
docker compose -f docker-compose up
docker compose -f docker-compose down

local :
docker exec -it salon_web_dev python manage.py createsuperuser
docker compose -f docker-compose.dev.yml up
docker compose -f docker-compose.dev.yml down

search : http://localhost,http://127.0.0.1