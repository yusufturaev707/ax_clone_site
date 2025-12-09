import os
import re
import time
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


class Section(models.Model):
    name = models.CharField(_('Name'), max_length=150, blank=True, default=None)
    key = models.PositiveSmallIntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ArticleType(models.Model):
    name = models.CharField(_('Name'), max_length=150, blank=True, default=None)
    key = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class ArticleLanguage(models.Model):
    name = models.CharField(_('Name'), max_length=150, blank=True, default=None)
    key = models.CharField(max_length=10, blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Stage(models.Model):
    name = models.CharField(_('Name'), max_length=100, default=None)
    key = models.PositiveSmallIntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ArticleStatus(models.Model):
    name = models.CharField(max_length=100, default=None)
    stage = models.ForeignKey('article_app.Stage', on_delete=models.CASCADE, blank=True, null=True)
    key = models.PositiveSmallIntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


def upload_to_file(instance, filename):
    time_sec = int(time.time())
    ext = filename.split('.')[-1]
    filename_new = f"{instance.article.author.id}{instance.article.id}{time_sec}.{ext}"
    return os.path.join(instance.directory_string_var, filename_new)


class Article(models.Model):
    article_type = models.ForeignKey('article_app.ArticleType', on_delete=models.CASCADE, blank=True)
    country = models.ForeignKey('user_app.Country', on_delete=models.CASCADE, blank=True)
    article_lang = models.ForeignKey('article_app.ArticleLanguage', on_delete=models.CASCADE, blank=True)
    section = models.ForeignKey('article_app.Section', verbose_name="Section", related_name="article_section",
                                on_delete=models.CASCADE, blank=True)
    author = models.ForeignKey('user_app.User', on_delete=models.CASCADE, related_name="article_author", blank=True)
    file = models.ForeignKey('article_app.ArticleFile', related_name="article_file", blank=True,
                             on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, blank=True)
    abstract = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    title_en = models.CharField(max_length=255, blank=True)
    abstract_en = models.TextField(blank=True)
    keywords_en = models.TextField(blank=True)
    article_status = models.ForeignKey('article_app.ArticleStatus', on_delete=models.CASCADE, blank=True, null=True)
    is_publish = models.BooleanField(default=False)
    is_resubmit = models.BooleanField(default=False)
    is_publish_journal = models.BooleanField(default=False)
    is_checked_upload_file = models.BooleanField(default=False)
    checked_upload_file = models.FileField(_("Pdf Fayl"), upload_to='uploads/', blank=True, null=True,
                                           validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    filePDF = models.FileField(_("Pdf Fayl"), upload_to=upload_to_file, blank=True, null=True,
                               validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    start_page = models.PositiveBigIntegerField(default=0)
    end_page = models.PositiveBigIntegerField(default=0)
    order_page = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    number = models.IntegerField(default=0)

    # abstract_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']


class ArticleFile(models.Model):
    article = models.ForeignKey('article_app.Article', on_delete=models.CASCADE, blank=True)
    file = models.FileField(_("Word, Pdf Fayl"), upload_to=upload_to_file, max_length=255, blank=True,
                            validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx'])],
                            help_text='Please upload only .doc or .docx or files!')
    directory_string_var = 'files/articles/'
    file_status = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def file_name(self):
        return str(self.file.name.split("/")[-1])

    def file_size(self):
        return self.file.size

    def file_type(self):
        name, type_f = os.path.splitext(self.file.name)
        return type_f

    # def get_absolute_url(self):
    #     return reverse('article_app:document-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.article)


class ExtraAuthor(models.Model):
    article = models.ForeignKey('article_app.Article', on_delete=models.CASCADE, blank=True)
    lname = models.CharField(max_length=50, blank=True)
    fname = models.CharField(max_length=50, blank=True)
    mname = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True)
    work = models.CharField(max_length=255, blank=True, null=True)
    scientific_degree = models.ForeignKey('user_app.ScientificDegree', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.fname


class NotificationStatus(models.Model):
    name = models.CharField(_('Name'), max_length=50, blank=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    article = models.ForeignKey('article_app.Article', on_delete=models.CASCADE, blank=True)
    from_user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, related_name="sender_user", blank=True,
                                  null=True)
    to_user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, related_name="recieve_user", blank=True,
                                null=True)
    message = models.TextField(_("Message"), blank=True)
    notification_status = models.ForeignKey('article_app.NotificationStatus', on_delete=models.CASCADE, blank=True,
                                            null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_update_article = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
