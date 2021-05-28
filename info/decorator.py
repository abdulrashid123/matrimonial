from django.core.exceptions import PermissionDenied
from .models import Profile
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404


def user_is_entry_author(function):
    def wrap(request, *args, **kwargs):
        try:
            profile = get_object_or_404(Profile,pk=request.user.profile.id)
        except:
            messages.error(request, "Profile is not created")
            return redirect('info:home')
        if profile.paid:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Fees not paid")
            return redirect('info:payment')
    # wrap.__doc__ = function.__doc__
    # wrap.__name__ = function.__name__
    return wrap