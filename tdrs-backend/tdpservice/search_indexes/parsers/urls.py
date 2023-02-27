"""Routing for DataFiles."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register("", ParsingErrorViewSet)

urlpatterns = [
    path('parsing_errors/', include(router.urls)),
]
