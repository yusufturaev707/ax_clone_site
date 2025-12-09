from modeltranslation.translator import register, TranslationOptions
from post.models import *


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'tag', 'desc')


@register(BlankPage)
class BlankPageTranslationOptions(TranslationOptions):
    fields = ('title', 'body')
