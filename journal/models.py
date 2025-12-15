import os
import time

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class JournalYear(models.Model):
    year = models.PositiveBigIntegerField(
        default=2000,
        validators=[
            MinValueValidator(1995, message="Son 1995 dan kichik bo'lishi mumkin emas."),
            MaxValueValidator(2100, message="Son 2100 dan katta bo'lishi mumkin emas.")
        ],
        help_text=_("Jurnal sonining yili (1995 dan 2100 gacha) bo'lishi kerak.")
    )
    status = models.BooleanField(default=True)
    year_img = models.ImageField(upload_to="image_year/", null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'png'])],
                              help_text='Please upload only image!')

    def __str__(self):
        return str(self.year)


class JournalNumber(models.Model):
    number = models.PositiveBigIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, message="Son 1 dan kichik bo'lishi mumkin emas."),
            MaxValueValidator(10, message="Son 10 dan katta bo'lishi mumkin emas.")
        ],
        help_text=_("Jurnal soni (1 dan 10 gacha) bo'lishi kerak.")
    )
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.number)


def user_directory_path(instance, filename):
    return 'files/journals/{0}'.format(filename)


class Journal(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="files/journal_images", max_length=255, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'png'])],
                              help_text='Please upload only image!')
    file_pdf = models.FileField(_("To'liq versiyasi"), upload_to=user_directory_path, max_length=255, blank=True,
                                null=True,
                                validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                                help_text='Please upload only .pdf!')
    file_head_pdf = models.FileField(_("Jurnalni bosh qismi"), upload_to="files/journals/head_template", max_length=255,
                                     blank=True, null=True,
                                     validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                                     help_text='Please upload only .pdf!')
    file_mundarija = models.FileField(_("Mundarija"), upload_to="files/journals/mundarija", max_length=255, null=True)
    count_of_head_file = models.PositiveSmallIntegerField(default=0)
    year = models.ForeignKey('journal.JournalYear', on_delete=models.CASCADE, blank=True, null=True)
    number = models.ForeignKey('journal.JournalNumber', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_publish = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    is_split = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Journal")


class JournalArticle(models.Model):
    journal = models.ForeignKey('journal.Journal', on_delete=models.CASCADE, related_name="journal_article")
    article = models.ForeignKey('article_app.Article', on_delete=models.CASCADE, related_name="article")
    start_page = models.PositiveBigIntegerField(default=0)
    end_page = models.PositiveBigIntegerField(default=0)
    order_page = models.IntegerField(default=0)
    article_pdf = models.FileField(_("Fayl"), upload_to="files/split_article", max_length=255, null=True,
                                   validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                                   help_text='Please upload only .pdf!')
    year = models.IntegerField(default=0)
    number = models.IntegerField(default=0)
    count_author = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.journal.name)


def upload_to_file(instance, filename):
    time_sec = int(time.time())
    ext = filename.split('.')[-1]
    filename_new = f"{instance.article.author.id}{instance.article.id}{time_sec}.{ext}"
    return os.path.join(instance.directory_string_var, filename_new)


class UploadFile(models.Model):
    article = models.ForeignKey('article_app.Article', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_to_file, max_length=255, blank=True,
                            validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    directory_string_var = 'uploads/'
