from django.db import models


# Create your models here.
class Admin1(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True)
    is_admin1 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.full_name


class TypeVoice(models.Model):
    name = models.CharField(max_length=255)
    key = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class AudioLanguage(models.Model):
    name = models.CharField(max_length=255)
    key = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class HistoryConvertedTextToSpeech(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True)
    text = models.TextField(blank=True)
    type_voice = models.ForeignKey('admin1.TypeVoice', on_delete=models.CASCADE, blank=True)
    language = models.ForeignKey('admin1.AudioLanguage', on_delete=models.CASCADE, blank=True)
    audio_name = models.CharField(max_length=255, blank=True, unique=True)
    audio_file = models.FilePathField(path="speech/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.audio_name


class TextLanguage(models.Model):
    name = models.CharField(max_length=255)
    key = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class GeneratedText(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True)
    theme = models.CharField(max_length=255, blank=True, null=True)
    word_count = models.PositiveSmallIntegerField(default=0)
    text = models.TextField(blank=True, null=True)
    language = models.ForeignKey('admin1.TextLanguage', on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    test_data = models.TextField(blank=True, null=True)
    is_english = models.BooleanField(default=False)

    def __str__(self):
        return self.theme
