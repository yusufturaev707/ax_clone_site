from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _


class BlankPage(models.Model):
    title = models.CharField(max_length=255, unique=True)
    body = RichTextField(blank=True, null=True)
    is_publish = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("BlankPage")
        verbose_name_plural = _("BlankPages")


class Post(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    tag = RichTextField(blank=True, null=True)
    img = models.ImageField(upload_to='blog/')
    desc = RichTextField(blank=True, null=True)
    is_publish = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.SlugField(max_length=200, unique=True)

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.url})

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.title, allow_unicode=True)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")