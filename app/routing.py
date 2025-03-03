from django.urls import path, re_path
from app.consumers.lobby_consumer import LobbyConsumer

from app.consumers.live_quiz_consumer import QuizConsumer
from app.consumers.student_quiz_consumer import StudentQuizConsumer

websocket_urlpatterns = [
    path('ws/lobby/<str:join_code>/', LobbyConsumer.as_asgi()),
    path('ws/live-quiz/<str:join_code>/', QuizConsumer.as_asgi()),  # Replaced re_path with path
]

