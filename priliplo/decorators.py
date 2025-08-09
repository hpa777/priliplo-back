from django.core.exceptions import PermissionDenied
from client.models import UserProfile
from django.shortcuts import redirect

def check_permission(request, need_permission):
    cur_user = UserProfile.objects.get(user=request.user)
    return cur_user.user_role == need_permission

def user_is_admin(function, verification_url="login"):
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs) if check_permission(request, 1) else redirect(verification_url)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_is_client(function, verification_url="login"):
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs) if check_permission(request, 2) else redirect(verification_url)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_is_company(function, verification_url="login"):
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs) if check_permission(request, 3) else redirect(verification_url)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_is_kassir(function, verification_url="login"):
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs) if check_permission(request, 4) else redirect(verification_url)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
