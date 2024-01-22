# myapp/urls.py
from django.urls import path
from .views import predict


urlpatterns = [
    path('proses', predict.as_view()),
]
