from django import forms
from .models import UserPreference

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['preferred_location', 'preferred_breakfast_type', 'preferred_price_range']  # Fields that match your HTML form
