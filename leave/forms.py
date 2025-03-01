from django import forms
from django.utils import timezone
from .models import LeaveRequest
from employees.models import Employee

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'leave_days', 'reason', 'attached_file']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'leave_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If this is an employee user creating their own leave request
        if self.user and self.user.role == 'Employee' and hasattr(self.user, 'employee_id'):
            self.fields['employee'].initial = self.user.employee_id
            self.fields['employee'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after or equal to start date")
            
            # Calculate leave days
            delta = (end_date - start_date).days + 1
            cleaned_data['leave_days'] = delta
        
        return cleaned_data

class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'approval_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'approval_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit status choices to only Approved or Rejected
        self.fields['status'].choices = [
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ]
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.approval_date = timezone.now().date()
        if commit:
            instance.save()
        return instance

class LeaveSearchForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='Working'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    leave_type = forms.ChoiceField(
        choices=[('', 'All')] + list(LeaveRequest.LEAVE_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + list(LeaveRequest.STATUS_CHOICES),
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