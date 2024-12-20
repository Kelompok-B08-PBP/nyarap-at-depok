import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Collection, CollectionItem, Restaurant
from .forms import CollectionForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wishlist, Collection, CollectionItem, Restaurant, WishlistItem
from main.views import get_product_by_id
import pandas as pd
import os
from django.conf import settings
from django.contrib.auth.signals import user_logged_in


logger = logging.getLogger(__name__)

@login_required
def add_to_wishlist(request, product_id):
    product = get_product_by_id(product_id)
    if not product:
        return redirect('main:product_details', product_id=product_id)

    # Create or get wishlist item in database
    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product_id=product_id,
        defaults={
            'name': product['name'],
            'restaurant': product.get('restaurant', ''),
            'category': product.get('category', 'umum'),
            'location': product.get('location', ''),
            'price': float(product.get('price', 0)),
            'rating': product.get('rating', 0.0),
            'operational_hours': product.get('operational_hours', ''),
            'image_url': product.get('image_url', '')
        }
    )

    # if created:
    #     messages.success(request, f"{product['name']} berhasil ditambahkan ke wishlist.")
    # else:
    #     messages.info(request, f"{product['name']} sudah ada di wishlist.")

    return redirect('nyarap_nanti:wishlist_page')


def load_wishlist_to_session(sender, request, user, **kwargs):
    wishlist_items = WishlistItem.objects.filter(user=user)
    session_wishlist = [
        {
            'id': item.product_id,
            'name': item.name,
            'restaurant': item.restaurant,
            'category': item.category,
            'location': item.location,
            'price': item.price,
            'rating': item.rating,
            'operational_hours': item.operational_hours,
            'image_url': item.image_url,
        }
        for item in wishlist_items
    ]
    request.session['wishlist'] = session_wishlist

user_logged_in.connect(load_wishlist_to_session)

@login_required
def wishlist_page(request):
    # Get items from database instead of session
    wishlist_items = WishlistItem.objects.filter(user=request.user).values(
        'product_id', 
        'name',
        'restaurant',
        'category', 
        'location',
        'price',
        'rating',
        'operational_hours',
        'image_url'
    )
    collections = Collection.objects.filter(wishlist__user=request.user)
    
    # Convert queryset to list of dictionaries with display price
    wishlist_items_list = []
    for item in wishlist_items:
        item_dict = dict(item)
        item_dict['id'] = item['product_id']
        item_dict['display_price'] = f"Rp {float(item['price']):,.0f}" if item['price'] else "Harga belum tersedia"
        wishlist_items_list.append(item_dict)

    return render(request, 'wishlist.html', {
        'collections': collections,
        'wishlist_items': wishlist_items_list,
    })



@login_required
def create_collection(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        Collection.objects.create(wishlist=wishlist, name=name)
        return redirect('nyarap_nanti:wishlist_page')
    return render(request, 'create_collection.html')

@login_required
def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, wishlist__user=request.user)
    items = collection.items.all()
    return render(request, 'collection_detail.html', {
        'collection': collection,
        'items': items
    })

@csrf_exempt
@login_required
def remove_collection(request, collection_id):
    if request.method == "POST":
        collection = get_object_or_404(Collection, id=collection_id, wishlist__user=request.user)
        collection.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, wishlist__user=request.user)
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            return redirect('nyarap_nanti:wishlist_page')
    else:
        form = CollectionForm(instance=collection)

    return render(request, 'edit_collection.html', {'form': form, 'collection': collection})


@login_required
def remove_from_wishlist(request, product_id):
    # Delete the wishlist item from database
    WishlistItem.objects.filter(user=request.user, product_id=product_id).delete()
    
    # Update session data
    wishlist = request.session.get('wishlist', [])
    wishlist = [item for item in wishlist if item['id'] != product_id]
    request.session['wishlist'] = wishlist
    
    
    return redirect('nyarap_nanti:wishlist_page')


def load_recommendations_from_excel():
    try:
        # Path dataset
        excel_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'dataset.xlsx')
        print(f"Membaca file dari: {excel_path}")

        # Baca file Excel
        df = pd.read_excel(excel_path, engine='openpyxl')

        # Debug kolom yang ada
        print(f"Kolom dalam dataset: {df.columns.tolist()}")

        # Mapping data ke dictionary
        recommendations = []
        for index, row in df.iterrows():
            try:
                recommendation = {
                    'id': index,  # Gunakan index jika tidak ada kolom ID
                    'kategori': str(row['Kategori']) if pd.notnull(row['Kategori']) else '',
                    'name': str(row['Nama Produk']) if pd.notnull(row['Nama Produk']) else '',
                    'restaurant': str(row['nama_restoran']) if pd.notnull(row['nama_restoran']) else '',
                    'operational_hours': str(row['Jam Operasional']) if pd.notnull(row['Jam Operasional']) else '',
                    'location': str(row['Lokasi']) if pd.notnull(row['Lokasi']) else '',
                    'kecamatan': str(row['Kecamatan']) if pd.notnull(row['Kecamatan']) else '',
                    'rating': float(row['Rating']) if pd.notnull(row['Rating']) else 0.0,
                    'price': float(row['Harga']) if pd.notnull(row['Harga']) else 0.0,
                    'image_url': str(row['Link Foto']) if pd.notnull(row['Link Foto']) else '',
                }
                recommendations.append(recommendation)
            except Exception as e:
                print(f"Error memproses baris {index}: {e}")
        return recommendations
    except Exception as e:
        print(f"Error loading recommendations: {e}")
        return []

@login_required
def add_to_collection(request, collection_id):
    if request.method == 'POST':
        collection = get_object_or_404(Collection, id=collection_id, wishlist__user=request.user)
        selected_items = json.loads(request.POST.get('selected_items', '[]'))
        
        # Get wishlist items for the current user
        wishlist_items = WishlistItem.objects.filter(user=request.user, product_id__in=selected_items)
        
        for item in wishlist_items:
            # Create or get restaurant
            restaurant, _ = Restaurant.objects.get_or_create(
                name=item.name,
                defaults={
                    'category': item.category,
                    'location': item.location,
                    'image_url': item.image_url
                }
            )
            
            # Create collection item if it doesn't exist
            CollectionItem.objects.get_or_create(
                collection=collection,
                restaurant=restaurant
            )
        
       
        return redirect('nyarap_nanti:collection_detail', collection_id=collection_id)
    
    return redirect('nyarap_nanti:wishlist_page')


@login_required
def wishlist_json(request):
    try:
        # Ambil wishlist untuk user yang sedang login
        wishlist_items = WishlistItem.objects.filter(user=request.user)

        # Serialisasi data ke JSON
        data = [
            {
                'id': item.product_id,
                'name': item.name,
                'category': item.category,
                'location': item.location,
                'price': item.price,
                'rating': item.rating,
                'operational_hours': item.operational_hours,
                'image_url': item.image_url,
            }
            for item in wishlist_items
        ]

        return JsonResponse({'wishlist': data}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)