from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Нет'
        self.fields['text'].widget.attrs['rows'] = 4

    class Meta:
        model = Post
        fields = ('text', 'group', 'image', 'video')

        def clean_subject(self):
            data = self.cleaned_data['video']
            if 'youtu' not in data.lower():
                raise forms.ValidationError(
                    'Видео должно быть из YoutTube')
            return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(),
        }
