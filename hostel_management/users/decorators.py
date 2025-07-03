from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin():
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    return wrapper