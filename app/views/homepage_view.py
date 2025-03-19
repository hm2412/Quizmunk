from django.shortcuts import render
from app.helpers.decorators import redirect_authenticated_to_dashboard
from django.views.decorators.cache import never_cache

@redirect_authenticated_to_dashboard
@never_cache
def homepage(request):
    return render(request, 'home.html')

def about_us(request):
    return render(request, 'about.html');
