#!/usr/bin/env bash
set -e

# ساخت پوشه‌ها اگر وجود ندارند
mkdir -p /app/staticfiles /app/media

# صبر کوتاه برای آماده شدن DB
python - <<'PY'
import time, os, socket
host = os.environ.get('DB_HOST', 'db'); port = int(os.environ.get('DB_PORT','5432'))
for i in range(30):
    try:
        s = socket.socket(); s.settimeout(1.0); s.connect((host, port)); s.close(); break
    except Exception:
        time.sleep(1)
PY

# مایگریشن و کالکت‌استاتیک
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# اجرای گونیکورن
exec gunicorn src.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --threads 3 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -



##!/usr/bin/env bash
#set -e
#
## صبر برای Postgres
#python - <<'PY'
#import time, os, socket
#host = os.environ.get('DB_HOST','db'); port = int(os.environ.get('DB_PORT','5432'))
#for _ in range(30):
#    s=socket.socket(); s.settimeout(1)
#    try:
#        s.connect((host,port)); s.close(); break
#    except Exception:
#        time.sleep(1)
#PY
#
## مایگریشن + استاتیک
#python manage.py migrate --noinput
#python manage.py collectstatic --noinput
#
## اجرای گونیکورن با src.wsgi
#exec gunicorn src.wsgi:application \
#  --bind 0.0.0.0:8000 \
#  --workers 3 \
#  --timeout 60 \
#  --access-logfile - \
#  --error-logfile -
