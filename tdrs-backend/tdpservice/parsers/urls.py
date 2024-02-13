"""Routing for DataFiles."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataFileSummaryViewSet

router = DefaultRouter()

router.register("dfs", DataFileSummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
