from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from rest_framework.permissions import AllowAny

# Create your views here.

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to access this view
    def post(self, request):# overriding the default post method
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
                
            if user is not None:
               
                # Generate JWT token for the authenticated user
                refresh = RefreshToken.for_user(user)
                response={
                    "status": status.HTTP_200_OK,
                    "message": "success",
                    "username" : user.username,
                    "role" : user.groups.all()[0].id
                    if user.groups.exists() else None,
                    "data":{
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    }
                }
                return Response(response,status=status.HTTP_200_OK)
            else:
                response={
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "message":"Invalid username or password!"
                }
                return Response(response,status= status.HTTP_401_UNAUTHORIZED)
        response ={
            "status":status.HTTP_400_BAD_REQUEST,
            "message":"bad request",
            "data": serializer.errors
        }
        return Response(response,status =status.HTTP_400_BAD_REQUEST)

        
