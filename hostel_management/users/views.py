from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404  # Add get_object_or_404 here
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .models import User
from rooms.models import Room, RoomMaintenance, RoomAllocation
from core.models import Payment, Complaint
from .decorators import admin_required

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_admin():
                return redirect('dashboard')
            else:
                return redirect('room_list')  # Assuming 'room_list' is the URL name for the room page
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

from .decorators import admin_required

@login_required
@admin_required
def dashboard(request):
    # Get maintenance statistics
    maintenance_stats = {
        'pending': RoomMaintenance.objects.filter(status='pending').count(),
        'in_progress': RoomMaintenance.objects.filter(status='in_progress').count(),
        'completed': RoomMaintenance.objects.filter(status='completed').count(),
    }

    context = {
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(status='available').count(),
        'total_residents': User.objects.filter(user_type='resident').count(),
        'pending_maintenance': maintenance_stats['pending'],
        'in_progress_maintenance': maintenance_stats['in_progress'],
        'completed_maintenance': maintenance_stats['completed'],
        'recent_payments': Payment.objects.order_by('-created_at')[:5],
        'recent_complaints': Complaint.objects.order_by('-created_at')[:5],
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def student_list(request):
    students = User.objects.filter(user_type='student').order_by('username')
    
    # Get search parameter
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(username__icontains=search_query)
    
    # Pagination
    paginator = Paginator(students, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get room allocation status for each student
    for student in page_obj:
        try:
            allocation = RoomAllocation.objects.filter(
                student=student,
                is_active=True,
                check_out_date__isnull=True
            ).first()
            student.current_room = allocation.room if allocation else None
        except AttributeError:
            student.current_room = None
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'users/student_list.html', context)

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id, user_type='student')
    
    # Get current room allocation
    current_allocation = RoomAllocation.objects.filter(
        student=student,
        is_active=True,
        check_out_date__isnull=True
    ).first()
    
    # Get allocation history
    allocation_history = RoomAllocation.objects.filter(
        student=student
    ).order_by('-check_in_date')
    
    # Get payment history
    payment_history = Payment.objects.filter(
        student=student
    ).order_by('-created_at')[:5]
    
    # Get complaints
    complaints = Complaint.objects.filter(
        student=student
    ).order_by('-created_at')[:5]
    
    context = {
        'student': student,
        'current_allocation': current_allocation,
        'allocation_history': allocation_history,
        'payment_history': payment_history,
        'complaints': complaints,
    }
    return render(request, 'users/student_detail.html', context)

@login_required
def settings_view(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            # Handle profile update
            user = request.user
            user.first_name = request.POST.get('full_name').split()[0]
            user.last_name = ' '.join(request.POST.get('full_name').split()[1:])
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone')
            
            # Add theme preference handling
            theme_preference = request.POST.get('theme_preference')
            if theme_preference in ['light', 'dark']:
                user.theme_preference = theme_preference
            
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            
            user.save()
            messages.success(request, 'Profile updated successfully!')
            
        elif 'update_notifications' in request.POST:
            # Handle notification preferences update
            user = request.user
            user.email_notifications = request.POST.get('email_notifications') == 'on'
            user.maintenance_notifications = request.POST.get('maintenance_notifications') == 'on'
            user.payment_notifications = request.POST.get('payment_notifications') == 'on'
            user.save()
            messages.success(request, 'Notification preferences updated successfully!')
            
        elif 'change_password' in request.POST:
            # Handle password change
            user = request.user
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if user.check_password(current_password):
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password changed successfully!')
                    return redirect('login')
                else:
                    messages.error(request, 'New passwords do not match!')
            else:
                messages.error(request, 'Current password is incorrect!')
    
    return render(request, 'users/settings.html')
