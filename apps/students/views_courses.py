from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Course, AcademicYear, Department
from apps.accounts.models import User


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('code', 'name', 'department', 'lecturer', 'credit_hours', 'academic_year', 'semester')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lecturer'].queryset = User.objects.filter(role='lecturer', is_active=True)


@login_required
def course_list(request):
    if not (request.user.is_admin or request.user.is_lecturer or request.user.is_staff_member):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.user.is_lecturer:
        courses = Course.objects.filter(lecturer=request.user).select_related('department', 'academic_year')
    else:
        courses = Course.objects.all().select_related('department', 'lecturer', 'academic_year')

    form = CourseForm()
    if request.method == 'POST' and request.user.is_admin:
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully.')
            return redirect('course_list')

    return render(request, 'students/course_list.html', {'courses': courses, 'form': form})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollments = course.enrollments.select_related('student__user')
    grades = course.grades.select_related('student__user').order_by('-uploaded_at')[:30]
    attendance = course.attendance_records.select_related('student__user').order_by('-date')[:30]

    return render(request, 'students/course_detail.html', {
        'course': course,
        'enrollments': enrollments,
        'grades': grades,
        'attendance': attendance,
    })
