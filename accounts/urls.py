from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Existing URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Email verification URLs
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('verify/resend/', views.resend_verification_email, name='resend_verification'),
    
    # Activity history URLs
    path('activity/', views.my_activity_history, name='my_activity_history'),
    path('activity/all/', views.activity_history, name='activity_history'),
    path('activity/user/<int:user_id>/', views.user_activity_history, name='user_activity_history'),
    path('activity/detail/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    
    # Password reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/reset/password_reset_done.html'), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        views.CustomPasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/reset/password_reset_complete.html'), 
        name='password_reset_complete'),
]