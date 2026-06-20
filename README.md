# Real-Time Student Performance Monitoring System
### University of Kigali — BIT Final Year Project
**Author:** NDAYISHIMIZE CLAVER (2301000358)  
**Supervisor:** Mr. Jean Marie Vianney MANIRARORA  
**Tech Stack:** Python 3.11 · Django 4.2 · Twilio SMS · Celery · Redis · SQLite/PostgreSQL

---

## System Overview

A web-based academic performance monitoring system that:

- Tracks student **grades**, **attendance**, and **assignment completion** in real-time
- Automatically sends **SMS alerts via Twilio** to students and lecturers when performance drops below thresholds
- Supports four user roles: **Admin**, **Lecturer**, **UoK Staff**, **Student**
- Generates **CSV reports** for grades, attendance, and student performance summaries
- Uses **Celery + Redis** for scheduled background alert scanning

---

## Project Structure

```
student_monitor/
├── manage.py
├── requirements.txt
├── setup.sh                        # One-command setup script
├── .env.example                    # Environment config template
│
├── student_monitor/                # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py                   # Celery configuration
│
├── apps/
│   ├── accounts/                   # Custom User model + Auth (roles)
│   │   ├── models.py               # User: admin, lecturer, staff, student
│   │   ├── views.py                # Login, logout, profile, manage users
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── students/                   # Core academic data
│   │   ├── models.py               # StudentProfile, Course, Grade, Attendance, Enrollment
│   │   ├── views.py                # Dashboard, student list, grade upload, attendance
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── management/commands/
│   │       └── seed_demo_data.py   # Demo data seeder
│   │
│   ├── notifications/              # Twilio SMS + Alert logic
│   │   ├── models.py               # NotificationLog, AlertThreshold
│   │   ├── services.py             # send_sms(), check_and_send_alerts()
│   │   ├── tasks.py                # Celery tasks (periodic + individual)
│   │   ├── views.py                # Notification log, alert settings
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   └── reports/                    # CSV export reports
│       ├── views.py
│       └── urls.py
│
├── templates/                      # HTML templates (Bootstrap 5)
│   ├── base.html                   # Sidebar layout
│   ├── accounts/
│   ├── students/
│   ├── notifications/
│   └── reports/
│
└── static/
    ├── css/main.css
    └── js/main.js
```

---

## Quick Setup

### 1. Clone / extract the project

```bash
cd student_monitor
```

### 2. Run the setup script (creates venv, installs deps, runs migrations)

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure Twilio in `.env`

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
```

### 4. Seed demo data (optional)

```bash
python manage.py seed_demo_data
```

### 5. Run the server

```bash
python manage.py runserver
```

---

## Running Background Tasks (SMS Scheduling)

In separate terminal windows:

```bash
# Celery worker (processes SMS jobs)
celery -A student_monitor worker -l info

# Celery beat (schedules periodic alert scans)
celery -A student_monitor beat -l info
```

Or use the Admin panel → **Periodic Tasks** (django-celery-beat) to configure the scan schedule.

---

## User Roles & Permissions

| Role         | Login | View Students | Upload Grades | Record Attendance | Manage Users | Reports | Alert Settings |
|--------------|-------|---------------|---------------|-------------------|--------------|---------|----------------|
| Admin        | ✅    | ✅            | ✅            | ✅                | ✅           | ✅      | ✅             |
| Lecturer     | ✅    | ✅ (own)      | ✅ (own)      | ✅ (own)          | ❌           | ✅      | ❌             |
| UoK Staff    | ✅    | ✅            | ❌            | ❌                | ❌           | ✅      | ❌             |
| Student      | ✅    | ❌ (own only) | ❌            | ❌                | ❌           | ❌      | ❌             |

---

## SMS Alert Logic

Alerts fire automatically when:
- A student's **overall grade average falls below 50%** (configurable)
- A student's **attendance rate falls below 75%** (configurable)

**Recipients:**
- The **student** receives an SMS on their registered phone number
- The **lecturer** of the relevant course also receives a notification

Alert thresholds are configurable from the **Alert Settings** page (Admin only).

---

## Demo Credentials (after seeding)

| Role     | Username    | Password    |
|----------|-------------|-------------|
| Admin    | admin       | admin123    |
| Lecturer | manirarora  | lecturer123 |
| Staff    | staff1      | staff123    |
| Student  | 2301000358  | student123  |

---

## Production Deployment Notes

1. Set `DEBUG=False` in `.env`
2. Switch from SQLite to **PostgreSQL** (configure `DB_*` vars in `.env`)
3. Set a strong `SECRET_KEY`
4. Run `python manage.py collectstatic`
5. Serve with **Gunicorn** behind **Nginx**
6. Use a managed Redis instance for Celery

---

*University of Kigali · Faculty of Business Information Technology · June 2026*
