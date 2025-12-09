from django import forms
from django.forms import Select, TextInput, Textarea, FileInput, TimeInput, NumberInput, ClearableFileInput, \
    RadioSelect, CheckboxInput

from test_maker.models import Test, Theme, Subject, LevelDifficulty, LanguageTest, Submission, Audio, Chapter
from django.utils.translation import gettext_lazy as _


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'status', 'is_lang', 'lang_key', 'key', 'picture', 'duration', 'limit_question']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'name': 'name',
                'id': 'id_name'
            }),
            'duration': TimeInput(attrs={
                'class': 'form-control',
                'name': 'duration',
                'id': 'id_duration'
            }),
            'limit_question': NumberInput(attrs={
                'class': 'form-control',
                'name': 'limit_question',
                'id': 'id_limit_question'
            }),
            'picture': ClearableFileInput(attrs={
                'class': 'form-control',
                'name': 'picture',
                'id': 'id_picture'
            }),
            'status': CheckboxInput(attrs={
                'class': 'form-control',
                'name': 'status',
                'id': 'id_status',
                'type': 'radio',
            }),
            'is_lang': CheckboxInput(attrs={
                'class': 'form-control',
                'name': 'is_lang',
                'id': 'id_is_lang',
                'type': 'radio',
            }),
            'lang_key': TextInput(attrs={
                'class': 'form-control',
                'name': 'lang_key',
                'id': 'id_lang_key'
            }),
            'key': TextInput(attrs={
                'class': 'form-control',
                'name': 'key',
                'id': 'id_key'
            }),
        }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class TestForm(forms.Form):
    file_word = MultipleFileField()


class AudioForm(forms.ModelForm):
    class Meta:
        model = Audio
        fields = ['audio']

        widgets = {
            'audio': FileInput(attrs={
                'class': 'form-control'
            })
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['subject', 'lang', 'type_test_upload']

        widgets = {
            'lang': Select(attrs={
                'class': 'form-control lang forshadow',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'lang',
                'id': 'Lang'
            }),
            'type_test_upload': Select(attrs={
                'class': 'form-control type_test_upload forshadow selectpicker',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'type_test_upload',
                'id': 'id_type_test_upload'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(SubmissionForm, self).__init__(*args, **kwargs)
        self.fields['lang'].empty_label = _("Tanlang")
        self.fields['type_test_upload'].empty_label = _("Tanlang")


class EditSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['topic', 'topic_n', 'level_d', 'level_dn', 'part', 'chapter', 'section', 'part_option']

        widgets = {
            'level_d': Select(attrs={
                'class': 'form-control level_d',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'level_d',
                'id': 'Level',
            }),
            'level_dn': Select(attrs={
                'class': 'form-control level_dn',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'level_dn',
                'id': 'id_level_dn',
            }),
            'part': Select(attrs={
                'class': 'form-control part',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'part',
                'id': 'id_part',
            }),
            'topic_n': TextInput(attrs={
                'class': 'form-control topic_n',
                'name': 'topic_n',
                'id': 'id_topic_n',
                'placeholder': 'Mavzuni kiriting',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EditSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['topic'].empty_label = _("Tanlang")
        self.fields['level_d'].empty_label = _("Tanlang")


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ['section', 'name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class AddSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'key', 'status']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'key': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class AddLevelDifficultyForm(forms.ModelForm):
    class Meta:
        model = LevelDifficulty
        fields = ['name', 'key']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'key': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class AddLanguageTestForm(forms.ModelForm):
    class Meta:
        model = LanguageTest
        fields = ['name', 'key']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'key': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['subject', 'name', 'status']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'subject': Select(attrs={
                'class': 'form-control',
            }),
        }
