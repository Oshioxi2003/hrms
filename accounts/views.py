from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import UserRegistrationForm, CustomLoginForm, CustomPasswordResetForm, UserProfileForm, UserManagementForm
from .models import User, SystemLog, UserActivity, ActivityType
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
import threading

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        # Log user login
        user = form.get_user()
        
        # Log in the existing SystemLog
        SystemLog.objects.create(
            user=user,
            action="Login",
            ip=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
        )
        
        # Also log in the new UserActivity system
        UserActivity.log(
            request=self.request,
            user=user,
            activity_type=ActivityType.LOGIN,
            description=f"User {user.username} logged in",
            module="accounts"
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Log failed login attempts
        username = form.cleaned_data.get('username', '')
        if username:
            UserActivity.log(
                request=self.request,
                user=None,
                activity_type=ActivityType.FAILED_LOGIN,
                description=f"Failed login attempt for username: {username}",
                module="accounts",
                extra_data={'username': username}
            )
        
        return super().form_invalid(form)
    
class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Log the logout action
            UserActivity.log(
                request=request,
                user=request.user,
                activity_type=ActivityType.LOGOUT,
                description=f"User {request.user.username} logged out",
                module="accounts"
            )
        
        # Proceed with standard logout
        return super().dispatch(request, *args, **kwargs)


from django.contrib.auth.tokens import PasswordResetTokenGenerator
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )
account_activation_token = TokenGenerator()

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=False)


def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('accounts/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    to_email = user.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.content_subtype = "html"
    EmailThread(email).start()
    
    # Log email activity
    UserActivity.log(
        request=request,
        user=None,  # No user is logged in during registration
        activity_type=ActivityType.EMAIL_SENT,
        description=f"Verification email sent to {to_email}",
        module="accounts",
        object_type="User",
        object_id=user.id,
        extra_data={'email_type': 'activation'}
    )


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Save user but mark as inactive until email verification
                user = form.save(commit=False)
                user.is_active = False  # Deactivate account till it is confirmed
                user.save()
                
                # Add user to Employee group by default
                employee_group, created = Group.objects.get_or_create(name='Employee')
                user.groups.add(employee_group)
                
                # Send activation email
                send_activation_email(request, user)
                
                # Log user registration
                SystemLog.objects.create(
                    action="User Registration",
                    details=f"User {user.username} registered (pending activation)",
                    ip=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                # Redirect to pending verification page
                return render(request, 'accounts/verification/pending.html', {'email': user.email})
            except Exception as e:
                # Log the error
                print(f"Registration error: {str(e)}")
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            # Form is not valid, errors will be displayed
            pass
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate Your Account'
    message = render_to_string('accounts/verification/email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    to_email = user.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.content_subtype = "html"
    EmailThread(email).start()

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        # Check if already verified
        if user.is_active:
            return render(request, 'accounts/verification/already_verified.html')
            
        user.is_active = True
        user.save()
        
        # Log successful account activation
        SystemLog.objects.create(
            user=user,
            action="Account Activation",
            details=f"User {user.username} activated their account",
            ip=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None
        )
        
        # Log in UserActivity
        UserActivity.log(
            request=request,
            user=user,
            activity_type=ActivityType.DATA_MODIFICATION,
            description=f"Account activated for {user.username}",
            module="accounts",
            object_type="User",
            object_id=user.id
        )
        
        return render(request, 'accounts/verification/success.html')
    else:
        return render(request, 'accounts/verification/failed.html')

def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Check if already verified
            if user.is_active:
                return render(request, 'accounts/verification/already_verified.html')
                
            # Send new verification email
            send_activation_email(request, user)
            
            # Log resend action
            SystemLog.objects.create(
                action="Resend Verification Email",
                details=f"Verification email resent to {email}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            # Log in UserActivity
            UserActivity.log(
                request=request,
                user=None,
                activity_type=ActivityType.EMAIL_SENT,
                description=f"Verification email resent to {email}",
                module="accounts",
                object_type="User",
                object_id=user.id,
                extra_data={'email_type': 'activation_resend'}
            )
            
            return render(request, 'accounts/verification/email_sent.html', {'email': email})
        except User.DoesNotExist:
            messages.error(request, "No account found with this email address.")
    
    return render(request, 'accounts/verification/resend.html')

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/reset/password_reset_form.html'
    email_template_name = 'accounts/reset/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        # Get the email
        email = form.cleaned_data.get('email', '')
        
        # Log the password reset request
        UserActivity.log(
            request=self.request,
            user=None,
            activity_type=ActivityType.PASSWORD_CHANGE,
            description=f"Password reset requested for email: {email}",
            module="accounts",
            extra_data={'email': email, 'action': 'request_reset'}
        )
        
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/reset/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        # Log the password reset completion
        UserActivity.log(
            request=self.request,
            user=self.user,
            activity_type=ActivityType.PASSWORD_CHANGE,
            description=f"Password reset completed for user: {self.user.username}",
            module="accounts",
            object_type="User",
            object_id=self.user.id,
            extra_data={'action': 'complete_reset'}
        )
        
        return super().form_valid(form)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            
            # Log profile update
            UserActivity.log(
                request=request,
                user=request.user,
                activity_type=ActivityType.PROFILE_UPDATE,
                description=f"User {request.user.username} updated their profile",
                module="accounts",
                object_type="User",
                object_id=request.user.id
            )
            
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
            with transaction.atomic():
                user = form.save(commit=False)
                # Set a default password
                user.set_password('hrms@123')
                user.save()
                
                # Add user to appropriate group based on role
                try:
                    group = Group.objects.get(name=user.role)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    # Run the setup_groups command to create the groups if they don't exist
                    from django.core.management import call_command
                    call_command('setup_groups')
                    
                    # Try again to add the user to the group
                    try:
                        group = Group.objects.get(name=user.role)
                        user.groups.add(group)
                    except Group.DoesNotExist:
                        # If still fails, create just this group
                        group = Group.objects.create(name=user.role)
                        user.groups.add(group)
                        messages.warning(request, f"Group '{user.role}' was created but permissions need to be set up. Please run 'python manage.py setup_groups'.")
                
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
                
                # Log in UserActivity
                UserActivity.log(
                    request=request,
                    user=request.user,
                    activity_type=ActivityType.DATA_MODIFICATION,
                    description=f"Created user {user.username} with role {user.role}",
                    module="accounts",
                    object_type="User",
                    object_id=user.id,
                    extra_data={'role': user.role}
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
            with transaction.atomic():
                updated_user = form.save()
                # Update user group if role has changed
                updated_user.groups.clear()
                
                try:
                    group = Group.objects.get(name=updated_user.role)
                    updated_user.groups.add(group)
                except Group.DoesNotExist:
                    # Run the setup_groups command to create the groups if they don't exist
                    from django.core.management import call_command
                    call_command('setup_groups')
                    
                    # Try again to add the user to the group
                    try:
                        group = Group.objects.get(name=updated_user.role)
                        updated_user.groups.add(group)
                    except Group.DoesNotExist:
                        # If still fails, create just this group
                        group = Group.objects.create(name=updated_user.role)
                        updated_user.groups.add(group)
                        messages.warning(request, f"Group '{updated_user.role}' was created but permissions need to be set up. Please run 'python manage.py setup_groups'.")
                
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
                
                # Log in UserActivity
                UserActivity.log(
                    request=request,
                    user=request.user,
                    activity_type=ActivityType.DATA_MODIFICATION,
                    description=f"Updated user {updated_user.username}",
                    module="accounts",
                    object_type="User",
                    object_id=updated_user.id,
                    extra_data={'role': updated_user.role}
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
        
        # Log in UserActivity before deleting the user
        UserActivity.log(
            request=request,
            user=request.user,
            activity_type=ActivityType.DATA_MODIFICATION,
            description=f"Deleted user {user.username}",
            module="accounts",
            extra_data={'deleted_username': user.username}
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




@login_required
def my_activity_history(request):
    """View for users to see their own activity history"""
    activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        activities = activities.filter(
            Q(description__icontains=query) |
            Q(module__icontains=query) |
            Q(activity_type__icontains=query)
        )
        
    # Filter by activity type
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
        
    # Pagination
    paginator = Paginator(activities, 25)  # Show 25 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'activity_types': ActivityType.choices,
        'selected_type': activity_type,
        'query': query,
    }
    
    return render(request, 'accounts/activity/my_activity_history.html', context)

@login_required
@permission_required('accounts.view_activity_history', raise_exception=True)
def activity_history(request):
    """Admin view to see all user activity"""
    activities = UserActivity.objects.all().select_related('user').order_by('-timestamp')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        activities = activities.filter(
            Q(user__username__icontains=query) |
            Q(description__icontains=query) |
            Q(module__icontains=query) |
            Q(ip_address__icontains=query) |
            Q(activity_type__icontains=query)
        )
        
    # Filter by activity type
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
        
    # Filter by user
    user_id = request.GET.get('user_id')
    if user_id:
        activities = activities.filter(user_id=user_id)
        
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        activities = activities.filter(timestamp__gte=start_date)
    if end_date:
        activities = activities.filter(timestamp__lte=end_date)
        
    # Pagination
    paginator = Paginator(activities, 50)  # Show 50 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'activity_types': ActivityType.choices,
        'selected_type': activity_type,
        'selected_user_id': user_id,
        'start_date': start_date,
        'end_date': end_date,
        'query': query,
    }
    
    return render(request, 'accounts/activity/activity_history.html', context)

@login_required
@permission_required('accounts.view_activity_history', raise_exception=True)
def user_activity_history(request, user_id):
    """View to see activity history for a specific user"""
    user = get_object_or_404(User, pk=user_id)
    activities = UserActivity.objects.filter(user=user).order_by('-timestamp')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        activities = activities.filter(
            Q(description__icontains=query) |
            Q(module__icontains=query) |
            Q(activity_type__icontains=query)
        )
        
    # Filter by activity type
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
        
    # Pagination
    paginator = Paginator(activities, 25)  # Show 25 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user_obj': user,
        'page_obj': page_obj,
        'activity_types': ActivityType.choices,
        'selected_type': activity_type,
        'query': query,
    }
    
    return render(request, 'accounts/activity/user_activity_history.html', context)

@login_required
def activity_detail(request, activity_id):
    """View to see detailed information about a specific activity"""
    # Check permissions - users can only view their own activities unless they have the view_activity_history permission
    activity = get_object_or_404(UserActivity, pk=activity_id)
    
    if activity.user != request.user and not request.user.has_perm('accounts.view_activity_history'):
        messages.error(request, "You don't have permission to view this activity.")
        return redirect('my_activity_history')
    
    return render(request, 'accounts/activity/activity_detail.html', {'activity': activity})