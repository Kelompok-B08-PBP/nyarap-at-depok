from django import forms
from .models import PostEntry

class PostEntryForm(forms.ModelForm):
    class Meta:
        model = PostEntry
        fields = ['title', 'caption', 'location', 'photo_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.Textarea(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
