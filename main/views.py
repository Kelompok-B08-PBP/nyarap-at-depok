import datetime
from django.shortcuts import render, redirect
from main.forms import PreferencesForm
from main.models import UserPreference
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import PreferencesForm
from .models import UserPreference
import pandas as pd
from django.conf import settings
import hashlib

def load_recommendations_from_excel():
    try:
        excel_path = settings.EXCEL_DATA_PATH
        df = pd.read_excel(excel_path)
        kategori_mapping = {
            'Sarapan Sehat': 'makanan_sehat',
            'sarapan sehat': 'makanan_sehat',
            'Makanan Sehat': 'makanan_sehat',
            'Sarapan Berat': 'makanan_berat',
            'sarapan berat': 'makanan_berat',
            'Makanan berat': 'makanan_berat'
        }
        
        # Standardisasi kategori sebelum lowercase dan strip
        df['Kategori'] = df['Kategori'].replace(kategori_mapping, regex=False)

        df['Kategori'] = df['Kategori'].str.lower().str.strip()
        df['Kecamatan'] = df['Kecamatan'].strip() if isinstance(df['Kecamatan'], str) else df['Kecamatan']
        
        recommendations = {}
        for _, row in df.iterrows():
            try:
                kategori = row['Kategori'] 
                kecamatan = row['Kecamatan']
                
                if kategori not in recommendations:
                    recommendations[kategori] = {}

                if kecamatan not in recommendations[kategori]:
                    recommendations[kategori][kecamatan] = []

              
                price = str(row['Harga'])
                if pd.isna(row['Harga']) or price.strip() == '':
                    clean_price = '0'  # Default price for missing values
                elif isinstance(row['Harga'], (int, float)):
                    clean_price = str(row['Harga'])
                else:
                    # Remove currency symbol, spaces, commas, and periods
                    clean_price = price.replace('Rp', '').replace(',', '').replace('.', '').replace(' ', '').strip()
                    if not clean_price:  # If empty after cleaning
                        clean_price = '0'
                
                # Process rating - Convert comma to dot for float conversion
                try:
                    rating = str(row['Rating']).replace(',', '.')
                    rating = float(rating) if rating and not pd.isna(rating) else 0.0
                except (ValueError, AttributeError):
                    rating = 0.0
                
                # Handle image URL
                image_url = row.get('Link Foto', '')
                if pd.isna(image_url) or not image_url.strip():
                    image_url = '/api/placeholder/400/320'

                recommendations[kategori][kecamatan].append({
                    'name': str(row['Nama Produk']).strip(),
                    'restaurant': str(row['nama_restoran']).strip(),
                    'rating': rating,
                    'operational_hours': str(row['Jam Operasional']).strip(),
                    'location': str(row['Lokasi']),
                    'price': clean_price,
                    'image_url': image_url
                })
                
            except KeyError as e:
                continue
            except Exception as e:
                continue

        return recommendations
        
    except Exception as e:
        return {}

def show_main(request):
    user_preferences = None
    filtered_recommendations = []

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if request.user.is_authenticated:
                UserPreference.objects.filter(user=request.user).delete()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    if request.user.is_authenticated:
        try:
            user_preferences = UserPreference.objects.get(user=request.user)
            breakfast_type = user_preferences.preferred_breakfast_type.lower()
            location = user_preferences.preferred_location.strip().title()
            
            if breakfast_type == 'masih_bingung':
                filtered_recommendations = get_recommendations_for_undecided(location, user_preferences.preferred_price_range)
                
            else:
                all_recommendations = load_recommendations_from_excel()
                
                if breakfast_type in all_recommendations:
                    location_recommendations = all_recommendations[breakfast_type].get(location, [])
                    
                    # Filter by price range
                    price_ranges = {
                        '0-15000': (0, 15000),
                        '15000-25000': (15000, 25000),
                        '25000-50000': (25000, 50000),
                        '50000-100000': (50000, 100000),
                        '100000+': (100000, float('inf'))
                    }
                    
                    min_price, max_price = price_ranges[user_preferences.preferred_price_range]
                    
                    for item in location_recommendations:
                        try:
                            price_str = item['price']
                            
                            # Create a new item with all necessary fields including kecamatan
                            new_item = item.copy()
                            new_item['kecamatan'] = location  # Add kecamatan from the location

                            # Check if price is empty, 'nan', or invalid
                            if price_str.lower() == 'nan' or price_str.strip() == '':
                                new_item['display_price'] = "Harga belum tersedia"
                                filtered_recommendations.append(new_item)
                            else:
                                try:
                                    # Try to convert price to float and remove any non-numeric characters
                                    clean_price = ''.join(c for c in price_str if c.isdigit() or c == '.')
                                    price_value = float(clean_price) if clean_price else 0
                                    
                                    if min_price <= price_value <= max_price or price_value == 0:
                                        if price_value == 0 or price_str.lower() == 'nan':
                                            new_item['display_price'] = "Harga belum tersedia"
                                        else:
                                            new_item['display_price'] = f"Rp {price_value:,.0f}"
                                        filtered_recommendations.append(new_item)
                                except ValueError:
                                    # If price conversion fails, include item with "Harga belum tersedia"
                                    new_item['display_price'] = "Harga belum tersedia"
                                    filtered_recommendations.append(new_item)
                            
                        except Exception as e:
                            continue
                    
                
        except UserPreference.DoesNotExist:
            user_preferences = None
        except Exception as e:
            user_preferences = None


    context = {
        'name': request.user.username if request.user.is_authenticated else 'Guest',
        'user_preferences': user_preferences,
        'recommendations': filtered_recommendations,
        'source': 'main',
    }

    return render(request, "main.html", context)


def create_preference_entry(request):
    form = PreferencesForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "create_preference_entry.html", context)

def show_xml(request):
    data = UserPreference.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = UserPreference.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = UserPreference.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_by_id(request, id):
    data = UserPreference.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
        user = form.get_user()
        login(request, user)
        response = HttpResponseRedirect(reverse("main:show_main"))
        response.set_cookie('last_login', str(datetime.datetime.now()))
        return response

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return redirect('main:login')

def recommendations(request):
    if request.method == 'POST':
        # Log request data for debugging
        
        breakfast_category = request.POST.get('breakfast_category')
        district_category = request.POST.get('district_category')
        price_range = request.POST.get('price_range')
        
        
        # Ensure all fields are provided
        if not all([breakfast_category, district_category, price_range]):
            messages.error(request, 'Mohon pilih semua kategori sebelum melanjutkan.')
            return HttpResponseRedirect(reverse('main:recommendations'))
        
        try:
            if request.user.is_authenticated:
                # Update or create preferences for authenticated user
                preference, created = UserPreference.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'preferred_breakfast_type': breakfast_category,
                        'preferred_location': district_category,
                        'preferred_price_range': price_range,
                    }
                )
            else:
                # Store preferences in session for non-authenticated users
                request.session['preferred_breakfast_type'] = breakfast_category
                request.session['preferred_location'] = district_category
                request.session['preferred_price_range'] = price_range
               
            
            return HttpResponseRedirect(reverse('main:recommendation_list'))
            
        except Exception as e:
            messages.error(request, 'Terjadi kesalahan saat menyimpan preferensi.')
            return HttpResponseRedirect(reverse('main:recommendations'))

    context = {
        'is_authenticated': request.user.is_authenticated,
        'name': request.user.username if request.user.is_authenticated else None,
    }
    
    # Get existing preferences for the form
    if request.user.is_authenticated:
        try:
            preference = UserPreference.objects.get(user=request.user)
            context['initial_data'] = {
                'breakfast_category': preference.preferred_breakfast_type,
                'district_category': preference.preferred_location,
                'price_range': preference.preferred_price_range,
            }
        except UserPreference.DoesNotExist:
            pass
            
    return render(request, 'recommendations.html', context)

def get_recommendations(breakfast_type, location, price_range):
    # Load recommendations from the Excel file
    recommendations = load_recommendations_from_excel()
    breakfast_type = breakfast_type.strip().lower()
    location = location.strip()
    
    if breakfast_type in recommendations:
        location_recommendations = recommendations.get(breakfast_type, {}).get(location, [])
    else:
        location_recommendations = []
    
    price_ranges = {
        '0-15000': (0, 15000),
        '15000-25000': (15000, 25000),
        '25000-50000': (25000, 50000),
        '50000-100000': (50000, 100000),
        '100000+': (100000, float('inf'))
    }
    
    min_price, max_price = price_ranges[price_range]
    filtered_recommendations = []
    
    for item in location_recommendations:
        try:
            price_str = str(item['price'])
            # Create a new copy of the item and add kecamatan
            new_item = item.copy()
            new_item['kecamatan'] = location
            
            if price_str.lower() == 'nan' or not price_str.strip():
                new_item['display_price'] = "Harga belum tersedia"
                filtered_recommendations.append(new_item)
            else:
                try:
                    clean_price = ''.join(c for c in price_str if c.isdigit() or c == '.')
                    price_value = float(clean_price) if clean_price else 0
                    
                    if min_price <= price_value <= max_price or price_value == 0:
                        if price_value == 0:
                            new_item['display_price'] = "Harga belum tersedia"
                        else:
                            new_item['display_price'] = f"Rp {price_value:,.0f}"
                        filtered_recommendations.append(new_item)
                except ValueError:
                    new_item['display_price'] = "Harga belum tersedia"
                    filtered_recommendations.append(new_item)
        except Exception as e:
            continue
    
    return filtered_recommendations

def get_recommendations_for_undecided(location, price_range):
    try:
        all_recommendations = load_recommendations_from_excel()
        filtered_recommendations = []
        
        price_ranges = {
            '0-15000': (0, 15000),
            '15000-25000': (15000, 25000),
            '25000-50000': (25000, 50000),
            '50000-100000': (50000, 100000),
            '100000+': (100000, float('inf'))
        }
        
        min_price, max_price = price_ranges[price_range]
        
        for kategori, locations in all_recommendations.items():
            if location in locations:
                for item in locations[location]:
                    try:
                        price_str = item['price']
                        new_item = item.copy()
                        new_item['category'] = kategori
                        new_item['kecamatan'] = location  # Add kecamatan information
                        
                        if price_str == '0' or not price_str.strip():
                            new_item['display_price'] = "Harga belum tersedia"
                            filtered_recommendations.append(new_item)
                        else:
                            try:
                                price_value = float(price_str)
                                if min_price <= price_value <= max_price:
                                    new_item['display_price'] = f"Rp {price_value:,.0f}"
                                    filtered_recommendations.append(new_item)
                            except ValueError:
                                new_item['display_price'] = "Harga belum tersedia"
                                filtered_recommendations.append(new_item)
                    except Exception as e:
                        continue
        
        filtered_recommendations.sort(key=lambda x: float(x['rating']), reverse=True)
        
        return filtered_recommendations
    except Exception as e:
        return []

# Function untuk mengambil rekomendasi berdasarkan kategori
def get_recommendations_by_category(category):
    try:
        all_recommendations = load_recommendations_from_excel()
        category_recommendations = []
        
        if category.lower() in all_recommendations:
            # Go through all locations for this category
            for location, items in all_recommendations[category.lower()].items():
                for item in items:
                    try:
                        new_item = item.copy()
                        price_str = item['price']
                        
                        # Handle price display
                        if price_str == '0' or not price_str.strip():
                            new_item['display_price'] = "Harga belum tersedia"
                        else:
                            try:
                                clean_price = ''.join(c for c in price_str if c.isdigit() or c == '.')
                                price_value = float(clean_price) if clean_price else 0
                                if price_value == 0:
                                    new_item['display_price'] = "Harga belum tersedia"
                                else:
                                    new_item['display_price'] = f"Rp {price_value:,.0f}"
                            except ValueError:
                                new_item['display_price'] = "Harga belum tersedia"
                        
                        # Add location information
                        new_item['kecamatan'] = location if location and location.lower() != 'nan' else 'Lokasi tidak tersedia'
                        
                        # Add to recommendations list
                        category_recommendations.append(new_item)
                
                        
                    except Exception as e:
                        continue
            
            # Sort by rating (highest first)
            category_recommendations.sort(key=lambda x: float(x['rating']), reverse=True)
        
        return category_recommendations
        
    except Exception as e:
        return []

    
def recommendation_list(request):
    # Dictionary to display human-readable values for the preferences
    breakfast_display = {
        'masih_bingung': 'Masih Bingung',
        'nasi': 'Nasi',
        'roti': 'Roti',
        'lontong': 'Lontong',
        'cemilan': 'Cemilan',
        'minuman': 'Minuman',
        'mie': 'Mie',
        'makanan_sehat': 'Sarapan Sehat',
        'bubur': 'Bubur',
        'makanan_berat': 'Sarapan Berat',
    }
    location_display = dict(UserPreference.KECAMATAN_CHOICES)
    price_display = dict(UserPreference.PRICE_CHOICES)

    # Get preferences either from database or session
    if request.user.is_authenticated:
        try:
            preference = UserPreference.objects.get(user=request.user)
            breakfast_type = preference.preferred_breakfast_type
            location = preference.preferred_location
            price_range = preference.preferred_price_range
        except UserPreference.DoesNotExist:
            return HttpResponseRedirect(reverse('main:recommendations'))
    else:
        breakfast_type = request.session.get('preferred_breakfast_type')
        location = request.session.get('preferred_location')
        price_range = request.session.get('preferred_price_range')
        if not all([breakfast_type, location, price_range]):
            return HttpResponseRedirect(reverse('main:recommendations'))

    # Get recommended products based on preferences
    if breakfast_type == 'masih_bingung':
        recommended_products = get_recommendations_for_undecided(location, price_range)
    else:
        recommended_products = get_recommendations(breakfast_type, location, price_range)

    # Add ID to each recommended product - Gunakan current_id untuk konsistensi
    recommendations_with_id = []
    current_id = 1  # Mulai dari 1
    
    for product in recommended_products:
        product_dict = product if isinstance(product, dict) else {
            'name': getattr(product, 'name', ''),
            'price': getattr(product, 'price', ''),
            'restaurant': getattr(product, 'restaurant', ''),
            'rating': getattr(product, 'rating', ''),
            'kategori': getattr(product, 'kategori', ''),
            'kecamatan': getattr(product, 'kecamatan', ''),
            'operational_hours': getattr(product, 'operational_hours', ''),
            'image_url': getattr(product, 'image_url', ''),
        }
        product_dict['id'] = current_id
        current_id += 1  # Increment ID
        recommendations_with_id.append(product_dict)

    context = {
        'preference': {
            'location': location_display[location],
            'breakfast_type': breakfast_display[breakfast_type],
            'price_range': price_display[price_range]
        },
        'recommendations': recommendations_with_id,
        'is_authenticated': request.user.is_authenticated,
        'name': request.user.username if request.user.is_authenticated else None,
        'source': 'recommendations'
    }
    
    return render(request, 'recommendation_list.html', context)


@login_required
def edit_preferences(request):
    if request.method == 'POST':
        # Log request data for debugging
        breakfast_category = request.POST.get('breakfast_category')
        district_category = request.POST.get('district_category')
        price_range = request.POST.get('price_range')
        
        # Ensure all fields are provided
        if not all([breakfast_category, district_category, price_range]):
            messages.error(request, 'Mohon pilih semua kategori sebelum melanjutkan.')
            return HttpResponseRedirect(reverse('main:edit_preferences'))
        
        try:
            # Update or create preferences for authenticated user
            preference, created = UserPreference.objects.update_or_create(
                user=request.user,
                defaults={
                    'preferred_breakfast_type': breakfast_category,
                    'preferred_location': district_category,
                    'preferred_price_range': price_range,
                }
            )
            
            messages.success(request, 'Preferensi berhasil diperbarui.')
            return HttpResponseRedirect(reverse('main:show_main'))
            
        except Exception as e:
            messages.error(request, 'Terjadi kesalahan saat menyimpan preferensi.')
            return HttpResponseRedirect(reverse('main:edit_preferences'))

    # For GET requests
    context = {
        'is_authenticated': request.user.is_authenticated,
        'name': request.user.username if request.user.is_authenticated else None,
    }
    
    # Get existing preferences for the form
    try:
        preference = UserPreference.objects.get(user=request.user)
        
        breakfast_choices = {
            'masih_bingung': 'Masih Bingung',
            'nasi': 'Nasi',
            'roti': 'Roti',
            'lontong': 'Lontong',
            'cemilan': 'Cemilan',
            'minuman': 'Minuman',
            'mie': 'Mie',
            'makanan_sehat': 'Sarapan Sehat',
            'bubur': 'Bubur',
            'makanan_berat': 'Sarapan Berat',
        }

        context.update({
            'initial_data': {
                'breakfast_category': preference.preferred_breakfast_type,
                'district_category': preference.preferred_location,
                'price_range': preference.preferred_price_range,
            },
            'breakfast_choices': breakfast_choices,
            'user_preferences': preference,
            'location_choices': UserPreference.KECAMATAN_CHOICES,
            'price_choices': UserPreference.PRICE_CHOICES,
        })
        
    except UserPreference.DoesNotExist:
        messages.error(request, 'Preferensi tidak ditemukan.')
        return HttpResponseRedirect(reverse('main:show_main'))
    
    return render(request, 'edit_preference_ajax.html', context)

def generate_product_id(name, restaurant, location):
    identifier = f"{name}_{restaurant}_{location}"
    hash_object = hashlib.md5(identifier.encode())
    return int(hash_object.hexdigest()[:8], 16)

def get_product_by_id(product_id):
    try:
        all_recommendations = load_recommendations_from_excel()
        
        for category, locations in all_recommendations.items():
            for location, items in locations.items():
                for item in items:
                    # Generate a consistent positive ID for the item
                    item_id = generate_product_id(item['name'], item['restaurant'], location)
                    
                    if item_id == product_id:
                        # Add additional fields needed for display
                        item['category'] = category
                        item['kecamatan'] = location
                        
                        # Format price display
                        try:
                            if isinstance(item['price'], (int, float)):
                                item['display_price'] = f"Rp {float(item['price']):,.0f}"
                            else:
                                price_str = str(item['price']).replace('Rp', '').replace(',', '').replace('.', '').strip()
                                if price_str and price_str.isdigit():
                                    item['display_price'] = f"Rp {float(price_str):,.0f}"
                                else:
                                    item['display_price'] = "Harga belum tersedia"
                        except (ValueError, KeyError):
                            item['display_price'] = "Harga belum tersedia"
                        
                        # Ensure rating is properly formatted
                        try:
                            item['rating'] = float(str(item['rating']).replace(',', '.'))
                        except (ValueError, KeyError):
                            item['rating'] = 0.0
                            
                        return item
        return None
        
    except Exception as e:
        return None

def get_recommendations_by_category(category):
    try:
        all_recommendations = load_recommendations_from_excel()
        category_recommendations = []
        
        if category.lower() in all_recommendations:
            for location, items in all_recommendations[category.lower()].items():
                for item in items:
                    # Create new item with additional fields
                    new_item = item.copy()
                    # Generate a positive integer ID
                    new_item['id'] = generate_product_id(item['name'], item['restaurant'], location)
                    new_item['kecamatan'] = location
                    
                    # Format price display
                    try:
                        price_value = float(str(item['price']).replace(',', ''))
                        new_item['display_price'] = f"Rp {price_value:,.0f}"
                    except (ValueError, KeyError):
                        new_item['display_price'] = "Harga belum tersedia"
                    
                    category_recommendations.append(new_item)
        
        # Sort by rating (highest first)
        category_recommendations.sort(key=lambda x: float(str(x.get('rating', '0')).replace(',', '.')), reverse=True)
        return category_recommendations
        
    except Exception as e:
        return []

def browse_category(request, category):

    try:
        # Validate category
        valid_categories = ['nasi', 'roti', 'lontong', 'cemilan', 'minuman', 'mie', 'makanan_sehat', 'bubur', 'makanan_berat']
        if category.lower() not in valid_categories:
            messages.error(request, 'Kategori tidak valid.')
            return redirect('main:show_main')
        
        # Get recommendations for category
        recommendations = get_recommendations_by_category(category)
        
        # Get display name for category
        category_display = {
            'nasi': 'Nasi',
            'roti': 'Roti',
            'lontong': 'Lontong',
            'cemilan': 'Cemilan',
            'minuman': 'Minuman',
            'mie': 'Mie',
            'makanan_sehat': 'Sarapan Sehat',
            'bubur': 'Bubur',
            'makanan_berat': 'Sarapan Berat',
        }
        
        context = {
            'category': category_display.get(category.lower(), category.title()),
            'raw_category': category.lower(),  # For URL generation in template
            'recommendations': recommendations,
            'is_authenticated': request.user.is_authenticated,
            'name': request.user.username if request.user.is_authenticated else None,
            'source': 'category',
        }
        
        return render(request, 'browse_category.html', context)
        
    except Exception as e:
        messages.error(request, 'Terjadi kesalahan saat memuat kategori.')
        return redirect('main:show_main')

def product_details(request, category, product_id):
    try:
        # Get product details using the product_id
        product = get_product_by_id(int(product_id))
        if not product:
            messages.error(request, 'Produk tidak ditemukan.')
            return redirect('main:browse_category', category=category)
        
        context = {
            'product': product,
            'category': category,
            'is_authenticated': request.user.is_authenticated,
            'name': request.user.username if request.user.is_authenticated else None,
        }
        return render(request, 'product_details.html', context)
    except ValueError:
        messages.error(request, 'ID produk tidak valid.')
        return redirect('main:browse_category', category=category)
    except Exception as e:
        messages.error(request, 'Terjadi kesalahan saat memuat detail produk.')
        return redirect('main:browse_category', category=category)

def get_product_by_id(product_id):
    try:
        all_recommendations = load_recommendations_from_excel()
        found_product = None
        
        # Counter for numeric ID matching
        current_id = 1
        
        # Search through all categories and locations
        for category, locations in all_recommendations.items():
            for location, items in locations.items():
                for item in items:
                    # Try both numeric ID and hash ID matching
                    hash_id = generate_product_id(item['name'], item['restaurant'], location)
                    
                    if product_id == current_id or product_id == hash_id:
                        found_product = item.copy()
                        found_product.update({
                            'id': current_id,  # Keep the numeric ID
                            'category': category,
                            'kecamatan': location,
                            'name': item['name'],
                            'restaurant': item['restaurant'],
                            'rating': float(str(item.get('rating', '0')).replace(',', '.')),
                            'operational_hours': item.get('operational_hours', ''),
                            'location': item.get('location', ''),
                             'image_url': item.get('image_url', '/api/placeholder/800/400'),
                        })
                        
                        # Handle price display
                        try:
                            if isinstance(item['price'], (int, float)):
                                found_product['display_price'] = f"Rp {float(item['price']):,.0f}"
                            else:
                                price_str = str(item['price']).replace('Rp', '').replace(',', '').replace('.', '').strip()
                                if price_str and price_str.isdigit():
                                    found_product['display_price'] = f"Rp {float(price_str):,.0f}"
                                else:
                                    found_product['display_price'] = "Harga belum tersedia"
                        except (ValueError, KeyError):
                            found_product['display_price'] = "Harga belum tersedia"
                            
                        return found_product
                    
                    current_id += 1
        
        return None
        
    except Exception as e:
        return None

def product_details_recommendation(request, product_id):
    try:
        # Get user preferences
        if request.user.is_authenticated:
            try:
                preference = UserPreference.objects.get(user=request.user)
                breakfast_type = preference.preferred_breakfast_type
                location = preference.preferred_location
                price_range = preference.preferred_price_range
            except UserPreference.DoesNotExist:
                messages.error(request, 'Preferensi tidak ditemukan.')
                return redirect('main:recommendation_list')
        else:
            breakfast_type = request.session.get('preferred_breakfast_type')
            location = request.session.get('preferred_location')
            price_range = request.session.get('preferred_price_range')
            if not all([breakfast_type, location, price_range]):
                messages.error(request, 'Preferensi tidak ditemukan.')
                return redirect('main:recommendation_list')

        # Get recommendations based on preferences
        if breakfast_type == 'masih_bingung':
            recommended_products = get_recommendations_for_undecided(location, price_range)
        else:
            recommended_products = get_recommendations(breakfast_type, location, price_range)

        # Find the product with matching ID
        try:
            product_index = int(product_id) - 1
            if 0 <= product_index < len(recommended_products):
                product = recommended_products[product_index]
                
                # Format the product data
                formatted_product = {
                    'id': int(product_id),
                    'name': product.get('name', ''),
                    'restaurant': product.get('restaurant', ''),
                    'rating': product.get('rating', 0.0),
                    'operational_hours': product.get('operational_hours', ''),
                    'location': product.get('location', ''),
                    'display_price': product.get('display_price', 'Harga belum tersedia'),
                    'image_url': product.get('image_url', '/api/placeholder/800/400'),
                    'kecamatan': product.get('kecamatan', ''),
                    'category': product.get('category', breakfast_type).title() if breakfast_type != 'masih_bingung' else product.get('category', '').title()
                }

                context = {
                    'product': formatted_product,
                    'is_authenticated': request.user.is_authenticated,
                    'name': request.user.username if request.user.is_authenticated else None,
                    'source': 'recommendations'
                }
                
                return render(request, 'product_details.html', context)
            else:
                raise ValueError('Product index out of range')
        except (ValueError, IndexError):
            messages.error(request, 'Produk tidak ditemukan.')
            return redirect('main:recommendation_list')
            
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan saat memuat detail produk: {str(e)}')
        return redirect('main:recommendation_list')
    
@login_required
@csrf_exempt
def delete_preferences(request):
    if request.method == 'POST':
        try:
            # Get and delete the user's preferences
            UserPreference.objects.filter(user=request.user).delete()
            
            # For AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Preferences deleted successfully'
                })
            
            # For regular form submissions
            return redirect('main:show_main')  # or whatever your home URL name is
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
            return redirect('main:show_main')
    
    # If not POST request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        })
    return redirect('main:home')

