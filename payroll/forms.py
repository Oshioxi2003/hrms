from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator
from .models import Salary, SalaryAdvance
from employees.models import Employee, EmploymentContract
from attendance.models import Attendance
from leave.models import LeaveRequest
import calendar
from datetime import datetime, date
from django.db import models



class SalaryAdvanceForm(forms.ModelForm):
    class Meta:
        model = SalaryAdvance
        fields = ['employee', 'advance_date', 'amount', 'reason', 'deduction_month', 'deduction_year']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'advance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'deduction_month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'deduction_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default deduction month and year to next month
        today = timezone.now().date()
        if today.month == 12:
            self.fields['deduction_month'].initial = 1
            self.fields['deduction_year'].initial = today.year + 1
        else:
            self.fields['deduction_month'].initial = today.month + 1
            self.fields['deduction_year'].initial = today.year

class SalaryAdvanceApprovalForm(forms.ModelForm):
    class Meta:
        model = SalaryAdvance
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit status choices to only Approved or Rejected
        self.fields['status'].choices = [
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ]

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = [
            'employee', 'month', 'year', 'work_days', 'leave_days', 'overtime_hours',
            'base_salary', 'allowance', 'income_tax', 'social_insurance', 'health_insurance',
            'unemployment_insurance', 'bonus', 'deductions', 'advance', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000}),
            'work_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'leave_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'allowance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'income_tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'social_insurance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'health_insurance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'unemployment_insurance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'advance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PayrollProcessForm(forms.Form):
    month = forms.IntegerField(
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
        initial=timezone.now().month
    )
    year = forms.IntegerField(
        validators=[MinValueValidator(2000)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 2000}),
        initial=timezone.now().year
    )
    
    def get_salary_data(self):
        month = self.cleaned_data['month']
        year = self.cleaned_data['year']
        
        # Get all active employees
        employees = Employee.objects.filter(status='Working')
        
        salary_data = []
        for employee in employees:
            # Check if salary already exists for this month/year
            existing_salary = Salary.objects.filter(
                employee=employee,
                month=month,
                year=year
            ).first()
            
            if existing_salary:
                salary_data.append(existing_salary)
                continue
            
            # Get the latest contract for base salary
            contract = EmploymentContract.objects.filter(
                employee=employee,
                status='Active'
            ).order_by('-start_date').first()
            
            if not contract:
                continue  # Skip if no active contract
            
            # Get attendance data for the month
            _, days_in_month = calendar.monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, days_in_month)
            
            attendances = Attendance.objects.filter(
                employee=employee,
                work_date__gte=start_date,
                work_date__lte=end_date
            )
            
            # Calculate work days and leave days
            work_days = attendances.filter(status='Present').count()
            leave_days = attendances.filter(status='On Leave').count()
            
            # Calculate overtime hours
            overtime_hours = attendances.aggregate(models.Sum('overtime_hours'))['overtime_hours__sum'] or 0
            
            # Get any advances for this month
            advances = SalaryAdvance.objects.filter(
                employee=employee,
                deduction_month=month,
                deduction_year=year,
                status='Approved'
            )
            advance_amount = advances.aggregate(models.Sum('amount'))['amount__sum'] or 0
            
            # Calculate standard deductions (simplified)
            base_salary = contract.base_salary
            allowance = contract.allowance
            
            # Simple calculation for deductions (you may want to customize this)
            income_tax = base_salary * 0.1  # 10% income tax
            social_insurance = base_salary * 0.08  # 8% social insurance
            health_insurance = base_salary * 0.015  # 1.5% health insurance
            unemployment_insurance = base_salary * 0.01  # 1% unemployment insurance
            
            # Create new salary object
            salary = Salary(
                employee=employee,
                month=month,
                year=year,
                work_days=work_days,
                leave_days=leave_days,
                overtime_hours=overtime_hours,
                base_salary=base_salary,
                allowance=allowance,
                income_tax=income_tax,
                social_insurance=social_insurance,
                health_insurance=health_insurance,
                unemployment_insurance=unemployment_insurance,
                bonus=0,  # Set bonus to 0 initially
                deductions=0,  # Set additional deductions to 0 initially
                advance=advance_amount
            )
            
            # Calculate net salary
            total_earnings = base_salary + allowance
            total_deductions = (
                income_tax + 
                social_insurance + 
                health_insurance + 
                unemployment_insurance + 
                advance_amount
            )
            salary.net_salary = total_earnings - total_deductions
            
            salary_data.append(salary)
        
        return salary_data

class SalarySearchForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='Working'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    month = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12})
    )
    year = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(2000)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 2000})
    )
    is_paid = forms.ChoiceField(
        choices=[('', 'All'), ('True', 'Paid'), ('False', 'Unpaid')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )