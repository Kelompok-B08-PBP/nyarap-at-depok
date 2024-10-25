from django.urls import path
from nyarap_detailer.views import detailer_list, detail_view

app_name = 'nyarap_detailer'

urlpatterns = [
    path('', detailer_list, name='detailer_list'),
    path('detail/<int:id>/', detail_view, name='detail'),
]

