from django.urls import path
from main.views import show_main, create_preference_entry, show_xml, show_json, show_xml_by_id, show_json_by_id, register, login_user,logout_user, recommendations, recommendation_list, edit_preferences


app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-preference-entry', create_preference_entry, name='create_preference_entry'),
    path('recommendations/', recommendations, name='recommendations'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('recommendations/list/', recommendation_list, name='recommendation_list'),
    path('edit-preferences/', edit_preferences, name='edit_preferences'),
]