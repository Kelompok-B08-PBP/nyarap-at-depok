from django.urls import path
from reviews.views import show_reviews, create_product_review, show_xml, show_json, show_xml_by_id, show_json_by_id, add_product_review_ajax
from . import views
# from reviews.views import edit_product_review
# from reviews.views import delete_product_review

app_name = 'reviews'

urlpatterns = [
    path('', show_reviews, name='show_reviews'),
    path('create-product-review', create_product_review, name='create_product_review'),
    path('xml/', show_xml, name='show_xml'),  
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    # path('edit-product-review/<uuid:id>', edit_product_review, name='edit_product_review'),
    # path('delete/<uuid:id>', delete_product_review, name='delete_product_review'),
    path('create-product-review-ajax', add_product_review_ajax, name='add_product_review_ajax'),
    path('show_reviews/', views.show_reviews, name='show_reviews'),

]