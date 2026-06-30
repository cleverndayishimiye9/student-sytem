from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username or Student ID',
        'class': 'form-control',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-control',
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='mb-3'),
            Field('password', css_class='mb-3'),
            Submit('submit', 'Login', css_class='btn btn-primary w-100'),
        )


class UserCreationFormCustom(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            Row(
                Column('username', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
            ),
            Row(
                Column('role', css_class='col-md-6'),
                Column('phone_number', css_class='col-md-6'),
            ),
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
            ),
            Submit('submit', 'Create User', css_class='btn btn-primary'),
        )


class StudentRegistrationForm(UserCreationForm):
    # Student info
    student_id = forms.CharField(max_length=20, label='Registration Number')
    year_of_study = forms.ChoiceField(choices=[(i, f'Year {i}') for i in range(1, 5)], label='Year of Study')
    department = forms.ModelChoiceField(queryset=None, label='Department')
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date of Birth', required=False
    )

    # Parent info
    guardian_name = forms.CharField(max_length=100, label='Parent/Guardian Name')
    guardian_phone = forms.CharField(max_length=20, label='Parent/Guardian Phone')

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email',
            'phone_number', 'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.students.models import Department
        self.fields['department'].queryset = Department.objects.all()
        self.fields['username'].label = 'Username (can use Reg Number)'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="fw-bold text-primary mt-3 mb-2"><i class="bi bi-person me-2"></i>Student Information</h6>'),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            Row(
                Column('student_id', css_class='col-md-6'),
                Column('username', css_class='col-md-6'),
            ),
            Row(
                Column('email', css_class='col-md-6'),
                Column('phone_number', css_class='col-md-6'),
            ),
            Row(
                Column('year_of_study', css_class='col-md-4'),
                Column('department', css_class='col-md-4'),
                Column('date_of_birth', css_class='col-md-4'),
            ),
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
            ),
            HTML('<h6 class="fw-bold text-success mt-3 mb-2"><i class="bi bi-people me-2"></i>Parent / Guardian Information</h6>'),
            Row(
                Column('guardian_name', css_class='col-md-6'),
                Column('guardian_phone', css_class='col-md-6'),
            ),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            from apps.students.models import StudentProfile, Department
            StudentProfile.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                year_of_study=self.cleaned_data['year_of_study'],
                department=self.cleaned_data['department'],
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                guardian_name=self.cleaned_data['guardian_name'],
                guardian_phone=self.cleaned_data['guardian_phone'],
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'profile_photo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update Profile', css_class='btn btn-primary'))