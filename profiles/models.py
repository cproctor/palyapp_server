from django.db import models

class Profile(models.Model):    
    user = models.OneToOneField('auth.User', related_name='profile')
    student_id = models.IntegerField()
    analytics_opt_out = models.BooleanField(default=False)

