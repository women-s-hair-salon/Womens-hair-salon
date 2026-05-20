# hairdresser
django_project

server :
docker compose -f docker-compose up
docker compose -f docker-compose down

local :
python manage.py createsuperuser
docker compose -f docker-compose.dev.yml up
docker compose -f docker-compose.dev.yml down