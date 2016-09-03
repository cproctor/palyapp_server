from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from profiles.serializers import UserSerializer
from rest_framework import permissions, status
from rest_framework.response import Response

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
        
