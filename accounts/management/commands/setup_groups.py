from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import User

class Command(BaseCommand):
    help = 'Create default permission groups'

    def handle(self, *args, **options):
        # Create Admin group
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Admin group created'))
        
        # Create HR group
        hr_group, created = Group.objects.get_or_create(name='HR')
        if created:
            self.stdout.write(self.style.SUCCESS('HR group created'))
        
        # Create Manager group
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            self.stdout.write(self.style.SUCCESS('Manager group created'))
        
        # Create Employee group
        employee_group, created = Group.objects.get_or_create(name='Employee')
        if created:
            self.stdout.write(self.style.SUCCESS('Employee group created'))
        
        # Get content type for User model
        content_type = ContentType.objects.get_for_model(User)
        
        # Get all permissions
        permissions = Permission.objects.filter(content_type=content_type)
        
        # Admin gets all permissions
        admin_permissions = permissions
        admin_group.permissions.set(admin_permissions)
        self.stdout.write(self.style.SUCCESS('Admin permissions set'))
        
        # HR permissions
        hr_permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                'view_employee_data', 'add_employee_data', 'change_employee_data', 'delete_employee_data',
                'view_contract', 'add_contract', 'change_contract', 'delete_contract',
                'view_attendance', 'add_attendance', 'change_attendance',
                'view_salary', 'process_payroll', 'manage_advances',
                'view_training', 'add_training', 'change_training',
                'view_evaluation', 'add_evaluation', 'change_evaluation',
                'view_leave', 'approve_leave',
                'view_reward_discipline', 'add_reward_discipline', 'change_reward_discipline',
                'view_reports', 'generate_reports',
            ]
        )
        hr_group.permissions.set(hr_permissions)
        self.stdout.write(self.style.SUCCESS('HR permissions set'))
        
        # Manager permissions
        manager_permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                'view_employee_data',
                'view_attendance', 'add_attendance', 'change_attendance',
                'view_training', 'add_training',
                'view_evaluation', 'add_evaluation', 'change_evaluation',
                'view_leave', 'approve_leave',
                'view_reward_discipline', 'add_reward_discipline',
                'view_reports',
            ]
        )
        manager_group.permissions.set(manager_permissions)
        self.stdout.write(self.style.SUCCESS('Manager permissions set'))
        
        # Employee permissions
        employee_permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                'view_leave', 'add_leave',
            ]
        )
        employee_group.permissions.set(employee_permissions)
        self.stdout.write(self.style.SUCCESS('Employee permissions set'))