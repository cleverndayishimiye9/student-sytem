from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.notification_log, name='notification_log'),
    path('settings/', views.alert_settings, name='alert_settings'),
    path('trigger/', views.trigger_bulk_alert, name='trigger_bulk_alert'),
]
