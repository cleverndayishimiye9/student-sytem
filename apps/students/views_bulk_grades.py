from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Course, StudentProfile, Enrollment, Grade
from apps.notifications.services import check_and_send_alerts


GRADE_COLUMNS = [
    ('ASSIGNMENT1', 'Assignment 1', 10),
    ('ASSIGNMENT2', 'Assignment 2', 10),
    ('CAT1', 'CAT 1', 20),
    ('CAT2', 'CAT 2', 20),
    ('FINAL', 'Final Exam', 40),
]


@login_required
def bulk_grade_entry(request):
    if not (request.user.is_admin or request.user.is_lecturer):
        messages.error(request, 'Only lecturers and admins can enter grades.')
        return redirect('dashboard')

    lecturer = request.user if request.user.is_lecturer else None
    courses = Course.objects.filter(lecturer=lecturer) if lecturer else Course.objects.all()

    selected_course = None
    students = []
    search = request.GET.get('search', request.POST.get('search', ''))

    course_id = request.POST.get('course_id') or request.GET.get('course_id')

    if course_id:
        try:
            selected_course = courses.get(pk=course_id)
        except Course.DoesNotExist:
            messages.error(request, 'Course not found.')
            return redirect('bulk_grade_entry')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save' and selected_course:
            enrollments = Enrollment.objects.filter(course=selected_course).select_related('student__user')
            saved_count = 0

            for e in enrollments:
                s = e.student
                for grade_type, label, max_score in GRADE_COLUMNS:
                    field_name = 'score_' + grade_type + '_' + str(s.pk)
                    score_value = request.POST.get(field_name, '').strip()

                    if score_value:
                        try:
                            score = float(score_value)
                        except ValueError:
                            continue

                        grade_obj, created = Grade.objects.update_or_create(
                            student=s,
                            course=selected_course,
                            grade_type=grade_type,
                            defaults={
                                'score': score,
                                'max_score': max_score,
                                'uploaded_by': request.user,
                            }
                        )
                        saved_count = saved_count + 1
                        check_and_send_alerts(s, course=selected_course, grade_type=grade_type, score=score, max_score=max_score)

            messages.success(request, str(saved_count) + ' grade entries saved for ' + selected_course.name + '.')
            return redirect('/dashboard/grades/bulk/?course_id=' + str(selected_course.pk))

    if selected_course:
        enrollments = Enrollment.objects.filter(course=selected_course).select_related('student__user')
        student_list = []
        for e in enrollments:
            student_list.append(e.student)

        if search:
            filtered_list = []
            for s in student_list:
                if search in s.student_id:
                    filtered_list.append(s)
            student_list = filtered_list

        for s in student_list:
            existing_grades = {}
            for g in Grade.objects.filter(student=s, course=selected_course):
                existing_grades[g.grade_type] = g

            if 'ASSIGNMENT1' in existing_grades:
                s.score_a1 = existing_grades['ASSIGNMENT1'].score
            else:
                s.score_a1 = ''

            if 'ASSIGNMENT2' in existing_grades:
                s.score_a2 = existing_grades['ASSIGNMENT2'].score
            else:
                s.score_a2 = ''

            if 'CAT1' in existing_grades:
                s.score_cat1 = existing_grades['CAT1'].score
            else:
                s.score_cat1 = ''

            if 'CAT2' in existing_grades:
                s.score_cat2 = existing_grades['CAT2'].score
            else:
                s.score_cat2 = ''

            if 'FINAL' in existing_grades:
                s.score_final = existing_grades['FINAL'].score
            else:
                s.score_final = ''

        students = student_list

    return render(request, 'students/bulk_grade_entry.html', {
        'courses': courses,
        'selected_course': selected_course,
        'students': students,
        'grade_columns': GRADE_COLUMNS,
        'search': search,
    })