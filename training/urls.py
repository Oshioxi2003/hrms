from django.urls import path
from . import views

urlpatterns = [
    # Training Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Training Participation URLs
    path('', views.participation_list, name='participation_list'),
    path('create/', views.participation_create, name='participation_create'),
    path('<int:pk>/edit/', views.participation_edit, name='participation_edit'),
    path('<int:pk>/delete/', views.participation_delete, name='participation_delete'),
    path('bulk/', views.bulk_participation, name='bulk_participation'),
]