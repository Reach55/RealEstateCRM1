from django.urls import path

from . import views


urlpatterns = [
    path('', views.agent_report, name='agent_report'),
]
