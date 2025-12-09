import os
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from user_app.validator import validate_file_size


class Country(models.Model):
    name = models.CharField(_('Name'), max_length=50)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    doc_give_place_id = models.BigIntegerField(default=0)

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey('user_app.Region', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(_('Name'), max_length=50)

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(_('Name'), max_length=10)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(_('Name'), max_length=255, unique=True)
    code_name = models.CharField(max_length=10, blank=True, null=True)
    level = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class ScientificDegree(models.Model):
    name = models.CharField(max_length=255, blank=True, unique=True)
    level = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField(_("Username"), max_length=100, blank=True, unique=True)
    last_name = models.CharField(_('Surname'), max_length=100, blank=True, null=True)
    first_name = models.CharField(_('Name'), max_length=100, blank=True, null=True)
    middle_name = models.CharField(_('Middle Name'), max_length=30, null=True, blank=True)
    birthday = models.DateField(_('Birthday'), null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True, blank=True)
    avatar = models.TextField(blank=True, null=True)
    email = models.EmailField(_('Email address'), max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Phone number')
    pser = models.CharField(_('Passport'), max_length=2, blank=True, null=True)
    pnum = models.CharField(_('Passport'), max_length=7, blank=True, null=True)
    work = models.CharField(max_length=255, null=True, blank=True)
    region = models.ForeignKey('user_app.Region', on_delete=models.CASCADE, verbose_name="Region", null=True,
                               blank=True)
    district = models.ForeignKey('user_app.District', on_delete=models.CASCADE, blank=True, null=True)
    roles = models.ManyToManyField('user_app.Role', related_name="user_roles", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sc_degree = models.ForeignKey('user_app.ScientificDegree', on_delete=models.CASCADE, blank=True, null=True)
    jshshr = models.CharField(max_length=14, blank=True)
    chosen_role = models.ForeignKey('user_app.Role', on_delete=models.CASCADE, blank=True)
    system_type = models.PositiveSmallIntegerField(default=0)
    is_blocked = models.BooleanField(default=True)

    @property
    def full_name(self):
        if self.first_name is not None and self.last_name is not None and self.middle_name is not None:
            full_name_user = f"{self.last_name} {self.first_name} {self.middle_name}"
        else:
            full_name_user = f"{self.username}"
        return full_name_user

    @property
    def get_roles(self):
        roles = []
        levels = []
        for role in self.roles.all():
            roles.append(role.id)
            levels.append(role.level)
        return roles, levels

    @property
    def is_full_personal_data(self):
        is_person = True
        if (self.birthday is None or self.gender is None or self.phone is None or self.pser is None or self.pnum is None
                or self.work is None or self.jshshr is None or self.sc_degree is None):
            is_person = False
        return is_person

    @property
    def is_get_ps_data(self):
        is_person = True
        if self.birthday is None or self.gender is None or self.pser is None or self.pnum is None or self.jshshr is None or self.last_name is None or self.first_name is None or self.middle_name is None:
            is_person = False
        return is_person

    @property
    def is_admin(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 1:
                is_ = True
        return is_

    @property
    def is_editor(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 2:
                is_ = True
        return is_

    @property
    def is_reviewer(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 3:
                is_ = True
        return is_

    @property
    def is_author(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 4:
                is_ = True
        return is_

    @property
    def is_expert(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 5:
                is_ = True
        return is_

    @property
    def is_moderator(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 6:
                is_ = True
        return is_

    @property
    def is_out_expert(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 7:
                is_ = True
        return is_

    @property
    def is_pupil(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 8:
                is_ = True
        return is_

    @property
    def is_translator(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 9:
                is_ = True
        return is_

    @property
    def is_admin1(self):
        is_ = False
        for role in self.roles.all():
            if role.level == 10:
                is_ = True
        return is_

    def __str__(self):
        return self.username


class Editor(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True)
    is_editor = models.BooleanField(default=False)


class Reviewer(models.Model):
    section = models.ManyToManyField('article_app.Section', related_name="reviewer_sections", blank=True)
    scientific_degree = models.ForeignKey('user_app.ScientificDegree', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    is_reviewer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReviewerFile(models.Model):
    reviewer = models.ForeignKey('user_app.Reviewer', on_delete=models.CASCADE, blank=True)
    file = models.FileField(_("Fayl"), upload_to="files/reviewer/%Y/%m/%d", max_length=255, blank=True, null=True)

    def clean(self):
        validator = FileExtensionValidator(allowed_extensions=['doc', 'docx', 'pdf'])
        if self.file:
            validator(self.file)

    def file_name(self):
        return str(self.file.name.split("/")[-1].replace('_', ' ').replace('-', ' '))

    def file_size(self):
        return self.file.size

    def file_type(self):
        name, type_f = os.path.splitext(self.file.name)
        return type_f


class ReviewerEditorStatus(models.Model):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class ReviewerEditor(models.Model):
    reviewer = models.ForeignKey('user_app.Reviewer', blank=True, on_delete=models.CASCADE)
    editor = models.ForeignKey('user_app.Editor', on_delete=models.CASCADE, blank=True)
    status = models.ForeignKey('user_app.ReviewerEditorStatus', on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StatusReview(models.Model):
    name = models.CharField(_('Name'), max_length=255, unique=True)

    def __str__(self):
        return self.name


class ReviewerArticle(models.Model):
    article = models.ForeignKey('article_app.Article', on_delete=models.CASCADE, related_name="review_article",
                                blank=True)
    editor = models.ForeignKey('user_app.Editor', on_delete=models.CASCADE, related_name="review_editor", blank=True)
    reviewer = models.ForeignKey('user_app.Reviewer', on_delete=models.CASCADE, related_name="review_reviewer",
                                 blank=True)
    status = models.ForeignKey('user_app.StatusReview', on_delete=models.CASCADE, related_name="review_status",
                               blank=True)
    comment = models.TextField(blank=True, null=True)
    result = models.PositiveSmallIntegerField(default=0)
    is_extra = models.BooleanField(default=False)
    notification = models.ForeignKey('article_app.Notification', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resubmit_reviewer = models.BooleanField(default=False)


class Menu(models.Model):
    name = models.CharField(max_length=100)
    icon_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    url_name = models.CharField(max_length=255, null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    status = models.BooleanField(default=True)
    allowed_roles = models.ManyToManyField('user_app.Role', related_name='allowed_role_menus', blank=True)
    type = models.PositiveSmallIntegerField(default=0)
    system_type = models.PositiveSmallIntegerField(default=0)

    def get_roles(self):
        return [p.name for p in self.allowed_roles.all()]

    def get_levels(self):
        return [l.level for l in self.allowed_roles.all()]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(f'{self.url_name}')
