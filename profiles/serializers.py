from rest_framework import serializers
from django.contrib.auth.models import User
from profiles.models import Profile
import logging

log = logging.getLogger('django')

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    student_id = serializers.IntegerField(source='profile_v1.student_id')
    #device_token = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)

    def validate_student_id(self, value):
        if Profile.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("Student ID is already registered")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already registered")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'), 
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        profile = Profile(
            student_id=validated_data.get('profile', {}).get('student_id'),
            user=user
        )
        profile.save()
        return user

class ProfileAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('analytics_opt_out',)

class ProfileDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('device_token',)
