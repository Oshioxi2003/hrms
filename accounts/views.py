from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import UserRegistrationForm, CustomLoginForm, CustomPasswordResetForm, UserProfileForm, UserManagementForm
from .models import User, SystemLog

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        # Log user login
        user = form.get_user()
        SystemLog.objects.create(
            user=user,
            action="Login",
            ip=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
        )
        return super().form_valid(form)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add user to Employee group by default
            employee_group = Group.objects.get(name='Employee')
            user.groups.add(employee_group)
            # Log user registration
            SystemLog.objects.create(
                action="User Registration",
                details=f"User {user.username} registered",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, 'Account created successfully. You can now login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_list(request):
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_create(request):
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set a default password
            user.set_password('hrms@123')
            user.save()
            # Add user to appropriate group based on role
            group = Group.objects.get(name=user.role)
            user.groups.add(group)
            # Log user creation
            SystemLog.objects.create(
                user=request.user,
                action="User Creation",
                object_type="User",
                object_id=user.id,
                details=f"Created user {user.username} with role {user.role}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'User {user.username} has been created successfully!')
            return redirect('user_list')
    else:
        form = UserManagementForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})

@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save()
            # Update user group if role has changed
            updated_user.groups.clear()
            group = Group.objects.get(name=updated_user.role)
            updated_user.groups.add(group)
            # Log user update
            SystemLog.objects.create(
                user=request.user,
                action="User Update",
                object_type="User",
                object_id=updated_user.id,
                details=f"Updated user {updated_user.username}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'User {updated_user.username} has been updated successfully!')
            return redirect('user_list')
    else:
        form = UserManagementForm(instance=user)
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User', 'user': user})

@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        # Log user deletion
        SystemLog.objects.create(
            user=request.user,
            action="User Deletion",
            object_type="User",
            details=f"Deleted user {user.username}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        username = user.username
        user.delete()
        messages.success(request, f'User {username} has been deleted successfully!')
        return redirect('user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

@login_required
def dashboard(request):
    # Get statistics for dashboard
    from employees.models import Employee
    from attendance.models import Attendance
    from leave.models import LeaveRequest
    from django.utils import timezone
    
    today = timezone.now().date()
    
    # Get employee stats
    total_employees = Employee.objects.filter(status='Working').count()
    
    # Get attendance stats for today
    present_today = Attendance.objects.filter(work_date=today, status='Present').count()
    on_leave = Attendance.objects.filter(work_date=today, status='On Leave').count()
    
    # Get pending leave requests
    pending_leave = LeaveRequest.objects.filter(status='Pending').count()
    
    # Get recent employees
    recent_employees = Employee.objects.all().order_by('-created_date')[:5]
    
    # Get pending leave requests for display
    pending_leave_requests = LeaveRequest.objects.filter(status='Pending').order_by('-created_date')[:5]
    
    # Get recent activities
    recent_activities = SystemLog.objects.all().order_by('-timestamp')[:10]
    
    context = {
        'total_employees': total_employees,
        'present_today': present_today,
        'on_leave': on_leave,
        'pending_leave': pending_leave,
        'recent_employees': recent_employees,
        'pending_leave_requests': pending_leave_requests,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'dashboard.html', context)