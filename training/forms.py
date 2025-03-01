from django import forms
from .models import TrainingCourse, TrainingParticipation
from employees.models import Employee

class TrainingCourseForm(forms.ModelForm):
    class Meta:
        model = TrainingCourse
        fields = [
            'course_name', 'description', 'start_date', 'end_date', 
            'location', 'cost', 'organizer', 'supervisor', 'status'
        ]
        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'organizer': forms.TextInput(attrs={'class': 'form-control'}),
            'supervisor': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class TrainingParticipationForm(forms.ModelForm):
    class Meta:
        model = TrainingParticipation
        fields = ['employee', 'course', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class ParticipationUpdateForm(forms.ModelForm):
    class Meta:
        model = TrainingParticipation
        fields = ['score', 'achievement', 'feedback', 'certificate', 'status']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'achievement': forms.TextInput(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'certificate': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class BulkParticipationForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=TrainingCourse.objects.filter(status__in=['Preparing', 'In Progress']),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employees = Employee.objects.filter(status='Working')
        
        for employee in employees:
            field_name = f'employee_{employee.id}'
            self.fields[field_name] = forms.BooleanField(
                required=False,
                label=employee.full_name,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )