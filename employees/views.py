from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from .models import Department, Position, EducationLevel, Employee, EmploymentContract, InsuranceAndTax
from .forms import (
    DepartmentForm, PositionForm, EducationLevelForm, EmployeeForm, 
    EmploymentContractForm, InsuranceAndTaxForm
)
from accounts.models import SystemLog

# Department Views
@login_required
@permission_required('accounts.view_employee_data', raise_exception=True)
def department_list(request):
    departments = Department.objects.all()
    query = request.GET.get('q')
    if query:
        departments = departments.filter(
            Q(department_name__icontains=query) | 
            Q(department_code__icontains=query)
        )
    return render(request, 'employees/department_list.html', {'departments': departments})

@login_required
@permission_required('accounts.add_employee_data', raise_exception=True)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Department Creation",
                object_type="Department",
                object_id=department.id,
                details=f"Created department: {department.department_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Department {department.department_name} has been created successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'employees/department_form.html', {'form': form, 'title': 'Create Department'})

@login_required
@permission_required('accounts.change_employee_data', raise_exception=True)
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Department Update",
                object_type="Department",
                object_id=department.id,
                details=f"Updated department: {department.department_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Department {department.department_name} has been updated successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'employees/department_form.html', {'form': form, 'title': 'Edit Department', 'department': department})

@login_required
@permission_required('accounts.delete_employee_data', raise_exception=True)
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept_name = department.department_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Department Deletion",
            object_type="Department",
            details=f"Deleted department: {dept_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        department.delete()
        messages.success(request, f'Department {dept_name} has been deleted successfully!')
        return redirect('department_list')
    return render(request, 'employees/department_confirm_delete.html', {'department': department})

# Position Views
@login_required
@permission_required('accounts.view_employee_data', raise_exception=True)
def position_list(request):
    positions = Position.objects.all()
    query = request.GET.get('q')
    if query:
        positions = positions.filter(
            Q(position_name__icontains=query) | 
            Q(position_code__icontains=query)
        )
    return render(request, 'employees/position_list.html', {'positions': positions})

@login_required
@permission_required('accounts.add_employee_data', raise_exception=True)
def position_create(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Position Creation",
                object_type="Position",
                object_id=position.id,
                details=f"Created position: {position.position_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Position {position.position_name} has been created successfully!')
            return redirect('position_list')
    else:
        form = PositionForm()
    return render(request, 'employees/position_form.html', {'form': form, 'title': 'Create Position'})

@login_required
@permission_required('accounts.change_employee_data', raise_exception=True)
def position_edit(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Position Update",
                object_type="Position",
                object_id=position.id,
                details=f"Updated position: {position.position_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Position {position.position_name} has been updated successfully!')
            return redirect('position_list')
    else:
        form = PositionForm(instance=position)
    return render(request, 'employees/position_form.html', {'form': form, 'title': 'Edit Position', 'position': position})

@login_required
@permission_required('accounts.delete_employee_data', raise_exception=True)
def position_delete(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        pos_name = position.position_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Position Deletion",
            object_type="Position",
            details=f"Deleted position: {pos_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        position.delete()
        messages.success(request, f'Position {pos_name} has been deleted successfully!')
        return redirect('position_list')
    return render(request, 'employees/position_confirm_delete.html', {'position': position})

# Education Level Views
@login_required
@permission_required('accounts.view_employee_data', raise_exception=True)
def education_list(request):
    education_levels = EducationLevel.objects.all()
    query = request.GET.get('q')
    if query:
        education_levels = education_levels.filter(
            Q(education_name__icontains=query) | 
            Q(education_code__icontains=query)
        )
    return render(request, 'employees/education_list.html', {'education_levels': education_levels})

@login_required
@permission_required('accounts.add_employee_data', raise_exception=True)
def education_create(request):
    if request.method == 'POST':
        form = EducationLevelForm(request.POST)
        if form.is_valid():
            education = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Education Level Creation",
                object_type="EducationLevel",
                object_id=education.id,
                details=f"Created education level: {education.education_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Education level {education.education_name} has been created successfully!')
            return redirect('education_list')
    else:
        form = EducationLevelForm()
    return render(request, 'employees/education_form.html', {'form': form, 'title': 'Create Education Level'})

@login_required
@permission_required('accounts.change_employee_data', raise_exception=True)
def education_edit(request, pk):
    education = get_object_or_404(EducationLevel, pk=pk)
    if request.method == 'POST':
        form = EducationLevelForm(request.POST, instance=education)
        if form.is_valid():
            education = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Education Level Update",
                object_type="EducationLevel",
                object_id=education.id,
                details=f"Updated education level: {education.education_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Education level {education.education_name} has been updated successfully!')
            return redirect('education_list')
    else:
        form = EducationLevelForm(instance=education)
    return render(request, 'employees/education_form.html', {'form': form, 'title': 'Edit Education Level', 'education': education})

@login_required
@permission_required('accounts.delete_employee_data', raise_exception=True)
def education_delete(request, pk):
    education = get_object_or_404(EducationLevel, pk=pk)
    if request.method == 'POST':
        edu_name = education.education_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Education Level Deletion",
            object_type="EducationLevel",
            details=f"Deleted education level: {edu_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        education.delete()
        messages.success(request, f'Education level {edu_name} has been deleted successfully!')
        return redirect('education_list')
    return render(request, 'employees/education_confirm_delete.html', {'education': education})

# Employee Views
@login_required
@permission_required('accounts.view_employee_data', raise_exception=True)
def employee_list(request):
    employees = Employee.objects.all()
    query = request.GET.get('q')
    if query:
        employees = employees.filter(
            Q(full_name__icontains=query) | 
            Q(id_card__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    
    department_id = request.GET.get('department')
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    position_id = request.GET.get('position')
    if position_id:
        employees = employees.filter(position_id=position_id)
    
    status = request.GET.get('status')
    if status:
        employees = employees.filter(status=status)
    
    departments = Department.objects.filter(status=True)
    positions = Position.objects.filter(status=True)
    
    context = {
        'employees': employees,
        'departments': departments,
        'positions': positions,
        'selected_department': department_id,
        'selected_position': position_id,
        'selected_status': status,
    }
    return render(request, 'employees/employee_list.html', context)

@login_required
@permission_required('accounts.view_employee_data', raise_exception=True)
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    contracts = EmploymentContract.objects.filter(employee=employee).order_by('-start_date')
    try:
        insurance = InsuranceAndTax.objects.get(employee=employee)
    except InsuranceAndTax.DoesNotExist:
        insurance = None
    
    context = {
        'employee': employee,
        'contracts': contracts,
        'insurance': insurance,
    }
    return render(request, 'employees/employee_detail.html', context)

@login_required
@permission_required('accounts.add_employee_data', raise_exception=True)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Employee Creation",
                object_type="Employee",
                object_id=employee.id,
                details=f"Created employee: {employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Employee {employee.full_name} has been created successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Create Employee'})

@login_required
@permission_required('accounts.change_employee_data', raise_exception=True)
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Employee Update",
                object_type="Employee",
                object_id=employee.id,
                details=f"Updated employee: {employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Employee {employee.full_name} has been updated successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Edit Employee', 'employee': employee})

@login_required
@permission_required('accounts.delete_employee_data', raise_exception=True)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        emp_name = employee.full_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Employee Deletion",
            object_type="Employee",
            details=f"Deleted employee: {emp_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        employee.delete()
        messages.success(request, f'Employee {emp_name} has been deleted successfully!')
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

# Contract Views
@login_required
@permission_required('accounts.view_contract', raise_exception=True)
def contract_list(request):
    contracts = EmploymentContract.objects.all().order_by('-created_date')
    query = request.GET.get('q')
    if query:
        contracts = contracts.filter(
            Q(employee__full_name__icontains=query) | 
            Q(contract_type__icontains=query)
        )
    
    status = request.GET.get('status')
    if status:
        contracts = contracts.filter(status=status)
    
    context = {
        'contracts': contracts,
        'selected_status': status,
    }
    return render(request, 'employees/contract_list.html', context)

@login_required
@permission_required('accounts.add_contract', raise_exception=True)
def contract_create(request):
    if request.method == 'POST':
        form = EmploymentContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Contract Creation",
                object_type="EmploymentContract",
                object_id=contract.id,
                details=f"Created contract for: {contract.employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Contract for {contract.employee.full_name} has been created successfully!')
            return redirect('contract_list')
    else:
        employee_id = request.GET.get('employee_id')
        if employee_id:
            form = EmploymentContractForm(initial={'employee': employee_id})
        else:
            form = EmploymentContractForm()
    return render(request, 'employees/contract_form.html', {'form': form, 'title': 'Create Contract'})

@login_required
@permission_required('accounts.change_contract', raise_exception=True)
def contract_edit(request, pk):
    contract = get_object_or_404(EmploymentContract, pk=pk)
    if request.method == 'POST':
        form = EmploymentContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            contract = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Contract Update",
                object_type="EmploymentContract",
                object_id=contract.id,
                details=f"Updated contract for: {contract.employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Contract for {contract.employee.full_name} has been updated successfully!')
            return redirect('contract_list')
    else:
        form = EmploymentContractForm(instance=contract)
    return render(request, 'employees/contract_form.html', {'form': form, 'title': 'Edit Contract', 'contract': contract})

@login_required
@permission_required('accounts.delete_contract', raise_exception=True)
def contract_delete(request, pk):
    contract = get_object_or_404(EmploymentContract, pk=pk)
    if request.method == 'POST':
        emp_name = contract.employee.full_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Contract Deletion",
            object_type="EmploymentContract",
            details=f"Deleted contract for: {emp_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        contract.delete()
        messages.success(request, f'Contract for {emp_name} has been deleted successfully!')
        return redirect('contract_list')
    return render(request, 'employees/contract_confirm_delete.html', {'contract': contract})

# Insurance and Tax Views
@login_required
@permission_required('accounts.view_employee_data', raise_exception=True)
def insurance_list(request):
    insurances = InsuranceAndTax.objects.all()
    query = request.GET.get('q')
    if query:
        insurances = insurances.filter(
            Q(employee__full_name__icontains=query) | 
            Q(social_insurance_number__icontains=query) |
            Q(health_insurance_number__icontains=query) |
            Q(tax_code__icontains=query)
        )
    
    status = request.GET.get('status')
    if status:
        insurances = insurances.filter(status=status)
    
    context = {
        'insurances': insurances,
        'selected_status': status,
    }
    return render(request, 'employees/insurance_list.html', context)

@login_required
@permission_required('accounts.add_employee_data', raise_exception=True)
def insurance_create(request):
    if request.method == 'POST':
        form = InsuranceAndTaxForm(request.POST)
        if form.is_valid():
            insurance = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Insurance & Tax Creation",
                object_type="InsuranceAndTax",
                object_id=insurance.id,
                details=f"Created insurance & tax record for: {insurance.employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Insurance & tax record for {insurance.employee.full_name} has been created successfully!')
            return redirect('insurance_list')
    else:
        employee_id = request.GET.get('employee_id')
        if employee_id:
            form = InsuranceAndTaxForm(initial={'employee': employee_id})
        else:
            form = InsuranceAndTaxForm()
    return render(request, 'employees/insurance_form.html', {'form': form, 'title': 'Create Insurance & Tax Record'})

@login_required
@permission_required('accounts.change_employee_data', raise_exception=True)
def insurance_edit(request, pk):
    insurance = get_object_or_404(InsuranceAndTax, pk=pk)
    if request.method == 'POST':
        form = InsuranceAndTaxForm(request.POST, instance=insurance)
        if form.is_valid():
            insurance = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Insurance & Tax Update",
                object_type="InsuranceAndTax",
                object_id=insurance.id,
                details=f"Updated insurance & tax record for: {insurance.employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Insurance & tax record for {insurance.employee.full_name} has been updated successfully!')
            return redirect('insurance_list')
    else:
        form = InsuranceAndTaxForm(instance=insurance)
    return render(request, 'employees/insurance_form.html', {'form': form, 'title': 'Edit Insurance & Tax Record', 'insurance': insurance})

@login_required
@permission_required('accounts.delete_employee_data', raise_exception=True)
def insurance_delete(request, pk):
    insurance = get_object_or_404(InsuranceAndTax, pk=pk)
    if request.method == 'POST':
        emp_name = insurance.employee.full_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Insurance & Tax Deletion",
            object_type="InsuranceAndTax",
            details=f"Deleted insurance & tax record for: {emp_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        insurance.delete()
        messages.success(request, f'Insurance & tax record for {emp_name} has been deleted successfully!')
        return redirect('insurance_list')
    return render(request, 'employees/insurance_confirm_delete.html', {'insurance': insurance})