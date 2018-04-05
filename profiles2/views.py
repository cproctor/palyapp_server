from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from django.views.decorators.csrf import csrf_exempt
from profiles2.serializers import UsernameProfileSerializer, SignupProfileSerializer, ProfileSerializer
from profiles2.models import Profile
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from push_notifications.models import APNSDevice

class ProfileViewSet(mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin, 
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    "Handles profile-related views, including user fields provided via profiles"
    permission_classes = (AllowAny,)
    queryset = Profile.objects.filter(user__is_active=True).all()

    def get_serializer_class(self):
        return {
            'create': SignupProfileSerializer,
            'retrieve': ProfileSerializer,
            'update': ProfileSerializer,
            'partial_update': ProfileSerializer,
            'list': UsernameProfileSerializer,
            'notify': ProfileSerializer
        }[self.action]

    @detail_route(methods=['post', 'get'])
    def notify(self, request, pk):
        "Sends a test push notification to the user"
        try:
            device = APNSDevice.objects.get(user=self.get_object().user)
            device.send_message(None, extra={
                "aps":{
                    "alert": "This is a test notification",
                    "sound": "default",
                    "badge": 1,
                    "deeplink": subject.ios_deeplink()
                }
            })
            return HttpResponse("Notification sent")

        except APNSDevice.DoesNotExist:
            return HttpResponse("User has not registered a device.", 
                    status=400)
            
        




