from django import forms
from .models import WishlistNote

class WishlistNoteForm(forms.ModelForm):
    class Meta:
        model = WishlistNote
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm resize-none focus:ring-blue-500 focus:border-blue-500',
                'rows': '3',
                'placeholder': 'Add your notes here...'
            })
        }
