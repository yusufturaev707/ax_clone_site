from modeltranslation.translator import register, TranslationOptions
from journal.models import *


@register(Journal)
class JournalTranslationOptions(TranslationOptions):
    fields = ('name',)
