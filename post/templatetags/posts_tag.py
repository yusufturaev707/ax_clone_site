from django import template
from post.models import Post

register = template.Library()


@register.simple_tag()
def get_last_posts():
    posts = Post.objects.all().order_by('-id')[:5]
    return posts