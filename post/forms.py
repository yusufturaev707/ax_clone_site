from django.forms import TextInput, NumberInput, FileInput, CheckboxInput, Textarea
from post.models import Post, BlankPage
from django import forms


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'tag', 'desc', 'img']

        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control title',
                'name': 'title',
                'id': 'id_title'
            }),
            'tag': Textarea(attrs={
                'class': 'form-control tag',
                'rows': '3',
                'name': 'tag',
                'id': 'id_tag',
            }),
            'desc': Textarea(attrs={
                'class': 'form-control desc',
                'rows': '3',
                'name': 'desc',
                'id': 'id_desc',
            }),
            'img': FileInput(attrs={
                'class': 'form-control image',
                'name': 'img',
                'id': 'id_img',
                'type': 'file',
                'accept': ".jpg, .jpeg, .png",
            }),
        }


class CreatePageForm(forms.ModelForm):
    class Meta:
        model = BlankPage
        fields = ['title', 'body', 'key', 'is_publish']

        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control title',
                'name': 'title',
                'id': 'id_title',
            }),
            'key': TextInput(attrs={
                'class': 'form-control key',
                'name': 'key',
                'id': 'id_key',
            }),
            'body': Textarea(attrs={
                'class': 'form-control body',
                'rows': '3',
                'name': 'body',
                'id': 'id_body',
            }),
        }


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'tag', 'desc', 'img', 'is_publish']

        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control title',
                'name': 'title',
                'id': 'id_title'
            }),
            'tag': Textarea(attrs={
                'class': 'form-control tag',
                'rows': '3',
                'name': 'tag',
                'id': 'id_tag',
            }),
            'desc': Textarea(attrs={
                'class': 'form-control desc',
                'rows': '3',
                'name': 'desc',
                'id': 'id_desc',
            }),
            'img': FileInput(attrs={
                'class': 'form-control image',
                'name': 'img',
                'id': 'id_img',
                'type': 'file',
                'accept': ".jpg, .jpeg, .png",
            }),

        }


class UpdatePageForm(forms.ModelForm):
    class Meta:
        model = BlankPage
        fields = ['title', 'body', 'key', 'is_publish']

        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control title',
                'name': 'title',
                'id': 'id_title'
            }),
            'body': Textarea(attrs={
                'class': 'form-control body',
                'rows': '3',
                'name': 'body',
                'id': 'id_body',
            }),
            'key': TextInput(attrs={
                'class': 'form-control key',
                'name': 'key',
                'id': 'id_key',
                'placeholder': 'key'
            }),
        }
