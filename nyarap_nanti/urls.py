# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('wishlist/create/', views.create_collection, name='create_collection'),
    path('wishlist/collection/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('wishlist/remove/<int:restaurant_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/collection/remove/<int:collection_id>/', views.remove_collection, name='remove_collection'),
    path('wishlist/edit/<int:collection_id>/', views.edit_collection, name='edit_collection'),  # URL untuk edit koleksi
]
