from ckeditor.fields import RichTextField
from django.db import models
from test_maker.models import Test
from expert.functions import generate_hash
from django.utils.translation import gettext_lazy as _


def image_dir_path(instance, filename):
    extension = filename.split('.')[-1]
    hash_name = generate_hash()
    new_filename = "certificates/%s.%s" % (hash_name, extension)
    return new_filename


class Expert(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE)
    subject = models.ForeignKey('test_maker.Subject', related_name="expert_subject", on_delete=models.CASCADE,
                                blank=True)
    lang_test = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE, blank=True)
    level = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.CASCADE, blank=True, null=True)
    is_expert = models.BooleanField(default=False)
    is_reviewed_before = models.BooleanField(default=False)
    is_have_cert = models.BooleanField(default=False)
    is_third_expert = models.BooleanField(default=False)
    certificate_training = models.TextField(blank=True, null=True)
    certificate_assessment = models.ImageField(upload_to=image_dir_path, blank=True, null=True)
    is_lang_specialist = models.BooleanField(default=False)
    is_sender = models.BooleanField(default=False)
    is_checker = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class CheckedTestCount(models.Model):
    expert = models.ForeignKey('expert.Expert', on_delete=models.CASCADE)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True)
    job_all_count = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.expert)


class CheckTestExpertStatus(models.Model):
    name = models.CharField(max_length=255, blank=True)
    code = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=255, blank=True)
    code = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class StepTest(models.Model):
    name = models.CharField(max_length=50)
    code = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Sheet(models.Model):
    name = models.CharField(max_length=255)
    code = models.PositiveSmallIntegerField(default=0)
    expertise_type = models.PositiveSmallIntegerField(default=0)
    part = models.ForeignKey('test_maker.Part', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class ControlSheet(models.Model):
    name = models.CharField(max_length=255)
    code = models.PositiveSmallIntegerField(default=0)
    sheet = models.ForeignKey('expert.Sheet', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class JobControlSheet(models.Model):
    job = models.ForeignKey('expert.CheckTestExpert', on_delete=models.CASCADE, blank=True)
    control_sheet = models.ForeignKey('expert.ControlSheet', on_delete=models.CASCADE, blank=True)
    result = models.SmallIntegerField(default=-1)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


# ----------- National Certificate ---------

class SheetNS(models.Model):
    name = models.CharField(max_length=255)
    code = models.PositiveSmallIntegerField(default=0)
    part = models.ForeignKey('test_maker.Part', on_delete=models.SET_NULL, blank=True, null=True)
    level = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class ControlSheetNS(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    code = models.PositiveSmallIntegerField(default=0)
    sheet = models.ForeignKey('expert.SheetNS', on_delete=models.SET_NULL, blank=True, null=True)
    status = models.BooleanField(default=False)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.SET_NULL, blank=True, null=True)
    part_option = models.ForeignKey('test_maker.OptionPart', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class JobControlSheetNS(models.Model):
    job = models.ForeignKey('expert.CheckTestExpert', on_delete=models.CASCADE, blank=True)
    control_sheet = models.ForeignKey('expert.ControlSheetNS', on_delete=models.CASCADE, blank=True)
    result = models.SmallIntegerField(default=-1)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


# Milliy sertifikatdagi moderator
class ExpertiseQuestionJob(models.Model):
    job = models.ForeignKey('moderator.ModeratorCheckTest', on_delete=models.CASCADE, blank=True)
    control_sheet = models.ForeignKey('expert.ControlSheetNS', on_delete=models.CASCADE, blank=True)
    result = models.SmallIntegerField(default=-1)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


# ----------------- END NS ------------------

class CheckTestExpert(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, null=True, blank=True)
    submission_test = models.ForeignKey('test_maker.SubmissionTest', on_delete=models.CASCADE, blank=True, null=True)
    expert = models.ForeignKey('expert.Expert', on_delete=models.SET_NULL, blank=True, null=True)
    is_check = models.BooleanField(default=False)
    status_test = models.ForeignKey('expert.CheckTestExpertStatus', on_delete=models.CASCADE, blank=True, null=True)
    step = models.ForeignKey('expert.StepTest', on_delete=models.CASCADE, blank=True, null=True)
    message = RichTextField(blank=True, null=True)
    result = models.PositiveSmallIntegerField(default=0)
    status = models.ForeignKey('expert.Status', on_delete=models.CASCADE, blank=True, null=True)
    is_extra_expert = models.BooleanField(default=False)
    file = models.FileField(upload_to="questions/", blank=True, null=True)
    is_job_given = models.SmallIntegerField(default=0)
    job_given_time = models.DateTimeField(blank=True, null=True)
    job_number = models.PositiveSmallIntegerField(default=1)
    is_third_expert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_data(self):
        topic = None
        level = None
        chapter = None
        section = None

        if self.submission_test.submission.type_test_upload.id == 1:
            if self.submission_test.submission.level_dn:
                level = self.submission_test.submission.level_dn.name
            if self.submission_test.submission.part:
                topic = self.submission_test.submission.part.name
        if self.submission_test.submission.type_test_upload.id == 2:
            if self.submission_test.submission.level_d:
                level = self.submission_test.submission.level_d.name
            if self.submission_test.submission.topic:
                topic = self.submission_test.submission.topic.name

        if self.submission_test.submission.chapter:
            chapter = self.submission_test.submission.chapter.name
        if self.submission_test.submission.section:
            section = self.submission_test.submission.section.name

        return {
            'id': self.id,
            'user_id': self.user.id,
            'user_fio': self.user.full_name,
            'submission_id': self.submission_test.submission.id,
            'expert_fio': self.expert.user.full_name,
            'expert_id': self.expert.id,
            'subject': self.submission_test.submission.subject.name,
            'lang': self.submission_test.submission.lang.name,
            'topic': topic,
            'chapter': chapter,
            'section': section,
            'level_d': level,
            'link_literature': self.submission_test.submission.link_literature,
            'step': self.step.name,
            'is_check': self.is_check,
            'status_test': self.status_test.name,
            'status_test_code': self.status_test.code,
            'job_type': self.submission_test.submission.type_test_upload.name,
            'job_given_time': self.job_given_time.strftime("%Y-%m-%d %H:%M:%S"),
            'job_number': self.job_number,
            'is_third_expert': self.is_third_expert,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self):
        return f"{self.id} {self.user.email} {self.submission_test.id} {self.submission_test.submission.subject.name}"
