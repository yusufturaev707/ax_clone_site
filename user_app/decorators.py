import numpy
from django.contrib.auth import logout
from django.shortcuts import redirect, render, get_object_or_404

from expert.models import Expert
from user_app.models import User, Role


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_admin or request.user.is_editor:
                return redirect('home')
            elif request.user.is_author:
                return redirect('dashboard')
            elif request.user.is_out_expert or request.user.is_expert or request.user.is_moderator:
                return redirect('my_submit_tests')
            elif request.user.is_pupil:
                return redirect('pupil_dashboard')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def orientation_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_admin or request.user.is_editor:
            return redirect('home')
        elif request.user.is_out_expert:
            return redirect('my_submit_tests')
        elif request.user.is_pupil:
            return redirect('pupil_dashboard')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def password_reset_authentification(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return redirect('password_reset')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(role=None):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if role is not None:
                user = get_object_or_404(User, pk=request.user.id)
                if len(role) == 1:
                    current_user_roles = user.roles.all()
                    rol = Role.objects.get(code_name=role[0])
                    if rol in current_user_roles:
                        return view_func(request, *args, **kwargs)
                    else:
                        return render(request, 'user_app/not_access.html')
                if len(role) > 1:
                    r, lv = user.get_roles
                    lv = numpy.array(lv)
                    levels = []
                    for code_name in role:
                        t = get_object_or_404(Role, code_name=code_name)
                        levels.append(t.level)
                    levels = numpy.array(levels)
                    current_role_level = numpy.intersect1d(lv, levels)

                    if len(current_role_level) > 0:
                        return view_func(request, *args, **kwargs)
                    else:
                        return render(request, 'user_app/not_access.html')

        return wrapper_func

    return decorator
