from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Payment, Complaint, Notification
from rooms.models import Room
from users.models import User
from users.decorators import admin_required

def create_complaint_notification(complaint, action_type, sender):
    """Create a notification for complaint updates."""
    if action_type == 'created':
        title = f'New Complaint: {complaint.title}'
        message = f'A new complaint has been reported regarding {complaint.get_category_display()}'
    elif action_type == 'updated':
        title = f'Complaint Updated: {complaint.title}'
        message = f'The complaint status has been updated to {complaint.get_status_display()}'
    elif action_type == 'assigned':
        title = f'Complaint Assigned: {complaint.title}'
        message = f'The complaint has been assigned to {complaint.assigned_to.get_full_name()}'
    elif action_type == 'resolved':
        title = f'Complaint Resolved: {complaint.title}'
        message = f'The complaint has been marked as resolved'
    
    # Create notification
    notification = Notification.objects.create(
        title=title,
        message=message,
        notification_type='complaint',
        priority='medium',
        sender=sender
    )
    
    # Add recipients
    recipients = [complaint.reported_by]  # Always notify the reporter
    if complaint.assigned_to:
        recipients.append(complaint.assigned_to)  # Notify assigned staff
    if complaint.room:
        # Notify all students allocated to the room
        room_students = User.objects.filter(roomallocation__room=complaint.room, roomallocation__check_out_date__isnull=True)
        recipients.extend(room_students)
    
    # Add unique recipients
    notification.recipients.add(*set(recipients))
    return notification

from users.decorators import admin_required

@login_required
@admin_required
def payment_list(request):
    # Get filter parameters
    status = request.GET.get('status', '')
    payment_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    payments = Payment.objects.all().order_by('-due_date')
    
    # Apply filters
    if status:
        payments = payments.filter(status=status)
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    if search_query:
        payments = payments.filter(
            Q(student__username__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(payments, 10)  # Show 10 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Payment.PAYMENT_STATUS_CHOICES,
        'type_choices': Payment.PAYMENT_TYPE_CHOICES,
        'selected_status': status,
        'selected_type': payment_type,
        'search_query': search_query,
    }
    return render(request, 'core/payment_list.html', context)

@login_required
def complaint_list(request):
    # Get filter parameters
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    complaints = Complaint.objects.all().order_by('-created_at')
    
    # Apply filters
    if status:
        complaints = complaints.filter(status=status)
    if category:
        complaints = complaints.filter(category=category)
    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(student__username__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(complaints, 10)  # Show 10 complaints per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Complaint.STATUS_CHOICES,
        'category_choices': Complaint.CATEGORY_CHOICES,
        'selected_status': status,
        'selected_category': category,
        'search_query': search_query,
    }
    return render(request, 'core/complaint_list.html', context)

@login_required
def create_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        room_id = request.POST.get('room')
        
        if title and description and category:
            try:
                room = Room.objects.get(id=room_id) if room_id else None
                complaint = Complaint.objects.create(
                    title=title,
                    description=description,
                    category=category,
                    room=room,
                    reported_by=request.user,
                    status='open'
                )
                # Create notification for new complaint
                create_complaint_notification(complaint, 'created', request.user)
                messages.success(request, 'Complaint reported successfully.')
                return redirect('complaint_list')
            except Room.DoesNotExist:
                messages.error(request, 'Invalid room selected.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    rooms = Room.objects.all()
    context = {
        'rooms': rooms,
        'category_choices': Complaint.CATEGORY_CHOICES
    }
    return render(request, 'core/create_complaint.html', context)

@login_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST' and (request.user.is_staff or request.user == complaint.reported_by):
        new_status = request.POST.get('status')
        resolution = request.POST.get('resolution')
        assigned_to_id = request.POST.get('assigned_to')
        
        if new_status:
            complaint.status = new_status
            if new_status in ['resolved', 'closed']:
                complaint.resolved_at = timezone.now()
                complaint.resolution = resolution
            
            old_status = complaint.status
            old_assigned_to = complaint.assigned_to
            
            if assigned_to_id and request.user.is_staff:
                try:
                    assigned_to = User.objects.get(id=assigned_to_id)
                    complaint.assigned_to = assigned_to
                except User.DoesNotExist:
                    messages.error(request, 'Invalid staff member selected.')
                    return redirect('complaint_detail', complaint_id=complaint.id)
            
            complaint.save()
            
            # Create notifications based on changes
            if complaint.assigned_to and complaint.assigned_to != old_assigned_to:
                create_complaint_notification(complaint, 'assigned', request.user)
            if complaint.status != old_status:
                if complaint.status in ['resolved', 'closed']:
                    create_complaint_notification(complaint, 'resolved', request.user)
                else:
                    create_complaint_notification(complaint, 'updated', request.user)
            
            messages.success(request, 'Complaint status updated successfully.')
            return redirect('complaint_detail', complaint_id=complaint.id)
    
    staff_members = User.objects.filter(is_staff=True)
    context = {
        'complaint': complaint,
        'status_choices': Complaint.STATUS_CHOICES,
        'staff_members': staff_members
    }
    return render(request, 'core/complaint_detail.html', context)

@login_required
def notification_list(request):
    # Get filter parameters
    notification_type = request.GET.get('type', '')
    priority = request.GET.get('priority', '')
    is_unread = request.GET.get('unread', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset - get notifications where the user is a recipient
    notifications = Notification.objects.filter(recipients=request.user).order_by('-created_at')
    
    # Apply filters
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    if priority:
        notifications = notifications.filter(priority=priority)
    if is_unread == 'true':
        notifications = notifications.exclude(read_by=request.user)
    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(notifications, 20)  # Show 20 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unread count
    unread_count = notifications.exclude(read_by=request.user).count()
    
    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
        'type_choices': Notification.NOTIFICATION_TYPE_CHOICES,
        'priority_choices': Notification.PRIORITY_CHOICES,
        'selected_type': notification_type,
        'selected_priority': priority,
        'is_unread': is_unread,
        'search_query': search_query,
    }
    return render(request, 'core/notification_list.html', context)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipients=request.user)
    notification.mark_as_read(request.user)
    messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')
