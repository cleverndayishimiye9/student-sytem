from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name='notifications.send_bulk_alerts')
def send_bulk_alerts_task():
    """
    Scheduled task: runs every hour to scan all students
    and send SMS alerts for those below thresholds.
    """
    from .services import send_bulk_alerts
    count = send_bulk_alerts()
    logger.info(f"Periodic alert task complete: {count} alerts sent.")
    return count


@shared_task(name='notifications.send_individual_alert')
def send_individual_alert_task(student_id):
    """Trigger alert check for a single student by profile ID."""
    from apps.students.models import StudentProfile
    from .services import check_and_send_alerts
    try:
        student = StudentProfile.objects.get(pk=student_id)
        alerts = check_and_send_alerts(student)
        return len(alerts)
    except StudentProfile.DoesNotExist:
        logger.error(f"Student profile {student_id} not found.")
        return 0
