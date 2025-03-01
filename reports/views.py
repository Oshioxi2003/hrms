from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from employees.models import Employee, Department
from attendance.models import Attendance
from leave.models import LeaveRequest
from payroll.models import Salary
from performance.models import EmployeeEvaluation
from django.db.models import Max, Min
from django.db.models.functions import Coalesce

@login_required
@permission_required('accounts.view_reports', raise_exception=True)
def report_dashboard(request):
    # Get current date and previous months
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Employee statistics
    total_employees = Employee.objects.filter(status='Working').count()
    new_employees = Employee.objects.filter(
        hire_date__month=current_month,
        hire_date__year=current_year
    ).count()
    resigned_employees = Employee.objects.filter(
        status='Resigned',
        updated_date__month=current_month,
        updated_date__year=current_year
    ).count()
    
    # Department distribution
    departments = Department.objects.filter(status=True)
    department_data = []
    
    for dept in departments:
        count = Employee.objects.filter(department=dept, status='Working').count()
        if count > 0:
            department_data.append({
                'name': dept.department_name,
                'count': count,
                'percentage': round((count / total_employees) * 100 if total_employees > 0 else 0, 2)
            })
    
    # Attendance statistics for current month
    _, days_in_month = calendar.monthrange(current_year, current_month)
    start_date = datetime(current_year, current_month, 1).date()
    end_date = datetime(current_year, current_month, days_in_month).date()
    
    attendance_stats = {
        'present': Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date,
            status='Present'
        ).count(),
        'absent': Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date,
            status='Absent'
        ).count(),
        'on_leave': Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date,
            status='On Leave'
        ).count(),
    }
    
    # Leave statistics for current month
    leave_stats = LeaveRequest.objects.filter(
        Q(start_date__gte=start_date, start_date__lte=end_date) |
        Q(end_date__gte=start_date, end_date__lte=end_date),
        status='Approved'
    ).aggregate(
        total_days=Sum('leave_days'),
        count=Count('id')
    )
    
    # Salary statistics for current month
    salary_stats = Salary.objects.filter(
        month=current_month,
        year=current_year
    ).aggregate(
        total_salary=Sum('net_salary'),
        avg_salary=Avg('net_salary'),
        count=Count('id')
    )
    
    # Performance statistics for current month
    performance_stats = EmployeeEvaluation.objects.filter(
        month=current_month,
        year=current_year
    ).aggregate(
        avg_achievement=Avg('achievement_rate'),
        count=Count('id')
    )
    
    context = {
        'today': today,
        'current_month': calendar.month_name[current_month],
        'current_year': current_year,
        'employee_stats': {
            'total': total_employees,
            'new': new_employees,
            'resigned': resigned_employees,
        },
        'department_data': department_data,
        'attendance_stats': attendance_stats,
        'leave_stats': leave_stats,
        'salary_stats': salary_stats,
        'performance_stats': performance_stats,
    }
    
    return render(request, 'reports/dashboard.html', context)

@login_required
@permission_required('accounts.view_reports', raise_exception=True)
def employee_report(request):
    # Filter parameters
    department_id = request.GET.get('department')
    position_id = request.GET.get('position')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset
    employees = Employee.objects.all().order_by('full_name')
    
    # Apply filters
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if position_id:
        employees = employees.filter(position_id=position_id)
    
    if status:
        employees = employees.filter(status=status)
    
    if date_from:
        employees = employees.filter(hire_date__gte=date_from)
    
    if date_to:
        employees = employees.filter(hire_date__lte=date_to)
    
    # Get departments and positions for filter dropdowns
    departments = Department.objects.filter(status=True)
    
    from employees.models import Position
    positions = Position.objects.filter(status=True)
    
    # Export to CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="employee_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Employee ID', 'Full Name', 'Gender', 'Date of Birth', 'ID Card',
            'Email', 'Phone', 'Department', 'Position', 'Education Level',
            'Hire Date', 'Status', 'Address'
        ])
        
        for employee in employees:
            writer.writerow([
                employee.id,
                employee.full_name,
                employee.gender,
                employee.date_of_birth,
                employee.id_card,
                employee.email,
                employee.phone,
                employee.department.department_name if employee.department else '',
                employee.position.position_name if employee.position else '',
                employee.education.education_name if employee.education else '',
                employee.hire_date,
                employee.status,
                employee.address
            ])
        
        return response
    
    context = {
        'employees': employees,
        'departments': departments,
        'positions': positions,
        'selected_department': department_id,
        'selected_position': position_id,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'reports/employee_report.html', context)

@login_required
@permission_required('accounts.view_reports', raise_exception=True)
def attendance_report(request):
    # Filter parameters
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    date_from = request.GET.get('date_from', (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', timezone.now().date().strftime('%Y-%m-%d'))
    status = request.GET.get('status')
    
    # Base queryset
    attendances = Attendance.objects.all().order_by('-work_date')
    
    # Apply filters
    if employee_id:
        attendances = attendances.filter(employee_id=employee_id)
    
    if department_id:
        attendances = attendances.filter(employee__department_id=department_id)
    
    if date_from:
        attendances = attendances.filter(work_date__gte=date_from)
    
    if date_to:
        attendances = attendances.filter(work_date__lte=date_to)
    
    if status:
        attendances = attendances.filter(status=status)
    
    # Get employees and departments for filter dropdowns
    employees = Employee.objects.filter(status='Working')
    departments = Department.objects.filter(status=True)
    
    # Calculate statistics
    stats = {
        'total': attendances.count(),
        'present': attendances.filter(status='Present').count(),
        'absent': attendances.filter(status='Absent').count(),
        'on_leave': attendances.filter(status='On Leave').count(),
        'overtime_hours': attendances.aggregate(Sum('overtime_hours'))['overtime_hours__sum'] or 0,
    }
    
    # Export to CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Employee ID', 'Employee Name', 'Department', 'Work Date',
            'Time In', 'Time Out', 'Shift', 'Actual Work Hours',
            'Overtime Hours', 'Status', 'Notes'
        ])
        
        for attendance in attendances:
            writer.writerow([
                attendance.employee.id,
                attendance.employee.full_name,
                attendance.employee.department.department_name if attendance.employee.department else '',
                attendance.work_date,
                attendance.time_in,
                attendance.time_out,
                attendance.shift.shift_name if attendance.shift else '',
                attendance.actual_work_hours,
                attendance.overtime_hours,
                attendance.status,
                attendance.notes
            ])
        
        return response
    
    context = {
        'attendances': attendances,
        'employees': employees,
        'departments': departments,
        'selected_employee': employee_id,
        'selected_department': department_id,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'stats': stats,
    }
    return render(request, 'reports/attendance_report.html', context)

@login_required
@permission_required('accounts.view_reports', raise_exception=True)
def leave_report(request):
    # Filter parameters
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    leave_type = request.GET.get('leave_type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from', (timezone.now().date() - timedelta(days=90)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', timezone.now().date().strftime('%Y-%m-%d'))
    
    # Base queryset
    from leave.models import LeaveRequest
    leave_requests = LeaveRequest.objects.all().order_by('-start_date')
    
    # Apply filters
    if employee_id:
        leave_requests = leave_requests.filter(employee_id=employee_id)
    
    if department_id:
        leave_requests = leave_requests.filter(employee__department_id=department_id)
    
    if leave_type:
        leave_requests = leave_requests.filter(leave_type=leave_type)
    
    if status:
        leave_requests = leave_requests.filter(status=status)
    
    if date_from:
        leave_requests = leave_requests.filter(Q(start_date__gte=date_from) | Q(end_date__gte=date_from))
    
    if date_to:
        leave_requests = leave_requests.filter(Q(start_date__lte=date_to) | Q(end_date__lte=date_to))
    
    # Get employees and departments for filter dropdowns
    employees = Employee.objects.filter(status='Working')
    departments = Department.objects.filter(status=True)
    
    # Calculate statistics
    stats = {
        'total_requests': leave_requests.count(),
        'approved_requests': leave_requests.filter(status='Approved').count(),
        'rejected_requests': leave_requests.filter(status='Rejected').count(),
        'pending_requests': leave_requests.filter(status='Pending').count(),
        'total_days': leave_requests.filter(status='Approved').aggregate(Sum('leave_days'))['leave_days__sum'] or 0,
    }
    
    # Export to CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="leave_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Employee ID', 'Employee Name', 'Department', 'Leave Type',
            'Start Date', 'End Date', 'Leave Days', 'Status',
            'Approved By', 'Approval Date', 'Reason'
        ])
        
        for leave in leave_requests:
            writer.writerow([
                leave.employee.id,
                leave.employee.full_name,
                leave.employee.department.department_name if leave.employee.department else '',
                leave.leave_type,
                leave.start_date,
                leave.end_date,
                leave.leave_days,
                leave.status,
                leave.approved_by.full_name if leave.approved_by else '',
                leave.approval_date,
                leave.reason
            ])
        
        return response
    
    context = {
        'leave_requests': leave_requests,
        'employees': employees,
        'departments': departments,
        'leave_types': LeaveRequest.LEAVE_TYPES,
        'status_choices': LeaveRequest.STATUS_CHOICES,
        'selected_employee': employee_id,
        'selected_department': department_id,
        'selected_leave_type': leave_type,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'stats': stats,
    }
    return render(request, 'reports/leave_report.html', context)

@login_required
@permission_required('accounts.view_reports', raise_exception=True)
def salary_report(request):
    # Filter parameters
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    month = request.GET.get('month')
    year = request.GET.get('year', timezone.now().year)
    is_paid = request.GET.get('is_paid')
    
    # Base queryset
    from payroll.models import Salary
    salaries = Salary.objects.all().order_by('-year', '-month', 'employee__full_name')
    
    # Apply filters
    if employee_id:
        salaries = salaries.filter(employee_id=employee_id)
    
    if department_id:
        salaries = salaries.filter(employee__department_id=department_id)
    
    if month:
        salaries = salaries.filter(month=month)
    
    if year:
        salaries = salaries.filter(year=year)
    
    if is_paid is not None:
        is_paid_bool = is_paid == 'True'
        salaries = salaries.filter(is_paid=is_paid_bool)
    
    # Get employees and departments for filter dropdowns
    employees = Employee.objects.filter(status='Working')
    departments = Department.objects.filter(status=True)
    
    # Calculate statistics
    stats = {
        'total_salaries': salaries.count(),
        'total_amount': salaries.aggregate(Sum('net_salary'))['net_salary__sum'] or 0,
        'avg_salary': salaries.aggregate(Avg('net_salary'))['net_salary__avg'] or 0,
        'total_base_salary': salaries.aggregate(Sum('base_salary'))['base_salary__sum'] or 0,
        'total_deductions': salaries.aggregate(
            total=Sum('income_tax') + Sum('social_insurance') + Sum('health_insurance') + 
            Sum('unemployment_insurance') + Sum('deductions') + Sum('advance')
        )['total'] or 0,
    }
    
    # Export to CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="salary_report_{year}_{month if month else "all"}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Employee ID', 'Employee Name', 'Department', 'Month', 'Year',
            'Work Days', 'Leave Days', 'Overtime Hours', 'Base Salary',
            'Allowance', 'Bonus', 'Income Tax', 'Social Insurance',
            'Health Insurance', 'Unemployment Insurance', 'Deductions',
            'Advance', 'Net Salary', 'Payment Status', 'Payment Date'
        ])
        
        for salary in salaries:
            writer.writerow([
                salary.employee.id,
                salary.employee.full_name,
                salary.employee.department.department_name if salary.employee.department else '',
                salary.month,
                salary.year,
                salary.work_days,
                salary.leave_days,
                salary.overtime_hours,
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
                'Paid' if salary.is_paid else 'Unpaid',
                salary.payment_date
            ])
        
        return response
    
    context = {
        'salaries': salaries,
        'employees': employees,
        'departments': departments,
        'selected_employee': employee_id,
        'selected_department': department_id,
        'selected_month': month,
        'selected_year': year,
        'selected_is_paid': is_paid,
        'stats': stats,
    }
    return render(request, 'reports/salary_report.html', context)

@login_required
@permission_required('accounts.view_reports', raise_exception=True)
def performance_report(request):
    # Filter parameters
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    month = request.GET.get('month')
    year = request.GET.get('year', timezone.now().year)
    kpi_id = request.GET.get('kpi')
    
    # Base queryset
    from performance.models import EmployeeEvaluation, KPI
    evaluations = EmployeeEvaluation.objects.all().order_by('-year', '-month', 'employee__full_name')
    
    # Apply filters
    if employee_id:
        evaluations = evaluations.filter(employee_id=employee_id)
    
    if department_id:
        evaluations = evaluations.filter(employee__department_id=department_id)
    
    if month:
        evaluations = evaluations.filter(month=month)
    
    if year:
        evaluations = evaluations.filter(year=year)
    
    if kpi_id:
        evaluations = evaluations.filter(kpi_id=kpi_id)
    
    # Get employees, departments, and KPIs for filter dropdowns
    employees = Employee.objects.filter(status='Working')
    departments = Department.objects.filter(status=True)
    kpis = KPI.objects.all()
    
    # Calculate statistics
    stats = {
        'total_evaluations': evaluations.count(),
        'avg_achievement': evaluations.aggregate(Avg('achievement_rate'))['achievement_rate__avg'] or 0,
        'max_achievement': evaluations.aggregate(Max('achievement_rate'))['achievement_rate__max'] or 0,
        'min_achievement': evaluations.aggregate(Min('achievement_rate'))['achievement_rate__min'] or 0,
    }
    
    # Export to CSV if requested
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="performance_report_{year}_{month if month else "all"}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Employee ID', 'Employee Name', 'Department', 'KPI Name', 'KPI Type',
            'Month', 'Year', 'Result', 'Target', 'Achievement Rate (%)',
            'Feedback', 'Evaluated By', 'Evaluation Date'
        ])
        
        for eval in evaluations:
            writer.writerow([
                eval.employee.id,
                eval.employee.full_name,
                eval.employee.department.department_name if eval.employee.department else '',
                eval.kpi.kpi_name,
                eval.kpi.kpi_type,
                eval.month,
                eval.year,
                eval.result,
                eval.target,
                eval.achievement_rate,
                eval.feedback,
                eval.evaluated_by.full_name if eval.evaluated_by else '',
                eval.evaluation_date
            ])
        
        return response
    
    context = {
        'evaluations': evaluations,
        'employees': employees,
        'departments': departments,
        'kpis': kpis,
        'selected_employee': employee_id,
        'selected_department': department_id,
        'selected_month': month,
        'selected_year': year,
        'selected_kpi': kpi_id,
        'stats': stats,
    }
    return render(request, 'reports/performance_report.html', context)