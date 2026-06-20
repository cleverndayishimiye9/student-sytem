"""
Notification services — Twilio SMS integration and alert logic.
"""
import logging
from django.conf import settings
from .models import NotificationLog, AlertThreshold

logger = logging.getLogger(__name__)


def normalize_phone(phone_number: str) -> str:
    """Convert local Rwandan number to E.164 format for Twilio."""
    phone = phone_number.strip().replace(" ", "").replace("-", "")
    if phone.startswith("07") or phone.startswith("08"):
        phone = "+250" + phone[1:]
    elif phone.startswith("250"):
        phone = "+" + phone
    return phone


def send_sms(phone_number: str, message: str, recipient=None, alert_type='general') -> dict:
    """
    Send an SMS via Twilio.
    Returns dict with 'success', 'sid', and 'error' keys.
    """
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials not configured. SMS not sent.")
        return {'success': False, 'sid': '', 'error': 'Twilio not configured'}

    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=normalize_phone(phone_number),
        )
        result = {'success': True, 'sid': msg.sid, 'error': ''}
    except Exception as e:
        logger.error(f"Twilio error: {e}")
        result = {'success': False, 'sid': '', 'error': str(e)}

    # Log the notification
    if recipient:
        NotificationLog.objects.create(
            recipient=recipient,
            channel='sms',
            alert_type=alert_type,
            message=message,
            status='sent' if result['success'] else 'failed',
            error_message=result['error'],
            twilio_sid=result['sid'],
        )

    return result


def get_active_thresholds():
    """Get the active alert threshold config (or fall back to settings defaults)."""
    threshold = AlertThreshold.objects.filter(is_active=True).first()
    if threshold:
        return threshold.grade_threshold, threshold.attendance_threshold
    return settings.GRADE_ALERT_THRESHOLD, settings.ATTENDANCE_ALERT_THRESHOLD


def check_and_send_alerts(student_profile):
    """
    Check a student's performance and send SMS alerts if thresholds are breached.
    Called after every grade upload or attendance record.
    """
    grade_threshold, attendance_threshold = get_active_thresholds()

    gpa = student_profile.overall_gpa
    attendance = student_profile.attendance_rate
    student_user = student_profile.user
    phone = student_user.phone_number
    guardian_phone = student_profile.guardian_phone

    alerts_sent = []

    # Grade alert
    if gpa < grade_threshold and gpa > 0:
        message = (
            f"Dear {student_user.get_full_name()}, "
            f"your current overall grade at UoK is {gpa:.1f}%, "
            f"which is below the passing threshold of {grade_threshold}%. "
            f"Please contact your lecturer or academic advisor for support. "
            f"- University of Kigali"
        )
        if phone:
            result = send_sms(phone, message, recipient=student_user, alert_type='grade_alert')
            alerts_sent.append(('grade', result))
        else:
            NotificationLog.objects.create(
                recipient=student_user,
                channel='system',
                alert_type='grade_alert',
                message=message,
                status='sent',
            )

        # Notify parent/guardian about grade
        if guardian_phone:
            parent_msg = (
                f"Dear Parent/Guardian of {student_user.get_full_name()}, "
                f"your child's current grade at UoK is {gpa:.1f}%, "
                f"which is below the passing threshold of {grade_threshold}%. "
                f"Please encourage them to seek academic support. "
                f"- University of Kigali"
            )
            send_sms(guardian_phone, parent_msg, recipient=student_user, alert_type='grade_alert')

        # Also notify the lecturer
        for enrollment in student_profile.enrollments.select_related('course__lecturer'):
            lecturer = enrollment.course.lecturer
            if lecturer and lecturer.phone_number:
                lecturer_msg = (
                    f"ALERT: Student {student_profile.student_id} "
                    f"({student_user.get_full_name()}) has an overall grade of {gpa:.1f}%. "
                    f"Course: {enrollment.course.code}. - UoK System"
                )
                send_sms(lecturer.phone_number, lecturer_msg, recipient=lecturer, alert_type='grade_alert')

    # Attendance alert
    if attendance < attendance_threshold and attendance > 0:
        message = (
            f"Dear {student_user.get_full_name()}, "
            f"your attendance rate at UoK is {attendance:.1f}%, "
            f"below the required {attendance_threshold}%. "
            f"Consistent attendance is required to sit for exams. "
            f"- University of Kigali"
        )
        if phone:
            result = send_sms(phone, message, recipient=student_user, alert_type='attendance_alert')
            alerts_sent.append(('attendance', result))
        else:
            NotificationLog.objects.create(
                recipient=student_user,
                channel='system',
                alert_type='attendance_alert',
                message=message,
                status='sent',
            )

        # Notify parent/guardian about attendance
        if guardian_phone:
            parent_att_msg = (
                f"Dear Parent/Guardian of {student_user.get_full_name()}, "
                f"your child's attendance at UoK is {attendance:.1f}%, "
                f"below the required {attendance_threshold}%. "
                f"Please ensure they attend classes regularly. "
                f"- University of Kigali"
            )
            send_sms(guardian_phone, parent_att_msg, recipient=student_user, alert_type='attendance_alert')

    return alerts_sent


def send_bulk_alerts():
    """
    Periodic task: scan all students and send alerts for those at risk.
    Called by Celery beat scheduler.
    """
    from apps.students.models import StudentProfile
    students = StudentProfile.objects.select_related('user').all()
    alert_count = 0
    for student in students:
        alerts = check_and_send_alerts(student)
        alert_count += len(alerts)
    logger.info(f"Bulk alert scan complete. {alert_count} alerts sent.")
    return alert_count