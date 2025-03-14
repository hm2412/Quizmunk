from django.urls import path
from app.consumers import LobbyConsumer, StudentQuizConsumer

websocket_urlpatterns = [
    path('ws/lobby/<str:join_code>/', LobbyConsumer.as_asgi()),
    path('ws/student/<str:room_code>/', StudentQuizConsumer.as_asgi()),
    #path('ws/tutor/<str:room_code>/', TutorQuizConsumer.as_asgi()),
    
]

