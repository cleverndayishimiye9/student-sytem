from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('export/students/', views.export_students_csv, name='export_students'),
    path('export/grades/', views.export_grades_csv, name='export_grades'),
    path('export/attendance/', views.export_attendance_csv, name='export_attendance'),
]
