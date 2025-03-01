from django.db import models
from employees.models import Employee

class RewardsAndDisciplinary(models.Model):
    TYPE_CHOICES = [
        ('Reward', 'Reward'),
        ('Disciplinary', 'Disciplinary'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    content = models.TextField()
    decision_date = models.DateField()
    decision_number = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    decided_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='decisions_made')
    attached_file = models.FileField(upload_to='rewards_documents/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Rewards and Disciplinary Records'
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.type} - {self.decision_date}"