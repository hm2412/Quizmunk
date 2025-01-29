from django.shortcuts import render
from quizsite.app.helpers.decorators import redirect_authenticated_to_dashboard

@redirect_authenticated_to_dashboard
def homepage(request):
    return render(request, 'home.html')
