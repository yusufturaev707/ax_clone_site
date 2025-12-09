from modeltranslation.translator import register, TranslationOptions
from user_app.models import *


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Gender)
class GenderTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Role)
class RoleTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Menu)
class MenuTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ScientificDegree)
class ScientificDegreeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(StatusReview)
class StatusReviewTranslationOptions(TranslationOptions):
    fields = ('name',)
