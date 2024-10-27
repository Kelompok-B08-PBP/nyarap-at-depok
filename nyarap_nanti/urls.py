from django.urls import path
from . import views

app_name = 'nyarap_nanti'

urlpatterns = [
    path('', views.wishlist_page, name='wishlist_page'),
    path('create/', views.create_collection, name='create_collection'),
    path('collection/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collection/remove/<int:collection_id>/', views.remove_collection, name='remove_collection'),
    path('edit/<int:collection_id>/', views.edit_collection, name='edit_collection'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist_by_id'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  
]
