from django.conf import settings
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status,viewsets
from .models import User
from .permissions import IsAdminRole
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from .authentication import enforce_csrf
from .serializers import RegisterSerializer, UserSerializer,AdminUserSerializer


def set_cookie(response, name, value, max_age):
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path="/",
    )


def access_max_age():
    return int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())


def refresh_max_age():
    return int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


    def get_authenticate_header(self, request):
        return "Bearer"

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        response = Response(UserSerializer(serializer.user).data)
        set_cookie(response, settings.AUTH_COOKIE_ACCESS, tokens["access"], access_max_age())
        set_cookie(response, settings.AUTH_COOKIE_REFRESH, tokens["refresh"], refresh_max_age())
        get_token(request)  # makes sure a fresh CSRF cookie is sent
        return response


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []


    def get_authenticate_header(self, request):
        return "Bearer"

    def post(self, request):
        enforce_csrf(request)
        refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if not refresh:
            return Response({"detail": "No refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)

        response = Response({"detail": "Token refreshed."})
        set_cookie(response, settings.AUTH_COOKIE_ACCESS, serializer.validated_data["access"], access_max_age())
        return response


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        enforce_csrf(request)
        response = Response({"detail": "Logged out."})
        response.delete_cookie(settings.AUTH_COOKIE_ACCESS, path="/")
        response.delete_cookie(settings.AUTH_COOKIE_REFRESH, path="/")
        return response


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    







class UserViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ["get", "post", "patch", "head", "options"]  # no DELETE

    def get_queryset(self):
        queryset = User.objects.all().order_by("-date_joined")
        role = self.request.query_params.get("role")
        if role in User.Role.values:
            queryset = queryset.filter(role=role)
        return queryset