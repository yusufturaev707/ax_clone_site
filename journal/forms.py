from django.forms import TextInput, NumberInput, FileInput, CheckboxInput, Select, Textarea

from article_app.models import Article
from journal.models import *
from django import forms
from django.utils.translation import gettext_lazy as _


class CreateJournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['name', 'year', 'number']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control name forshadow',
                'name': 'name',
                'value': 'Axborotnoma',
                'id': 'id_name'
            }),
            'year': Select(attrs={
                'class': 'form-control year selectpicker forshadow',
                'name': 'year',
                'id': 'id_year',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data - parsley - required': "true",
            }),

            'number': Select(attrs={
                'class': 'form-control number selectpicker forshadow',
                'name': 'number',
                'id': 'id_number',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data - parsley - required': "true",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CreateJournalForm, self).__init__(*args, **kwargs)
        self.fields['year'].empty_label = _("Tanlang")
        self.fields['number'].empty_label = _("Tanlang")


class UpdateJournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['name', 'year', 'number', 'is_publish', 'status', 'image', 'file_head_pdf']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control forshadow',
                'data - parsley - required': "true",
            }),
            'year': Select(attrs={
                'class': 'form-control year selectpicker forshadow',
                'name': 'year',
                'id': 'id_year',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data - parsley - required': "true",
            }),

            'number': Select(attrs={
                'class': 'form-control number selectpicker forshadow',
                'name': 'number',
                'id': 'id_number',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data - parsley - required': "true",
            }),

            'file_head_pdf': FileInput(attrs={
                'class': 'form-control file_head_pdf forshadow',
                'name': 'file_head_pdf',
                'type': 'file',
                'id': 'id_file_head_pdf',
            }),

            'image': FileInput(attrs={
                'class': 'form-control image forshadow',
                'name': 'image',
                'id': 'id_image',
                'type': 'file',
                'accept': ".jpg, .jpeg, .png",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateJournalForm, self).__init__(*args, **kwargs)
        self.fields['year'].empty_label = _("Tanlang")
        self.fields['number'].empty_label = _("Tanlang")


class UploadArticleFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['article', 'file']

        widgets = {
            'file': FileInput(attrs={
                'class': 'form-control',
                'name': 'file',
                'id': 'file',
                'accept': ".pdf",
                'data - parsley - required': "true",
            }),
        }


class JournalYearForm(forms.ModelForm):
    class Meta:
        model = JournalYear
        fields = ['year', 'status']

        widgets = {
            'year': NumberInput(attrs={
                'class': 'form-control year',
                'name': 'year',
                'id': 'id_year',
            }),
        }


class JournalNumberForm(forms.ModelForm):
    class Meta:
        model = JournalNumber
        fields = ['number', 'status']

        widgets = {
            'number': NumberInput(attrs={
                'class': 'form-control number',
                'name': 'number',
                'id': 'id_number',
            }),
        }


class UpdateArticleAbKeyForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['abstract', 'keywords', 'abstract_en', 'keywords_en']

        widgets = {
            'abstract': Textarea(attrs={
                'class': 'form-control',
                'name': 'abstract',
                'id': 'id_abstract',
            }),
            'abstract_en': Textarea(attrs={
                'class': 'form-control',
                'name': 'abstract_en',
                'id': 'id_abstract_en',
            }),
            'keywords': Textarea(attrs={
                'class': 'form-control',
                'name': 'keywords',
                'id': 'id_keywords',
            }),
            'keywords_en': Textarea(attrs={
                'class': 'form-control',
                'name': 'keywords_en',
                'id': 'id_keywords_en',
            }),
        }
