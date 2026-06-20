from django.contrib import admin
from .models import StudentProfile, Course, Grade, AttendanceRecord, Enrollment, AcademicYear, Department


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'is_current', 'start_date', 'end_date')
    list_editable = ('is_current',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'lecturer', 'department', 'semester', 'academic_year')
    list_filter = ('academic_year', 'semester', 'department')
    search_fields = ('code', 'name')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'year_of_study', 'department', 'overall_gpa', 'risk_level', 'guardian_name', 'guardian_phone')
    list_filter = ('year_of_study', 'department')
    search_fields = ('student_id', 'user__first_name', 'user__last_name')
    readonly_fields = ('overall_gpa', 'attendance_rate', 'risk_level')
    fieldsets = (
        ('Student Info', {
            'fields': ('user', 'student_id', 'year_of_study', 'department', 'date_of_birth')
        }),
        ('Guardian / Parent', {
            'fields': ('guardian_name', 'guardian_phone')
        }),
        ('Performance (Read Only)', {
            'fields': ('overall_gpa', 'attendance_rate', 'risk_level')
        }),
    )


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'grade_type', 'score', 'max_score', 'percentage', 'letter_grade', 'uploaded_at')
    list_filter = ('grade_type', 'course__academic_year')
    search_fields = ('student__student_id', 'course__code')


@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status', 'recorded_by')
    list_filter = ('status', 'date', 'course')
    search_fields = ('student__student_id', 'course__code')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    search_fields = ('student__student_id', 'course__code')