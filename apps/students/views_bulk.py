"""
Bulk attendance view — add to apps/students/views.py or import from here.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Course, StudentProfile, Enrollment, AttendanceRecord
from apps.notifications.services import check_and_send_alerts


@login_required
def bulk_attendance(request):
    if not (request.user.is_admin or request.user.is_lecturer):
        messages.error(request, 'Only lecturers and admins can record attendance.')
        return redirect('dashboard')

    lecturer = request.user if request.user.is_lecturer else None
    courses = Course.objects.filter(lecturer=lecturer) if lecturer else Course.objects.all()

    selected_course = None
    students = []
    today = timezone.now().date().isoformat()

    if request.method == 'POST':
        action = request.POST.get('action')
        course_id = request.POST.get('course_id')
        date_str = request.POST.get('date', today)

        if course_id:
            try:
                selected_course = courses.get(pk=course_id)
            except Course.DoesNotExist:
                messages.error(request, 'Course not found.')
                return redirect('bulk_attendance')

        if action == 'load' and selected_course:
            enrollments = Enrollment.objects.filter(course=selected_course).select_related('student__user')
            from datetime import date as date_cls
            load_date = date_cls.fromisoformat(date_str)
            for e in enrollments:
                s = e.student
                # Check if already recorded
                existing = AttendanceRecord.objects.filter(
                    student=s, course=selected_course, date=load_date
                ).first()
                s.today_status = existing.status if existing else 'present'
                students.append(s)
            return render(request, 'students/bulk_attendance.html', {
                'courses': courses,
                'selected_course': selected_course,
                'students': students,
                'today': date_str,
            })

        elif action == 'save' and selected_course:
            from datetime import date as date_cls
            save_date = date_cls.fromisoformat(date_str)
            enrollments = Enrollment.objects.filter(course=selected_course).select_related('student')
            saved = 0
            for e in enrollments:
                s = e.student
                status = request.POST.get(f'status_{s.pk}', 'present')
                notes = request.POST.get(f'notes_{s.pk}', '')
                obj, created = AttendanceRecord.objects.update_or_create(
                    student=s, course=selected_course, date=save_date,
                    defaults={'status': status, 'notes': notes, 'recorded_by': request.user}
                )
                check_and_send_alerts(s)
                saved += 1
            messages.success(request, f'Attendance saved for {saved} students.')
            return redirect('bulk_attendance')

    return render(request, 'students/bulk_attendance.html', {
        'courses': courses,
        'today': today,
    })
