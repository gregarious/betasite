from django import forms
from onlyinpgh.chatter.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content',)

    def __init__(self, author, *args, **kwargs):
        self.author = author
        super(PostForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.author or not self.author.is_authenticated():
            raise forms.ValidationError('User must be logged in to post.')

    def save(self, commit=True, *args, **kwargs):
        post = super(PostForm, self).save(commit=False, *args, **kwargs)
        post.author = self.author
        if commit:
            post.save()
        return post
