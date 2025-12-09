from modeltranslation.translator import register, TranslationOptions
from article_app.models import *


@register(Section)
class SectionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ArticleType)
class ArticleTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ArticleLanguage)
class ArticleLanguageTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Stage)
class StageTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ArticleStatus)
class ArticleStatusPageTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(NotificationStatus)
class NotificationStatusTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Notification)
class NotificationTranslationOptions(TranslationOptions):
    fields = ('message',)
