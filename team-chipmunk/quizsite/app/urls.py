from django.urls import path
from .views.homepage_view import homepage
from .views.dashboard_view import student_dashboard, tutor_dashboard

urlpatterns = [
    path('', homepage, name='homepage'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('tutor-dashboard/', tutor_dashboard, name='tutor_dashboard'),
]
