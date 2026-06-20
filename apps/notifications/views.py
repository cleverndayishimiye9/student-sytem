from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NotificationLog, AlertThreshold
from .services import check_and_send_alerts, send_sms
from django import forms


class ThresholdForm(forms.ModelForm):
    class Meta:
        model = AlertThreshold
        fields = ('name', 'grade_threshold', 'attendance_threshold', 'is_active')


@login_required
def notification_log(request):
    if request.user.is_student_role:
        logs = NotificationLog.objects.filter(recipient=request.user)
    else:
        logs = NotificationLog.objects.select_related('recipient').all()
    return render(request, 'notifications/log.html', {'logs': logs})


@login_required
def alert_settings(request):
    if not request.user.is_admin:
        messages.error(request, 'Admins only.')
        return redirect('dashboard')

    thresholds = AlertThreshold.objects.all()
    form = ThresholdForm()

    if request.method == 'POST':
        form = ThresholdForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.created_by = request.user
            t.save()
            messages.success(request, 'Alert threshold saved.')
            return redirect('alert_settings')

    return render(request, 'notifications/alert_settings.html', {
        'thresholds': thresholds,
        'form': form,
    })


@login_required
def trigger_bulk_alert(request):
    """Admin can manually trigger bulk alert scan."""
    if not request.user.is_admin:
        messages.error(request, 'Admins only.')
        return redirect('dashboard')

    if request.method == 'POST':
        from .tasks import send_bulk_alerts_task
        send_bulk_alerts_task.delay()
        messages.success(request, 'Bulk alert scan queued successfully.')
    return redirect('alert_settings')
