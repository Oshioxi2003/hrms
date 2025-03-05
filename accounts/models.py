from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('HR', 'HR'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    
    employee_id = models.IntegerField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Employee')
    phone = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=[
            ('Active', 'Active'),
            ('Locked', 'Locked'),
            ('Pending Activation', 'Pending Activation'),
        ],
        default='Active'
    )
    
    class Meta:
        permissions = [
            # Employee Management
            ("view_employee_data", "Can view employee data"),
            ("add_employee_data", "Can add employee data"),
            ("change_employee_data", "Can change employee data"),
            ("delete_employee_data", "Can delete employee data"),
            
            # Contract Management
            ("view_contract", "Can view contract"),
            ("add_contract", "Can add contract"),
            ("change_contract", "Can change contract"),
            ("delete_contract", "Can delete contract"),
            
            # Attendance Management
            ("view_attendance", "Can view attendance"),
            ("add_attendance", "Can add attendance"),
            ("change_attendance", "Can change attendance"),
            ("delete_attendance", "Can delete attendance"),
            
            # Salary Management
            ("view_salary", "Can view salary"),
            ("process_payroll", "Can process payroll"),
            ("manage_advances", "Can manage salary advances"),
            
            # Training Management
            ("view_training", "Can view training"),
            ("add_training", "Can add training"),
            ("change_training", "Can change training"),
            ("delete_training", "Can delete training"),
            
            # Performance Evaluation
            ("view_evaluation", "Can view evaluation"),
            ("add_evaluation", "Can add evaluation"),
            ("change_evaluation", "Can change evaluation"),
            
            # Leave Management
            ("view_leave", "Can view leave requests"),
            ("add_leave", "Can add leave requests"),
            ("approve_leave", "Can approve leave requests"),
            
            # Reward and Discipline
            ("view_reward_discipline", "Can view rewards and disciplines"),
            ("add_reward_discipline", "Can add rewards and disciplines"),
            ("change_reward_discipline", "Can change rewards and disciplines"),
            
            # Reporting
            ("view_reports", "Can view reports"),
            ("generate_reports", "Can generate reports"),
            
            # User Management
            ("manage_users", "Can manage user accounts"),
            ("assign_permissions", "Can assign permissions"),
            
            # Activity History
            ("view_activity_history", "Can view all activity history"),
        ]

class SystemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    object_type = models.CharField(max_length=50, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    ip = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.action} - {self.timestamp}"

class ActivityType(models.TextChoices):
    LOGIN = 'LOGIN', _('Login')
    LOGOUT = 'LOGOUT', _('Logout')
    PROFILE_UPDATE = 'PROFILE_UPDATE', _('Profile Update')
    PASSWORD_CHANGE = 'PASSWORD_CHANGE', _('Password Change')
    FAILED_LOGIN = 'FAILED_LOGIN', _('Failed Login Attempt')
    DATA_ACCESS = 'DATA_ACCESS', _('Data Access')
    DATA_MODIFICATION = 'DATA_MODIFICATION', _('Data Modification')
    REPORT_GENERATION = 'REPORT_GENERATION', _('Report Generation')
    PERMISSION_CHANGE = 'PERMISSION_CHANGE', _('Permission Change')
    SYSTEM_CONFIGURATION = 'SYSTEM_CONFIGURATION', _('System Configuration')
    EMAIL_SENT = 'EMAIL_SENT', _('Email Sent')
    DOCUMENT_DOWNLOAD = 'DOCUMENT_DOWNLOAD', _('Document Download')

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    activity_type = models.CharField(
        max_length=30,
        choices=ActivityType.choices,
        default=ActivityType.DATA_ACCESS
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    browser = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    device = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    module = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=100, null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['module']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else 'Anonymous'
        return f"{username} - {self.get_activity_type_display()} - {self.timestamp}"

    @classmethod
    def log(cls, request=None, user=None, activity_type=None, description=None, 
           module=None, object_id=None, object_type=None, extra_data=None):
        """
        Log a user activity with the given parameters.
        """
        if not user and request and request.user.is_authenticated:
            user = request.user
            
        # Extract browser and OS info from user agent
        browser, os_name, device = cls._parse_user_agent(request.META.get('HTTP_USER_AGENT', '') if request else '')
        
        activity = cls(
            user=user,
            activity_type=activity_type or ActivityType.DATA_ACCESS,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None,
            browser=browser,
            os=os_name,
            device=device,
            description=description,
            module=module,
            object_id=object_id,
            object_type=object_type,
            extra_data=extra_data
        )
        activity.save()
        return activity
    
    @staticmethod
    def _parse_user_agent(user_agent_string):
        """
        Parse user agent string to extract browser, OS and device info
        """
        browser = "Unknown"
        os_name = "Unknown"
        device = "Desktop"
        
        if 'Mobile' in user_agent_string:
            device = "Mobile"
        elif 'Tablet' in user_agent_string:
            device = "Tablet"
            
        # Browser detection
        if 'Firefox' in user_agent_string:
            browser = "Firefox"
        elif 'Chrome' in user_agent_string and 'Edge' not in user_agent_string:
            browser = "Chrome"
        elif 'Safari' in user_agent_string and 'Chrome' not in user_agent_string:
            browser = "Safari"
        elif 'Edge' in user_agent_string:
            browser = "Edge"
        elif 'MSIE' in user_agent_string or 'Trident' in user_agent_string:
            browser = "Internet Explorer"
            
        # OS detection
        if 'Windows' in user_agent_string:
            os_name = "Windows"
        elif 'Mac OS' in user_agent_string:
            os_name = "macOS"
        elif 'Linux' in user_agent_string:
            os_name = "Linux"
        elif 'Android' in user_agent_string:
            os_name = "Android"
        elif 'iOS' in user_agent_string or 'iPhone' in user_agent_string or 'iPad' in user_agent_string:
            os_name = "iOS"
            
        return browser, os_name, device
