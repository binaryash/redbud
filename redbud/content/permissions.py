#!/usr/bin/env python3

"""
Permissions module for managing content access based on user roles.

The class ensures:
- Managers can create or edit all content.
- Trainers can only create or edit content associated with their training.
- All users must be authenticated to access the content.
- Read access (safe methods like GET) is allowed for managers to all content
- Trainers can only read content assigned to their training.
"""

from rest_framework import permissions


class IsManagerOrTrainerForContent(permissions.BasePermission):
    """
    Permission to check if user can create/edit content.

    - Managers can create/edit all content
    - Trainers can create/edit content for their assigned trainings
    """

    message = "Only managers or trainers can manage content."

    def has_permission(self, request, view):
        """Check if user can perform action based on role."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return (
            request.user.is_authenticated
            and request.user.role in ['manager', 'trainer']
            )

    def has_object_permission(self, request, view, obj):
        """Verify if user can act on specific content."""
        user = request.user

        # Read permissions
        if request.method in permissions.SAFE_METHODS:
            if user.role == 'manager':
                return True
            elif user.role == 'trainer':
                return obj.training.assigned_trainer == user
            else:
                return user in obj.training.employees.all()

        # Write permissions
        if user.role == 'manager':
            return True
        elif user.role == 'trainer':
            return obj.training.assigned_trainer == user

        return False





    # Modify the has_object_permission method in IsManagerOrTrainerForContent class

    def has_object_permission(self, request, view, obj):
        """Verify if user can act on specific content."""
        user = request.user

        # Special case: summarize action is available to all authenticated users
        if view.action == 'summarize':
            return request.user.is_authenticated

        # Read permissions
        if request.method in permissions.SAFE_METHODS:
            if user.role == 'manager':
                return True
            elif user.role == 'trainer':
                return obj.training.assigned_trainer == user
            else:
                return user in obj.training.employees.all()

        # Write permissions
        if user.role == 'manager':
            return True
        elif user.role == 'trainer':
            return obj.training.assigned_trainer == user

        return False
