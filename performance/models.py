from django.db import models
from employees.models import Employee

class KPI(models.Model):
    KPI_TYPES = [
        ('Individual', 'Individual'),
        ('Department', 'Department'),
        ('Company', 'Company'),
    ]
    
    kpi_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    min_target = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_target = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight_factor = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    kpi_type = models.CharField(max_length=20, choices=KPI_TYPES, default='Individual')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.kpi_name

class EmployeeEvaluation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)
    month = models.IntegerField(help_text="Month (1-12)")
    year = models.IntegerField()
    result = models.DecimalField(max_digits=10, decimal_places=2)
    target = models.DecimalField(max_digits=10, decimal_places=2)
    achievement_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    evaluation_date = models.DateField(auto_now_add=True)
    evaluated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations_given')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'kpi', 'month', 'year']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.kpi.kpi_name} - {self.month}/{self.year}"
    
    def save(self, *args, **kwargs):
        # Calculate achievement rate if not provided
        if self.result and self.target and self.achievement_rate is None:
            self.achievement_rate = (self.result / self.target) * 100
        super().save(*args, **kwargs)