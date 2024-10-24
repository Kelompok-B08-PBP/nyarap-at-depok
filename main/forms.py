# forms.py
from django import forms
from .models import UserPreference

class PreferencesForm(forms.ModelForm):
    BREAKFAST_CHOICES = [
        ('nasi_uduk', 'Nasi Uduk'),
        ('bubur_ayam', 'Bubur Ayam'),
        ('nasi_kuning', 'Nasi Kuning'),
        ('roti_bakar', 'Roti Bakar'),
        ('dimsum', 'Dimsum'),
    ]

    LOCATION_CHOICES = [
        ('beji', 'Beji'),
        ('pocin', 'Pocin'),
        ('margonda', 'Margonda'),
        ('ui', 'UI'),
    ]

    PRICE_RANGE_CHOICES = [
        ('under_10k', 'Di bawah Rp 10.000'),
        ('10k_20k', 'Rp 10.000 - Rp 20.000'),
        ('above_20k', 'Di atas Rp 20.000'),
    ]

    preferred_breakfast_type = forms.ChoiceField(choices=BREAKFAST_CHOICES, label='Tipe Sarapan')
    preferred_location = forms.ChoiceField(choices=LOCATION_CHOICES, label='Lokasi')
    preferred_price_range = forms.ChoiceField(choices=PRICE_RANGE_CHOICES, label='Rentang Harga')

    class Meta:
        model = UserPreference
        fields = ['preferred_breakfast_type', 'preferred_location', 'preferred_price_range']
        labels = {
            'preferred_breakfast_type': 'Tipe Sarapan',
            'preferred_location': 'Lokasi',
            'preferred_price_range': 'Rentang Harga'
        }


