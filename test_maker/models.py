import os
import time
import hashlib

from django.core.validators import FileExtensionValidator
from django.db import models
from ckeditor.fields import RichTextField
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from config import settings


class Teacher(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE)
    token_for_pupil = models.UUIDField(blank=True, null=True)


class State(models.Model):
    name = models.CharField(max_length=255)
    key = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class SubjectBox(models.Model):
    teacher = models.ForeignKey('test_maker.Teacher', on_delete=models.CASCADE)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE)
    lang = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE)
    count = models.BigIntegerField(default=0)

    def __str__(self):
        return self.teacher.user.username


class QuestionBox(models.Model):
    subject_box = models.ForeignKey('test_maker.SubjectBox', on_delete=models.CASCADE)
    box_number = models.PositiveIntegerField(default=0)
    count_question = models.PositiveIntegerField(default=0)
    limit_question = models.PositiveSmallIntegerField(default=5)
    questions = models.ManyToManyField('question.QuestionAdmission', related_name='questions', blank=True)

    def __str__(self):
        return str(self.id)

    def get_percent(self):
        return f"{int(round(self.count_question * 100 / self.limit_question, 1))}"


class LanguageTest(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class LevelDifficulty(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=10)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class LevelDifficultyNational(models.Model):
    name = models.CharField(max_length=255)
    ielts = models.FloatField(default=0)
    key = models.CharField(max_length=10, blank=True, null=True)
    desc = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(_("Fan nomi"), max_length=255, blank=True)
    status = models.BooleanField(default=True)
    is_lang = models.BooleanField(default=False)
    lang_key = models.CharField(max_length=10, blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    picture = models.ImageField(upload_to="subjects/", default="no-image.png")
    duration = models.DurationField(default="00:30:00")
    limit_question = models.PositiveSmallIntegerField(default=30)

    def __str__(self):
        return self.name


class TypeTestUpload(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class Chapter(models.Model):
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    chapter = models.ForeignKey('test_maker.Chapter', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Theme(models.Model):
    section = models.ForeignKey('test_maker.Section', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Part(models.Model):
    is_lang = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=10, blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Test(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    file_word = models.FileField(upload_to="documents/", max_length=255, blank=True,
                                 validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx'])])
    file_pdf = models.FileField(upload_to="questions/", max_length=255, blank=True, null=True,
                                validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    tex_code = models.TextField(blank=True, null=True)
    file_tex = models.FileField(upload_to="questions/", max_length=255, blank=True, null=True,
                                validators=[FileExtensionValidator(allowed_extensions=['tex'])])
    number = models.CharField(max_length=8, blank=True, null=True)
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def file_name(self):
        return str(self.file_word.name.split("/")[-1])

    def __str__(self):
        return self.file_word.name


def upload_image_file(instance, filename):
    ext = filename.split('.')[-1]
    test = get_object_or_404(Test, instance=instance.test)
    number = test.number
    path = f"{settings.MEDIA_ROOT}questions/{number}/images"
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(f"{path}/", filename)


class TestImage(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    test = models.ForeignKey('test_maker.Test', on_delete=models.CASCADE, blank=True, null=True)
    img = models.ImageField(upload_to=upload_image_file, blank=True, null=True,
                            validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])
    number = models.CharField(max_length=8, blank=True, null=True)
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Audio(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    audio = models.FileField(blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['mp3'])])
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OptionPart(models.Model):
    type_test_upload = models.ForeignKey('test_maker.TypeTestUpload', on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True, null=True)
    lang_s = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE, blank=True, null=True)
    part = models.ForeignKey('test_maker.Part', on_delete=models.CASCADE, blank=True, null=True)
    level = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=True)
    key = models.CharField(max_length=50, blank=True, null=True)
    number_question = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TemplateQuestion(models.Model):
    type_test_upload = models.ForeignKey('test_maker.TypeTestUpload', on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True, null=True)
    lang_s = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE, blank=True, null=True)
    part = models.ForeignKey('test_maker.Part', on_delete=models.CASCADE, blank=True, null=True)
    level = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.CASCADE, blank=True, null=True)
    part_option = models.ForeignKey('test_maker.OptionPart', on_delete=models.CASCADE, blank=True, null=True)
    template_file = models.FileField(upload_to="question_templates/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['docx', 'doc'])])
    name = models.CharField(max_length=255, blank=True, null=True)
    number_question = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Submission(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE)
    chapter = models.ForeignKey('test_maker.Chapter', on_delete=models.CASCADE, blank=True, null=True)
    section = models.ForeignKey('test_maker.Section', on_delete=models.CASCADE, blank=True, null=True)
    topic = models.ForeignKey('test_maker.Theme', on_delete=models.CASCADE, blank=True, null=True)
    topic_n = models.CharField(max_length=255, blank=True, null=True)
    level_d = models.ForeignKey('test_maker.LevelDifficulty', on_delete=models.CASCADE, blank=True, null=True)
    level_dn = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.CASCADE, blank=True, null=True)
    lang = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE)
    link_literature = RichTextField(blank=True, null=True)
    type_test_upload = models.ForeignKey('test_maker.TypeTestUpload', on_delete=models.CASCADE, blank=True, null=True)
    type_test = models.ForeignKey('test_maker.TypeTest', on_delete=models.CASCADE, blank=True, null=True)
    part = models.ForeignKey('test_maker.Part', on_delete=models.CASCADE, blank=True, null=True)
    part_option = models.ForeignKey('test_maker.OptionPart', on_delete=models.CASCADE, blank=True, null=True)
    is_have_audio = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject.name


class SubmissionTest(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    submission = models.ForeignKey('test_maker.Submission', related_name='submissions',
                                   on_delete=models.CASCADE, blank=True, null=True)
    test = models.ForeignKey('test_maker.Test', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='test_files')
    step = models.ForeignKey('test_maker.State', on_delete=models.CASCADE, blank=True, null=True)
    status = models.ForeignKey('test_maker.StatusCheck', on_delete=models.CASCADE, blank=True, null=True)
    message_full = models.TextField(blank=True, null=True)
    is_check_finish = models.BooleanField(default=False)
    test_type = models.ForeignKey('test_maker.TypeTest', on_delete=models.CASCADE, blank=True, null=True)
    audio = models.ForeignKey('test_maker.Audio', on_delete=models.CASCADE, blank=True, null=True)
    a = models.TextField(blank=True, null=True)
    b = models.TextField(blank=True, null=True)
    c = models.TextField(blank=True, null=True)
    d = models.TextField(blank=True, null=True)
    a_text = models.TextField(blank=True, null=True)
    is_have_img = models.BooleanField(default=False)
    is_have_audio = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.submission.subject.name

    def get_data(self):
        level_d = None
        topic = None
        topic_n = None
        part = None
        part_option = None
        chapter = None
        section = None

        if self.submission.type_test_upload.id == 1:
            if self.submission.level_dn:
                level_d = self.submission.level_dn.name
            if self.submission.part:
                part = self.submission.part.name
                topic_n = self.submission.topic_n
            if self.submission.part_option:
                part_option = self.submission.part_option.name

        if self.submission.type_test_upload.id == 2:
            if self.submission.level_d:
                level_d = self.submission.level_d.name
            if self.submission.topic:
                topic = self.submission.topic.name
            if self.submission.chapter:
                chapter = self.submission.chapter.name
            if self.submission.section:
                section = self.submission.section.name

        return {
            'id': self.id,
            'test_type': self.submission.type_test_upload.id,
            'test_type_name': self.submission.type_test_upload.name,
            'user_id': self.user.id,
            'submission_id': self.submission.id,
            'number': self.test.number,
            'last_name': self.user.last_name,
            'first_name': self.user.first_name,
            'middle_name': self.user.middle_name,
            'subject': self.submission.subject.name,
            'lang': self.submission.lang.name,
            'chapter': chapter,
            'section': section,
            'topic': topic,
            'topic_n': topic_n,
            'part': part,
            'part_option_name': part_option,
            'level_d': level_d,
            'step': self.step.name,
            'step_code': self.step.key,
            'status': self.status.name,
            'status_code': self.status.code,
            'file': self.test.file_word.url,
            'is_check_finish': self.is_check_finish,
            'is_editable': self.is_editable,
            'is_have_audio': self.is_have_audio,
            'is_have_img': self.is_have_img,
            'created_at': self.created_at.strftime("%d.%m.%Y"),
        }


class StatusCheck(models.Model):
    name = models.CharField(max_length=50)
    code = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class TypeTest(models.Model):
    name = models.CharField(max_length=50)
    code = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class TestConfirmationCount(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.SET_NULL, blank=True, null=True)
    subject_lang = models.ForeignKey('test_maker.LanguageTest', on_delete=models.SET_NULL, blank=True, null=True)
    level = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.SET_NULL, blank=True, null=True)
    section = models.ForeignKey('test_maker.Part', on_delete=models.SET_NULL, blank=True, null=True)
    part = models.ForeignKey('test_maker.OptionPart', on_delete=models.SET_NULL, blank=True, null=True)
    count = models.PositiveBigIntegerField(default=0)
    template_q = models.ForeignKey('test_maker.TemplateQuestion', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.user}-{self.level}-{self.section}-{self.part}: {self.count}"
