import hashlib

from django import forms
from rest_framework import serializers


class GetFileListForm(forms.Form):
    pageNo = forms.IntegerField(min_value=0, required=False)
    pageSize = forms.IntegerField(min_value=0, required=False)
    fileNameFuzzy = forms.CharField(max_length=255, required=False)
    filePid = forms.IntegerField(required=True)
    searchFilename = forms.CharField(required=False)