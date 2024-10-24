from django.urls import path
from main.views import show_main, create_product_review, show_xml, show_json, show_xml_by_id, show_json_by_id, add_product_review_ajax
from main.views import register
from main.views import login_user
from main.views import logout_user
# from main.views import edit_product_review
# from main.views import delete_product_review

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-product-review', create_product_review, name='create_product_review'),
    path('xml/', show_xml, name='show_xml'),  
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    # path('edit-product-review/<uuid:id>', edit_product_review, name='edit_product_review'),
    # path('delete/<uuid:id>', delete_product_review, name='delete_product_review'),
    path('create-product-review-ajax', add_product_review_ajax, name='add_product_review_ajax'),

]