from django.db import models
from employees.models import Employee

class TrainingCourse(models.Model):
    STATUS_CHOICES = [
        ('Preparing', 'Preparing'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200, blank=True, null=True)
    cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    organizer = models.CharField(max_length=100, blank=True, null=True)
    supervisor = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Preparing')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course_name} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after or equal to start date")
        super().clean()

class TrainingParticipation(models.Model):
    STATUS_CHOICES = [
        ('Registered', 'Registered'),
        ('Participating', 'Participating'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    registration_date = models.DateField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    achievement = models.CharField(max_length=100, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    certificate = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Registered')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'course']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.course.course_name}"