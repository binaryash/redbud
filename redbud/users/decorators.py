#!/usr/bin/env python3

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def role_required(*roles):
    """
    Decorator to restrict access based on user role
    Usage: @role_required('manager', 'trainer')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.role not in roles:
                messages.error(request, "You don't have permission to access this page.")
                return HttpResponseForbidden("You don't have permission to access this page.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
