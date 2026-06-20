#!/bin/bash
# ============================================================
#  UoK Student Performance Monitoring System
#  Quick Setup Script
# ============================================================

echo "============================================="
echo " UoK Student Performance Monitoring System  "
echo " Setup Script                               "
echo "============================================="

# 1. Create virtual environment
echo ""
echo "[1/6] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
echo "[2/6] Installing dependencies..."
pip install -r requirements.txt

# 3. Create .env from example
if [ ! -f .env ]; then
  echo "[3/6] Creating .env file (fill in your Twilio credentials)..."
  cp .env.example .env
  echo "      ⚠️  Edit .env with your Twilio credentials before running."
else
  echo "[3/6] .env already exists, skipping."
fi

# 4. Run migrations
echo "[4/6] Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
echo "[5/6] Creating admin superuser..."
echo "      (Enter credentials when prompted)"
python manage.py createsuperuser

# 6. Collect static files
echo "[6/6] Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "============================================="
echo " Setup complete!"
echo ""
echo " To run the development server:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo " To run Celery worker (SMS background tasks):"
echo "   celery -A student_monitor worker -l info"
echo ""
echo " To run Celery beat (scheduled scans):"
echo "   celery -A student_monitor beat -l info"
echo ""
echo " Admin panel: http://127.0.0.1:8000/admin/"
echo " System:      http://127.0.0.1:8000/"
echo "============================================="
