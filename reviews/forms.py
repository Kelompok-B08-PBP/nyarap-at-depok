from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['restaurant_name', 'food_name', 'review', 'rating']
