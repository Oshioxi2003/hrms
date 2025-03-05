from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg, Q, F, Value, FloatField
from django.utils import timezone
import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from employees.models import Employee, Department, Position
from attendance.models import Attendance
from leave.models import LeaveRequest
from payroll.models import Salary
from performance.models import EmployeeEvaluation, KPI
from django.db.models import Max, Min
from django.db.models.functions import Coalesce, TruncMonth

import json

@login_required
@permission_required('accounts.view_reports', raise_exception=True)
def report_dashboard(request):
    # Get current date and previous months
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Allow selecting different months for the dashboard
    selected_month = request.GET.get('month', str(current_month))
    selected_year = request.GET.get('year', str(current_year))
    
    try:
        selected_month = int(selected_month)
        selected_year = int(selected_year)
        # Validate month and year
        if selected_month < 1 or selected_month > 12:
            selected_month = current_month
        if selected_year < 2000 or selected_year > 2100:
            selected_year = current_year
    except (ValueError, TypeError):
        selected_month = current_month
        selected_year = current_year
    
    # Calculate start and end dates for the selected month
    _, days_in_month = calendar.monthrange(selected_year, selected_month)
    start_date = datetime(selected_year, selected_month, 1).date()
    end_date = datetime(selected_year, selected_month, days_in_month).date()
    
    # Employee statistics
    try:
        total_employees = Employee.objects.filter(status='Working').count()
        
        new_employees = Employee.objects.filter(
            hire_date__gte=start_date,
            hire_date__lte=end_date
        ).count()
        
        # For resigned employees, check status change date if available, otherwise use updated_date
        resigned_employees = Employee.objects.filter(
            status='Resigned',
            updated_date__gte=start_date,
            updated_date__lte=end_date
        ).count()
    except Exception as e:
        print(f"Error fetching employee statistics: {e}")
        total_employees = 0
        new_employees = 0
        resigned_employees = 0
    
    # Department distribution
    try:
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
        
        # Sort by count descending
        department_data = sorted(department_data, key=lambda x: x['count'], reverse=True)
    except Exception as e:
        print(f"Error fetching department distribution: {e}")
        department_data = []
    
    # Attendance statistics for selected month
    try:
        present_count = Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date,
            status='Present'
        ).count()
        
        absent_count = Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date,
            status='Absent'
        ).count()
        
        on_leave_count = Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date,
            status='On Leave'
        ).count()
        
        attendance_stats = {
            'present': present_count,
            'absent': absent_count,
            'on_leave': on_leave_count,
        }
        
        # Calculate total working days in the month
        working_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday (0-4)
                working_days += 1
            current_date += timedelta(days=1)
        
        # Calculate attendance rate
        total_attendance_records = sum(attendance_stats.values())
        expected_records = total_employees * working_days
        attendance_rate = (present_count / expected_records * 100) if expected_records > 0 else 0
        
        attendance_stats['working_days'] = working_days
        attendance_stats['attendance_rate'] = round(attendance_rate, 2)
        
        # Get total overtime hours
        overtime_result = Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date
        ).aggregate(
            total=Sum('overtime_hours')
        )
        
        attendance_stats['total_overtime_hours'] = overtime_result['total'] or 0
    except Exception as e:
        print(f"Error fetching attendance statistics: {e}")
        attendance_stats = {'present': 0, 'absent': 0, 'on_leave': 0, 'working_days': 0, 'attendance_rate': 0, 'total_overtime_hours': 0}
    
    # Leave statistics for selected month
    try:
        leave_query = LeaveRequest.objects.filter(
            Q(start_date__gte=start_date, start_date__lte=end_date) |
            Q(end_date__gte=start_date, end_date__lte=end_date) |
            Q(start_date__lte=start_date, end_date__gte=end_date),
            status='Approved'
        )
        
        leave_stats = {
            'total_days': leave_query.aggregate(Sum('leave_days'))['leave_days__sum'] or 0,
            'count': leave_query.count()
        }
        
        # Get leave by type
        leave_by_type = leave_query.values('leave_type').annotate(
            count=Count('id'),
            days=Sum('leave_days') or 0
        ).order_by('-days')
        
        leave_stats['by_type'] = list(leave_by_type)
    except Exception as e:
        print(f"Error fetching leave statistics: {e}")
        leave_stats = {'total_days': 0, 'count': 0, 'by_type': []}
    
    # Salary statistics for selected month
    try:
        salary_query = Salary.objects.filter(
            month=selected_month,
            year=selected_year
        )
        
        # Calculate totals
        salary_totals = salary_query.aggregate(
            total_salary=Sum('net_salary') or 0,
            avg_salary=Avg('net_salary') or 0,
            total_base=Sum('base_salary') or 0,
            total_allowance=Sum('allowance') or 0,
            total_bonus=Sum('bonus') or 0,
            total_income_tax=Sum('income_tax') or 0,
            total_social_insurance=Sum('social_insurance') or 0,
            total_health_insurance=Sum('health_insurance') or 0,
            total_unemployment=Sum('unemployment_insurance') or 0,
            total_deductions=Sum('deductions') or 0,
            total_advance=Sum('advance') or 0
        )
        
        salary_stats = {
            'total_salary': salary_totals['total_salary'] or 0,
            'avg_salary': salary_totals['avg_salary'] or 0,
            'count': salary_query.count(),
            'total_base': salary_totals['total_base'] or 0,
            'total_allowance': salary_totals['total_allowance'] or 0,
            'total_bonus': salary_totals['total_bonus'] or 0,
            'total_deductions': (
                (salary_totals['total_income_tax'] or 0) +
                (salary_totals['total_social_insurance'] or 0) +
                (salary_totals['total_health_insurance'] or 0) +
                (salary_totals['total_unemployment'] or 0) +
                (salary_totals['total_deductions'] or 0) +
                (salary_totals['total_advance'] or 0)
            )
        }
        
        # Calculate salary distribution
        salary_ranges = [
            {'min': 0, 'max': 5000000, 'label': 'Under 5M', 'count': 0},
            {'min': 5000000, 'max': 10000000, 'label': '5M-10M', 'count': 0},
            {'min': 10000000, 'max': 15000000, 'label': '10M-15M', 'count': 0},
            {'min': 15000000, 'max': 20000000, 'label': '15M-20M', 'count': 0},
            {'min': 20000000, 'max': float('inf'), 'label': 'Over 20M', 'count': 0}
        ]
        
        for salary in salary_query:
            for range_info in salary_ranges:
                if range_info['min'] <= salary.net_salary < range_info['max']:
                    range_info['count'] += 1
                    break
        
        salary_stats['distribution'] = salary_ranges
    except Exception as e:
        print(f"Error fetching salary statistics: {e}")
        salary_stats = {
            'total_salary': 0, 'avg_salary': 0, 'count': 0, 
            'total_base': 0, 'total_allowance': 0, 'total_bonus': 0,
            'total_deductions': 0, 'distribution': []
        }
    
    # Performance statistics for selected month
    try:
        # First, get basic statistics
        performance_stats = {
            'avg_achievement': 0,
            'count': 0,
            'count_above_target': 0,
            'count_below_target': 0,
            'by_department': []
        }
        
        # Get evaluations for the selected month
        evaluations = EmployeeEvaluation.objects.filter(
            month=selected_month,
            year=selected_year
        )
        
        # Calculate statistics if there are evaluations
        if evaluations.exists():
            # Average achievement rate
            avg_achievement = evaluations.aggregate(
                avg=Avg('achievement_rate')
            )['avg'] or 0
            
            # Count of evaluations
            total_count = evaluations.count()
            
            # Count above/below target
            above_target = evaluations.filter(achievement_rate__gte=100).count()
            below_target = evaluations.filter(achievement_rate__lt=100).count()
            
            # Update the statistics dictionary
            performance_stats['avg_achievement'] = avg_achievement
            performance_stats['count'] = total_count
            performance_stats['count_above_target'] = above_target
            performance_stats['count_below_target'] = below_target
            
            # Calculate performance by department
            performance_by_dept = (
                evaluations.values('employee__department__department_name')
                .annotate(
                    avg_achievement=Avg('achievement_rate') or 0,
                    count=Count('id')
                )
                .order_by('-avg_achievement')
            )
            
            performance_stats['by_department'] = list(performance_by_dept)
    except Exception as e:
        print(f"Error fetching performance statistics: {e}")
        performance_stats = {
            'avg_achievement': 0, 
            'count': 0, 
            'count_above_target': 0, 
            'count_below_target': 0,
            'by_department': []
        }
    
    # Prepare month/year selection options
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = range(current_year - 5, current_year + 1)
    
    # Prepare trend data for the last 6 months
    trend_months = []
    employee_trend = []
    attendance_trend = []
    
    for i in range(5, -1, -1):
        try:
            trend_date = today - relativedelta(months=i)
            trend_month = trend_date.month
            trend_year = trend_date.year
            trend_month_name = calendar.month_name[trend_month][:3] + " " + str(trend_year)
            trend_months.append(trend_month_name)
            
            # Employee count for this month - Fixed query
            working_employees = Employee.objects.filter(
                hire_date__lte=trend_date,
                status='Working'
            ).count()
            
            resigned_employees = Employee.objects.filter(
                hire_date__lte=trend_date,
                status='Resigned',
                updated_date__gt=trend_date
            ).count()
            
            employee_count = working_employees + resigned_employees
            employee_trend.append(employee_count)
            
            # Attendance rate for this month
            month_start = datetime(trend_year, trend_month, 1).date()
            _, days_in_month = calendar.monthrange(trend_year, trend_month)
            month_end = datetime(trend_year, trend_month, days_in_month).date()
            
            present_count = Attendance.objects.filter(
                work_date__gte=month_start,
                work_date__lte=month_end,
                status='Present'
            ).count()
            
            # Calculate working days in the month
            working_days = 0
            current_date = month_start
            while current_date <= month_end:
                if current_date.weekday() < 5:  # Monday to Friday (0-4)
                    working_days += 1
                current_date += timedelta(days=1)
            
            expected_attendance = employee_count * working_days
            attendance_rate = (present_count / expected_attendance * 100) if expected_attendance > 0 else 0
            attendance_trend.append(round(attendance_rate, 2))
        except Exception as e:
            print(f"Error calculating trend data for month -{i}: {e}")
            trend_months.append(f"Month -{i}")
            employee_trend.append(0)
            attendance_trend.append(0)
    
    context = {
        'today': today,
        'current_month': calendar.month_name[current_month],
        'current_year': current_year,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_month_name': calendar.month_name[selected_month],
        'months': months,
        'years': years,
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
        'trend_data': {
            'months': json.dumps(trend_months),
            'employee_trend': json.dumps(employee_trend),
            'attendance_trend': json.dumps(attendance_trend),
        }
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


@login_required
def dashboard(request):
    try:
        # Get current date information
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year
        
        # Calculate start and end dates for the current month
        _, days_in_month = calendar.monthrange(current_year, current_month)
        start_date = datetime(current_year, current_month, 1).date()
        end_date = datetime(current_year, current_month, days_in_month).date()
        
        # Employee Statistics - Using select_related to reduce queries
        total_employees = Employee.objects.filter(status='Working').count()
        
        employee_stats = {
            'total': total_employees,
            'new': Employee.objects.filter(
                hire_date__gte=start_date,
                hire_date__lte=end_date
            ).count(),
            'resigned': Employee.objects.filter(
                status='Resigned',
                updated_date__gte=start_date,
                updated_date__lte=end_date
            ).count()
        }
        
        # Department Distribution - Using prefetch_related to optimize
        departments = Department.objects.filter(status=True).prefetch_related('employee_set')
        department_data = []
        
        for dept in departments:
            count = dept.employee_set.filter(status='Working').count()
            if count > 0:
                department_data.append({
                    'name': dept.department_name,
                    'count': count,
                    'percentage': round((count / total_employees) * 100 if total_employees > 0 else 0, 2)
                })
        
        # Sort by count descending
        department_data = sorted(department_data, key=lambda x: x['count'], reverse=True)
        
        # Attendance Statistics - Using aggregate for better performance
        attendance_counts = Attendance.objects.filter(
            work_date__gte=start_date,
            work_date__lte=end_date
        ).values('status').annotate(count=Count('id'))
        
        attendance_stats = {
            'present': 0,
            'absent': 0,
            'on_leave': 0
        }
        
        for item in attendance_counts:
            if item['status'] in attendance_stats:
                attendance_stats[item['status'].lower()] = item['count']
        
        # Leave Statistics
        leave_stats = LeaveRequest.objects.filter(
            status='Approved',
            start_date__gte=start_date,
            end_date__lte=end_date
        ).aggregate(
            count=Count('id'),
            total_days=Sum('leave_days')
        )
        
        if leave_stats['total_days'] is None:
            leave_stats['total_days'] = 0
        
        # Salary Statistics
        salary_stats = Salary.objects.filter(
            month=current_month,
            year=current_year
        ).aggregate(
            total_salary=Sum('net_salary'),
            avg_salary=Avg('net_salary')
        )
        
        if salary_stats['total_salary'] is None:
            salary_stats['total_salary'] = 0
        if salary_stats['avg_salary'] is None:
            salary_stats['avg_salary'] = 0
        
        # Performance Statistics
        performance_stats = EmployeeEvaluation.objects.filter(
            month=current_month,
            year=current_year
        ).aggregate(
            count=Count('id'),
            avg_achievement=Avg('achievement_rate')
        )
        
        if performance_stats['count'] is None:
            performance_stats['count'] = 0
        if performance_stats['avg_achievement'] is None:
            performance_stats['avg_achievement'] = 0
        
        context = {
            'current_month': calendar.month_name[current_month],
            'current_year': current_year,
            'employee_stats': employee_stats,
            'department_data': department_data,
            'attendance_stats': attendance_stats,
            'leave_stats': leave_stats,
            'salary_stats': salary_stats,
            'performance_stats': performance_stats
        }
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard error: {str(e)}")
        
        # Provide a minimal context with error information
        context = {
            'current_month': calendar.month_name[timezone.now().month],
            'current_year': timezone.now().year,
            'error_message': "There was an error loading the dashboard data. Please try again later.",
            'employee_stats': {'total': 0, 'new': 0, 'resigned': 0},
            'department_data': [],
            'attendance_stats': {'present': 0, 'absent': 0, 'on_leave': 0},
            'leave_stats': {'count': 0, 'total_days': 0},
            'salary_stats': {'total_salary': 0, 'avg_salary': 0},
            'performance_stats': {'count': 0, 'avg_achievement': 0}
        }
        
        return render(request, 'dashboard.html', context)
