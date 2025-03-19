from django.urls import path
from app.consumers.lobby_consumer import LobbyConsumer
from app.consumers.tutor_live_quiz_consumer import TutorQuizConsumer
from app.consumers.student_live_quiz_consumer import StudentQuizConsumer

websocket_urlpatterns = [
    path('ws/lobby/<str:join_code>/', LobbyConsumer.as_asgi()),
    path('ws/live-quiz/<str:join_code>/', TutorQuizConsumer.as_asgi()),
    path('ws/student/<str:join_code>/', StudentQuizConsumer.as_asgi()),
]