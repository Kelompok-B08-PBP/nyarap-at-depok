import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Restaurant, WishlistNote
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wishlist, Restaurant, WishlistItem
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
    wishlist_items = WishlistItem.objects.filter(user=request.user).prefetch_related('notes')
    # collections = Collection.objects.filter(wishlist__user=request.user)

    # Siapkan data untuk template
    wishlist_items_list = []
    for item in wishlist_items:
        wishlist_items_list.append({
            'id': item.product_id,
            'name': item.name,
            'restaurant': item.restaurant,
            'category': item.category,
            'location': item.location,
            'price': item.price,
            'rating': item.rating,
            'operational_hours': item.operational_hours,
            'image_url': item.image_url,
            'notes': list(item.notes.values('id', 'content', 'created_at', 'updated_at'))
        })

    return render(request, 'wishlist.html', {
        # 'collections': collections,
        'wishlist_items': wishlist_items_list,
    })



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
def wishlist_json(request):
    try:
        # Ambil wishlist untuk user yang sedang login
        wishlist_items = WishlistItem.objects.filter(user=request.user)

        # Serialisasi data ke JSON
        data = [
            {
                'product_id': item.product_id,
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
    

@login_required
def add_note(request, product_id):
    wishlist_item = get_object_or_404(WishlistItem, product_id=product_id, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'success': False, 'error': 'Note content cannot be empty'}, status=400)

        # Simpan catatan ke database
        note = WishlistNote.objects.create(
            wishlist_item=wishlist_item,
            content=content
        )

        return JsonResponse({
            'success': True,
            'note_id': note.id,
            'content': note.content,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'success': False}, status=400)



@login_required
def update_note(request, note_id):
    note = get_object_or_404(WishlistNote, id=note_id, wishlist_item__user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'success': False, 'error': 'Note content cannot be empty'}, status=400)

        note.content = content
        note.save()

        return JsonResponse({
            'success': True,
            'note_id': note.id,
            'content': note.content,
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'success': False}, status=400)


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(WishlistNote, id=note_id, wishlist_item__user=request.user)
    if request.method == 'POST':
        note.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@login_required
def notes_json(request, product_id=None):
    try:
        # Base query untuk notes milik user yang login
        notes_query = WishlistNote.objects.filter(wishlist_item__user=request.user)
        
        # Filter berdasarkan product_id jika ada
        if product_id:
            notes_query = notes_query.filter(wishlist_item__product_id=product_id)

        # Serialisasi data notes ke JSON
        data = [
            {
                'id': note.id,
                'content': note.content,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'product_id': note.wishlist_item.product_id,
                'product_name': note.wishlist_item.name
            }
            for note in notes_query
        ]

        return JsonResponse({'notes': data}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)