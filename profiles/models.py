from django.db import models
from push_notifications.models import APNSDevice
from django.dispatch import receiver

class Profile(models.Model):    
    user = models.OneToOneField('auth.User', related_name='profile')
    student_id = models.IntegerField()
    analytics_opt_out = models.BooleanField(default=False)
    device_token = models.TextField(max_length=200, blank=True)

@receiver(models.signals.post_save, sender=Profile)
def create_device(sender, instance, **kwargs):
    "Keeps user's APNS device synced with profile, if exists"
    if instance.device_token:
        try:
            device = APNSDevice.objects.get(user=instance.user)
            device.registration_id = instance.device_token
            device.save()
        except APNSDevice.DoesNotExist:
            device = APNSDevice(user=instance.user, registration_id=instance.device.token)
            device.save()
            

