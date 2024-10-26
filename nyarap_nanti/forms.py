from django import forms
from .models import Collection

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter collection name',  # Anda juga bisa menambahkan placeholder
            }),
        }
