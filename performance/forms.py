from django import forms
from django.utils import timezone
from .models import KPI, EmployeeEvaluation
from employees.models import Employee

class KPIForm(forms.ModelForm):
    class Meta:
        model = KPI
        fields = [
            'kpi_name', 'description', 'unit', 'min_target', 
            'max_target', 'weight_factor', 'kpi_type'
        ]
        widgets = {
            'kpi_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'min_target': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_target': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'weight_factor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1'}),
            'kpi_type': forms.Select(attrs={'class': 'form-select'}),
        }

class EmployeeEvaluationForm(forms.ModelForm):
    class Meta:
        model = EmployeeEvaluation
        fields = [
            'employee', 'kpi', 'month', 'year', 'result', 
            'target', 'feedback', 'evaluated_by'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'kpi': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000}),
            'result': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'target': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'evaluated_by': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set initial month and year
        today = timezone.now()
        self.fields['month'].initial = today.month
        self.fields['year'].initial = today.year
        
        # If user has an employee ID, set evaluated_by
        if user and hasattr(user, 'employee_id') and user.employee_id:
            self.fields['evaluated_by'].initial = user.employee_id

class EvaluationSearchForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='Working'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    kpi = forms.ModelChoiceField(
        queryset=KPI.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    month = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12})
    )
    year = forms.IntegerField(
        required=False,
        min_value=2000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 2000})
    )