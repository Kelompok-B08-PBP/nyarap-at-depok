import json
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
def add_product_review_ajax(request,id):
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
        user=user,
        product_identifier=str(id),
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

@csrf_exempt
def add_product_review_ajax_all(request):
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User not authenticated'
                }, status=403)

            # Ambil data dari form (request.POST) atau JSON (request.body)
            data = request.POST if request.POST else json.loads(request.body)

            # Pastikan kita ambil semua field
            restaurant_name = data.get('restaurant_name')
            food_name = data.get('food_name')
            rating = data.get('rating')
            review_text = data.get('review')
            
            # Ambil product_identifier dari hidden input (HTML) atau dari Flutter
            product_identifier = data.get('product_identifier', '')

            # Validasi
            if not all([restaurant_name, food_name, rating, review_text]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)

            # Convert rating ke int
            try:
                rating = int(rating)
            except ValueError:
                rating = 0

            # Buat review baru (pakai model Product di sini, jika memang 1 table)
            new_review = Product.objects.create(
                user=request.user,
                restaurant_name=restaurant_name,
                food_name=food_name,
                rating=rating,
                review=review_text,
                product_identifier=product_identifier,
            )

            return JsonResponse({
                'status': 'success',
                'data': {
                    "model": "reviews.product",
                    "pk": new_review.id,
                    "fields": {
                        "user": new_review.user.id,
                        "restaurant_name": new_review.restaurant_name,
                        "food_name": new_review.food_name,
                        "review": new_review.review,
                        "rating": new_review.rating,
                        "date_added": new_review.date_added.strftime("%Y-%m-%d"),
                        "product_identifier": new_review.product_identifier,
                    }
                }
            })
        except Exception as e:
            print(f"Error adding review: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
def delete_product_review(request, id):
    if request.method == 'POST':
        try:
            review = Product.objects.get(pk=id)
            
            # Pastikan user yang menghapus adalah pemilik review
            if review.user == request.user:
                review.delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Not authorized to delete this review'
                }, status=403)
        except Product.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Review not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
def edit_product_review(request, id):
    try:
        review = Product.objects.get(pk=id)
        
        # Handle GET request untuk render form edit
        if request.method == 'GET':
            # Untuk web view
            if request.headers.get('Accept', '').find('text/html') != -1:
                form = ProductForm(instance=review)
                return render(request, 'edit_product_review.html', {
                    'form': form, 
                    'review': review
                })
            # Untuk API/Flutter
            else:
                return JsonResponse({
                    'status': 'success',
                    'data': {
                        "model": "reviews.product",
                        "pk": review.id,
                        "fields": {
                            "user": review.user.id,
                            "restaurant_name": review.restaurant_name,
                            "food_name": review.food_name,
                            "review": review.review,
                            "rating": review.rating,
                            "date_added": review.date_added.strftime("%Y-%m-%d"),
                            "product_identifier": ""
                        }
                    }
                })
                
        # Handle POST request untuk update data
        elif request.method == 'POST':
            if request.user != review.user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Not authorized to edit this review'
                }, status=403)

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                data = request.POST

            review.restaurant_name = data.get('restaurant_name', review.restaurant_name)
            review.food_name = data.get('food_name', review.food_name)
            review.rating = int(data.get('rating', review.rating))
            review.review = data.get('review', review.review)
            review.save()

            # Untuk web view
            if request.headers.get('Accept', '').find('text/html') != -1:
                return redirect('reviews:show_reviews')
            # Untuk API/Flutter
            else:
                return JsonResponse({
                    'status': 'success',
                    'data': {
                        "model": "reviews.product",
                        "pk": review.id,
                        "fields": {
                            "user": review.user.id,
                            "restaurant_name": review.restaurant_name,
                            "food_name": review.food_name,
                            "review": review.review,
                            "rating": review.rating,
                            "date_added": review.date_added.strftime("%Y-%m-%d"),
                            "product_identifier": ""
                        }
                    }
                })

    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Review not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

def get_reviews(request):
    reviews = Product.objects.all().order_by('-date_added')
    review_data = serializers.serialize('json', reviews)
    return HttpResponse(review_data, content_type="application/json")

@login_required
def get_user_id(request):
    return JsonResponse({
        'user_id': request.user.id,
        'status': 'success'
    })

@login_required
def get_reviews_for_product(request, product_id):
    try:
        # Pastikan format product_id konsisten
        sanitized_id = str(product_id).strip()
        print(f"Getting reviews for product: {sanitized_id}")  # Debug log
        
        reviews = Product.objects.filter(product_identifier=sanitized_id).order_by('-date_added')
        print(f"Found {reviews.count()} reviews")  # Debug log
        
        return HttpResponse(
            serializers.serialize('json', reviews),
            content_type="application/json"
        )
    except Exception as e:
        print(f"Error getting reviews: {e}")  # Debug log
        return JsonResponse([], safe=False)