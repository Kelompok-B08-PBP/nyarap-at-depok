from django.forms import ModelForm
from main.models import UserPreference

class PreferencesForm(ModelForm):
    class Meta:
        model = UserPreference
        fields = ["preferred_location", "preferred_breakfast_type", "preferred_price_range"]