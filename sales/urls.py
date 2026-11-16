from django.urls import path
from . import views

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('add/', views.sale_add, name='sale_add'),
    path('edit/<int:pk>/', views.sale_edit, name='sale_edit'),
    path('delete/<int:pk>/', views.sale_delete, name='sale_delete'),
]