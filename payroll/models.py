from django.db import models
from django.core.validators import MinValueValidator
from employees.models import Employee
from attendance.models import Attendance

class SalaryAdvance(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Repaid', 'Repaid'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    advance_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.TextField(blank=True, null=True)
    deduction_month = models.IntegerField(validators=[MinValueValidator(1)], help_text="Month (1-12)")
    deduction_year = models.IntegerField(validators=[MinValueValidator(2000)])
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_advances')
    approval_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.amount} - {self.advance_date}"

class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.IntegerField(validators=[MinValueValidator(1)], help_text="Month (1-12)")
    year = models.IntegerField(validators=[MinValueValidator(2000)])
    work_days = models.IntegerField(default=0)
    leave_days = models.IntegerField(default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    base_salary = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    income_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    social_insurance = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    health_insurance = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    unemployment_insurance = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    advance = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    net_salary = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'month', 'year']
        verbose_name_plural = 'Salaries'
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year} - {self.net_salary}"
    
    def save(self, *args, **kwargs):
        # Calculate net salary if not already calculated
        if self.net_salary == 0:
            total_earnings = self.base_salary + self.allowance + self.bonus
            total_deductions = (
                self.income_tax + 
                self.social_insurance + 
                self.health_insurance + 
                self.unemployment_insurance + 
                self.deductions + 
                self.advance
            )
            self.net_salary = total_earnings - total_deductions
        super().save(*args, **kwargs)