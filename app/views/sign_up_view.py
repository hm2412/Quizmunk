from django.shortcuts import render, redirect
from django.contrib.auth import login
from app.forms import SignUpForm
from app.models import User
from django.views.decorators.cache import never_cache
from app.helpers.decorators import redirect_authenticated_to_dashboard

@redirect_authenticated_to_dashboard
@never_cache
def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homepage')  # Redirect to the home page or dashboard
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})
