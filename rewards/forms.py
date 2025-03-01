from django import forms
from django.utils import timezone
from .models import RewardsAndDisciplinary
from employees.models import Employee

class RewardsAndDisciplinaryForm(forms.ModelForm):
    class Meta:
        model = RewardsAndDisciplinary
        fields = [
            'employee', 'type', 'content', 'decision_date', 'decision_number',
            'amount', 'decided_by', 'attached_file', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'decision_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'decision_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'decided_by': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set initial decision date to today
        self.fields['decision_date'].initial = timezone.now().date()
        
        # If user has an employee ID, set decided_by
        if user and hasattr(user, 'employee_id') and user.employee_id:
            self.fields['decided_by'].initial = user.employee_id

class RewardSearchForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='Working'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    type = forms.ChoiceField(
        choices=[('', 'All')] + list(RewardsAndDisciplinary.TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )