from django.shortcuts import render, redirect, reverse 
from .forms import ProductForm
from .models import Product
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ProductForm

# Memastikan hanya pengguna yang sudah login bisa mengakses halaman review
@login_required(login_url='/login')
def show_reviews(request):
    # Mengambil semua review produk, diurutkan dari yang terbaru
    reviews = Product.objects.all().order_by('-date_added')
    return render(request, 'reviews.html', {'reviews': reviews})

# Memastikan hanya pengguna yang sudah login yang bisa menambahkan review via AJAX, bebas dari CSRF, dan hanya bisa diakses via POST
@login_required(login_url='/login')
@csrf_exempt
@require_POST
def add_product_review_ajax(request):
    # Mengambil dan membersihkan data form dari permintaan POST
    restaurant_name = strip_tags(request.POST.get("restaurant_name"))
    food_name = strip_tags(request.POST.get("food_name"))
    rating = int(strip_tags(request.POST.get("rating")))
    review_text = strip_tags(request.POST.get("review"))
    user = request.user

    # Membuat dan menyimpan instance baru dari Product sebagai review
    new_review = Product(
        restaurant_name=restaurant_name,
        food_name=food_name,
        rating=rating,
        review=review_text,
        user=user  
    )
    new_review.save()

    # Mengembalikan respon dalam bentuk JSON yang berisi detail review baru
    return JsonResponse({
        'id': new_review.id,
        'restaurant_name': new_review.restaurant_name,
        'food_name': new_review.food_name,
        'rating': new_review.rating,
        'review': new_review.review,
        'date_added': new_review.date_added.strftime("%Y-%m-%d"),
    })

# Mengembalikan data produk dalam format XML untuk produk pengguna yang sedang login
def show_xml(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

# Mengembalikan data produk dalam format JSON untuk produk pengguna yang sedang login
def show_json(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

# Mengembalikan data XML untuk produk tertentu berdasarkan ID
def show_xml_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

# Mengembalikan data JSON untuk produk tertentu berdasarkan ID
def show_json_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

# Menghapus review produk berdasarkan ID dan mengarahkan kembali ke halaman daftar review
def delete_product_review(request, id):
    review = Product.objects.get(pk=id)
    review.delete()
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    # Regular form submission - redirect
    return HttpResponseRedirect(reverse('reviews:show_reviews'))

# Menampilkan form untuk mengedit review produk berdasarkan ID, lalu menyimpan perubahan jika valid
def edit_product_review(request, id):
    review = Product.objects.get(pk=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('reviews:show_reviews') 
    else:
        form = ProductForm(instance=review)

    return render(request, 'edit_product_review.html', {'form': form, 'review': review})