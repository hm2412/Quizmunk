from django.urls import re_path
from app.consumers.lobby_consumer import LobbyConsumer
from app.consumers.live_quiz_consumer import QuizConsumer

websocket_urlpatterns = [
    re_path(r"ws/lobby/(?P<join_code>\w+)/$", LobbyConsumer.as_asgi()),
    re_path(r"ws/live-quiz/(?P<join_code>\w+)/$", QuizConsumer.as_asgi()),
]