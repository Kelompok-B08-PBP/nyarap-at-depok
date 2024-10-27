from django import forms
from .models import Product
from django.utils.html import strip_tags

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['restaurant_name', 'food_name', 'review', 'rating']

    def clean_restaurant_name(self):
        restaurant_name = self.cleaned_data.get("restaurant_name")
        return strip_tags(restaurant_name)

    def clean_food_name(self):
        food_name = self.cleaned_data.get("food_name")
        return strip_tags(food_name)

    def clean_review(self):
        review = self.cleaned_data.get("review")
        return strip_tags(review)

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        return rating 