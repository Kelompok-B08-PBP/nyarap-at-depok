from django.urls import path
from nyarap_detailer.views import detailer_list

app_name = 'nyarap_detailer'

urlpatterns = [
    path('', detailer_list, name='detailer_list'),

]

