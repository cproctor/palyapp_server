from django.contrib import admin
from profiles2.models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
