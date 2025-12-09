from django.core.validators import FileExtensionValidator
from django.db import models


class TemplateFile(models.Model):
    name = models.CharField(max_length=255, blank=True)
    template_file = models.FileField(upload_to="files/template/%Y/%m/%d", max_length=255, blank=True,
                                     validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx'])],
                                     help_text='Please upload only .doc or .docx files!')
    code_name = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
