#!/usr/bin/env python3

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentViewSet

router = DefaultRouter()
router.register(r'contents', ContentViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
]
