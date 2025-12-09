from django import forms

from moderator.models import *
from test_maker.models import Test, TestImage, SubmissionTest
from django.forms import Select, TextInput, Textarea
from django.utils.translation import gettext_lazy as _


class TexTestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['tex_code']

        widgets = {
            'tex_code': Textarea(attrs={
                'class': 'form-control tex_code',
                'name': 'tex_code',
                'id': 'id_tex_code',
                'rows': '15',
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


class TestImageForm(forms.Form):
    images = MultipleFileField(required=False)


class AnswerTestFillForm(forms.ModelForm):
    class Meta:
        model = SubmissionTest
        fields = ['a', 'b', 'c', 'd']

        widgets = {
            'a': Textarea(attrs={
                'class': 'form-control',
                'name': 'a',
                'id': 'id_a',
                'rows': '2',
            }),
            'b': Textarea(attrs={
                'class': 'form-control',
                'name': 'b',
                'id': 'id_b',
                'rows': '2',
            }),
            'c': Textarea(attrs={
                'class': 'form-control',
                'name': 'c',
                'id': 'id_c',
                'rows': '2',
            }),
            'd': Textarea(attrs={
                'class': 'form-control',
                'name': 'd',
                'id': 'id_d',
                'rows': '2',
            }),
        }


class CheckJobModeratorForm(forms.ModelForm):
    class Meta:
        model = ModeratorCheckTest
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super(CheckJobModeratorForm, self).__init__(*args, **kwargs)
        self.fields['status'].empty_label = _("Tanlang")
