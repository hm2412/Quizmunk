from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from quizsite.user.forms.forms import SignUpForm, LoginForm
from quizsite.user.models import User, Student, Tutor

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  
            if user.role == User.STUDENT:
                Student.objects.create(user=user, name="Default Student Name")
            elif user.role == User.TUTOR:
                Tutor.objects.create(user=user, name="Default Tutor Name")
            login(request, user)
            return redirect('home')  # Redirect to the home page or dashboard
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data['email_address']
            password = form.cleaned_data['password']
            user = authenticate(request, email_address=email_address, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')  # Redirect to the home or dashboard page
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def home_view(request):
    return render(request, 'home.html', {})
