from django.urls import path
from main.views import show_main, create_preference_entry, show_xml, show_json, show_xml_by_id, show_json_by_id, register, login_user,logout_user, recommendations, recommendation_list, edit_preferences, browse_category, product_details, product_details_recommendation, delete_preferences, add_to_wishlist, add_comment, delete_comment, edit_comment


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
    path('category/<str:category>/', browse_category, name='browse_category'),
    path('category/<str:category>/product/<int:product_id>/', product_details, name='product_details'),
    path('recommendations/list/product/<int:product_id>/', product_details_recommendation, name='product_details_recommendation'),
    path('delete-preferences/', delete_preferences, name='delete_preferences'),
    path('add-to-wishlist/<int:product_id>/', 
         add_to_wishlist, 
         name='add_to_wishlist'),
    path('add_comment/<int:product_id>/', add_comment, name='add_comment'),  # Pastikan ini sesuai
    path('delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
]
    
