from django import forms

from expert.models import CheckTestExpert
from django.forms import Select, Textarea, FileInput
from django.utils.translation import gettext_lazy as _


class CheckTestExpertForm(forms.ModelForm):
    class Meta:
        model = CheckTestExpert
        fields = ['message', 'status', 'file']

        widgets = {
            'message': Textarea(attrs={
                'class': 'form-control message',
                'name': 'message',
                'id': 'id_message',
                'rows': '2',
            }),
            'status': Select(attrs={
                'class': 'form-control selectpicker status',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'status',
                'id': 'id_status'
            }),
            'file': FileInput(attrs={
                'class': 'form-control',
                'type': 'file',
                'name': 'file',
                'id': 'id_file',
                'accept': ".docx, .doc,",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CheckTestExpertForm, self).__init__(*args, **kwargs)
        self.fields['status'].empty_label = _("Tanlang")
