# -*- coding: utf-8 -*-

from django import forms
from models import *


class SitesForm(forms.ModelForm):
    class Meta:
        model = Sites
        fields = ['name','domain', 'status']

class UsersForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['firstname','lastname', 'emailaddress', 'siteid', 'usertype']


class RawDataFilesForm(forms.ModelForm):
    class Meta:
        fields = ['siteid','filename', 'status', 'narration']
        model = RawDataFiles
        widgets = {
          'narration': forms.Textarea(attrs={'rows':3, 'cols':55}),
        }

class RawDataFilesFormUpdate(forms.ModelForm):
    class Meta:
        fields = ['siteid','filename', 'status', 'refreshcache', 'narration']
        model = RawDataFiles
        widgets = {
          'narration': forms.Textarea(attrs={'rows':3, 'cols':55}),
        }

#custom search form, not based on django model
class SearchForm(forms.Form):
    startDate = forms.DateField()
    endDate = forms.DateField()
    siteID= forms.ModelChoiceField(queryset=Sites.objects.all())

