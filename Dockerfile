FROM python:3.12-slim
#FROM mirror.gcr.io/library/python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Tehran

# سیستم‌وابستگی‌های لازم برای psycopg و Pillow و cron
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev cron tzdata curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

WORKDIR /app

# نصب نیازمندی‌ها
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# کد پروژه
COPY . /app/

# پوشه‌های استاتیک/مدیا (اگر نبود بساز)
RUN mkdir -p /app/staticfiles /app/media

# entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000





#FROM python:3.12-slim
#
#ENV PYTHONDONTWRITEBYTECODE=1 \
#    PYTHONUNBUFFERED=1 \
#    TZ=Asia/Tehran
#
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    cron tzdata build-essential libpq-dev \
#  && rm -rf /var/lib/apt/lists/* \
#  && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#
#WORKDIR /app
#
## اول فقط نیازمندی‌ها تا کش بهتر شود
#COPY requirements.txt /app/
#RUN pip install --no-cache-dir -r requirements.txt
#
## حالا کل پروژه را کپی کن (حتماً entrypoint.sh در همین ریشه وجود داشته باشد)
#COPY . /app/
#
## اطمینان از قابل اجرا بودن اسکریپت‌ها
## اگر روی ویندوز ادیت شده، تبدیل CRLF به LF
#RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh
#
## اگر manage.py هم نیاز به اجرا مستقیم داشت:
## RUN chmod +x /app/manage.py
#
## اجرای اسکریپت در زمان ران (collectstatic اینجا اجرا نمی‌شود)
#ENTRYPOINT ["/app/entrypoint.sh"]


## --- مرحله بیلد CSS با Tailwind ---
#FROM node:20-alpine AS assets
#WORKDIR /build
## اگر tailwind.config.js داری کپی کن؛ در غیر اینصورت هم cli کار می‌کند.
#COPY assets ./assets
#COPY tailwind.config.js ./tailwind.config.js 2>/dev/null || true
## خروجی را به مسیر ثابت پروژه بسازیم
#RUN npx --yes @tailwindcss/cli -i ./assets/css/input.css -o ./static/css/output.css
#
## --- وب: Django + Gunicorn ---
#FROM python:3.12-slim
#
#ENV PYTHONDONTWRITEBYTECODE=1 \
#    PYTHONUNBUFFERED=1
#
#WORKDIR /app
#
## وابستگی‌های سیستمی
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential libpq-dev curl && \
#    rm -rf /var/lib/apt/lists/*
#
## پکیج‌ها
#COPY requirements.txt /app/
#RUN pip install --no-cache-dir -r requirements.txt
#
## کد
#COPY . /app/
#
## CSS بیلد شده را کپی کن داخل تصویر نهایی
#RUN mkdir -p /app/static/css
#COPY --from=assets /build/static/css/output.css /app/static/css/output.css
#
## entrypoint
#COPY deploy/entrypoint.sh /app/entrypoint.sh
#RUN chmod +x /app/entrypoint.sh
#
#EXPOSE 8000
