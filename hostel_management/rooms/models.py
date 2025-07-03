from django.db import models
from users.models import User

class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('quad', 'Quad'),
    )

    ROOM_STATUS_CHOICES = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    )

    room_number = models.CharField(max_length=10, unique=True)
    floor = models.PositiveIntegerField()
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='available')
    monthly_rent = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    amenities = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['floor', 'room_number']

    def __str__(self):
        return f'Room {self.room_number} ({self.get_room_type_display()})'

    def is_available(self):
        return self.status == 'available'

    def has_space(self):
        return self.current_occupancy < self.capacity

class RoomAllocation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_allocations')
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Room Allocation'
        verbose_name_plural = 'Room Allocations'
        unique_together = ['room', 'student', 'check_in_date']

    def __str__(self):
        return f'{self.student.get_full_name()} - Room {self.room.room_number}'

class RoomMaintenance(models.Model):
    MAINTENANCE_TYPE_CHOICES = (
        ('repair', 'Repair'),
        ('cleaning', 'Cleaning'),
        ('inspection', 'Inspection'),
        ('renovation', 'Renovation'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_maintenance')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_maintenance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Room Maintenance'
        verbose_name_plural = 'Room Maintenance Records'
        ordering = ['-scheduled_date', 'status']

    def __str__(self):
        return f'Maintenance - Room {self.room.room_number} ({self.get_maintenance_type_display()})'
