from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from django.views.decorators.csrf import csrf_exempt
from profiles2.serializers import UsernameProfileSerializer, SignupProfileSerializer, ProfileSerializer
from profiles2.models import Profile
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework import mixins
from rest_framework.permissions import AllowAny

class ProfileViewSet(mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin, 
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    "Handles profile-related views, including user fields provided via profiles"
    permission_classes = (AllowAny,)
    queryset = Profile.objects.filter(user__is_active=True).all()
    #lookup_field = 'auth_token'

    def get_serializer_class(self):
        if self.request.method == 'GET': 
            return UsernameProfileSerializer
        elif self.request.method == 'POST':
            return SignupProfileSerializer
        else:
            return ProfileSerializer
