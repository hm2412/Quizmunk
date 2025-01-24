from django.shortcuts import render, redirect
from django.contrib.auth import login
from quizsite.app.forms import SignUpForm
from quizsite.app.models import User, Student, Tutor

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
            return redirect('homepage')  # Redirect to the home page or dashboard
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})
