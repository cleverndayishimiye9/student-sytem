from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.conf import settings

from .models import StudentProfile, Course, Grade, AttendanceRecord, Enrollment, AcademicYear
from .forms import GradeUploadForm, AttendanceForm, StudentProfileForm, EnrollmentForm
from apps.notifications.services import check_and_send_alerts


@login_required
def dashboard(request):
    """Main dashboard — adapts content based on user role."""
    user = request.user
    context = {'user': user}

    if user.is_admin or user.is_staff_member:
        students = StudentProfile.objects.all()
        context.update({
            'total_students': students.count(),
            'at_risk_high': [s for s in students if s.risk_level == 'HIGH'],
            'at_risk_medium': [s for s in students if s.risk_level == 'MEDIUM'],
            'total_courses': Course.objects.count(),
            'recent_grades': Grade.objects.select_related('student', 'course').order_by('-uploaded_at')[:10],
        })

    elif user.is_lecturer:
        my_courses = Course.objects.filter(lecturer=user)
        my_students = StudentProfile.objects.filter(enrollments__course__in=my_courses).distinct()
        context.update({
            'my_courses': my_courses,
            'my_students': my_students,
            'at_risk': [s for s in my_students if s.risk_level in ('HIGH', 'MEDIUM')],
            'recent_grades': Grade.objects.filter(course__in=my_courses).order_by('-uploaded_at')[:10],
        })

    elif user.is_student_role:
        try:
            profile = user.student_profile
            grades = profile.grades.select_related('course').order_by('-uploaded_at')
            attendance = profile.attendance_records.select_related('course').order_by('-date')[:20]
            context.update({
                'profile': profile,
                'grades': grades,
                'attendance': attendance,
                'gpa': profile.overall_gpa,
                'attendance_rate': profile.attendance_rate,
                'risk_level': profile.risk_level,
            })
        except StudentProfile.DoesNotExist:
            messages.warning(request, 'Your student profile is not yet set up. Please contact admin.')

    return render(request, 'students/dashboard.html', context)


@login_required
def student_list(request):
    if not (request.user.is_admin or request.user.is_lecturer or request.user.is_staff_member):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    students = StudentProfile.objects.select_related('user', 'department').all()
    risk_filter = request.GET.get('risk', '')
    if risk_filter:
        students = [s for s in students if s.risk_level == risk_filter.upper()]

    return render(request, 'students/student_list.html', {'students': students, 'risk_filter': risk_filter})


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)

    # Students can only see their own profile
    if request.user.is_student_role and request.user.student_profile != student:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    grades = student.grades.select_related('course').order_by('-uploaded_at')
    attendance = student.attendance_records.select_related('course').order_by('-date')
    enrollments = student.enrollments.select_related('course')

    return render(request, 'students/student_detail.html', {
        'student': student,
        'grades': grades,
        'attendance': attendance,
        'enrollments': enrollments,
    })


@login_required
def upload_grade(request):
    if not (request.user.is_admin or request.user.is_lecturer):
        messages.error(request, 'Only lecturers and admins can upload grades.')
        return redirect('dashboard')

    lecturer = request.user if request.user.is_lecturer else None
    form = GradeUploadForm(lecturer=lecturer)

    if request.method == 'POST':
        form = GradeUploadForm(request.POST, lecturer=lecturer)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.uploaded_by = request.user
            grade.save()
            messages.success(request, f'Grade uploaded for {grade.student}.')
            # Trigger alert check
            check_and_send_alerts(grade.student)
            return redirect('upload_grade')

    return render(request, 'students/upload_grade.html', {'form': form})


@login_required
def record_attendance(request):
    if not (request.user.is_admin or request.user.is_lecturer):
        messages.error(request, 'Only lecturers and admins can record attendance.')
        return redirect('dashboard')

    lecturer = request.user if request.user.is_lecturer else None
    form = AttendanceForm(lecturer=lecturer)

    if request.method == 'POST':
        form = AttendanceForm(request.POST, lecturer=lecturer)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, 'Attendance recorded.')
            check_and_send_alerts(record.student)
            return redirect('record_attendance')

    return render(request, 'students/record_attendance.html', {'form': form})


@login_required
def enroll_student(request):
    if not request.user.is_admin:
        messages.error(request, 'Admins only.')
        return redirect('dashboard')

    form = EnrollmentForm()
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student enrolled successfully.')
            return redirect('enroll_student')

    return render(request, 'students/enroll_student.html', {'form': form})


@login_required
def at_risk_students(request):
    if not (request.user.is_admin or request.user.is_lecturer or request.user.is_staff_member):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    all_students = StudentProfile.objects.select_related('user', 'department').all()
    high_risk = [s for s in all_students if s.risk_level == 'HIGH']
    medium_risk = [s for s in all_students if s.risk_level == 'MEDIUM']

    return render(request, 'students/at_risk.html', {
        'high_risk': high_risk,
        'medium_risk': medium_risk,
    })
