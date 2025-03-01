from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from .models import RewardsAndDisciplinary
from .forms import RewardsAndDisciplinaryForm, RewardSearchForm
from accounts.models import SystemLog

@login_required
@permission_required('accounts.view_reward_discipline', raise_exception=True)
def reward_list(request):
    form = RewardSearchForm(request.GET)
    records = RewardsAndDisciplinary.objects.all().order_by('-decision_date')
    
    if form.is_valid():
        employee = form.cleaned_data.get('employee')
        record_type = form.cleaned_data.get('type')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if employee:
            records = records.filter(employee=employee)
        
        if record_type:
            records = records.filter(type=record_type)
        
        if start_date:
            records = records.filter(decision_date__gte=start_date)
        
        if end_date:
            records = records.filter(decision_date__lte=end_date)
    
    # Calculate totals
    total_rewards = records.filter(type='Reward').aggregate(Sum('amount'))['amount__sum'] or 0
    total_disciplinary = records.filter(type='Disciplinary').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Pagination
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_rewards': total_rewards,
        'total_disciplinary': total_disciplinary,
    }
    return render(request, 'rewards/reward_list.html', context)

@login_required
@permission_required('accounts.add_reward_discipline', raise_exception=True)
def reward_create(request):
    if request.method == 'POST':
        form = RewardsAndDisciplinaryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            record = form.save()
            # Log action
            action_type = "Reward" if record.type == 'Reward' else "Disciplinary"
            SystemLog.objects.create(
                user=request.user,
                action=f"{action_type} Record Creation",
                object_type="RewardsAndDisciplinary",
                object_id=record.id,
                details=f"Created {action_type.lower()} record for: {record.employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'{action_type} record for {record.employee.full_name} has been created successfully!')
            return redirect('reward_list')
    else:
        employee_id = request.GET.get('employee_id')
        record_type = request.GET.get('type', 'Reward')
        
        initial_data = {'type': record_type}
        if employee_id:
            initial_data['employee'] = employee_id
            
        form = RewardsAndDisciplinaryForm(initial=initial_data, user=request.user)
    
    return render(request, 'rewards/reward_form.html', {'form': form, 'title': 'Create Record'})

@login_required
@permission_required('accounts.change_reward_discipline', raise_exception=True)
def reward_edit(request, pk):
    record = get_object_or_404(RewardsAndDisciplinary, pk=pk)
    if request.method == 'POST':
        form = RewardsAndDisciplinaryForm(request.POST, request.FILES, instance=record, user=request.user)
        if form.is_valid():
            record = form.save()
            # Log action
            action_type = "Reward" if record.type == 'Reward' else "Disciplinary"
            SystemLog.objects.create(
                user=request.user,
                action=f"{action_type} Record Update",
                object_type="RewardsAndDisciplinary",
                object_id=record.id,
                details=f"Updated {action_type.lower()} record for: {record.employee.full_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'{action_type} record for {record.employee.full_name} has been updated successfully!')
            return redirect('reward_list')
    else:
        form = RewardsAndDisciplinaryForm(instance=record, user=request.user)
    
    return render(request, 'rewards/reward_form.html', {'form': form, 'title': 'Edit Record', 'record': record})

@login_required
@permission_required('accounts.delete_reward_discipline', raise_exception=True)
def reward_delete(request, pk):
    record = get_object_or_404(RewardsAndDisciplinary, pk=pk)
    if request.method == 'POST':
        employee_name = record.employee.full_name
        action_type = "Reward" if record.type == 'Reward' else "Disciplinary"
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action=f"{action_type} Record Deletion",
            object_type="RewardsAndDisciplinary",
            details=f"Deleted {action_type.lower()} record for: {employee_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        record.delete()
        messages.success(request, f'{action_type} record for {employee_name} has been deleted successfully!')
        return redirect('reward_list')
    return render(request, 'rewards/reward_confirm_delete.html', {'record': record})