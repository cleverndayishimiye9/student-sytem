from django.contrib import admin
from .models import NotificationLog, AlertThreshold


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'alert_type', 'channel', 'status', 'sent_at')
    list_filter = ('alert_type', 'channel', 'status')
    search_fields = ('recipient__username', 'message')
    readonly_fields = ('sent_at', 'twilio_sid')


@admin.register(AlertThreshold)
class AlertThresholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade_threshold', 'attendance_threshold', 'is_active', 'created_at')
    list_editable = ('is_active',)
