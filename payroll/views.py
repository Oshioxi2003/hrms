from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import Salary, SalaryAdvance
from .forms import SalaryForm, SalaryAdvanceForm, SalaryAdvanceApprovalForm, PayrollProcessForm, SalarySearchForm
from employees.models import Employee
from accounts.models import SystemLog

# Salary Advance Views
@login_required
@permission_required('accounts.manage_advances', raise_exception=True)
def advance_list(request):
    advances = SalaryAdvance.objects.all().order_by('-created_date')
    
    # Filter by employee name
    employee_name = request.GET.get('employee_name')
    if employee_name:
        advances = advances.filter(employee__full_name__icontains=employee_name)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        advances = advances.filter(status=status)
    
    # Pagination
    paginator = Paginator(advances, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': SalaryAdvance.STATUS_CHOICES,
        'selected_status': status,
    }
    return render(request, 'payroll/advance_list.html', context)

@login_required
@permission_required('accounts.manage_advances', raise_exception=True)
def advance_create(request):
    if request.method == 'POST':
        form = SalaryAdvanceForm(request.POST)
        if form.is_valid():
            advance = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Salary Advance Creation",
                object_type="SalaryAdvance",
                object_id=advance.id,
                details=f"Created salary advance for: {advance.employee.full_name}, Amount: {advance.amount}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Salary advance for {advance.employee.full_name} has been created successfully!')
            return redirect('advance_list')
    else:
        employee_id = request.GET.get('employee_id')
        if employee_id:
            form = SalaryAdvanceForm(initial={'employee': employee_id})
        else:
            form = SalaryAdvanceForm()
    return render(request, 'payroll/advance_form.html', {'form': form, 'title': 'Create Salary Advance'})

@login_required
@permission_required('accounts.manage_advances', raise_exception=True)
def advance_edit(request, pk):
    advance = get_object_or_404(SalaryAdvance, pk=pk)
    
    # Only allow editing if the advance is still pending
    if advance.status != 'Pending':
        messages.error(request, "You can only edit pending advances.")
        return redirect('advance_list')
    
    if request.method == 'POST':
        form = SalaryAdvanceForm(request.POST, instance=advance)
        if form.is_valid():
            advance = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Salary Advance Update",
                object_type="SalaryAdvance",
                object_id=advance.id,
                details=f"Updated salary advance for: {advance.employee.full_name}, Amount: {advance.amount}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Salary advance for {advance.employee.full_name} has been updated successfully!')
            return redirect('advance_list')
    else:
        form = SalaryAdvanceForm(instance=advance)
    return render(request, 'payroll/advance_form.html', {'form': form, 'title': 'Edit Salary Advance', 'advance': advance})

@login_required
@permission_required('accounts.manage_advances', raise_exception=True)
def advance_approve(request, pk):
    advance = get_object_or_404(SalaryAdvance, pk=pk)
    
    # Only allow approval if the advance is still pending
    if advance.status != 'Pending':
        messages.error(request, "You can only approve/reject pending advances.")
        return redirect('advance_list')
    
    if request.method == 'POST':
        form = SalaryAdvanceApprovalForm(request.POST, instance=advance)
        if form.is_valid():
            advance = form.save(commit=False)
            advance.approved_by_id = request.user.employee_id
            advance.approval_date = timezone.now().date()
            advance.save()
            
            # Log action
            action = "Salary Advance Approved" if advance.status == 'Approved' else "Salary Advance Rejected"
            SystemLog.objects.create(
                user=request.user,
                action=action,
                object_type="SalaryAdvance",
                object_id=advance.id,
                details=f"{action}: {advance.employee.full_name}, Amount: {advance.amount}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'Salary advance has been {advance.status.lower()} successfully!')
            return redirect('advance_list')
    else:
        form = SalaryAdvanceApprovalForm(instance=advance)
    
    return render(request, 'payroll/advance_approve.html', {'form': form, 'advance': advance})

@login_required
@permission_required('accounts.manage_advances', raise_exception=True)
def advance_delete(request, pk):
    advance = get_object_or_404(SalaryAdvance, pk=pk)
    
    # Only allow deletion if the advance is still pending
    if advance.status != 'Pending':
        messages.error(request, "You can only delete pending advances.")
        return redirect('advance_list')
    
    if request.method == 'POST':
        employee_name = advance.employee.full_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Salary Advance Deletion",
            object_type="SalaryAdvance",
            details=f"Deleted salary advance for: {employee_name}, Amount: {advance.amount}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        advance.delete()
        messages.success(request, f'Salary advance for {employee_name} has been deleted successfully!')
        return redirect('advance_list')
    
    return render(request, 'payroll/advance_confirm_delete.html', {'advance': advance})

# Salary Views
@login_required
@permission_required('accounts.view_salary', raise_exception=True)
def salary_list(request):
    form = SalarySearchForm(request.GET)
    salaries = Salary.objects.all().order_by('-year', '-month', 'employee__full_name')
    
    if form.is_valid():
        employee = form.cleaned_data.get('employee')
        month = form.cleaned_data.get('month')
        year = form.cleaned_data.get('year')
        is_paid = form.cleaned_data.get('is_paid')
        
        if employee:
            salaries = salaries.filter(employee=employee)
        
        if month:
            salaries = salaries.filter(month=month)
        
        if year:
            salaries = salaries.filter(year=year)
        
        if is_paid:
            is_paid_bool = is_paid == 'True'
            salaries = salaries.filter(is_paid=is_paid_bool)
    
    # Calculate totals
    total_net_salary = salaries.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
    
    # Pagination
    paginator = Paginator(salaries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_net_salary': total_net_salary,
    }
    return render(request, 'payroll/salary_list.html', context)

@login_required
@permission_required('accounts.view_salary', raise_exception=True)
def salary_detail(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    
    # Calculate total earnings and deductions for display
    total_earnings = salary.base_salary + salary.allowance + salary.bonus
    total_deductions = (
        salary.income_tax + 
        salary.social_insurance + 
        salary.health_insurance + 
        salary.unemployment_insurance + 
        salary.deductions + 
        salary.advance
    )
    
    context = {
        'salary': salary,
        'total_earnings': total_earnings,
        'total_deductions': total_deductions,
    }
    return render(request, 'payroll/salary_detail.html', context)

@login_required
@permission_required('accounts.process_payroll', raise_exception=True)
def salary_create(request):
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            salary = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Salary Creation",
                object_type="Salary",
                object_id=salary.id,
                details=f"Created salary for: {salary.employee.full_name}, Month: {salary.month}/{salary.year}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Salary for {salary.employee.full_name} has been created successfully!')
            return redirect('salary_detail', pk=salary.pk)
    else:
        employee_id = request.GET.get('employee_id')
        month = request.GET.get('month', timezone.now().month)
        year = request.GET.get('year', timezone.now().year)
        
        initial_data = {'month': month, 'year': year}
        if employee_id:
            employee = get_object_or_404(Employee, pk=employee_id)
            initial_data['employee'] = employee.id
            
            # Get the latest contract for base salary
            from employees.models import EmploymentContract
            contract = EmploymentContract.objects.filter(
                employee=employee,
                status='Active'
            ).order_by('-start_date').first()
            
            if contract:
                initial_data['base_salary'] = contract.base_salary
                initial_data['allowance'] = contract.allowance
        
        form = SalaryForm(initial=initial_data)
    
    return render(request, 'payroll/salary_form.html', {'form': form, 'title': 'Create Salary'})

@login_required
@permission_required('accounts.process_payroll', raise_exception=True)
def salary_edit(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    
    # Don't allow editing if salary is already paid
    if salary.is_paid:
        messages.error(request, "You cannot edit a salary that has already been paid.")
        return redirect('salary_detail', pk=salary.pk)
    
    if request.method == 'POST':
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            salary = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Salary Update",
                object_type="Salary",
                object_id=salary.id,
                details=f"Updated salary for: {salary.employee.full_name}, Month: {salary.month}/{salary.year}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Salary for {salary.employee.full_name} has been updated successfully!')
            return redirect('salary_detail', pk=salary.pk)
    else:
        form = SalaryForm(instance=salary)
    
    return render(request, 'payroll/salary_form.html', {'form': form, 'title': 'Edit Salary', 'salary': salary})

@login_required
@permission_required('accounts.process_payroll', raise_exception=True)
def salary_delete(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    
    # Don't allow deleting if salary is already paid
    if salary.is_paid:
        messages.error(request, "You cannot delete a salary that has already been paid.")
        return redirect('salary_detail', pk=salary.pk)
    
    if request.method == 'POST':
        employee_name = salary.employee.full_name
        month_year = f"{salary.month}/{salary.year}"
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Salary Deletion",
            object_type="Salary",
            details=f"Deleted salary for: {employee_name}, Month: {month_year}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        salary.delete()
        messages.success(request, f'Salary for {employee_name} ({month_year}) has been deleted successfully!')
        return redirect('salary_list')
    
    return render(request, 'payroll/salary_confirm_delete.html', {'salary': salary})

@login_required
@permission_required('accounts.process_payroll', raise_exception=True)
def salary_mark_as_paid(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    
    if salary.is_paid:
        messages.error(request, "This salary has already been marked as paid.")
        return redirect('salary_detail', pk=salary.pk)
    
    if request.method == 'POST':
        salary.is_paid = True
        salary.payment_date = timezone.now().date()
        salary.save()
        
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Salary Payment",
            object_type="Salary",
            object_id=salary.id,
            details=f"Marked salary as paid for: {salary.employee.full_name}, Month: {salary.month}/{salary.year}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, f'Salary for {salary.employee.full_name} has been marked as paid successfully!')
        return redirect('salary_detail', pk=salary.pk)
    
    return render(request, 'payroll/salary_mark_as_paid.html', {'salary': salary})

@login_required
@permission_required('accounts.process_payroll', raise_exception=True)
def process_payroll(request):
    if request.method == 'POST':
        form = PayrollProcessForm(request.POST)
        if form.is_valid():
            salary_data = form.get_salary_data()
            
            # Save all salary records
            for salary in salary_data:
                if not isinstance(salary, Salary):  # Only save if it's a new salary object
                    salary.save()
            
            # Log action
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            SystemLog.objects.create(
                user=request.user,
                action="Payroll Processing",
                details=f"Processed payroll for month: {month}/{year}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'Payroll for {month}/{year} has been processed successfully!')
            return redirect('salary_list')
    else:
        form = PayrollProcessForm()
    
    return render(request, 'payroll/process_payroll.html', {'form': form})

@login_required
@permission_required('accounts.process_payroll', raise_exception=True)
def export_payroll(request):
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    
    # Get all salaries for the specified month and year
    salaries = Salary.objects.filter(month=month, year=year).order_by('employee__full_name')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payroll_{month}_{year}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'Employee Name', 'Department', 'Position', 
        'Base Salary', 'Allowance', 'Bonus', 'Income Tax', 
        'Social Insurance', 'Health Insurance', 'Unemployment Insurance', 
        'Deductions', 'Advance', 'Net Salary', 'Payment Status'
    ])
    
    for salary in salaries:
        writer.writerow([
            salary.employee.id,
            salary.employee.full_name,
            salary.employee.department.department_name if salary.employee.department else '',
            salary.employee.position.position_name if salary.employee.position else '',
            salary.base_salary,
            salary.allowance,
            salary.bonus,
            salary.income_tax,
            salary.social_insurance,
            salary.health_insurance,
            salary.unemployment_insurance,
            salary.deductions,
            salary.advance,
            salary.net_salary,
            'Paid' if salary.is_paid else 'Unpaid'
        ])
    
    # Log action
    SystemLog.objects.create(
        user=request.user,
        action="Payroll Export",
        details=f"Exported payroll data for month: {month}/{year}",
        ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    return response