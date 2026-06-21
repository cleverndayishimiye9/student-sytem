from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Grade, AttendanceRecord, StudentProfile, Course, Enrollment


class GradeUploadForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('student', 'course', 'grade_type', 'score', 'max_score', 'comments')
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, lecturer=None, **kwargs):
        super().__init__(*args, **kwargs)
        if lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=lecturer)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('student', css_class='col-md-6'),
                Column('course', css_class='col-md-6'),
            ),
            Row(
                Column('grade_type', css_class='col-md-4'),
                Column('score', css_class='col-md-4'),
                Column('max_score', css_class='col-md-4'),
            ),
            'comments',
            Submit('submit', 'Upload Grade', css_class='btn btn-success'),
        )


class GradeEditForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('student', 'course', 'grade_type', 'score', 'max_score', 'comments')
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('student', css_class='col-md-6'),
                Column('course', css_class='col-md-6'),
            ),
            Row(
                Column('grade_type', css_class='col-md-4'),
                Column('score', css_class='col-md-4'),
                Column('max_score', css_class='col-md-4'),
            ),
            'comments',
            Submit('submit', 'Update Grade', css_class='btn btn-primary'),
        )


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ('student', 'course', 'date', 'status', 'notes')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, lecturer=None, **kwargs):
        super().__init__(*args, **kwargs)
        if lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=lecturer)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('student', css_class='col-md-6'),
                Column('course', css_class='col-md-6'),
            ),
            Row(
                Column('date', css_class='col-md-4'),
                Column('status', css_class='col-md-4'),
            ),
            'notes',
            Submit('submit', 'Record Attendance', css_class='btn btn-primary'),
        )


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('student_id', 'year_of_study', 'department', 'date_of_birth', 'guardian_name', 'guardian_phone')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save Profile', css_class='btn btn-primary'))


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('student', 'course')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('student', css_class='col-md-6'),
                Column('course', css_class='col-md-6'),
            ),
            Submit('submit', 'Enroll Student', css_class='btn btn-primary'),
        )