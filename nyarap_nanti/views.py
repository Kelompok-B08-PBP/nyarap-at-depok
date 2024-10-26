from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Collection, CollectionItem, Restaurant
from .forms import CollectionForm

@login_required
def wishlist_page(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    collections = wishlist.collections.all()
    wishlist_items = CollectionItem.objects.filter(collection__wishlist=wishlist)
    return render(request, 'wishlist.html', {
        'collections': collections,
        'wishlist_items': wishlist_items
    })

@login_required
def create_collection(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        Collection.objects.create(wishlist=wishlist, name=name)
        return redirect('wishlist_page')
    return render(request, 'create_collection.html')

@login_required
def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, wishlist__user=request.user)
    items = collection.items.all()
    return render(request, 'collection_detail.html', {
        'collection': collection,
        'items': items
    })

@login_required
def remove_from_wishlist(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    CollectionItem.objects.filter(restaurant=restaurant).delete()
    return redirect('wishlist_page')

@login_required
def remove_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, wishlist__user=request.user)
    collection.delete()
    return redirect('wishlist_page')

@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, wishlist__user=request.user)
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            return redirect('wishlist_page')
    else:
        form = CollectionForm(instance=collection)

    return render(request, 'edit_collection.html', {'form': form, 'collection': collection})
