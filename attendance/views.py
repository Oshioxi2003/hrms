from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import WorkShift, ShiftAssignment, Attendance
from .forms import WorkShiftForm, ShiftAssignmentForm, AttendanceForm, AttendanceSearchForm, BulkAttendanceForm
from employees.models import Employee
from accounts.models import SystemLog

# Work Shift Views
@login_required
@permission_required('accounts.view_attendance', raise_exception=True)
def shift_list(request):
    shifts = WorkShift.objects.all()
    query = request.GET.get('q')
    if query:
        shifts = shifts.filter(shift_name__icontains=query)
    
    status = request.GET.get('status')
    if status:
        if status == 'active':
            shifts = shifts.filter(status=True)
        elif status == 'inactive':
            shifts = shifts.filter(status=False)
    
    return render(request, 'attendance/shift_list.html', {'shifts': shifts, 'selected_status': status})

@login_required
@permission_required('accounts.add_attendance', raise_exception=True)
def shift_create(request):
    if request.method == 'POST':
        form = WorkShiftForm(request.POST)
        if form.is_valid():
            shift = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Work Shift Creation",
                object_type="WorkShift",
                object_id=shift.id,
                details=f"Created work shift: {shift.shift_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Work shift {shift.shift_name} has been created successfully!')
            return redirect('shift_list')
    else:
        form = WorkShiftForm()
    return render(request, 'attendance/shift_form.html', {'form': form, 'title': 'Create Work Shift'})

@login_required
@permission_required('accounts.change_attendance', raise_exception=True)
def shift_edit(request, pk):
    shift = get_object_or_404(WorkShift, pk=pk)
    if request.method == 'POST':
        form = WorkShiftForm(request.POST, instance=shift)
        if form.is_valid():
            shift = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Work Shift Update",
                object_type="WorkShift",
                object_id=shift.id,
                details=f"Updated work shift: {shift.shift_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Work shift {shift.shift_name} has been updated successfully!')
            return redirect('shift_list')
    else:
        form = WorkShiftForm(instance=shift)
    return render(request, 'attendance/shift_form.html', {'form': form, 'title': 'Edit Work Shift', 'shift': shift})

@login_required
@permission_required('accounts.delete_attendance', raise_exception=True)
def shift_delete(request, pk):
    shift = get_object_or_404(WorkShift, pk=pk)
    if request.method == 'POST':
        shift_name = shift.shift_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Work Shift Deletion",
            object_type="WorkShift",
            details=f"Deleted work shift: {shift_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        shift.delete()
        messages.success(request, f'Work shift {shift_name} has been deleted successfully!')
        return redirect('shift_list')
    return render(request, 'attendance/shift_confirm_delete.html', {'shift': shift})

# Shift Assignment Views
@login_required
@permission_required('accounts.view_attendance', raise_exception=True)
def assignment_list(request):
    assignments = ShiftAssignment.objects.all().order_by('-effective_date')
    query = request.GET.get('q')
    if query:
        assignments = assignments.filter(
            Q(employee__full_name__icontains=query) | 
            Q(shift__shift_name__icontains=query)
        )
    
    status = request.GET.get('status')
    if status:
        assignments = assignments.filter(status=status)
    
    # Pagination
    paginator = Paginator(assignments, 20)  # Show 20 assignments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'attendance/assignment_list.html', {
        'page_obj': page_obj,
        'selected_status': status
    })

@login_required
@permission_required('accounts.add_attendance', raise_exception=True)
def assignment_create(request):
    if request.method == 'POST':
        form = ShiftAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Shift Assignment Creation",
                object_type="ShiftAssignment",
                object_id=assignment.id,
                details=f"Created shift assignment: {assignment.employee.full_name} to {assignment.shift.shift_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Shift assignment for {assignment.employee.full_name} has been created successfully!')
            return redirect('assignment_list')
    else:
        employee_id = request.GET.get('employee_id')
        if employee_id:
            form = ShiftAssignmentForm(initial={'employee': employee_id})
        else:
            form = ShiftAssignmentForm()
    return render(request, 'attendance/assignment_form.html', {'form': form, 'title': 'Create Shift Assignment'})

@login_required
@permission_required('accounts.change_attendance', raise_exception=True)
def assignment_edit(request, pk):
    assignment = get_object_or_404(ShiftAssignment, pk=pk)
    if request.method == 'POST':
        form = ShiftAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Shift Assignment Update",
                object_type="ShiftAssignment",
                object_id=assignment.id,
                details=f"Updated shift assignment: {assignment.employee.full_name} to {assignment.shift.shift_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Shift assignment for {assignment.employee.full_name} has been updated successfully!')
            return redirect('assignment_list')
    else:
        form = ShiftAssignmentForm(instance=assignment)
    return render(request, 'attendance/assignment_form.html', {'form': form, 'title': 'Edit Shift Assignment', 'assignment': assignment})

@login_required
@permission_required('accounts.delete_attendance', raise_exception=True)
def assignment_delete(request, pk):
    assignment = get_object_or_404(ShiftAssignment, pk=pk)
    if request.method == 'POST':
        emp_name = assignment.employee.full_name
        shift_name = assignment.shift.shift_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Shift Assignment Deletion",
            object_type="ShiftAssignment",
            details=f"Deleted shift assignment: {emp_name} from {shift_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        assignment.delete()
        messages.success(request, f'Shift assignment for {emp_name} has been deleted successfully!')
        return redirect('assignment_list')
    return render(request, 'attendance/assignment_confirm_delete.html', {'assignment': assignment})

# Attendance Views
@login_required
@permission_required('accounts.view_attendance', raise_exception=True)
def attendance_list(request):
    form = AttendanceSearchForm(request.GET)
    attendances = Attendance.objects.all().order_by('-work_date')
    
    if form.is_valid():
        employee = form.cleaned_data.get('employee')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        status = form.cleaned_data.get('status')
        
        if employee:
            attendances = attendances.filter(employee=employee)
        
        if start_date:
            attendances = attendances.filter(work_date__gte=start_date)
        
        if end_date:
            attendances = attendances.filter(work_date__lte=end_date)
        
        if status:
            attendances = attendances.filter(status=status)
    
    # Pagination
    paginator = Paginator(attendances, 30)  # Show 30 attendance records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj
    }
    return render(request, 'attendance/attendance_list.html', context)

@login_required
@permission_required('accounts.add_attendance', raise_exception=True)
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Attendance Record Creation",
                object_type="Attendance",
                object_id=attendance.id,
                details=f"Created attendance record for: {attendance.employee.full_name} on {attendance.work_date}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Attendance record for {attendance.employee.full_name} on {attendance.work_date} has been created successfully!')
            return redirect('attendance_list')
    else:
        employee_id = request.GET.get('employee_id')
        work_date = request.GET.get('work_date', timezone.now().date())
        
        initial_data = {'work_date': work_date}
        if employee_id:
            initial_data['employee'] = employee_id
            
            # Try to get the employee's assigned shift
            try:
                assignment = ShiftAssignment.objects.filter(
                    employee_id=employee_id,
                    effective_date__lte=work_date,
                    status='Active'
                ).filter(
                    Q(end_date__isnull=True) | Q(end_date__gte=work_date)
                ).latest('effective_date')
                
                initial_data['shift'] = assignment.shift.id
            except ShiftAssignment.DoesNotExist:
                pass
        
        form = AttendanceForm(initial=initial_data)
    return render(request, 'attendance/attendance_form.html', {'form': form, 'title': 'Create Attendance Record'})

@login_required
@permission_required('accounts.change_attendance', raise_exception=True)
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Attendance Record Update",
                object_type="Attendance",
                object_id=attendance.id,
                details=f"Updated attendance record for: {attendance.employee.full_name} on {attendance.work_date}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Attendance record for {attendance.employee.full_name} on {attendance.work_date} has been updated successfully!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'attendance/attendance_form.html', {'form': form, 'title': 'Edit Attendance Record', 'attendance': attendance})

@login_required
@permission_required('accounts.delete_attendance', raise_exception=True)
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        emp_name = attendance.employee.full_name
        work_date = attendance.work_date
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Attendance Record Deletion",
            object_type="Attendance",
            details=f"Deleted attendance record for: {emp_name} on {work_date}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        attendance.delete()
        messages.success(request, f'Attendance record for {emp_name} on {work_date} has been deleted successfully!')
        return redirect('attendance_list')
    return render(request, 'attendance/attendance_confirm_delete.html', {'attendance': attendance})

@login_required
@permission_required('accounts.add_attendance', raise_exception=True)
def bulk_attendance(request):
    employees = Employee.objects.filter(status='Working').order_by('full_name')
    
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST, employees=employees)
        if form.is_valid():
            work_date = form.cleaned_data['work_date']
            
            for employee in employees:
                status = form.cleaned_data.get(f'status_{employee.id}')
                time_in = form.cleaned_data.get(f'time_in_{employee.id}')
                time_out = form.cleaned_data.get(f'time_out_{employee.id}')
                shift = form.cleaned_data.get(f'shift_{employee.id}')
                notes = form.cleaned_data.get(f'notes_{employee.id}')
                
                # Check if an attendance record already exists
                attendance, created = Attendance.objects.update_or_create(
                    employee=employee,
                    work_date=work_date,
                    defaults={
                        'status': status,
                        'time_in': time_in,
                        'time_out': time_out,
                        'shift': shift,
                        'notes': notes
                    }
                )
            
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Bulk Attendance Creation",
                details=f"Created/updated bulk attendance records for {work_date}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Attendance records for {work_date} have been saved successfully!')
            return redirect('attendance_list')
    else:
        # Get the date from query param or use today
        work_date = request.GET.get('date', timezone.now().date())
        if isinstance(work_date, str):
            try:
                work_date = datetime.strptime(work_date, '%Y-%m-%d').date()
            except ValueError:
                work_date = timezone.now().date()
        
        # Initialize form with today's date
        form = BulkAttendanceForm(initial={'work_date': work_date}, employees=employees)
        
        # Pre-populate form with existing attendance records for this date
        existing_records = {
            a.employee_id: a for a in Attendance.objects.filter(work_date=work_date)
        }
        
        for employee in employees:
            if employee.id in existing_records:
                record = existing_records[employee.id]
                form.fields[f'status_{employee.id}'].initial = record.status
                form.fields[f'time_in_{employee.id}'].initial = record.time_in
                form.fields[f'time_out_{employee.id}'].initial = record.time_out
                form.fields[f'shift_{employee.id}'].initial = record.shift.id if record.shift else None
                form.fields[f'notes_{employee.id}'].initial = record.notes
            else:
                # Try to get the employee's assigned shift
                try:
                    assignment = ShiftAssignment.objects.filter(
                        employee=employee,
                        effective_date__lte=work_date,
                        status='Active'
                    ).filter(
                        Q(end_date__isnull=True) | Q(end_date__gte=work_date)
                    ).latest('effective_date')
                    
                    form.fields[f'shift_{employee.id}'].initial = assignment.shift.id
                except ShiftAssignment.DoesNotExist:
                    pass
    # Prepare context with employees and form
    context = {
        'form': form,
        'employees': employees,
        'work_date': work_date,
        'prev_date': (work_date - timedelta(days=1)).strftime('%Y-%m-%d'),
        'next_date': (work_date + timedelta(days=1)).strftime('%Y-%m-%d'),
        'today': timezone.now().date().strftime('%Y-%m-%d')
    }
    return render(request, 'attendance/bulk_attendance.html', context)