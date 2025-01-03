from pdb import post_mortem
from pickletools import pybytes_or_str
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import PostEntry
from .forms import PostEntryForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PostEntryForm




# from django.views.decorators.http import require_POST

# @login_required(login_url='/login')
def show_post(request):
    # Logic to display posts
    context = {
        'posts': PostEntry.objects.all(),  # Example query
        'user': request.user,
    }
    return render(request, 'main_post.html', context) # Tambahkan context


@login_required 
def edit_post(request, id):
    post = get_object_or_404(PostEntry, id=id, user=request.user)  # Hanya izinkan edit jika user adalah pemilik
    form = PostEntryForm(request.POST or None, instance=post)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('discovery:show_post')

    context = {'form': form, 'post': post}  # Tambahkan post ke context
    return render(request, "edit_post.html", context)

@login_required 
def delete_post(request, id):
    post = get_object_or_404(PostEntry, pk=id)  # Mengambil postingan berdasarkan id
    if request.method == "POST":
        post.delete()  # Menghapus postingan
        return redirect('discovery:show_post')  # Redirect ke halaman daftar posting
    return redirect('discovery:show_post')


@login_required  # Tambahkan ini untuk memastikan user sudah login
def create_post_entry(request):
    if request.method == "POST":
        form = PostEntryForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('discovery:show_post')
    else:
        form = PostEntryForm()
    
    context = {'form': form}
    return render(request, "create_post_entry.html", context)

def show_xml(request):
    data = PostEntry.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = PostEntry.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = PostEntry.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_by_id(request, id):
    data = PostEntry.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_discovery(request):
    # Get all posts for "For You" section
    all_posts = post_mortem.objects.all().order_by('-created_at')
    
    # Get user's posts for "Yours" section
    user_posts = []
    if request.user.is_authenticated:
        user_posts = pybytes_or_str.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'all_posts': all_posts,
        'user_posts': user_posts,
    }
    
    return render(request, 'discovery.html', context)

def get_posts(request):
    filter_type = request.GET.get('filter', 'for_you')
    
    if filter_type == 'yours' and request.user.is_authenticated:
        posts = PostEntry.objects.filter(user=request.user).order_by('-created_at')
    else:
        posts = PostEntry.objects.all().order_by('-created_at')
        
    return render(request, 'post_list_partial.html', {'posts': posts})

def discovery_page(request):
    # Get all posts for initial load (For You)
    posts = PostEntry.objects.all().order_by('-created_at')
    return render(request, 'discovery.html', {'posts': posts})

# community/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from .models import PostEntry
from django.contrib.auth.decorators import login_required

def get_posts_flutter(request):
    try:
        posts = PostEntry.objects.all()
        posts_json = serializers.serialize('json', posts)
        
        # Parse JSON untuk menambahkan informasi tambahan jika diperlukan
        posts_data = json.loads(posts_json)
        
        # Add authenticated user info to response if user is logged in
        user_info = None
        if request.user.is_authenticated:
            user_info = {
                'id': request.user.id,
                'username': request.user.username
            }
        
        return JsonResponse({
            'status': 'success',
            'results': posts_data,
            'user': user_info  # Include user info in response
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
def create_post_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create post
            post = PostEntry.objects.create(
                title=data.get('title'),
                caption=data.get('caption', ''),
                location=data.get('location', ''),
                photo_url=data.get('photo_url', ''),
                user=request.user
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Post created successfully',
                'data': {
                    'id': post.id,
                    'title': post.title
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
@login_required
def update_post_flutter(request, post_id):
    if request.method == 'POST':  # Changed from PUT to POST
        try:
            post = PostEntry.objects.get(id=post_id, user=request.user)
            data = json.loads(request.body)
            
            post.title = data.get('title', post.title)
            post.caption = data.get('caption', post.caption)
            post.location = data.get('location', post.location)
            post.photo_url = data.get('photo_url', post.photo_url)
            post.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Post updated successfully'
            })
        except PostEntry.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Post not found'
            })
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
@login_required
def delete_post_flutter(request, post_id):
    if request.method == 'POST':  # Changed from DELETE to POST
        try:
            post = PostEntry.objects.get(id=post_id, user=request.user)
            post.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Post deleted successfully'
            })
        except PostEntry.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Post not found'
            })
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
@login_required
def edit_post_flutter(request, post_id):
    if request.method == 'POST':
        try:
            # Get the post and verify ownership
            post = PostEntry.objects.get(id=post_id, user=request.user)
            
            # Parse the request data
            data = json.loads(request.body)
            
            # Update post fields
            post.title = data.get('title', post.title)
            post.caption = data.get('caption', post.caption)
            post.location = data.get('location', post.location)
            post.photo_url = data.get('photo_url', post.photo_url)
            post.save()
            
            # Serialize the updated post
            post_json = serializers.serialize('json', [post])
            post_data = json.loads(post_json)[0]
            
            return JsonResponse({
                'status': 'success',
                'message': 'Post updated successfully',
                'data': post_data
            })
            
        except PostEntry.DoesNotExist:
            return JsonResponse({
                'status': 'error', 
                'message': 'Post not found or unauthorized'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

