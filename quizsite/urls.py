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
from django.conf import settings
from django.conf.urls.static import static
from app.views.homepage_view import homepage
from app.views.sign_up_view import sign_up_view
from app.views.login_view import login_view, logout_view
from app.views.join_quiz_view import join_quiz
from app.views.lobby_view import lobby, setup_quiz
from app.views.dashboard_view import student_dashboard, tutor_dashboard
from app.views.profile_view import student_profile, tutor_profile
from app.views.quiz_view import create_quiz_view,edit_quiz_view,delete_question_view, get_question_view, your_quizzes_view, delete_quiz_view
from app.views.live_quiz_view import tutor_live_quiz, start_quiz, next_question, end_quiz, student_live_quiz
from app.views.password_reset_view import password_reset
from app.views.live_quiz_view import student_live_quiz, tutor_live_quiz, start_quiz, next_question, end_quiz
from app.views.classroom_view import tutor_classroom_view, tutor_classroom_detail_view, student_classroom_view, accept_classroom_invite, decline_classroom_invite, student_classroom_detail_view
from app.views.stats_view import stats_view, stats_details, csv_download, player_responses

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('sign-up/', sign_up_view, name='sign_up'),
    path('login/', login_view, name='login'), 
    path('logout/', logout_view, name='logout'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('tutor-dashboard/', tutor_dashboard, name='tutor_dashboard'),
    path('create-quiz/', create_quiz_view, name='create_quiz'),
    path('edit-quiz/<int:quiz_id>/', edit_quiz_view, name='edit_quiz'),
    path('delete-question/<int:question_id>/', delete_question_view, name='delete_question'),
    path('get_question/<int:quiz_id>/', get_question_view, name='get_question'),
    path('student-profile/', student_profile, name='student_profile'),
    path('tutor-profile/', tutor_profile, name='tutor_profile'),
    path('join-quiz/', join_quiz, name='join_quiz'),
    path('setup_quiz/<int:quiz_id>/', setup_quiz, name='setup_quiz'),
    path('lobby/<str:join_code>', lobby, name='lobby'),
    #path('live-quiz/<str:join_code>', tutor_live_quiz, name='tutor_live_quiz'),
    path('live-quiz/<int:quiz_id>/<str:join_code>/', tutor_live_quiz, name='tutor_live_quiz'),
    path('start-quiz/<str:join_code>', start_quiz, name='start_quiz'),
    path('next-question/<str:join_code>', next_question, name='next_question'),
    path('end-quiz/<str:join_code>', end_quiz, name='end_quiz'),
    path('your-quizzes/', your_quizzes_view, name='your_quizzes'),
    path('delete-quiz/<int:quiz_id>/', delete_quiz_view, name='delete_quiz'),
    # path("password-reset/", password_reset, name="password_reset"),
    path('tutor-classrooms/', tutor_classroom_view, name='tutor_classroom_view'),
    path('tutor-classrooms/<int:classroom_id>/', tutor_classroom_detail_view, name='tutor_classroom_detail'),
    path('student-classrooms/', student_classroom_view, name='student_classroom_view'),
    path('student-classrooms/<int:classroom_id>', student_classroom_detail_view, name='student_classroom_detail_view'),
    path('accept-classroom-invite/<int:invite_id>/', accept_classroom_invite, name="accept_classroom_invite"),
    path('decline-classroom-invite/<int:invite_id>/', decline_classroom_invite, name="decline_classroom_invite"),
    path("student/live-quiz/<str:room_code>/", student_live_quiz, name="student_live_quiz"),
    path("tutor-stats/", stats_view, name='stats'),
    path("tutor-stats/<int:stats_id>/", stats_details, name='stats_details'),
    path("tutor-stats/<int:stats_id>/download/", csv_download, name='stats_download'),
    path('player-responses/<int:room_id>/int:player_id/', player_responses, name='player_responses')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)