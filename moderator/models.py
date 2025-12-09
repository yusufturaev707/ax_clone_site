from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator
from django.db import models


# Create your models here.
class Status(models.Model):
    name = models.CharField(max_length=255, blank=True)
    key = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Moderator(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE)
    is_moderator = models.BooleanField(default=False)
    upload_type = models.ForeignKey('test_maker.TypeTestUpload', on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey('test_maker.LanguageTest', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.full_name


class ModeratorCheckTest(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE)
    submission_test = models.ForeignKey('test_maker.SubmissionTest', on_delete=models.CASCADE, blank=True, null=True)
    moderator = models.ForeignKey('moderator.Moderator', on_delete=models.CASCADE, blank=True, null=True)
    status = models.ForeignKey('moderator.Status', on_delete=models.CASCADE, blank=True, null=True)
    result = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_job_given = models.PositiveSmallIntegerField(default=0)
    job_given_time = models.DateTimeField(blank=True, null=True)
    job_finish_time = models.DateTimeField(blank=True, null=True)
    upload_type = models.ForeignKey('test_maker.TypeTestUpload', on_delete=models.CASCADE, blank=True)
    is_check = models.BooleanField(default=False)

    def __str__(self):
        return self.moderator.user.full_name


class ConvertTexCount(models.Model):
    moderator = models.ForeignKey('moderator.Moderator', on_delete=models.CASCADE)
    converted_count = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.moderator)


class CheckedTest(models.Model):
    moderator = models.ForeignKey('moderator.Moderator', on_delete=models.CASCADE)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True, null=True)
    converted_count = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.moderator)
