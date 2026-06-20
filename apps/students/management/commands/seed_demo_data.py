"""
Management command: python manage.py seed_demo_data
Creates sample data for testing the system.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with demo data for testing'

    def handle(self, *args, **kwargs):
        from apps.accounts.models import User
        from apps.students.models import (
            AcademicYear, Department, Course, StudentProfile, Enrollment, Grade, AttendanceRecord
        )

        self.stdout.write('Seeding demo data...')

        # Academic year
        year, _ = AcademicYear.objects.get_or_create(
            year='2025/2026',
            defaults={'is_current': True, 'start_date': date(2025, 9, 1), 'end_date': date(2026, 6, 30)}
        )

        # Departments
        bit_dept, _ = Department.objects.get_or_create(name='Business Information Technology', code='BIT')
        cs_dept, _ = Department.objects.get_or_create(name='Computer Science', code='CS')

        # Users: Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'System', 'last_name': 'Admin', 'role': 'admin',
                      'email': 'admin@uok.ac.rw', 'phone_number': '+250788000001', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('  Created admin user (username: admin, password: admin123)')

        # Lecturer
        lecturer, created = User.objects.get_or_create(
            username='manirarora',
            defaults={'first_name': 'Jean Marie Vianney', 'last_name': 'MANIRARORA',
                      'role': 'lecturer', 'email': 'manirarora@uok.ac.rw', 'phone_number': '+250788000002'}
        )
        if created:
            lecturer.set_password('lecturer123')
            lecturer.save()
            self.stdout.write('  Created lecturer (username: manirarora, password: lecturer123)')

        # Staff
        staff, created = User.objects.get_or_create(
            username='staff1',
            defaults={'first_name': 'Uwase', 'last_name': 'Marie',
                      'role': 'staff', 'email': 'staff1@uok.ac.rw', 'phone_number': '+250788000003'}
        )
        if created:
            staff.set_password('staff123')
            staff.save()
            self.stdout.write('  Created staff (username: staff1, password: staff123)')

        # Courses
        course1, _ = Course.objects.get_or_create(
            code='BIT301', defaults={
                'name': 'Database Systems', 'department': bit_dept,
                'lecturer': lecturer, 'credit_hours': 3,
                'academic_year': year, 'semester': 'Semester 1'
            }
        )
        course2, _ = Course.objects.get_or_create(
            code='BIT302', defaults={
                'name': 'Software Engineering', 'department': bit_dept,
                'lecturer': lecturer, 'credit_hours': 3,
                'academic_year': year, 'semester': 'Semester 1'
            }
        )
        course3, _ = Course.objects.get_or_create(
            code='BIT303', defaults={
                'name': 'Web Development', 'department': bit_dept,
                'lecturer': lecturer, 'credit_hours': 3,
                'academic_year': year, 'semester': 'Semester 1'
            }
        )

        # Students
        students_data = [
            ('2301000358', 'NDAYISHIMIZE', 'CLAVER', 4, '+250788100001'),
            ('2301000359', 'UWIMANA', 'ALICE', 3, '+250788100002'),
            ('2301000360', 'HABIMANA', 'JEAN', 2, '+250788100003'),
            ('2301000361', 'MUGISHA', 'ERIC', 4, '+250788100004'),
            ('2301000362', 'IMANISHIMWE', 'GRACE', 1, '+250788100005'),
        ]

        created_students = []
        for sid, last, first, year_num, phone in students_data:
            user, created = User.objects.get_or_create(
                username=sid,
                defaults={'first_name': first, 'last_name': last, 'role': 'student',
                          'email': f'{sid}@student.uok.ac.rw', 'phone_number': phone}
            )
            if created:
                user.set_password('student123')
                user.save()

            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={'student_id': sid, 'year_of_study': year_num, 'department': bit_dept}
            )
            created_students.append(profile)

            # Enroll in courses
            for course in [course1, course2, course3]:
                Enrollment.objects.get_or_create(student=profile, course=course)

        self.stdout.write(f'  Created {len(created_students)} student profiles')

        # Grades (varying performance — some at risk)
        grade_types = ['CAT1', 'CAT2', 'ASSIGNMENT', 'MIDTERM']
        scores_map = {
            0: [75, 80, 72, 68],   # CLAVER — good
            1: [85, 90, 88, 82],   # ALICE — excellent
            2: [40, 35, 42, 38],   # JEAN — HIGH RISK
            3: [55, 60, 48, 52],   # ERIC — MEDIUM RISK
            4: [70, 65, 75, 68],   # GRACE — OK
        }

        for i, student in enumerate(created_students):
            for j, course in enumerate([course1, course2, course3]):
                for k, gtype in enumerate(grade_types):
                    base_score = scores_map[i][k]
                    score = max(0, min(100, base_score + random.randint(-5, 5)))
                    Grade.objects.get_or_create(
                        student=student, course=course, grade_type=gtype,
                        defaults={'score': score, 'max_score': 100, 'uploaded_by': lecturer}
                    )

        # Attendance
        for i, student in enumerate(created_students):
            for course in [course1, course2, course3]:
                for day_offset in range(20):
                    record_date = date.today() - timedelta(days=day_offset * 2)
                    # JEAN has very poor attendance
                    if i == 2:
                        status = random.choice(['absent', 'absent', 'absent', 'present'])
                    else:
                        status = random.choice(['present', 'present', 'present', 'absent', 'late'])
                    AttendanceRecord.objects.get_or_create(
                        student=student, course=course, date=record_date,
                        defaults={'status': status, 'recorded_by': lecturer}
                    )

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin:    admin / admin123')
        self.stdout.write('  Lecturer: manirarora / lecturer123')
        self.stdout.write('  Staff:    staff1 / staff123')
        self.stdout.write('  Students: <student_id> / student123 (e.g. 2301000358)')
