from django.db import models
from django.core.exceptions import ValidationError
from employees.models import Employee

class WorkShift(models.Model):
    shift_name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    salary_coefficient = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True, help_text='1: Active, 0: Inactive')
    
    def __str__(self):
        return f"{self.shift_name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        super().clean()

class ShiftAssignment(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Ended', 'Ended'),
        ('Cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(WorkShift, on_delete=models.CASCADE)
    assignment_date = models.DateField(auto_now_add=True)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'shift', 'effective_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.shift.shift_name} - {self.effective_date}"
    
    def clean(self):
        if self.effective_date and self.end_date and self.effective_date >= self.end_date:
            raise ValidationError("End date must be after effective date")
        super().clean()

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('On Leave', 'On Leave'),
        ('Absent', 'Absent'),
        ('Holiday', 'Holiday'),
        ('Business Trip', 'Business Trip'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    work_date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    shift = models.ForeignKey(WorkShift, on_delete=models.SET_NULL, null=True, blank=True)
    actual_work_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Present')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'work_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.work_date} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Calculate actual work hours if time_in and time_out are provided
        if self.time_in and self.time_out:
            time_in_hours = self.time_in.hour + self.time_in.minute / 60
            time_out_hours = self.time_out.hour + self.time_out.minute / 60
            
            # If time_out is earlier than time_in, assume it's the next day
            if time_out_hours < time_in_hours:
                time_out_hours += 24
                
            self.actual_work_hours = round(time_out_hours - time_in_hours, 2)
            
            # Calculate overtime if a shift is assigned
            if self.shift:
                shift_start_hours = self.shift.start_time.hour + self.shift.start_time.minute / 60
                shift_end_hours = self.shift.end_time.hour + self.shift.end_time.minute / 60
                
                # If shift end is earlier than shift start, assume it spans midnight
                if shift_end_hours < shift_start_hours:
                    shift_end_hours += 24
                
                standard_hours = shift_end_hours - shift_start_hours
                
                if self.actual_work_hours > standard_hours:
                    self.overtime_hours = round(self.actual_work_hours - standard_hours, 2)
        
        super().save(*args, **kwargs)