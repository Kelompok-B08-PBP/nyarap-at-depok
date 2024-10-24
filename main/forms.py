from django import forms
from .models import UserPreference

class PreferencesForm(forms.Form):
    preferred_location = forms.ChoiceField(
        choices=UserPreference.KECAMATAN_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500'
        })
    )
    preferred_breakfast_type = forms.ChoiceField(
        choices=UserPreference.BREAKFAST_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500'
        })
    )
    preferred_price_range = forms.ChoiceField(
        choices=UserPreference.PRICE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500'
        })
    )

class BreakfastForm(forms.Form):
    preferred_breakfast_type = forms.ChoiceField(
        choices=UserPreference.BREAKFAST_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500'
        })
    )

class LocationForm(forms.Form):
    preferred_location = forms.ChoiceField(
        choices=UserPreference.KECAMATAN_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500'
        })
    )

class PriceForm(forms.Form):
    preferred_price_range = forms.ChoiceField(
        choices=UserPreference.PRICE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500'
        })
    )

