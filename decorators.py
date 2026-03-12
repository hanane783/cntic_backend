from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Group

def verified_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_verified:
            return Response({"error": "Account not verified. Please verify your OTP first."}, status=status.HTTP_403_FORBIDDEN)
        return func(self, request, *args, **kwargs)
    return wrapper


def paid_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_paid:
            return Response({"error": "Payment required. Please complete your payment first."}, status=status.HTTP_403_FORBIDDEN)
        return func(self, request, *args, **kwargs)
    return wrapper


def verified_and_paid_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_verified:
            return Response({"error": "Account not verified. Please verify your OTP first."}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_paid:
            return Response({"error": "Payment required. Please complete your payment first."}, status=status.HTTP_403_FORBIDDEN)
        return func(self, request, *args, **kwargs)
    return wrapper



def group_required(*allowed_groups):
    """
    Decorator للتحقق من أن المستخدم ينتمي لإحدى المجموعات المسموح بها
    Usage: @group_required('admin', 'student')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            user_groups = request.user.groups.values_list('name', flat=True)
            if not any(group in allowed_groups for group in user_groups):
                return Response(
                    {"error": "You do not have permission to access this resource."},
                    status=status.HTTP_403_FORBIDDEN
                )
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator