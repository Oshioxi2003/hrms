from django import forms
from .models import Department, Position, EducationLevel, Employee, EmploymentContract, InsuranceAndTax
from django.db.models import Q

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'department_code', 'description', 'status']
        widgets = {
            'department_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department name'}),
            'department_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left empty', 'readonly': False}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department description'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = "Active"
        self.fields['status'].help_text = "Inactive departments won't appear in employee forms"
        
        # Make department_code readonly if editing an existing department
        if self.instance and self.instance.pk:
            self.fields['department_code'].widget.attrs['readonly'] = True

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['position_name', 'position_code', 'description', 'status']
        widgets = {
            'position_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter position name'}),
            'position_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left empty', 'readonly': False}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Position description'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = "Active"
        self.fields['status'].help_text = "Inactive positions won't appear in employee forms"
        
        # Make position_code readonly if editing an existing position
        if self.instance and self.instance.pk:
            self.fields['position_code'].widget.attrs['readonly'] = True

class EducationLevelForm(forms.ModelForm):
    class Meta:
        model = EducationLevel
        fields = ['education_name', 'education_code', 'description']  # Removed status field
        widgets = {
            'education_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter education level name'}),
            'education_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left empty', 'readonly': False}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Education level description'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make education_code readonly if editing an existing education level
        if self.instance and self.instance.pk:
            self.fields['education_code'].widget.attrs['readonly'] = True

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'full_name', 'date_of_birth', 'gender', 'id_card', 'email', 'phone', 
            'address', 'department', 'position', 'education', 'hire_date', 
            'profile_image', 'status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'id_card': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID card number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter to only show active departments and positions
        # If editing an existing employee, include their current selections even if inactive
        if self.instance and self.instance.pk:
            current_dept_id = self.instance.department_id if self.instance.department else None
            current_pos_id = self.instance.position_id if self.instance.position else None
            current_edu_id = self.instance.education_id if self.instance.education else None
            
            self.fields['department'].queryset = Department.objects.filter(
                Q(status=True) | Q(id=current_dept_id)
            )
            self.fields['position'].queryset = Position.objects.filter(
                Q(status=True) | Q(id=current_pos_id)
            )
            
            # Since EducationLevel doesn't have status field, we don't filter it
            # self.fields['education'].queryset = EducationLevel.objects.all()
        else:
            # For new employees, only show active options for departments and positions
            self.fields['department'].queryset = Department.objects.filter(status=True)
            self.fields['position'].queryset = Position.objects.filter(status=True)
            # No filtering for education level
        
        # Add empty label for optional fields
        self.fields['department'].empty_label = "-- Select Department --"
        self.fields['position'].empty_label = "-- Select Position --"
        self.fields['education'].empty_label = "-- Select Education Level --"
        
        # Add help text for image field
        self.fields['profile_image'].help_text = "Recommended size: 300x300 pixels. Max size: 2MB"

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
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000'}),
            'allowance': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000'}),
            'sign_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'signed_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of signatory'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter to only show active employees
        # If editing an existing contract, include the current employee even if inactive
        if self.instance and self.instance.pk:
            current_employee_id = self.instance.employee_id
            self.fields['employee'].queryset = Employee.objects.filter(
                Q(status='Working') | Q(id=current_employee_id)
            )
        else:
            # For new contracts, only show active employees
            self.fields['employee'].queryset = Employee.objects.filter(status='Working')
        
        # Make end_date optional with clear help text
        self.fields['end_date'].required = False
        self.fields['end_date'].help_text = "Leave empty for indefinite contracts"
        
        # Add help text for file upload
        self.fields['attached_file'].help_text = "Upload contract document (PDF, DOC, DOCX). Max size: 5MB"
        
        # Add empty label
        self.fields['employee'].empty_label = "-- Select Employee --"

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
            'social_insurance_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Social insurance number'}),
            'social_insurance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'social_insurance_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issuing authority'}),
            'health_insurance_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Health insurance number'}),
            'health_insurance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'health_insurance_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issuing authority'}),
            'health_care_provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Healthcare provider name'}),
            'tax_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tax identification number'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter to only show active employees
        # If editing an existing record, include the current employee even if inactive
        if self.instance and self.instance.pk:
            current_employee_id = self.instance.employee_id
            self.fields['employee'].queryset = Employee.objects.filter(
                Q(status='Working') | Q(id=current_employee_id)
            )
        else:
            # For new records, only show active employees
            self.fields['employee'].queryset = Employee.objects.filter(status='Working')
        
        # Add empty label
        self.fields['employee'].empty_label = "-- Select Employee --"
        
        # Add field groups for better UI organization
        self.fieldsets = {
            'employee_info': ['employee', 'status'],
            'social_insurance': ['social_insurance_number', 'social_insurance_date', 'social_insurance_place'],
            'health_insurance': ['health_insurance_number', 'health_insurance_date', 'health_insurance_place', 'health_care_provider'],
            'tax_info': ['tax_code'],
        }
