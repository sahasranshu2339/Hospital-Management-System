from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import PatientMeView, PatientViewSet, MyPatientsView

router = SimpleRouter()
router.register("", PatientViewSet, basename="patient")

urlpatterns = [
    path("me/", PatientMeView.as_view(), name="patient-me"),
    path("my-patients/", MyPatientsView.as_view(), name="my-patients"),
    path("", include(router.urls)),
]