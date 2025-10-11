#!/usr/bin/env python3

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserViewSet, TrainingViewSet, TrainingModuleViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'trainings', TrainingViewSet, basename='training')
router.register(r'modules', TrainingModuleViewSet, basename='training-module')

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Router URLs
    path('', include(router.urls)),
]
