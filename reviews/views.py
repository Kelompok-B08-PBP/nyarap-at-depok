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

@login_required(login_url='/login')
def show_reviews(request):
    reviews = Product.objects.all().order_by('-date_added')
    return render(request, 'reviews.html', {'reviews': reviews})

@login_required(login_url='/login')
@csrf_exempt
@require_POST
def add_product_review_ajax(request):
    restaurant_name = strip_tags(request.POST.get("restaurant_name"))
    food_name = strip_tags(request.POST.get("food_name"))
    rating = int(strip_tags(request.POST.get("rating")))
    review_text = strip_tags(request.POST.get("review"))
    user = request.user

    new_review = Product(
        restaurant_name=restaurant_name,
        food_name=food_name,
        rating=rating,
        review=review_text,
        user=user  
    )
    new_review.save()
    return HttpResponse(b"CREATED", status=201)

def show_xml(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def delete_product_review(request, id):
    review = Product.objects.get(pk = id)
    review.delete()
    return HttpResponseRedirect(reverse('reviews:show_reviews'))

def edit_product_review(request, id):
    review = Product.objects.get(pk = id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('reviews:show_reviews') 
    else:
        form = ProductForm(instance=review)

    return render(request, 'edit_product_review.html', {'form': form, 'review': review})


# def edit_product_review(request, id):
#     # Get product review berdasarkan id
#     review = Product.objects.get(pk = id)

#     # Set product sebagai instance dari form
#     form = ProductForm(request.POST or None, instance=review)

#     if form.is_valid() and request.method == "POST":
#         # Simpan form dan kembali ke halaman awal
#         form.save()
#         return HttpResponseRedirect(reverse('main:show_main'))

#     context = {'form': form}
#     return render(request, "edit_product_review.html", context)

# def delete_product_review(request, id):
#     # Get product review berdasarkan id
#     review = Product.objects.get(pk = id)
#     review.delete()
#     # Kembali ke halaman awal
#     return HttpResponseRedirect(reverse('main:show_main'))

# @csrf_exempt
# @require_POST
# def add_product_review_ajax(request):
#     name = strip_tags(request.POST.get("name"))
#     review = strip_tags(request.POST.get("review"))
#     rating = strip_tags(request.POST.get("rating"))
#     user = request.user

#     new_review = Product(
#         name=name,
#         review=review,
#         rating=rating,
#         user=user
#     )
#     new_review.save()
#     return HttpResponse(b"CREATED", status=201)