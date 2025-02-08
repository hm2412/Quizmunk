from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from functools import wraps

def is_student(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'student':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have access to the Student Dashboard.")
    return _wrapped_view

def is_tutor(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'tutor':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have access to the Tutor Dashboard.")
    return _wrapped_view

# Logged in users will be directed to dashboard when trying to access pages for users not signed in
def redirect_authenticated_to_dashboard(view_func): 
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 'student':
                return HttpResponseRedirect(reverse('student_dashboard'))
            elif request.user.role == 'tutor':
                return HttpResponseRedirect(reverse('tutor_dashboard'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def redirect_unauthenticated_to_homepage(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('homepage'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
