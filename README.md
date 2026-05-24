# Women's Hair Salon

A real-world website and online booking platform for a women's hair salon, built with Django, PostgreSQL, Docker, Tailwind CSS, OTP-based authentication, a dedicated staff panel, appointment booking, Zarinpal deposit payments, and SMS notifications.

> This is not just a UI mockup. The project includes real booking logic, appointment capacity control, payments, staff workflows, user management, service management, tutorials, contact messages, media handling, and scheduled maintenance jobs.

## Preview

<table>
  <tr>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-46-33.png" alt="Project screenshot 1" /></td>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-48-37.png" alt="Project screenshot 2" /></td>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-49-08.png" alt="Project screenshot 3" /></td>
  </tr>
  <tr>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-49-23.png" alt="Project screenshot 4" /></td>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-50-30.png" alt="Project screenshot 5" /></td>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-52-44.png" alt="Project screenshot 6" /></td>
  </tr>
  <tr>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-52-49.png" alt="Project screenshot 7" /></td>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-47-13.png" alt="Mobile screenshot 1" /></td>
    <td width="33%"><img src="media/Pictures%20from%20the%20project/Screenshot%20from%202026-05-21%2002-49-54.png" alt="Mobile screenshot 2" /></td>
  </tr>
</table>

## Features

- Phone number registration and login with OTP verification
- Custom user model built around Iranian mobile numbers
- User profile completion checks before booking
- Salon service catalog with categories, descriptions, and images
- Step-by-step booking flow: service, date, time slot, and deposit payment
- Appointment capacity management with duplicate active-booking protection
- Zarinpal payment request, callback handling, verification, and reference tracking
- SMS notification after successful booking
- Dedicated staff panel with Step-Up password verification for sensitive actions
- Staff service management with create, update, delete, archive, and active/inactive controls
- Single and bulk time-slot creation using Jalali dates, date ranges, weekdays, and time steps
- Staff user list, search, booked reservation list, and dashboard statistics
- Contact message management, reply tracking, and deletion tools
- Tutorial system with lessons, images, and video support
- About page gallery and Google Maps direction link
- Production deployment with Docker, Nginx, PostgreSQL, Certbot, and scheduler services
- S3-compatible media storage support through Django Storages

## Tech Stack

| Layer | Tools |
| --- | --- |
| Backend | Python, Django 5.1.5 |
| Database | PostgreSQL 16 |
| Frontend | Django Templates, Tailwind CSS |
| Auth | Custom user model, phone number login, OTP |
| Payment | Zarinpal |
| SMS | Kavenegar |
| Media Storage | Django Storages, S3-compatible storage |
| Deployment | Docker, Docker Compose, Nginx, Certbot |
| Scheduling | cron inside Docker scheduler service |

## Project Structure

```text
.
├── accounts/                 # Custom user, OTP, login, registration, and profile
├── home/                     # Public pages, contact, about, tutorials, and display catalog
├── services/                 # Booking, payment, services, slots, and staff panel
├── templates/                # Main Django templates
├── static/                   # Built static files
├── assets/                   # Frontend source assets and Tailwind input
├── media/                    # Uploaded files and project screenshots
├── deploy/                   # Nginx configuration
├── src/                      # Main Django project settings
├── docker-compose.yml        # Production Docker setup
├── docker-compose.dev.yml    # Development Docker setup
├── Dockerfile
└── Dockerfile.scheduler
```

## Main Routes

| Route | Description |
| --- | --- |
| `/` | Home page |
| `/aboutus/` | About page and gallery |
| `/contact/` | Contact form |
| `/servicesss_list/` | Service category listing |
| `/tutorials/` | Tutorial listing |
| `/accounts/` | Login, registration, OTP, and profile routes |
| `/services/services/` | Booking service list |
| `/services/payment/callback/` | Payment callback |
| `/services/staff/` | Staff dashboard |
| `/services/staff/slots/` | Time-slot management |
| `/services/staff/reservations/` | Successful reservations |
| `/staff/catalog/` | Display catalog management |
| `/staff/messages/` | Contact message management |
| `/admin/` | Django admin |

## Requirements

- Docker and Docker Compose for the recommended setup
- Python 3.12 for direct local execution
- Node.js for building Tailwind CSS
- PostgreSQL, usually through Docker in development and production

## Environment Variables

The project uses `.env` and `.env.dev`. For a safe production setup, do not commit real production secrets to a public repository.

Example variables:

```env
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

DB_NAME=salon
DB_USER=salon_user
DB_PASSWORD=strong-password
DB_HOST=db
DB_PORT=5432

ZARINPAL_SANDBOX=True
ZARINPAL_MERCHANT_ID=
ZARINPAL_CALLBACK_URL=

S3_CDN_DOMAIN=
KAVENEGAR_API_KEY=
```

## Run With Docker

Development:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Stop development:

```bash
docker compose -f docker-compose.dev.yml down
```

Create a superuser inside the development container:

```bash
docker exec -it salon_web_dev python manage.py createsuperuser
```

After startup, open:

```text
http://localhost
http://127.0.0.1
```

## Run Locally Without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
npm run build:css
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

For active Tailwind development:

```bash
npm run dev:css
```

Or run Django and Tailwind together:

```bash
npm run dev
```

## Reservation Flow

1. The user signs in with a mobile phone number and OTP.
2. If the user profile is incomplete, the user is redirected to complete it before booking.
3. The user selects an active salon service.
4. The system displays future dates and available time slots with remaining capacity.
5. A reservation is created as `draft`, then moved to `pending` after capacity checks.
6. The user is sent to Zarinpal, or in sandbox mode the app redirects directly to the local callback.
7. After successful payment verification, the reservation becomes `booked` and SMS notifications are sent.

## Staff Panel

The staff panel uses normal authentication plus Step-Up password verification for sensitive administrative actions. It supports:

- Dashboard statistics and quick operational overview
- User search by phone number or name
- Booking service management and active/inactive state control
- Time-slot management with capacity controls
- Bulk slot creation with Jalali dates
- Paid reservation listing
- Public catalog management
- Tutorial and lesson management
- Contact message review and replies

## Scheduled Jobs

The Docker `scheduler` service is used for recurring maintenance tasks. In production, a cron job is configured for cleaning up or archiving old slots:

```bash
python manage.py purge_old_slots
```

## Production Notes

- Keep `DEBUG=False` in production.
- `SECRET_KEY`, S3 credentials, SMS credentials, and payment gateway credentials must be loaded from environment variables.
- Before publishing the repository, remove real `.env` files and any leaked secrets from git history.
- Configure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` explicitly for the production domain.
- SSL support is planned through Nginx and Certbot in the production compose file.

## License

This project is a real salon booking platform. Update the license according to the owner's distribution policy before publishing it publicly.
