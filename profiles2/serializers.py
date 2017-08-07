from rest_framework import serializers
from django.contrib.auth.models import User
from profiles2.models import Profile
import logging
import re

log = logging.getLogger('django')

class ProfileSerializer(serializers.ModelSerializer):
    uid = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    def get_uid(self, obj):
        return obj.user.id

    def get_active(self, obj):
        return obj.active

    class Meta:
        model = Profile
        fields = ('uid', 'username', 'analytics', 'device_token', 'active', 'role', 'gender', 'race_ethnicity')
        read_only_fields = ('auth_token', 'active')
    
class UsernameProfileSerializer(serializers.ModelSerializer):
    uid = serializers.SerializerMethodField()

    def get_uid(self, obj):
        return obj.user.id

    class Meta:
        model = Profile
        fields = ('username', 'publication', 'uid')

class SignupProfileSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    auth_token = serializers.CharField(max_length=100, read_only=True)

    def validate_username(self, value):
        if not re.match("^[0-9A-Za-z]*$", value):
            raise serializers.ValidationError("Username must consist of letters and numbers")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already registered")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'), 
            password=User.objects.make_random_password()
        )
        user.save()
        self.validated_data['auth_token'] = User.objects.make_random_password()
        profile = Profile(
            auth_token=self.validated_data['auth_token'], 
            user=user, 
            username=validated_data['username']
        )
        profile.save()
        return profile

class AuthTokenUserSerializer(serializers.Serializer):
    "Translates an auth token into a user"
    auth_token = serializers.CharField(max_length=100, write_only=True)

    def validate_auth_token(self, value):
        try:
            profile = Profile.objects.get(auth_token=value)
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Invalid auth token")
        return value

    def create(self, validated_data):
        profile = Profile.objects.get(auth_token=validated_data['auth_token'])
        return profile.user


