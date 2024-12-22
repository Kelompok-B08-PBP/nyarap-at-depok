# urls.py
from django.urls import path
from . import views

app_name = 'nyarap_nanti'

urlpatterns = [
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/json/', views.wishlist_json, name='wishlist_json'),
    path('wishlist/note/add/<int:product_id>/', views.add_note, name='add_note'),
    path('wishlist/note/update/<int:note_id>/', views.update_note, name='update_note'),
    path('wishlist/note/delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('wishlist/notes/json/', views.notes_json, name='notes_json'),
    path('wishlist/notes/json/<int:product_id>/', views.notes_json, name='notes_json_by_product'),
    path('wishlist/remove-json/<int:product_id>/', views.remove_from_wishlist_json, name='remove_from_wishlist_json'),
    path('wishlist/note/add-flutter/<int:product_id>/', views.add_note_flutter, name='add_note_flutter'),
    path('wishlist/note/edit-flutter/<int:note_id>/', views.edit_note_flutter, name='edit_note_flutter'),
    path('wishlist/note/delete-flutter/<int:note_id>/', views.delete_note_flutter, name='delete_note_flutter'),


]
