from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import csv
from apps.students.models import StudentProfile, Grade, AttendanceRecord, Course


@login_required
def reports_dashboard(request):
    if not (request.user.is_admin or request.user.is_staff_member or request.user.is_lecturer):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return render(request, 'reports/dashboard.html')


@login_required
def export_students_csv(request):
    """Export all students performance summary as CSV."""
    if not (request.user.is_admin or request.user.is_staff_member):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_performance.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Full Name', 'Year', 'Department',
        'Overall GPA (%)', 'Attendance Rate (%)', 'Risk Level'
    ])

    for student in StudentProfile.objects.select_related('user', 'department').all():
        writer.writerow([
            student.student_id,
            student.user.get_full_name(),
            student.year_of_study,
            student.department.name if student.department else '',
            student.overall_gpa,
            student.attendance_rate,
            student.risk_level,
        ])

    return response


@login_required
def export_grades_csv(request):
    if not (request.user.is_admin or request.user.is_lecturer):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="grades_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Student Name', 'Course Code', 'Course Name',
        'Grade Type', 'Score', 'Max Score', 'Percentage', 'Letter Grade', 'Uploaded At'
    ])

    grades = Grade.objects.select_related('student__user', 'course').all()
    if request.user.is_lecturer:
        grades = grades.filter(course__lecturer=request.user)

    for g in grades:
        writer.writerow([
            g.student.student_id,
            g.student.user.get_full_name(),
            g.course.code,
            g.course.name,
            g.get_grade_type_display(),
            g.score,
            g.max_score,
            g.percentage,
            g.letter_grade,
            g.uploaded_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response


@login_required
def export_attendance_csv(request):
    if not (request.user.is_admin or request.user.is_lecturer):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Course Code', 'Date', 'Status', 'Notes'])

    records = AttendanceRecord.objects.select_related('student__user', 'course').all()
    if request.user.is_lecturer:
        records = records.filter(course__lecturer=request.user)

    for r in records:
        writer.writerow([
            r.student.student_id,
            r.student.user.get_full_name(),
            r.course.code,
            r.date,
            r.get_status_display(),
            r.notes,
        ])

    return response
