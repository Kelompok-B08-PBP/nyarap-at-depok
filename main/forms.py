from django import forms
from .models import UserPreference, Comment

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['preferred_location', 'preferred_breakfast_type', 'preferred_price_range']  # Fields that match your HTML form

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tambahkan komentar Anda...'}),
        }
