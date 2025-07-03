from django.contrib import admin
from .models import Payment, Notification, Complaint



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'payment_type', 'amount', 'status', 'due_date', 'payment_date')
    list_filter = ('payment_type', 'status', 'due_date')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'transaction_id')
    ordering = ('-due_date', 'status')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('student', 'room_allocation')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'priority', 'sender', 'created_at', 'scheduled_for')
    list_filter = ('notification_type', 'priority', 'created_at')
    search_fields = ('title', 'message', 'sender__username')
    ordering = ('-created_at', 'priority')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('sender',)
    filter_horizontal = ('recipients', 'read_by')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'room', 'reported_by', 'assigned_to', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description', 'room__room_number', 'reported_by__username')
    ordering = ('-created_at', 'status')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('room', 'reported_by', 'assigned_to')
