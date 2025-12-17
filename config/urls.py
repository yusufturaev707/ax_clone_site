from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

# 1. i18n URL (til prefiksisiz) - TO'G'RI
urlpatterns = [
    path('ax_clone_site/i18n/', include('django.conf.urls.i18n')),
]

# 2. Media va Static (til prefiksisiz)
urlpatterns += [
    re_path(r'^ax_clone_site/media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^ax_clone_site/static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# 3. Barcha boshqa URL'lar (til prefiksli)
urlpatterns += i18n_patterns(
    path('ax_clone_site/admin/', admin.site.urls),
    path('ax_clone_site/captcha/', include('captcha.urls')),
    path('ax_clone_site/', include('article_app.urls')),
    path('ax_clone_site/profile/', include('user_app.urls')),
    path('ax_clone_site/journal/', include('journal.urls')),
    path('ax_clone_site/post/', include('post.urls')),
    path('ax_clone_site/fileapp/', include('fileapp.urls')),
    path('ax_clone_site/test_maker/', include('test_maker.urls')),
    path('ax_clone_site/expert/', include('expert.urls')),
    path('ax_clone_site/moderator/', include('moderator.urls')),
    path('ax_clone_site/question/', include('question.urls')),
    path('ax_clone_site/pupil/', include('pupil.urls')),
    path('ax_clone_site/exam/', include('exam.urls')),
    path('ax_clone_site/admin1/', include('admin1.urls')),
    path('ax_clone_site/ckeditor/', include('ckeditor_uploader.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'user_app.views.error_404'
handler500 = 'user_app.views.error_500'