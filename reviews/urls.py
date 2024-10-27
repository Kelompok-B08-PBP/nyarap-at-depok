from django.urls import path
from reviews.views import * 

app_name = 'reviews'

urlpatterns = [
    path('show_reviews/', show_reviews, name='show_reviews'),  
    path('add/', add_product_review_ajax, name='add_product_review_ajax'),  
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<int:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<int:id>/', show_json_by_id, name='show_json_by_id'),
    path('delete/<int:id>', delete_product_review, name='delete_product_review'),
    path('edit-product-review/<int:id>/', edit_product_review, name='edit_product_review'), 

]