from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import AppointmentViewSet, AvailabilityViewSet, SlotsView

router = SimpleRouter()
router.register("availability", AvailabilityViewSet, basename="availability")
router.register("", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("slots/", SlotsView.as_view(), name="slots"),
    path("", include(router.urls)),
]