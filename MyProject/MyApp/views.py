# MyApp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import SignupForm, LoginForm
from .models import User
from django.contrib import messages

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
    form = LoginForm(request.POST or None)
    message = ''
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']

            user = authenticate(request, email=email, password=password)
            if user is not None and user.role == role:
                login(request, user)
                return redirect('home')  # change 'home' to your dashboard page
            else:
                message = 'Invalid credentials or role.'

    return render(request, 'login.html', {'form': form, 'message': message})
