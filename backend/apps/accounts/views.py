from rest_framework import generics, permissions
from rest_framework.throttling import ScopedRateThrottle

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # public endpoint
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"