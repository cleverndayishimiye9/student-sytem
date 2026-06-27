from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from .models import Grade, AttendanceRecord, StudentProfile, Course, Enrollment


# Max marks for each grade type based on UoK marking scheme
GRADE_MAX_SCORES = {
    'CAT1': 20,
    'CAT2': 20,
    'ASSIGNMENT': 20,
    'FINAL': 40,
    'MIDTERM': 40,
    'PROJECT': 20,
}


class GradeUploadForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('student', 'course', 'grade_type', 'score', 'max_score', 'comments')
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 2}),
            'max_score': forms.NumberInput(attrs={'id': 'id_max_score'}),
            'grade_type': forms.Select(attrs={'id': 'id_grade_type', 'onchange': 'updateMaxScore(this.value)'}),
        }

    def __init__(self, *args, lecturer=None, **kwargs):
        super().__init__(*args, **kwargs)
        if lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=lecturer)
        self.fields['max_score'].initial = 20
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
            HTML("""
            <script>
            const maxScores = {
                'CAT1': 20,
                'CAT2': 20,
                'ASSIGNMENT': 20,
                'FINAL': 40,
                'MIDTERM': 40,
                'PROJECT': 20,
            };
            function updateMaxScore(gradeType) {
                const maxScoreField = document.getElementById('id_max_score');
                if (maxScores[gradeType]) {
                    maxScoreField.value = maxScores[gradeType];
                }
            }
            // Set on page load
            document.addEventListener('DOMContentLoaded', function() {
                const gradeTypeField = document.getElementById('id_grade_type');
                if (gradeTypeField.value) {
                    updateMaxScore(gradeTypeField.value);
                }
            });
            </script>
            """),
            Submit('submit', 'Upload Grade', css_class='btn btn-success'),
        )

    def clean(self):
        cleaned_data = super().clean()
        grade_type = cleaned_data.get('grade_type')
        score = cleaned_data.get('score')
        max_score = cleaned_data.get('max_score')

        # Auto set max score based on grade type
        if grade_type and grade_type in GRADE_MAX_SCORES:
            cleaned_data['max_score'] = GRADE_MAX_SCORES[grade_type]
            max_score = GRADE_MAX_SCORES[grade_type]

        # Validate score doesn't exceed max score
        if score is not None and max_score is not None:
            if score > max_score:
                raise forms.ValidationError(
                    f'Score cannot exceed max score of {max_score} for {grade_type}.'
                )
        return cleaned_data


class GradeEditForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('student', 'course', 'grade_type', 'score', 'max_score', 'comments')
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 2}),
            'max_score': forms.NumberInput(attrs={'id': 'id_max_score'}),
            'grade_type': forms.Select(attrs={'id': 'id_grade_type', 'onchange': 'updateMaxScore(this.value)'}),
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
            HTML("""
            <script>
            const maxScores = {
                'CAT1': 20,
                'CAT2': 20,
                'ASSIGNMENT': 20,
                'FINAL': 40,
                'MIDTERM': 40,
                'PROJECT': 20,
            };
            function updateMaxScore(gradeType) {
                const maxScoreField = document.getElementById('id_max_score');
                if (maxScores[gradeType]) {
                    maxScoreField.value = maxScores[gradeType];
                }
            }
            document.addEventListener('DOMContentLoaded', function() {
                const gradeTypeField = document.getElementById('id_grade_type');
                if (gradeTypeField.value) {
                    updateMaxScore(gradeTypeField.value);
                }
            });
            </script>
            """),
            Submit('submit', 'Update Grade', css_class='btn btn-primary'),
        )

    def clean(self):
        cleaned_data = super().clean()
        grade_type = cleaned_data.get('grade_type')
        score = cleaned_data.get('score')

        # Auto set max score based on grade type
        if grade_type and grade_type in GRADE_MAX_SCORES:
            cleaned_data['max_score'] = GRADE_MAX_SCORES[grade_type]
            max_score = GRADE_MAX_SCORES[grade_type]
        else:
            max_score = cleaned_data.get('max_score')

        # Validate score doesn't exceed max score
        if score is not None and max_score is not None:
            if score > max_score:
                raise forms.ValidationError(
                    f'Score cannot exceed max score of {max_score} for {grade_type}.'
                )
        return cleaned_data


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