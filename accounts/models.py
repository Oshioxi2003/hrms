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