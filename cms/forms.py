from django import forms
from django.contrib.auth.models import User

from .models import Post, Review, Subscription


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['categories'].form = forms.MultipleChoiceField()
        self.fields['categories'].widget.attrs['class'] = 'ui multiple search selection dropdown'

        author_qs = User.objects.filter(groups__name='authors').exclude(username=self.user.username)

        self.fields['authors'].form = forms.ModelMultipleChoiceField(queryset=author_qs)
        self.fields['authors'].queryset = author_qs
        self.fields['authors'].widget.attrs['class'] = 'ui multiple search selection dropdown'

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'categories', 'authors', ]


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['content']
        labels = {'content': 'Review'}


class SubscriptionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories'].form = forms.MultipleChoiceField()
        self.fields['categories'].widget.attrs['class'] = 'ui multiple search selection dropdown'

        self.fields['authors'].form = forms.ModelMultipleChoiceField(queryset=None)
        self.fields['authors'].queryset = User.objects.filter(groups__name='authors')
        self.fields['authors'].widget.attrs['class'] = 'ui multiple search selection dropdown'

    class Meta:
        model = Subscription
        fields = ['authors', 'categories', ]


class AssignForm(forms.Form):

    editors = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['editors'].queryset = User.objects.filter(groups__name='editor')
        self.fields['editors'].widget.attrs['class'] = 'ui multiple search selection dropdown'

