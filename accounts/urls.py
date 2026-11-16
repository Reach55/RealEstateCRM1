from django.urls import path ,include
from . import views

urlpatterns = [
    # Login and logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # User management
    path('', views.user_list, name='user_list'),
    path('add/', views.user_add, name='user_add'),
    path('edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('delete/<int:pk>/', views.user_delete, name='user_delete'),
]