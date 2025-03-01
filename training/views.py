from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import TrainingCourse, TrainingParticipation
from .forms import TrainingCourseForm, TrainingParticipationForm, ParticipationUpdateForm, BulkParticipationForm
from employees.models import Employee
from accounts.models import SystemLog

# Training Course Views
@login_required
@permission_required('accounts.view_training', raise_exception=True)
def course_list(request):
    courses = TrainingCourse.objects.all().order_by('-start_date')
    
    # Filter by course name
    course_name = request.GET.get('course_name')
    if course_name:
        courses = courses.filter(course_name__icontains=course_name)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        courses = courses.filter(status=status)
    
    # Pagination
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': TrainingCourse.STATUS_CHOICES,
        'selected_status': status,
    }
    return render(request, 'training/course_list.html', context)

@login_required
@permission_required('accounts.view_training', raise_exception=True)
def course_detail(request, pk):
    course = get_object_or_404(TrainingCourse, pk=pk)
    participants = TrainingParticipation.objects.filter(course=course)
    
    context = {
        'course': course,
        'participants': participants,
    }
    return render(request, 'training/course_detail.html', context)

@login_required
@permission_required('accounts.add_training', raise_exception=True)
def course_create(request):
    if request.method == 'POST':
        form = TrainingCourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Training Course Creation",
                object_type="TrainingCourse",
                object_id=course.id,
                details=f"Created training course: {course.course_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Training course {course.course_name} has been created successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = TrainingCourseForm()
    return render(request, 'training/course_form.html', {'form': form, 'title': 'Create Training Course'})

@login_required
@permission_required('accounts.change_training', raise_exception=True)
def course_edit(request, pk):
    course = get_object_or_404(TrainingCourse, pk=pk)
    if request.method == 'POST':
        form = TrainingCourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Training Course Update",
                object_type="TrainingCourse",
                object_id=course.id,
                details=f"Updated training course: {course.course_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Training course {course.course_name} has been updated successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = TrainingCourseForm(instance=course)
    return render(request, 'training/course_form.html', {'form': form, 'title': 'Edit Training Course', 'course': course})

@login_required
@permission_required('accounts.delete_training', raise_exception=True)
def course_delete(request, pk):
    course = get_object_or_404(TrainingCourse, pk=pk)
    if request.method == 'POST':
        course_name = course.course_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Training Course Deletion",
            object_type="TrainingCourse",
            details=f"Deleted training course: {course_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        course.delete()
        messages.success(request, f'Training course {course_name} has been deleted successfully!')
        return redirect('course_list')
    return render(request, 'training/course_confirm_delete.html', {'course': course})

# Training Participation Views
@login_required
@permission_required('accounts.view_training', raise_exception=True)
def participation_list(request):
    participations = TrainingParticipation.objects.all().order_by('-created_date')
    
    # Filter by employee name
    employee_name = request.GET.get('employee_name')
    if employee_name:
        participations = participations.filter(employee__full_name__icontains=employee_name)
    
    # Filter by course name
    course_name = request.GET.get('course_name')
    if course_name:
        participations = participations.filter(course__course_name__icontains=course_name)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        participations = participations.filter(status=status)
    
    # Pagination
    paginator = Paginator(participations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': TrainingParticipation.STATUS_CHOICES,
        'selected_status': status,
    }
    return render(request, 'training/participation_list.html', context)

@login_required
@permission_required('accounts.add_training', raise_exception=True)
def participation_create(request):
    if request.method == 'POST':
        form = TrainingParticipationForm(request.POST)
        if form.is_valid():
            participation = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Training Participation Creation",
                object_type="TrainingParticipation",
                object_id=participation.id,
                details=f"Added {participation.employee.full_name} to course: {participation.course.course_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'{participation.employee.full_name} has been added to {participation.course.course_name} successfully!')
            return redirect('participation_list')
    else:
        course_id = request.GET.get('course_id')
        employee_id = request.GET.get('employee_id')
        
        initial_data = {}
        if course_id:
            initial_data['course'] = course_id
        if employee_id:
            initial_data['employee'] = employee_id
            
        form = TrainingParticipationForm(initial=initial_data)
    return render(request, 'training/participation_form.html', {'form': form, 'title': 'Add Participant'})

@login_required
@permission_required('accounts.change_training', raise_exception=True)
def participation_edit(request, pk):
    participation = get_object_or_404(TrainingParticipation, pk=pk)
    if request.method == 'POST':
        form = ParticipationUpdateForm(request.POST, instance=participation)
        if form.is_valid():
            participation = form.save()
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Training Participation Update",
                object_type="TrainingParticipation",
                object_id=participation.id,
                details=f"Updated participation record for {participation.employee.full_name} in course: {participation.course.course_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, f'Participation record for {participation.employee.full_name} has been updated successfully!')
            return redirect('participation_list')
    else:
        form = ParticipationUpdateForm(instance=participation)
    
    context = {
        'form': form, 
        'title': 'Update Participant', 
        'participation': participation
    }
    return render(request, 'training/participation_form.html', context)

@login_required
@permission_required('accounts.delete_training', raise_exception=True)
def participation_delete(request, pk):
    participation = get_object_or_404(TrainingParticipation, pk=pk)
    if request.method == 'POST':
        employee_name = participation.employee.full_name
        course_name = participation.course.course_name
        # Log action
        SystemLog.objects.create(
            user=request.user,
            action="Training Participation Deletion",
            object_type="TrainingParticipation",
            details=f"Removed {employee_name} from course: {course_name}",
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        participation.delete()
        messages.success(request, f'{employee_name} has been removed from {course_name} successfully!')
        return redirect('participation_list')
    return render(request, 'training/participation_confirm_delete.html', {'participation': participation})

@login_required
@permission_required('accounts.add_training', raise_exception=True)
def bulk_participation(request):
    if request.method == 'POST':
        form = BulkParticipationForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            added_count = 0
            
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('employee_') and value:
                    employee_id = int(field_name.split('_')[1])
                    employee = Employee.objects.get(id=employee_id)
                    
                    # Check if participation already exists
                    participation, created = TrainingParticipation.objects.get_or_create(
                        employee=employee,
                        course=course,
                        defaults={'status': 'Registered'}
                    )
                    
                    if created:
                        added_count += 1
            
            # Log action
            SystemLog.objects.create(
                user=request.user,
                action="Bulk Training Participation",
                object_type="TrainingCourse",
                object_id=course.id,
                details=f"Added {added_count} participants to course: {course.course_name}",
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'{added_count} participants have been added to {course.course_name} successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        course_id = request.GET.get('course_id')
        initial_data = {}
        if course_id:
            initial_data['course'] = course_id
            
        form = BulkParticipationForm(initial=initial_data)
    
    return render(request, 'training/bulk_participation.html', {'form': form})