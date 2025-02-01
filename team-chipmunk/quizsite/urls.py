"""
URL configuration for quizsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from quizsite.app.views.homepage_view import homepage
from quizsite.app.views.dashboard_view import student_dashboard, tutor_dashboard
from quizsite.app.views.sign_up_view import sign_up_view
from quizsite.app.views.login_view import login_view
from quizsite.app.views.quiz_view import create_quiz_view,edit_quiz_view,delete_question_view, get_question_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('sign-up/', sign_up_view, name='sign_up'),
    path('login/', login_view, name='login'), 
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('tutor-dashboard/', tutor_dashboard, name='tutor_dashboard'),
    path('create-quiz/', create_quiz_view, name='create_quiz'),
    path('edit-quiz/<int:quiz_id>/', edit_quiz_view, name='edit_quiz'),
    path('delete-question/<int:question_id>/', delete_question_view, name='delete_question'),
    path('get_question/<int:quiz_id>/', get_question_view, name='get_question'),
]
