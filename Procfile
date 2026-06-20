web: gunicorn student_monitor.wsgi --log-file -
worker: celery -A student_monitor worker -l info
beat: celery -A student_monitor beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
