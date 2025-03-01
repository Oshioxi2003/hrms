from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_list, name='leave_list'),
    path('create/', views.leave_create, name='leave_create'),
    path('<int:pk>/', views.leave_detail, name='leave_detail'),
    path('<int:pk>/edit/', views.leave_edit, name='leave_edit'),
    path('<int:pk>/cancel/', views.leave_cancel, name='leave_cancel'),
    path('<int:pk>/approve/', views.leave_approve, name='leave_approve'),
]