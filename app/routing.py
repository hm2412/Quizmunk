from django.urls import path, re_path
from app.consumers import QuizConsumer

websocket_urlpatterns = [
    path('ws/lobby/<str:join_code>/', QuizConsumer.as_asgi()),
    path('ws/student/<str:join_code>/', QuizConsumer.as_asgi()),
    path('ws/live-quiz/<str:join_code>/', QuizConsumer.as_asgi()),
    #re_path(r'ws/live-quiz/(?P<join_code>\w+)/$', QuizConsumer.as_asgi()),
    #path('ws/tutor/<str:room_code>/', TutorQuizConsumer.as_asgi()),
    
]