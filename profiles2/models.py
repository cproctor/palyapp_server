from django.db import models
from stories2.models import Publication
from push_notifications.models import APNSDevice
from django.dispatch import receiver
from django.contrib.auth.models import User

class Profile(models.Model):    
    user = models.OneToOneField('auth.User', related_name='profile')
    username = models.CharField(max_length=200, unique=True)
    publication = models.ForeignKey(Publication, related_name='authors', null=True)
    auth_token = models.CharField(max_length=200, primary_key=True)
    analytics = models.BooleanField(default=True)
    device_token = models.TextField(max_length=200, blank=True)
    role = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=100, null=True)
    race_ethnicity = models.CharField(max_length=100, null=True)

    @property
    def active(self):
        return self.user.is_active

    @active.setter
    def active(self, value):
        self.user.is_active = value

    def default_auth_token(self):
        return User.objects.make_random_password()

    def __str__(self):
        return self.username

@receiver(models.signals.post_save, sender=Profile)
def post_save(sender, instance, **kwargs):
    "Saves related user and keeps user's APNS device synced with profile, if exists"
    instance.user.username = instance.username
    instance.user.save()

    if instance.device_token:
        try:
            device = APNSDevice.objects.get(user=instance.user)
            device.registration_id = instance.device_token
            device.save()
        except APNSDevice.DoesNotExist:
            device = APNSDevice(user=instance.user, registration_id=instance.device_token)
            device.save()
