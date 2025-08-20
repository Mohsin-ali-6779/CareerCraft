from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, StudentDetail, InstructorDetail, AdminDetail
from .models import Profile, Achievement
# Signup Form
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'username', 'phone', 'dob', 'gender', 'role', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


from .models import User

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Instructor', 'Instructor'),
        ('Admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    remember_me = forms.BooleanField(required=False)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone_number'] 
class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['record_type', 'course', 'title', 'description']