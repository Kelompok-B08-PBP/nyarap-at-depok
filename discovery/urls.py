from django.urls import path
from discovery.views import show_post, create_post_entry, show_xml, show_json, show_xml_by_id, show_json_by_id
from discovery import views


app_name = 'discovery'

urlpatterns = [
    path('discovery/', views.show_post, name='show_post'),
    path('create-post-entry', create_post_entry, name='create_post_entry'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('post/', show_post, name='show_post'),
    path('post/edit/<int:id>/', views.edit_post, name='edit_post'),
    path('delete/<int:id>/', views.delete_post, name='delete_post'),
    path('get-posts/', views.get_posts, name='get_posts'),
    
   
]