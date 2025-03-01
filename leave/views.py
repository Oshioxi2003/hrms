from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import LeaveRequest
from .forms import LeaveRequestForm, LeaveApprovalForm, LeaveSearchForm
from employees.models import Employee
from accounts.models import SystemLog, User

@login_required
def leave_list(request):
    # Different behavior based on user role
    user = request.user
    if user.role == 'Employee':
        # Employees can only see their own leave requests
        leave_requests = LeaveRequest.objects.filter(employee_id=user.employee_id).order_by('-created_date')
        form = None
    else:
        # Admin, HR, and Manager can see all leave requests and filter them
        form = LeaveSearchForm(request.GET)
        leave_requests = LeaveRequest.objects.all().order_by('-created_date')
        
        if form.is_valid():
            employee = form.cleaned_data.get('employee')
            leave_type = form.cleaned_data.get('leave_type')
            status = form.cleaned_data.get('status')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            
            if employee:
                leave_requests = leave_requests.filter(employee=employee)
            
            if leave_type:
                leave_requests = leave_requests.filter(leave_type=leave_type)
            
            if status:
                leave_requests = leave_requests.filter(status=status)
            
            if start_date:
                leave_requests = leave_requests.filter(Q(start_date__gte=start_date) | Q(end_date__gte=start_date))
            
            if end_date:
                leave_requests = leave_requests.filter(Q(start_date__lte=end_date) | Q(end_date__lte=end_date))
    
    # Pagination
    paginator = Paginator(leave_requests, 10)  # Show 10 leave requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'user_role': user.role
    }
    return render(request, 'leave/leave_list.html', context)

@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            leave_request = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Leave Request Creation",
                object_type="LeaveRequest",
                object_id=leave_request.id,
                details=f"Created leave request: {leave_request.employee.full_name} - {leave_request.leave_type}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, 'Your leave request has been submitted successfully!')
            return redirect('leave_list')
    else:
        form = LeaveRequestForm(user=request.user)
    
    return render(request, 'leave/leave_form.html', {'form': form, 'title': 'Create Leave Request'})

@login_required
def leave_detail(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Check if user has permission to view this leave request
    if request.user.role == 'Employee' and request.user.employee_id != leave_request.employee_id:
        messages.error(request, "You don't have permission to view this leave request.")
        return redirect('leave_list')
    
    return render(request, 'leave/leave_detail.html', {'leave_request': leave_request})

@login_required
def leave_edit(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Check if user has permission to edit this leave request
    if request.user.role == 'Employee' and request.user.employee_id != leave_request.employee_id:
        messages.error(request, "You don't have permission to edit this leave request.")
        return redirect('leave_list')
    
    # Only allow editing if the leave request is still pending
    if leave_request.status != 'Pending':
        messages.error(request, "You can only edit pending leave requests.")
        return redirect('leave_detail', pk=leave_request.pk)
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES, instance=leave_request, user=request.user)
        if form.is_valid():
            leave_request = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Leave Request Update",
                object_type="LeaveRequest",
                object_id=leave_request.id,
                details=f"Updated leave request: {leave_request.employee.full_name} - {leave_request.leave_type}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, 'Your leave request has been updated successfully!')
            return redirect('leave_detail', pk=leave_request.pk)
    else:
        form = LeaveRequestForm(instance=leave_request, user=request.user)
    
    return render(request, 'leave/leave_form.html', {'form': form, 'title': 'Edit Leave Request', 'leave_request': leave_request})

@login_required
def leave_cancel(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Check if user has permission to cancel this leave request
    if request.user.role == 'Employee' and request.user.employee_id != leave_request.employee_id:
        messages.error(request, "You don't have permission to cancel this leave request.")
        return redirect('leave_list')
    
    # Only allow cancellation if the leave request is still pending
    if leave_request.status != 'Pending':
        messages.error(request, "You can only cancel pending leave requests.")
        return redirect('leave_detail', pk=leave_request.pk)
    
    if request.method == 'POST':
        leave_request.status = 'Cancelled'
        leave_request.save()
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Leave Request Cancellation",
            object_type="LeaveRequest",
            object_id=leave_request.id,
            details=f"Cancelled leave request: {leave_request.employee.full_name} - {leave_request.leave_type}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        messages.success(request, 'Your leave request has been cancelled successfully!')
        return redirect('leave_list')
    
    return render(request, 'leave/leave_cancel.html', {'leave_request': leave_request})

@login_required
@permission_required('accounts.approve_leave', raise_exception=True)
def leave_approve(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Only allow approval if the leave request is still pending
    if leave_request.status != 'Pending':
        messages.error(request, "You can only approve/reject pending leave requests.")
        return redirect('leave_detail', pk=leave_request.pk)
    
    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST, instance=leave_request)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.approved_by_id = request.user.employee_id
            leave_request.approval_date = timezone.now().date()
            leave_request.save()
            
            # If approved, create attendance records for the leave period
            if leave_request.status == 'Approved':
                from attendance.models import Attendance
                from datetime import timedelta
                
                current_date = leave_request.start_date
                while current_date <= leave_request.end_date:
                    # Create or update attendance record
                    Attendance.objects.update_or_create(
                        employee=leave_request.employee,
                        work_date=current_date,
                        defaults={
                            'status': 'On Leave',
                            'notes': f"{leave_request.leave_type}: {leave_request.reason}"
                        }
                    )
                    current_date += timedelta(days=1)
            
            # Log action
            action = "Leave Request Approved" if leave_request.status == 'Approved' else "Leave Request Rejected"
            SystemLog.objects.create(
                user=request.user,
                action=action,
                object_type="LeaveRequest",
                object_id=leave_request.id,
                details=f"{action}: {leave_request.employee.full_name} - {leave_request.leave_type}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'Leave request has been {leave_request.status.lower()} successfully!')
            return redirect('leave_list')
    else:
        form = LeaveApprovalForm(instance=leave_request)
    
    return render(request, 'leave/leave_approve.html', {'form': form, 'leave_request': leave_request})