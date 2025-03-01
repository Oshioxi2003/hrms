from django.db import models
from django.utils import timezone

class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True, help_text='1: Active, 0: Inactive')
    
    def __str__(self):
        return self.department_name

class Position(models.Model):
    position_name = models.CharField(max_length=100)
    position_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True, help_text='1: Active, 0: Inactive')
    
    def __str__(self):
        return self.position_name

class EducationLevel(models.Model):
    education_name = models.CharField(max_length=100)
    education_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.education_name

class Employee(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Working', 'Working'),
        ('Resigned', 'Resigned'),
        ('On Leave', 'On Leave'),
    ]
    
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    id_card = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    education = models.ForeignKey(EducationLevel, on_delete=models.SET_NULL, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='employees/profiles/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Working')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.full_name
    
    @property
    def has_user_account(self):
        from accounts.models import User
        return User.objects.filter(employee_id=self.id).exists()

class EmploymentContract(models.Model):
    CONTRACT_TYPES = [
        ('Probation', 'Probation'),
        ('Fixed-term', 'Fixed-term'),
        ('Indefinite-term', 'Indefinite-term'),
        ('Seasonal', 'Seasonal'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Terminated', 'Terminated'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    base_salary = models.DecimalField(max_digits=15, decimal_places=2)
    allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    attached_file = models.FileField(upload_to='contracts/', null=True, blank=True)
    sign_date = models.DateField(null=True, blank=True)
    signed_by = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.contract_type} - {self.start_date}"

class InsuranceAndTax(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    social_insurance_number = models.CharField(max_length=20, null=True, blank=True)
    social_insurance_date = models.DateField(null=True, blank=True)
    social_insurance_place = models.CharField(max_length=100, null=True, blank=True)
    health_insurance_number = models.CharField(max_length=20, null=True, blank=True)
    health_insurance_date = models.DateField(null=True, blank=True)
    health_insurance_place = models.CharField(max_length=100, null=True, blank=True)
    health_care_provider = models.CharField(max_length=100, null=True, blank=True)
    tax_code = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - Insurance & Tax"