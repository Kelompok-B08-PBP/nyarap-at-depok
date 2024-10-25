from django.shortcuts import render, redirect, reverse 
from .forms import ProductForm
from .models import Product
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ProductForm


# Create your views here.
@login_required(login_url='/login')
def create_product_review(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reviews')  # Redirect to a page displaying reviews or a success message
    else:
        form = ProductForm()
    return render(request, 'create_product_review.html', {'form': form})

def show_reviews(request):
    form = ProductForm()  # Assuming ProductForm is set up for adding a review
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reviews:show_reviews')  # Redirect back to review page after submission
    return render(request, 'show_reviews.html', {'form': form})


def show_xml(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data_id = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data_id), content_type="application/xml")

def show_json_by_id(request, id):
    data_id = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data_id), content_type="application/json")

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

def show_reviews(request):
    reviews = Product.objects.all()  # Fetch all reviews
    return render(request, 'reviews.html', {'reviews': reviews})

@csrf_exempt
@require_POST
def add_product_review_ajax(request):
    name = strip_tags(request.POST.get("name"))
    review = strip_tags(request.POST.get("review"))
    rating = strip_tags(request.POST.get("rating"))
    user = request.user

    new_review = Product(
        name=name,
        review=review,
        rating=rating,
        user=user
    )
    new_review.save()
    return HttpResponse(b"CREATED", status=201)