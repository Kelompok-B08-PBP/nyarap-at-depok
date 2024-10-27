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
from .models import Wishlist, Collection, CollectionItem, Restaurant
from main.views import get_product_by_id

logger = logging.getLogger(__name__)

@login_required
def add_to_wishlist(request, product_id):
    # Mengambil data produk berdasarkan ID
    product = get_product_by_id(product_id)  
    if not product:
        messages.error(request, "Produk tidak ditemukan.")
        return redirect('main:product_details', product_id=product_id)

    # Ambil wishlist dari sesi atau buat baru jika belum ada
    wishlist = request.session.get('wishlist', [])

    # Cek apakah produk sudah ada di wishlist
    if not any(item['id'] == product_id for item in wishlist):
        wishlist.append({
            'id': product_id,
            'name': product['name'],
            'category': product.get('category', 'umum'),
            'location': product.get('location', ''),
            'price': float(product.get('price', 0)),
            'rating': product.get('rating', 0.0),
            'operational_hours': product.get('operational_hours', ''),
            'restaurant': product.get('restaurant', ''),
            'image_url': product.get('image_url', '/api/placeholder/400/320'),  # Tambahkan image_url
            'display_price': product.get('display_price', 'Harga belum tersedia')
        })
        request.session['wishlist'] = wishlist
        messages.success(request, f"{product['name']} berhasil ditambahkan ke wishlist.")
    else:
        messages.info(request, f"{product['name']} sudah ada di wishlist.")

    return redirect('nyarap_nanti:wishlist_page')

@login_required
def wishlist_page(request):
    try:
        # Get the wishlist from session
        wishlist_items = request.session.get('wishlist', [])
        
        # Get all collections for the user
        collections = Collection.objects.filter(wishlist__user=request.user)
        
        # Add any missing fields to wishlist items
        for item in wishlist_items:
            if 'image_url' not in item:
                item['image_url'] = '/api/placeholder/400/320'
            if 'display_price' not in item:
                item['display_price'] = f"Rp {float(item.get('price', 0)):,.0f}"
                
        context = {
            'collections': collections,
            'wishlist_items': wishlist_items,
            'is_authenticated': request.user.is_authenticated,
            'name': request.user.username if request.user.is_authenticated else None,
        }
        
        return render(request, 'wishlist.html', context)
    except Exception as e:
        logger.error(f"Error in wishlist_page: {str(e)}")
        messages.error(request, "Terjadi kesalahan saat memuat wishlist.")
        return redirect('main:show_main')

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
def add_to_wishlist(request, product_id):
    # Mengambil data produk berdasarkan ID
    product = get_product_by_id(product_id)  
    if not product:
        messages.error(request, "Produk tidak ditemukan.")
        return redirect('main:product_details', product_id=product_id)

    # Ambil wishlist dari sesi atau buat baru jika belum ada
    wishlist = request.session.get('wishlist', [])

    # Cek apakah produk sudah ada di wishlist
    if not any(item['id'] == product_id for item in wishlist):
        wishlist.append({
            'id': product_id,
            'name': product['name'],
            'category': product.get('category', 'umum'),  # Tambahkan default kategori
            'location': product.get('location', ''),
            'price': float(product.get('price', 0)),
            'rating': product.get('rating', 0.0),
            'operational_hours': product.get('operational_hours', '')
        })
        request.session['wishlist'] = wishlist  # Simpan perubahan ke sesi
        messages.success(request, f"{product['name']} berhasil ditambahkan ke wishlist.")
    else:
        messages.info(request, f"{product['name']} sudah ada di wishlist.")

    return redirect('nyarap_nanti:wishlist_page')

@login_required
def remove_from_wishlist(request, product_id):
    wishlist = request.session.get('wishlist', [])
    # Hapus item dari wishlist berdasarkan `product_id`
    wishlist = [item for item in wishlist if item['id'] != product_id]
    request.session['wishlist'] = wishlist  # Simpan perubahan ke sesi
    messages.success(request, "Produk berhasil dihapus dari wishlist.")
    return redirect('nyarap_nanti:wishlist_page')



