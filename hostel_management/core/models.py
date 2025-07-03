from django.db import models
from users.models import User
from rooms.models import Room, RoomAllocation

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('rent', 'Room Rent'),
        ('deposit', 'Security Deposit'),
        ('maintenance', 'Maintenance Fee'),
        ('utility', 'Utility Bill'),
        ('other', 'Other Charges'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    room_allocation = models.ForeignKey(RoomAllocation, on_delete=models.SET_NULL, null=True, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-due_date', 'status']

    def __str__(self):
        return f'Payment - {self.student.get_full_name()} ({self.get_payment_type_display()})'

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('payment', 'Payment Reminder'),
        ('maintenance', 'Maintenance Update'),
        ('announcement', 'General Announcement'),
        ('complaint', 'Complaint Update'),
        ('event', 'Event Information'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    recipients = models.ManyToManyField(User, related_name='received_notifications')
    read_by = models.ManyToManyField(User, related_name='read_notifications', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at', 'priority']

    def __str__(self):
        return f'{self.title} ({self.get_notification_type_display()})'

    def mark_as_read(self, user):
        self.read_by.add(user)
        self.save()

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    CATEGORY_CHOICES = (
        ('maintenance', 'Maintenance'),
        ('cleanliness', 'Cleanliness'),
        ('security', 'Security'),
        ('noise', 'Noise'),
        ('facility', 'Facility'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='complaints')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_complaints')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_complaints')
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        ordering = ['-created_at', 'status']

    def __str__(self):
        return f'{self.title} - {self.get_category_display()}'
