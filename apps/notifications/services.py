"""
Notification services — Twilio SMS integration and alert logic.
UoK Student Performance Monitoring System
Marking Scheme: Assignment=20, CAT1=20, CAT2=20, Final=40, Total=100
Pass mark: 50% for all components
"""
import logging
from django.conf import settings
from .models import NotificationLog, AlertThreshold

logger = logging.getLogger(__name__)

PASS_MARK = 50  # 50% pass mark for all components


def normalize_phone(phone_number: str) -> str:
    """Convert local Rwandan number to E.164 format for Twilio."""
    phone = phone_number.strip().replace(" ", "").replace("-", "")
    if phone.startswith("07") or phone.startswith("08"):
        phone = "+250" + phone[1:]
    elif phone.startswith("250"):
        phone = "+" + phone
    return phone


def send_sms(phone_number: str, message: str, recipient=None, alert_type='general') -> dict:
    """Send an SMS via Twilio."""
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
    """Get the active alert threshold config."""
    threshold = AlertThreshold.objects.filter(is_active=True).first()
    if threshold:
        return threshold.grade_threshold, threshold.attendance_threshold
    return settings.GRADE_ALERT_THRESHOLD, settings.ATTENDANCE_ALERT_THRESHOLD


def check_component_alerts(student_profile, course, grade_type, score, max_score):
    """
    Check a specific grade component and send early warning SMS if below 50%.
    Called immediately after each grade upload.
    """
    student_user = student_profile.user
    phone = student_user.phone_number
    guardian_phone = student_profile.guardian_phone
    full_name = student_user.get_full_name()
    course_name = course.name
    alerts_sent = []

    percentage = round((float(score) / float(max_score)) * 100, 1) if max_score > 0 else 0

    if percentage < PASS_MARK:
        component_names = {
            'ASSIGNMENT': 'Assignment',
            'CAT1': 'CAT 1',
            'CAT2': 'CAT 2',
            'FINAL': 'Final Exam',
            'MIDTERM': 'Mid-Term',
            'PROJECT': 'Project',
        }
        component_name = component_names.get(grade_type, grade_type)

        # Urgency based on component
        if grade_type == 'FINAL':
            urgency = "URGENT: "
            action = "Please meet your lecturer immediately and seek academic support."
        elif grade_type == 'CAT2':
            urgency = "WARNING: "
            action = "You still have the Final Exam. Please study hard and seek help from your lecturer."
        elif grade_type == 'CAT1':
            urgency = "EARLY WARNING: "
            action = "You still have CAT 2 and the Final Exam. Please improve now before it is too late."
        else:
            urgency = "NOTICE: "
            action = "Please improve your performance. You still have CATs and Final Exam ahead."

        # SMS to student
        student_msg = (
            f"{urgency}Dear {full_name}, "
            f"your {component_name} score in {course_name} is {score}/{max_score} ({percentage}%), "
            f"which is below the pass mark of {PASS_MARK}%. "
            f"{action} - University of Kigali"
        )

        if phone:
            result = send_sms(phone, student_msg, recipient=student_user, alert_type='grade_alert')
            alerts_sent.append((grade_type, result))
        else:
            NotificationLog.objects.create(
                recipient=student_user,
                channel='system',
                alert_type='grade_alert',
                message=student_msg,
                status='sent',
            )

        # SMS to guardian
        if guardian_phone:
            guardian_msg = (
                f"Dear Parent/Guardian of {full_name}, "
                f"your child scored {score}/{max_score} ({percentage}%) "
                f"in {component_name} for {course_name} at UoK. "
                f"This is below the pass mark of {PASS_MARK}%. "
                f"Please encourage them to seek academic support. - University of Kigali"
            )
            send_sms(guardian_phone, guardian_msg, recipient=student_user, alert_type='grade_alert')

        # SMS to lecturer
        lecturer = course.lecturer
        if lecturer and lecturer.phone_number:
            lecturer_msg = (
                f"ALERT: Student {student_profile.student_id} ({full_name}) "
                f"scored {score}/{max_score} ({percentage}%) in {component_name} "
                f"for {course_name}. Below pass mark. Please intervene. - UoK System"
            )
            send_sms(lecturer.phone_number, lecturer_msg, recipient=lecturer, alert_type='grade_alert')

    return alerts_sent


def check_cumulative_alerts(student_profile, course):
    """
    Check cumulative performance after each grade upload.
    Warns if total coursework (Assignment + CAT1 + CAT2) is trending to failure.
    """
    grades = {g.grade_type: g for g in student_profile.grades.filter(course=course)}
    student_user = student_profile.user
    phone = student_user.phone_number
    full_name = student_user.get_full_name()
    alerts_sent = []

    # Check CAT total (CAT1 + CAT2 = 40 marks)
    if 'CAT1' in grades and 'CAT2' in grades:
        cat_total = float(grades['CAT1'].score) + float(grades['CAT2'].score)
        cat_percentage = round((cat_total / 40) * 100, 1)

        if cat_percentage < PASS_MARK and phone:
            msg = (
                f"WARNING: Dear {full_name}, "
                f"your combined CAT score in {course.name} is {cat_total}/40 ({cat_percentage}%), "
                f"below the pass mark of {PASS_MARK}%. "
                f"You need to perform well in the Final Exam (40 marks) to pass. "
                f"Please seek help immediately. - University of Kigali"
            )
            result = send_sms(phone, msg, recipient=student_user, alert_type='grade_alert')
            alerts_sent.append(('CAT_TOTAL', result))

    # Check overall coursework (Assignment + CAT1 + CAT2 = 60 marks)
    if all(k in grades for k in ['ASSIGNMENT', 'CAT1', 'CAT2']):
        coursework_total = (
            float(grades['ASSIGNMENT'].score) +
            float(grades['CAT1'].score) +
            float(grades['CAT2'].score)
        )
        coursework_percentage = round((coursework_total / 60) * 100, 1)
        min_needed_in_final = 50 - coursework_total

        if min_needed_in_final > 40 and phone:
            # Cannot pass even with full marks in final
            msg = (
                f"URGENT: Dear {full_name}, "
                f"your coursework total in {course.name} is {coursework_total}/60 ({coursework_percentage}%). "
                f"Even with full marks in the Final Exam, you may not reach the pass mark. "
                f"Please consult your lecturer or academic advisor urgently. - University of Kigali"
            )
            result = send_sms(phone, msg, recipient=student_user, alert_type='grade_alert')
            alerts_sent.append(('COURSEWORK_CRITICAL', result))

        elif coursework_percentage < PASS_MARK and phone:
            msg = (
                f"WARNING: Dear {full_name}, "
                f"your total coursework in {course.name} is {coursework_total}/60 ({coursework_percentage}%). "
                f"You need at least {max(0, min_needed_in_final):.0f}/40 in the Final Exam to pass. "
                f"Please prepare well. - University of Kigali"
            )
            result = send_sms(phone, msg, recipient=student_user, alert_type='grade_alert')
            alerts_sent.append(('COURSEWORK_WARNING', result))

    return alerts_sent


def check_and_send_alerts(student_profile, course=None, grade_type=None, score=None, max_score=None):
    """
    Main alert function. Called after every grade upload or attendance record.
    """
    alerts_sent = []

    # Component-level early warning
    if course and grade_type and score is not None and max_score is not None:
        alerts_sent += check_component_alerts(student_profile, course, grade_type, score, max_score)
        alerts_sent += check_cumulative_alerts(student_profile, course)

    # Overall GPA alert (fallback when no specific component)
    if not alerts_sent:
        grade_threshold, attendance_threshold = get_active_thresholds()
        gpa = student_profile.overall_gpa
        student_user = student_profile.user
        phone = student_user.phone_number
        guardian_phone = student_profile.guardian_phone

        if gpa < grade_threshold and gpa > 0:
            message = (
                f"Dear {student_user.get_full_name()}, "
                f"your overall grade at UoK is {gpa:.1f}%, "
                f"below the passing threshold of {grade_threshold}%. "
                f"Please contact your lecturer or academic advisor. - University of Kigali"
            )
            if phone:
                result = send_sms(phone, message, recipient=student_user, alert_type='grade_alert')
                alerts_sent.append(('overall_grade', result))

            if guardian_phone:
                parent_msg = (
                    f"Dear Parent/Guardian of {student_user.get_full_name()}, "
                    f"your child's overall grade at UoK is {gpa:.1f}%, "
                    f"below the passing threshold of {grade_threshold}%. "
                    f"Please encourage them to seek academic support. - University of Kigali"
                )
                send_sms(guardian_phone, parent_msg, recipient=student_user, alert_type='grade_alert')

    # Attendance alert
    grade_threshold, attendance_threshold = get_active_thresholds()
    attendance = student_profile.attendance_rate
    student_user = student_profile.user
    phone = student_user.phone_number
    guardian_phone = student_profile.guardian_phone

    if attendance < attendance_threshold and attendance > 0:
        message = (
            f"Dear {student_user.get_full_name()}, "
            f"your attendance rate at UoK is {attendance:.1f}%, "
            f"below the required {attendance_threshold}%. "
            f"Consistent attendance is required to sit for exams. - University of Kigali"
        )
        if phone:
            result = send_sms(phone, message, recipient=student_user, alert_type='attendance_alert')
            alerts_sent.append(('attendance', result))

        if guardian_phone:
            parent_att_msg = (
                f"Dear Parent/Guardian of {student_user.get_full_name()}, "
                f"your child's attendance at UoK is {attendance:.1f}%, "
                f"below the required {attendance_threshold}%. "
                f"Please ensure they attend classes regularly. - University of Kigali"
            )
            send_sms(guardian_phone, parent_att_msg, recipient=student_user, alert_type='attendance_alert')

    return alerts_sent


def send_bulk_alerts():
    """Periodic task: scan all students and send alerts for those at risk."""
    from apps.students.models import StudentProfile
    students = StudentProfile.objects.select_related('user').all()
    alert_count = 0
    for student in students:
        alerts = check_and_send_alerts(student)
        alert_count += len(alerts)
    logger.info(f"Bulk alert scan complete. {alert_count} alerts sent.")
    return alert_count