from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import Select, TextInput, SelectMultiple, NumberInput, Textarea, PasswordInput
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from user_app.models import *
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField, CaptchaTextInput, CaptchaAnswerInput


class CreateUserForm(UserCreationForm):
    captcha = CaptchaField(widget=CaptchaTextInput())

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'chosen_role']


class LoginForm(AuthenticationForm):
    captcha = CaptchaField(
        widget=CaptchaTextInput(),
        error_messages={'invalid': 'Xato belgilar kiritildi!'})

    class Meta:
        model = User
        fields = ['username', 'password']

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control username',
            }),
            'password': PasswordInput(attrs={
                'class': 'form-control password',
            }),
        }


class UpdateUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'work', 'sc_degree']

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control username',
                'type': 'text',
            }),
            'phone': TextInput(attrs={
                'class': 'form-control phone',
                'type': 'text',
                'id': 'masked-input-phone',
            }),
            'email': TextInput(attrs={
                'class': 'form-control email',
                'type': 'email',
            }),
            'work': TextInput(attrs={
                'class': 'form-control work',
                'type': 'text',
            }),
            'sc_degree': Select(attrs={
                'class': 'form-control sc_degree',
                'data-live-search': "true",
                'data-style': "btn-white",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.fields['sc_degree'].empty_label = _("Tanlang")


class ReviewerFileForm(forms.ModelForm):
    file = forms.FileField(
        label="Files",
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True, "name": "file"}), required=False
    )

    class Meta:
        model = ReviewerFile
        fields = ['file']


class AddReviewerForm(forms.ModelForm):
    class Meta:
        model = Reviewer
        fields = ['user', 'section']

        widgets = {
            'section': SelectMultiple(attrs={
                'class': 'multiple-select2 form-control',
                'multiple': 'multiple',
                'name': 'section',
            }),
        }


class CreateCountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateRegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateGenderForm(forms.ModelForm):
    class Meta:
        model = Gender
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'code_name', 'level']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'code_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'level': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateScientificDegreeForm(forms.ModelForm):
    class Meta:
        model = ScientificDegree
        fields = ['name', 'level']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'level': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateMenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'url', 'url_name', 'icon_name', 'order', 'status', 'type', 'allowed_roles']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'url': TextInput(attrs={
                'class': 'form-control',
            }),
            'url_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'icon_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'order': NumberInput(attrs={
                'class': 'form-control',
            }),
            'type': NumberInput(attrs={
                'class': 'form-control',
            }),
            'allowed_roles': SelectMultiple(attrs={
                'class': 'multiple-select2 form-control',
                'multiple': 'multiple',
                'name': 'allowed_roles',
            }),
        }


class ReviewArticleForm(forms.ModelForm):
    class Meta:
        model = ReviewerArticle
        fields = ['comment']

        widgets = {
            'comment': Textarea(attrs={
                'class': 'form-control desc',
                'rows': '3',
                'name': 'comment',
                'id': 'id_comment',
            }),

        }
