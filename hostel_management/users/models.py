from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('student', 'Student'),
        ('parent', 'Parent/Guardian'),
    )
    
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_user_type_display()})'

    def is_admin(self):
        return self.user_type == 'admin'

    def is_staff_member(self):
        return self.user_type == 'staff'

    def is_student(self):
        return self.user_type == 'student'

    def is_parent(self):
        return self.user_type == 'parent'
