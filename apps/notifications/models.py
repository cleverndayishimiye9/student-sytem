from django.db import models
from django.conf import settings


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ('sms', 'SMS (Twilio)'),
        ('email', 'Email'),
        ('system', 'System Alert'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    ALERT_TYPE_CHOICES = [
        ('grade_alert', 'Low Grade Alert'),
        ('attendance_alert', 'Low Attendance Alert'),
        ('risk_alert', 'At-Risk Student Alert'),
        ('general', 'General Notification'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='sms')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, default='general')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    twilio_sid = models.CharField(max_length=50, blank=True)  # Twilio message SID for tracking

    def __str__(self):
        return f"{self.recipient} | {self.alert_type} | {self.status} | {self.sent_at:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ['-sent_at']


class AlertThreshold(models.Model):
    """Configurable thresholds — Admin can adjust these per academic year."""
    name = models.CharField(max_length=100)
    grade_threshold = models.PositiveIntegerField(default=50, help_text='Alert if grade below this %')
    attendance_threshold = models.PositiveIntegerField(default=75, help_text='Alert if attendance below this %')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Grade<{self.grade_threshold}%, Att<{self.attendance_threshold}%)"

    class Meta:
        verbose_name = 'Alert Threshold Configuration'
