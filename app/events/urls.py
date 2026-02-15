from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, EventViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'events', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
]