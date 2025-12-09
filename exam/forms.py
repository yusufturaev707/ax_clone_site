from django import forms

from exam.models import Appeal
from django.forms import Select, TextInput, Textarea, FileInput
from django.utils.translation import gettext_lazy as _


class AppealForm(forms.ModelForm):
    class Meta:
        model = Appeal
        fields = ['pupil', 'exam', 'question', 'category', 'content']

        widgets = {
            'content': Textarea(attrs={
                'class': 'form-control',
                'name': 'content',
                'id': 'id_content',
                'placeholder': 'Izoh...',
                'rows': '2',
            }),
            'category': Select(attrs={
                'class': 'form-control',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'category',
                'id': 'id_category'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(AppealForm, self).__init__(*args, **kwargs)
        self.fields['category'].empty_label = _("Tanlang")