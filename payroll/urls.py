from django.urls import path
from . import views

urlpatterns = [
    # Salary Advance URLs
    path('advances/', views.advance_list, name='advance_list'),
    path('advances/create/', views.advance_create, name='advance_create'),
    path('advances/<int:pk>/edit/', views.advance_edit, name='advance_edit'),
    path('advances/<int:pk>/approve/', views.advance_approve, name='advance_approve'),
    path('advances/<int:pk>/delete/', views.advance_delete, name='advance_delete'),
    
    # Salary URLs
    path('', views.salary_list, name='salary_list'),
    path('<int:pk>/', views.salary_detail, name='salary_detail'),
    path('create/', views.salary_create, name='salary_create'),
    path('<int:pk>/edit/', views.salary_edit, name='salary_edit'),
    path('<int:pk>/delete/', views.salary_delete, name='salary_delete'),
    path('<int:pk>/mark-as-paid/', views.salary_mark_as_paid, name='salary_mark_as_paid'),
    
    # Payroll Processing
    path('process/', views.process_payroll, name='process_payroll'),
    path('export/', views.export_payroll, name='export_payroll'),
]