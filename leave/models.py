from django.db import models
from django.core.exceptions import ValidationError
from employees.models import Employee

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('Annual Leave', 'Annual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Maternity Leave', 'Maternity Leave'),
        ('Personal Leave', 'Personal Leave'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_days = models.DecimalField(max_digits=3, decimal_places=1)
    reason = models.TextField(blank=True, null=True)
    attached_file = models.FileField(upload_to='leave_documents/', blank=True, null=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approval_date = models.DateField(null=True, blank=True)
    approval_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} - {self.start_date} to {self.end_date}"
    
    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after or equal to start date")
        
        # Calculate leave days if not provided
        if self.start_date and self.end_date and not self.leave_days:
            # Simple calculation, not accounting for weekends or holidays
            delta = (self.end_date - self.start_date).days + 1
            self.leave_days = delta
        
        super().clean()