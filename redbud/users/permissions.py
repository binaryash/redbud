#!/usr/bin/env python3

#!/usr/bin/env python3

from rest_framework import permissions


class IsManager(permissions.BasePermission):
    """
    Permission class to check if user is a Manager
    """
    message = "Only managers can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'


class IsTrainer(permissions.BasePermission):
    """
    Permission class to check if user is a Trainer
    """
    message = "Only trainers can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'trainer'


class IsEmployee(permissions.BasePermission):
    """
    Permission class to check if user is an Employee
    """
    message = "Only employees can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'


class IsManagerOrTrainer(permissions.BasePermission):
    """
    Permission class to check if user is a Manager or Trainer
    """
    message = "Only managers or trainers can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['manager', 'trainer']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.created_by == request.user


class CanAccessTraining(permissions.BasePermission):
    """
    Permission to check if user can access a training
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Manager can access all trainings
        if user.role == 'manager':
            return True

        # Trainer can access assigned trainings
        if user.role == 'trainer' and obj.assigned_trainer == user:
            return True

        # Employee can access their trainings
        if user.role == 'employee' and user in obj.employees.all():
            return True

        return False
