from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from post.forms import CreatePostForm, UpdatePostForm, CreatePageForm, UpdatePageForm
from post.models import Post, BlankPage
from django.utils.translation import gettext_lazy as _

from user_app.decorators import allowed_users


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def post_detail(request, slug):
    post = get_object_or_404(Post, url=slug)
    context = {
        'post': post,
    }
    return render(request, "post/post_detail.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def post_dashboard(request):
    posts = Post.objects.all()
    context = {
        'posts': posts,
    }
    return render(request, "post/post_dashboard.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def page_dashboard(request):
    pages = BlankPage.objects.all()
    context = {
        'pages': pages,
    }
    return render(request, "post/page_dashboard.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_post(request):
    if request.method == 'POST' and is_ajax(request):
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Muvaffaqiyatli yaratildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _("Forma to'liq emas!"),
            }
            return JsonResponse(data)

    form = CreatePostForm()
    context = {
        'form': form
    }
    return render(request, "post/create_post.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_page(request):
    if request.method == 'POST' and is_ajax(request):
        form = CreatePageForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Sahifa muvaffaqiyatli yaratildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _("Forma to'liq emas!"),
            }
            return JsonResponse(data)

    form = CreatePageForm()
    context = {
        'form': form
    }
    return render(request, "post/create_page.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST" and is_ajax(request):
        form = UpdatePostForm(request.POST, request.FILES, instance=post)
        if not form.has_changed():
            data = {"message": _("Ma'lumotlarda o'zgarish yo'q"), "result": False}
            return JsonResponse(data)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Muvaffaqiyatli bajarildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _("Xatolik yuz berdi!")
            }
            return JsonResponse(data)
    context = {
        'form': UpdatePostForm(instance=post),
        'post': post,
    }
    return render(request, "post/edit_post.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_page(request, pk):
    page = get_object_or_404(BlankPage, pk=pk)
    if request.method == "POST" and is_ajax(request):
        form = UpdatePageForm(request.POST, instance=page)
        if not form.has_changed():
            data = {"message": _("Ma'lumotlarda o'zgarish yo'q"), "result": False}
            return JsonResponse(data)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Muvaffaqiyatli bajarildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _("Xatolik yuz berdi!")
            }
            return JsonResponse(data)
    context = {
        'form': UpdatePageForm(instance=page),
        'page': page,
    }
    return render(request, "post/edit_page.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST" and is_ajax(request):
        post.delete()
        return JsonResponse({"message": _("Muvaffaqiyatli bajarildi!")})

    data = {"post": post}
    return render(request, "post/delete_post.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_page(request, pk):
    page = get_object_or_404(BlankPage, pk=pk)
    if request.method == "POST" and is_ajax(request):
        page.delete()
        return JsonResponse({"message": _("Muvaffaqiyatli bajarildi!")})

    data = {"page": page}
    return render(request, "post/delete_page.html", context=data)
