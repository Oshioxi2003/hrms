from django.urls import path
from . import views

urlpatterns = [
    # KPI URLs
    path('kpis/', views.kpi_list, name='kpi_list'),
    path('kpis/create/', views.kpi_create, name='kpi_create'),
    path('kpis/<int:pk>/edit/', views.kpi_edit, name='kpi_edit'),
    path('kpis/<int:pk>/delete/', views.kpi_delete, name='kpi_delete'),
    
    # Evaluation URLs
    path('', views.evaluation_list, name='evaluation_list'),
    path('create/', views.evaluation_create, name='evaluation_create'),
    path('<int:pk>/edit/', views.evaluation_edit, name='evaluation_edit'),
    path('<int:pk>/delete/', views.evaluation_delete, name='evaluation_delete'),
    path('employee/<int:employee_id>/', views.employee_performance, name='employee_performance'),
]