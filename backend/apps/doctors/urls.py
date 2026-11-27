from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import DoctorMeView, DoctorViewSet

router = SimpleRouter()
router.register("", DoctorViewSet, basename="doctor")

urlpatterns = [
    path("me/", DoctorMeView.as_view(), name="doctor-me"),
    path("", include(router.urls)),
]