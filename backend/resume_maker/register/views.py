from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User


class RegisterView(APIView):
    """
    POST: Register a new user.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        if not username or not password:
            return Response({"error": "Missing username or password"}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)
        
        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User registered successfully"}, status=201)