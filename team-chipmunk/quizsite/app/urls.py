from django.urls import path
from .views.homepage_view import homepage

urlpatterns = [
    path('', homepage, name='homepage'),
]
