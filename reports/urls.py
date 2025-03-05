from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('employee-report/', views.employee_report, name='employee_report'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),
    path('leave-report/', views.leave_report, name='leave_report'),
    path('salary-report/', views.salary_report, name='salary_report'),
    path('performance-report/', views.performance_report, name='performance_report'),

    path('report_dashboard', views.report_dashboard, name='report_dashboard'),
    path('employees/', views.employee_report, name='employee_report'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('leave/', views.leave_report, name='leave_report'),
    path('salary/', views.salary_report, name='salary_report'),
    path('performance/', views.performance_report, name='performance_report'),
]