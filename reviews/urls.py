from django.urls import path
from reviews import views
from reviews.views import * 

app_name = 'reviews'

urlpatterns = [
    path('show_reviews/', show_reviews, name='show_reviews'),  
    path('add/<str:id>', add_product_review_ajax, name='add_product_review_ajax'),  
    path('add/', add_product_review_ajax_all, name='add_product_review_ajax_all'),  
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<int:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<int:id>/', show_json_by_id, name='show_json_by_id'),
    path('delete/<int:id>/', delete_product_review, name='delete_product_review'),
    path('edit-product-review/<int:id>/', edit_product_review, name='edit_product_review'), 
    path('get-reviews/', get_reviews, name='get_reviews'),
    path('get-user-id/', views.get_user_id, name='get_user_id'),
    path('get-reviews-for-product/<str:product_id>/', views.get_reviews_for_product, name='get_reviews_for_product'),
]