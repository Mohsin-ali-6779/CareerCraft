# MyApp/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from .forms import SignupForm, LoginForm, ProfileForm, AchievementForm
from .models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Course


# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the user
            messages.success(request, 'Your account has been created successfully! Please login.')
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    
    return render(request, 'signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']

            # Use email for authentication (not username)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.role == role:  # role match
                    login(request, user)
                    messages.success(request, "Login successful 🎉")
                    return redirect('courses')   # Redirect to courses page
                else:
                    messages.error(request, "Role mismatch! Please choose the correct role.")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def courses(request):
    return render(request, 'courses.html')  # create this template

def home(request):
    return render(request, 'home.html')

@login_required
def my_courses(request):
    return render(request, 'my_courses.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

@login_required
def enroll_course(request, course_id):
    if request.method == "POST":
        # later we will use DB, for now just success message
        messages.success(request, f"You have successfully enrolled in course {course_id}!")
        return redirect('my_courses')

    return redirect('courses')

@login_required
def profile_view(request):
    user = request.user
    enrolled = user.enrolledcourse_set.select_related('course').all()
    completed = enrolled.filter(is_completed=True)
    achievements = user.achievement_set.all()
    
    return render(request, 'profile.html', {
        'user': user,
        'enrolled_courses': enrolled,
        'completed_courses': completed,
        'achievements': achievements,
    })
@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def add_achievement(request):
    if request.method == "POST":
        form = AchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.user = request.user
            achievement.save()
            return redirect('profile')
    else:
        form = AchievementForm()
    return render(request, 'add_achievement.html', {'form': form})
