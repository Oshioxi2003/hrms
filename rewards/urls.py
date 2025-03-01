from django.urls import path
from . import views

urlpatterns = [
    path('', views.reward_list, name='reward_list'),
    path('create/', views.reward_create, name='reward_create'),
    path('<int:pk>/edit/', views.reward_edit, name='reward_edit'),
    path('<int:pk>/delete/', views.reward_delete, name='reward_delete'),
]