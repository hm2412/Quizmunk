from django.urls import path
from app.consumers.lobby_consumer import LobbyConsumer
from app.consumers.live_quiz_consumer import QuizConsumer

websocket_urlpatterns = [
    path("ws/lobby/<str:join_code>/", LobbyConsumer.as_asgi()),
    path("ws/live-quiz/", QuizConsumer.as_asgi()),
]