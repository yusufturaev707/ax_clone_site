from django import forms
from django.forms import TextInput, FileInput, NumberInput
from fileapp.models import *


class CreateFileForm(forms.ModelForm):
    class Meta:
        model = TemplateFile
        fields = ['name', 'template_file']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),

            'template_file': FileInput(attrs={
                'class': 'form-control',
                'name': 'template_file',
                'id': 'id_template_file',
                'accept': ".docx, .doc",
                'data - parsley - required': "true",
            }),
        }
