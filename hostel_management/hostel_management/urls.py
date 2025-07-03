from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from rooms import views as room_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.dashboard, name='dashboard'),
    path('login/', user_views.login_view, name='login'),
    path('logout/', user_views.logout_view, name='logout'),
    path('settings/', user_views.settings_view, name='settings'),  # Updated this line
    
    # Room management URLs
    path('rooms/', room_views.room_list, name='room_list'),
    path('rooms/<int:room_id>/', room_views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/allocate/', room_views.allocate_room, name='allocate_room'),
    path('rooms/<int:room_id>/maintenance/', room_views.report_maintenance, name='report_maintenance'),
    
    # Student management URLs
    path('students/', user_views.student_list, name='student_list'),
    path('students/<int:student_id>/', user_views.student_detail, name='student_detail'),
    
    # Payment management URLs
    path('payments/', core_views.payment_list, name='payment_list'),
    
    # Maintenance management URLs
    path('maintenance/', room_views.maintenance_list, name='maintenance_list'),
    
    # Complaint management URLs
    path('complaints/', core_views.complaint_list, name='complaint_list'),
    path('complaints/create/', core_views.create_complaint, name='create_complaint'),
    path('complaints/<int:complaint_id>/', core_views.complaint_detail, name='complaint_detail'),
    
    # Notification URLs
    path('notifications/', core_views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/mark-read/', core_views.mark_notification_read, name='mark_notification_read'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
