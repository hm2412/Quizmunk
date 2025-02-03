from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from quizsite.app.forms import LoginForm
from quizsite.app.helpers.decorators import redirect_authenticated_to_dashboard

@redirect_authenticated_to_dashboard
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
                if user.role == 'student':
                    return HttpResponseRedirect(reverse('student_dashboard'))
                elif user.role == 'tutor':
                    return HttpResponseRedirect(reverse('tutor_dashboard'))
            else:
                messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')
