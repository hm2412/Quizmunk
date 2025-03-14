from django.urls import path
from app.consumers.lobby_consumer import LobbyConsumer
from app.consumers.student_quiz_consumer import StudentQuizConsumer
from app.consumers.tutor_live_quiz_consumer import TutorQuizConsumer

websocket_urlpatterns = [
    path('ws/lobby/<str:join_code>/', LobbyConsumer.as_asgi()),
    path('ws/student/<str:room_code>/', StudentQuizConsumer.as_asgi()),
    path('ws/tutor/<str:room_code>/', TutorQuizConsumer.as_asgi()),
]

