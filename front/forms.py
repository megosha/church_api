from django import forms

from api import models


class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        exclude = ['user', 'position', 'active']


class NewsForm(forms.ModelForm):
    class Meta:
        model = models.News
        exclude = ['active']
