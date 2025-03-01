from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import KPI, EmployeeEvaluation
from .forms import KPIForm, EmployeeEvaluationForm, EvaluationSearchForm
from employees.models import Employee
from accounts.models import SystemLog

# KPI Views
@login_required
@permission_required('accounts.view_evaluation', raise_exception=True)
def kpi_list(request):
    kpis = KPI.objects.all().order_by('kpi_name')
    
    # Filter by KPI name
    kpi_name = request.GET.get('kpi_name')
    if kpi_name:
        kpis = kpis.filter(kpi_name__icontains=kpi_name)
    
    # Filter by KPI type
    kpi_type = request.GET.get('kpi_type')
    if kpi_type:
        kpis = kpis.filter(kpi_type=kpi_type)
    
    # Pagination
    paginator = Paginator(kpis, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'kpi_types': KPI.KPI_TYPES,
        'selected_type': kpi_type,
    }
    return render(request, 'performance/kpi_list.html', context)

@login_required
@permission_required('accounts.add_evaluation', raise_exception=True)
def kpi_create(request):
    if request.method == 'POST':
        form = KPIForm(request.POST)
        if form.is_valid():
            kpi = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="KPI Creation",
                object_type="KPI",
                object_id=kpi.id,
                details=f"Created KPI: {kpi.kpi_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'KPI {kpi.kpi_name} has been created successfully!')
            return redirect('kpi_list')
    else:
        form = KPIForm()
    return render(request, 'performance/kpi_form.html', {'form': form, 'title': 'Create KPI'})

@login_required
@permission_required('accounts.change_evaluation', raise_exception=True)
def kpi_edit(request, pk):
    kpi = get_object_or_404(KPI, pk=pk)
    if request.method == 'POST':
        form = KPIForm(request.POST, instance=kpi)
        if form.is_valid():
            kpi = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="KPI Update",
                object_type="KPI",
                object_id=kpi.id,
                details=f"Updated KPI: {kpi.kpi_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'KPI {kpi.kpi_name} has been updated successfully!')
            return redirect('kpi_list')
    else:
        form = KPIForm(instance=kpi)
    return render(request, 'performance/kpi_form.html', {'form': form, 'title': 'Edit KPI', 'kpi': kpi})

@login_required
@permission_required('accounts.delete_evaluation', raise_exception=True)
def kpi_delete(request, pk):
    kpi = get_object_or_404(KPI, pk=pk)
    if request.method == 'POST':
        kpi_name = kpi.kpi_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="KPI Deletion",
            object_type="KPI",
            details=f"Deleted KPI: {kpi_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        kpi.delete()
        messages.success(request, f'KPI {kpi_name} has been deleted successfully!')
        return redirect('kpi_list')
    return render(request, 'performance/kpi_confirm_delete.html', {'kpi': kpi})

# Employee Evaluation Views
@login_required
@permission_required('accounts.view_evaluation', raise_exception=True)
def evaluation_list(request):
    form = EvaluationSearchForm(request.GET)
    evaluations = EmployeeEvaluation.objects.all().order_by('-year', '-month', 'employee__full_name')
    
    if form.is_valid():
        employee = form.cleaned_data.get('employee')
        kpi = form.cleaned_data.get('kpi')
        month = form.cleaned_data.get('month')
        year = form.cleaned_data.get('year')
        
        if employee:
            evaluations = evaluations.filter(employee=employee)
        
        if kpi:
            evaluations = evaluations.filter(kpi=kpi)
        
        if month:
            evaluations = evaluations.filter(month=month)
        
        if year:
            evaluations = evaluations.filter(year=year)
    
    # Calculate average achievement rate
    avg_achievement = evaluations.aggregate(Avg('achievement_rate'))['achievement_rate__avg'] or 0
    
    # Pagination
    paginator = Paginator(evaluations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'avg_achievement': round(avg_achievement, 2),
    }
    return render(request, 'performance/evaluation_list.html', context)

@login_required
@permission_required('accounts.view_evaluation', raise_exception=True)
def employee_performance(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # Get evaluations for this employee
    evaluations = EmployeeEvaluation.objects.filter(employee=employee).order_by('-year', '-month', 'kpi__kpi_name')
    
    # Filter by month and year if provided
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month:
        evaluations = evaluations.filter(month=month)
    
    if year:
        evaluations = evaluations.filter(year=year)
    
    # Calculate average achievement rate
    avg_achievement = evaluations.aggregate(Avg('achievement_rate'))['achievement_rate__avg'] or 0
    
    context = {
        'employee': employee,
        'evaluations': evaluations,
        'avg_achievement': round(avg_achievement, 2),
        'selected_month': month,
        'selected_year': year,
    }
    return render(request, 'performance/employee_performance.html', context)

@login_required
@permission_required('accounts.add_evaluation', raise_exception=True)
def evaluation_create(request):
    if request.method == 'POST':
        form = EmployeeEvaluationForm(request.POST, user=request.user)
        if form.is_valid():
            evaluation = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Evaluation Creation",
                object_type="EmployeeEvaluation",
                object_id=evaluation.id,
                details=f"Created evaluation for: {evaluation.employee.full_name}, KPI: {evaluation.kpi.kpi_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Evaluation for {evaluation.employee.full_name} has been created successfully!')
            return redirect('evaluation_list')
    else:
        employee_id = request.GET.get('employee_id')
        kpi_id = request.GET.get('kpi_id')
        
        initial_data = {}
        if employee_id:
            initial_data['employee'] = employee_id
        if kpi_id:
            initial_data['kpi'] = kpi_id
            # Get target from KPI if available
            try:
                kpi = KPI.objects.get(pk=kpi_id)
                if kpi.min_target:
                    initial_data['target'] = kpi.min_target
            except KPI.DoesNotExist:
                pass
            
        form = EmployeeEvaluationForm(initial=initial_data, user=request.user)
    
    return render(request, 'performance/evaluation_form.html', {'form': form, 'title': 'Create Evaluation'})

@login_required
@permission_required('accounts.change_evaluation', raise_exception=True)
def evaluation_edit(request, pk):
    evaluation = get_object_or_404(EmployeeEvaluation, pk=pk)
    if request.method == 'POST':
        form = EmployeeEvaluationForm(request.POST, instance=evaluation, user=request.user)
        if form.is_valid():
            evaluation = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Evaluation Update",
                object_type="EmployeeEvaluation",
                object_id=evaluation.id,
                details=f"Updated evaluation for: {evaluation.employee.full_name}, KPI: {evaluation.kpi.kpi_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Evaluation for {evaluation.employee.full_name} has been updated successfully!')
            return redirect('evaluation_list')
    else:
        form = EmployeeEvaluationForm(instance=evaluation, user=request.user)
    
    return render(request, 'performance/evaluation_form.html', {'form': form, 'title': 'Edit Evaluation', 'evaluation': evaluation})

@login_required
@permission_required('accounts.delete_evaluation', raise_exception=True)
def evaluation_delete(request, pk):
    evaluation = get_object_or_404(EmployeeEvaluation, pk=pk)
    if request.method == 'POST':
        employee_name = evaluation.employee.full_name
        kpi_name = evaluation.kpi.kpi_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Evaluation Deletion",
            object_type="EmployeeEvaluation",
            details=f"Deleted evaluation for: {employee_name}, KPI: {kpi_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        evaluation.delete()
        messages.success(request, f'Evaluation for {employee_name} has been deleted successfully!')
        return redirect('evaluation_list')
    return render(request, 'performance/evaluation_confirm_delete.html', {'evaluation': evaluation})