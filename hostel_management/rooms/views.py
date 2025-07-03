from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Room, RoomAllocation, RoomMaintenance
from users.models import User

@login_required
def room_list(request):
    rooms = Room.objects.all()
    context = {
        'rooms': rooms,
        'total_rooms': rooms.count(),
        'available_rooms': rooms.filter(status='available').count(),
        'occupied_rooms': rooms.filter(status='occupied').count(),
        'maintenance_rooms': rooms.filter(status='maintenance').count(),
    }
    return render(request, 'rooms/room_list.html', context)

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Change roomallocation_set to allocations
    allocations = room.allocations.all().order_by('-created_at')
    maintenance_records = room.maintenance_records.all().order_by('-created_at')
    context = {
        'room': room,
        'allocations': allocations,
        'maintenance_records': maintenance_records,
    }
    return render(request, 'rooms/room_detail.html', context)

@login_required
def allocate_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        student_id = request.POST.get('student')
        check_in_date = request.POST.get('check_in_date')
        
        if student_id and check_in_date:
            student = get_object_or_404(User, id=student_id)
            if room.status == 'available' and room.has_space():
                allocation = RoomAllocation.objects.create(
                    room=room,
                    student=student,
                    check_in_date=check_in_date
                )
                room.current_occupancy += 1
                if room.current_occupancy >= room.capacity:
                    room.status = 'occupied'
                room.save()
                messages.success(request, f'Room {room.room_number} has been allocated to {student.get_full_name()}')
                return redirect('room_detail', room_id=room.id)
            else:
                messages.error(request, 'This room is not available for allocation or is at full capacity')
        else:
            messages.error(request, 'Please select a student and check-in date')
    
    available_students = User.objects.filter(user_type='student')
    context = {
        'room': room,
        'available_students': available_students,
    }
    return render(request, 'rooms/allocate_room.html', context)

@login_required
def report_maintenance(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        maintenance_type = request.POST.get('maintenance_type')
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        
        if maintenance_type and description and scheduled_date:
            maintenance = RoomMaintenance.objects.create(
                room=room,
                maintenance_type=maintenance_type,
                description=description,
                reported_by=request.user,
                scheduled_date=scheduled_date,
                status='pending'
            )
            room.status = 'maintenance'
            room.save()
            messages.success(request, f'Maintenance issue reported for Room {room.room_number}')
            return redirect('room_detail', room_id=room.id)
        else:
            messages.error(request, 'Please fill in all required fields')
    
    context = {
        'room': room,
        'maintenance_types': dict(RoomMaintenance.MAINTENANCE_TYPE_CHOICES)
    }
    return render(request, 'rooms/report_maintenance.html', context)

@login_required
def maintenance_list(request):
    # Get filter parameters
    status = request.GET.get('status', '')
    maintenance_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    maintenance_records = RoomMaintenance.objects.all().order_by('-scheduled_date')
    
    # Apply filters
    if status:
        maintenance_records = maintenance_records.filter(status=status)
    if maintenance_type:
        maintenance_records = maintenance_records.filter(maintenance_type=maintenance_type)
    if search_query:
        maintenance_records = maintenance_records.filter(
            Q(room__room_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(reported_by__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(maintenance_records, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': RoomMaintenance.STATUS_CHOICES,
        'type_choices': RoomMaintenance.MAINTENANCE_TYPE_CHOICES,
        'selected_status': status,
        'selected_type': maintenance_type,
        'search_query': search_query,
    }
    return render(request, 'rooms/maintenance_list.html', context)
