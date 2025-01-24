from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from quizsite.app.forms import LoginForm

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
                return HttpResponseRedirect(reverse('homepage'))  # Redirect to the home or dashboard page
            else:
                messages.error(request, "Invalid email or password")
                return render(request,'login.html',{'form': form})  
                
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
