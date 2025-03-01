from django import forms
from .models import Department, Position, EducationLevel, Employee, EmploymentContract, InsuranceAndTax

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'department_code', 'description', 'status']
        widgets = {
            'department_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department_code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['position_name', 'position_code', 'description', 'status']
        widgets = {
            'position_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position_code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EducationLevelForm(forms.ModelForm):
    class Meta:
        model = EducationLevel
        fields = ['education_name', 'education_code', 'description']
        widgets = {
            'education_name': forms.TextInput(attrs={'class': 'form-control'}),
            'education_code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'full_name', 'date_of_birth', 'gender', 'id_card', 'email', 'phone', 
            'address', 'department', 'position', 'education', 'hire_date', 
            'profile_image', 'status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'id_card': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class EmploymentContractForm(forms.ModelForm):
    class Meta:
        model = EmploymentContract
        fields = [
            'employee', 'contract_type', 'start_date', 'end_date', 'base_salary',
            'allowance', 'attached_file', 'sign_date', 'signed_by', 'notes', 'status'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'allowance': forms.NumberInput(attrs={'class': 'form-control'}),
            'sign_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'signed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class InsuranceAndTaxForm(forms.ModelForm):
    class Meta:
        model = InsuranceAndTax
        fields = [
            'employee', 'social_insurance_number', 'social_insurance_date',
            'social_insurance_place', 'health_insurance_number', 'health_insurance_date',
            'health_insurance_place', 'health_care_provider', 'tax_code', 'status'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'social_insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
            'social_insurance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'social_insurance_place': forms.TextInput(attrs={'class': 'form-control'}),
            'health_insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
            'health_insurance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'health_insurance_place': forms.TextInput(attrs={'class': 'form-control'}),
            'health_care_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_code': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }