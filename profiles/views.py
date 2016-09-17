from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from django.views.decorators.csrf import csrf_exempt
from profiles.serializers import UserSerializer, ProfileAnalyticsSerializer
from profiles.models import Profile
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class Signup(APIView):
    "An endpoint for creating new users"
    
    permission_classes = (permissions.AllowAny,)

    @csrf_exempt
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateAnalytics(UpdateAPIView):
    "An endpoint for toggling analytics opt-in"
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileAnalyticsSerializer

    def get_object(self):
        studentId = self.request.data.get('student_id', -1)
        return get_object_or_404(Profile, student_id=studentId)
        
