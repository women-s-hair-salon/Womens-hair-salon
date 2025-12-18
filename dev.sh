#!/usr/bin/env bash
set -e
npx @tailwindcss/cli -i ./assets/css/input.css -o ./static/css/output.css -w &
CSS_PID=$!
python manage.py runserver 0.0.0.0:8000
kill $CSS_PID
