from django import forms
from django.forms import modelformset_factory
from django.utils import timezone
from .models import WorkShift, ShiftAssignment, Attendance
from employees.models import Employee

class WorkShiftForm(forms.ModelForm):
    class Meta:
        model = WorkShift
        fields = ['shift_name', 'start_time', 'end_time', 'salary_coefficient', 'description', 'status']
        widgets = {
            'shift_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'salary_coefficient': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ShiftAssignmentForm(forms.ModelForm):
    class Meta:
        model = ShiftAssignment
        fields = ['employee', 'shift', 'effective_date', 'end_date', 'notes', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'work_date', 'time_in', 'time_out', 'shift', 'notes', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'work_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class AttendanceSearchForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='Working'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + list(Attendance.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class BulkAttendanceForm(forms.Form):
    work_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now().date
    )
    
    def __init__(self, *args, **kwargs):
        employees = kwargs.pop('employees', Employee.objects.filter(status='Working'))
        super().__init__(*args, **kwargs)
        
        for employee in employees:
            field_name = f'status_{employee.id}'
            self.fields[field_name] = forms.ChoiceField(
                choices=Attendance.STATUS_CHOICES,
                initial='Present',
                widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
            )
            
            field_name = f'time_in_{employee.id}'
            self.fields[field_name] = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={'class': 'form-control form-control-sm', 'type': 'time'})
            )
            
            field_name = f'time_out_{employee.id}'
            self.fields[field_name] = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={'class': 'form-control form-control-sm', 'type': 'time'})
            )
            
            field_name = f'shift_{employee.id}'
            self.fields[field_name] = forms.ModelChoiceField(
                queryset=WorkShift.objects.filter(status=True),
                required=False,
                widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
            )
            
            field_name = f'notes_{employee.id}'
            self.fields[field_name] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
            )