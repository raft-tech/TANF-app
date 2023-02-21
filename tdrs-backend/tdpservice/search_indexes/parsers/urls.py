"""Routing for DataFiles."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register("", ParsingErrorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('parsing_errors/', ParsingErrorViewSet.as_view({'get': 'list'}), name='parsing_errors'),
]
