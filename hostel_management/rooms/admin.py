from django.contrib import admin
from .models import Room, RoomAllocation, RoomMaintenance

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'floor', 'room_type', 'capacity', 'current_occupancy', 'status', 'monthly_rent')
    list_filter = ('floor', 'room_type', 'status')
    search_fields = ('room_number', 'description')
    ordering = ('floor', 'room_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ('room', 'student', 'check_in_date', 'check_out_date', 'is_active')
    list_filter = ('is_active', 'check_in_date')
    search_fields = ('room__room_number', 'student__username', 'student__first_name', 'student__last_name')
    ordering = ('-check_in_date',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('room', 'student')

@admin.register(RoomMaintenance)
class RoomMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('room', 'maintenance_type', 'status', 'scheduled_date', 'completion_date')
    list_filter = ('maintenance_type', 'status', 'scheduled_date')
    search_fields = ('room__room_number', 'description', 'remarks')
    ordering = ('-scheduled_date', 'status')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('room', 'reported_by', 'assigned_to')
