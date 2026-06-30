from django.urls import path
from . import views
from .views_bulk import bulk_attendance
from .views_bulk_grades import bulk_grade_entry
from .views_courses import course_list, course_detail

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('grades/upload/', views.upload_grade, name='upload_grade'),
    path('grades/bulk/', bulk_grade_entry, name='bulk_grade_entry'),
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/<int:grade_id>/edit/', views.edit_grade, name='edit_grade'),
    path('grades/<int:grade_id>/delete/', views.delete_grade, name='delete_grade'),
    path('attendance/record/', views.record_attendance, name='record_attendance'),
    path('attendance/bulk/', bulk_attendance, name='bulk_attendance'),
    path('enroll/', views.enroll_student, name='enroll_student'),
    path('at-risk/', views.at_risk_students, name='at_risk_students'),
    path('courses/', course_list, name='course_list'),
    path('courses/<int:course_id>/', course_detail, name='course_detail'),
]