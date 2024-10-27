import datetime
from django.shortcuts import render, redirect
from main.forms import PreferencesForm
from main.models import UserPreference
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import PreferencesForm  # Updated import name
from .models import UserPreference
import pandas as pd
from django.conf import settings
import hashlib


def load_recommendations_from_excel():
    try:
        excel_path = settings.EXCEL_DATA_PATH
        df = pd.read_excel(excel_path)
        print(f"Loaded Excel file with {len(df)} rows")
        
        # Clean the data first
        df['Kategori'] = df['Kategori'].str.lower().str.strip()
        df['Kecamatan'] = df['Kecamatan'].strip() if isinstance(df['Kecamatan'], str) else df['Kecamatan']
        
        # Convert to dictionary grouped by Kategori (breakfast type) and Kecamatan (location)
        recommendations = {}
        for _, row in df.iterrows():
            try:
                kategori = row['Kategori']  # Already cleaned above
                kecamatan = row['Kecamatan']
                
                # Debug: Print each row's category and location
                print(f"Processing row - Category: '{kategori}', Location: '{kecamatan}'")
                
                if kategori not in recommendations:
                    recommendations[kategori] = {}
                    print(f"Created new category entry: '{kategori}'")

                if kecamatan not in recommendations[kategori]:
                    recommendations[kategori][kecamatan] = []
                    print(f"Created new location entry for '{kategori}' in '{kecamatan}'")

                # Clean and process price data
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
                
                recommendations[kategori][kecamatan].append({
                    'name': str(row['Nama Produk']).strip(),
                    'restaurant': str(row['nama_restoran']).strip(),
                    'rating': rating,
                    'operational_hours': str(row['Jam Operasional']).strip(),
                    'location': str(row['Lokasi']).strip(),
                    'price': clean_price
                })
                print(f"Added item '{row['Nama Produk']}' to '{kategori}' in '{kecamatan}'")
                
            except KeyError as e:
                print(f"Missing column in row: {str(e)}")
                continue
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue

        # Debug: Print final structure
        print("\nFinal recommendations structure:")
        for kategori, locations in recommendations.items():
            print(f"\nCategory: {kategori}")
            for location, items in locations.items():
                print(f"  Location: {location} ({len(items)} items)")
                # Print detail of items for debugging
                for item in items:
                    print(f"    - {item['name']} at {item['restaurant']} (Rating: {item['rating']}, Price: {item['price']})")
        
        return recommendations
        
    except Exception as e:
        print(f"Error loading Excel file: {str(e)}")
        return {}

def show_main(request):
    user_preferences = None
    filtered_recommendations = []
    
    if request.user.is_authenticated:
        try:
            user_preferences = UserPreference.objects.get(user=request.user)
            breakfast_type = user_preferences.preferred_breakfast_type.lower()
            location = user_preferences.preferred_location.strip().title()
            
            print(f"Cleaned preferences - Type: {breakfast_type}, Location: {location}")
            
            # Check if user is undecided ('masih_bingung')
            if breakfast_type == 'masih_bingung':
                filtered_recommendations = get_recommendations_for_undecided(location, user_preferences.preferred_price_range)
                print(f"Found {len(filtered_recommendations)} undecided recommendations")
            else:
                all_recommendations = load_recommendations_from_excel()
                
                if breakfast_type in all_recommendations:
                    location_recommendations = all_recommendations[breakfast_type].get(location, [])
                    print(f"Found {len(location_recommendations)} recommendations for location {location}")
                    
                    # Print all recommendations before price filtering
                    for rec in location_recommendations:
                        print(f"Restaurant: {rec['restaurant']}, Price: {rec['price']}")
                    
                    # Filter by price range
                    price_ranges = {
                        '0-15000': (0, 15000),
                        '15000-25000': (15000, 25000),
                        '25000-50000': (25000, 50000),
                        '50000-100000': (50000, 100000),
                        '100000+': (100000, float('inf'))
                    }
                    
                    min_price, max_price = price_ranges[user_preferences.preferred_price_range]
                    print(f"Filtering prices between {min_price} and {max_price}")
                    
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
                                print(f"Added recommendation without price: {item['name']}")
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
                                        print(f"Added recommendation: {item['name']} with price {new_item['display_price']} in {new_item['kecamatan']}")
                                except ValueError:
                                    # If price conversion fails, include item with "Harga belum tersedia"
                                    new_item['display_price'] = "Harga belum tersedia"
                                    filtered_recommendations.append(new_item)
                                    print(f"Added recommendation with invalid price: {item['name']} in {new_item['kecamatan']}")
                            
                        except Exception as e:
                            print(f"Error processing item: {item.get('name', 'unknown')}")
                            print(f"Error details: {str(e)}")
                            continue
                    
                print(f"Final filtered recommendations count: {len(filtered_recommendations)}")
                
        except UserPreference.DoesNotExist:
            print("No user preferences found")
            user_preferences = None
        except Exception as e:
            print(f"Error in show_main: {str(e)}")
            user_preferences = None

    context = {
        'name': request.user.username if request.user.is_authenticated else 'Guest',
        'user_preferences': user_preferences,
        'recommendations': filtered_recommendations,
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
    
    print(f"get_recommendations - Looking for: breakfast_type='{breakfast_type}', location='{location}'")
    
    if breakfast_type in recommendations:
        location_recommendations = recommendations.get(breakfast_type, {}).get(location, [])
        print(f"Found {len(location_recommendations)} recommendations for {location}")
    else:
        print(f"Category '{breakfast_type}' not found in recommendations")
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
                print(f"Added item without price: {new_item['name']} in {new_item['kecamatan']}")
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
                        print(f"Added item: {new_item['name']} with price {new_item['display_price']} in {new_item['kecamatan']}")
                except ValueError:
                    new_item['display_price'] = "Harga belum tersedia"
                    filtered_recommendations.append(new_item)
                    print(f"Added item with invalid price: {new_item['name']} in {new_item['kecamatan']}")
        except Exception as e:
            print(f"Error processing item: {str(e)}")
            continue
    
    print(f"Final filtered recommendations count: {len(filtered_recommendations)}")
    return filtered_recommendations

def get_recommendations_for_undecided(location, price_range):
    """
    Get recommendations for users who are undecided (masih_bingung)
    Shows all categories filtered by location and price range
    """
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
                        print(f"Error processing item: {str(e)}")
                        continue
        
        filtered_recommendations.sort(key=lambda x: float(x['rating']), reverse=True)
        
        return filtered_recommendations
    except Exception as e:
        print(f"Error in get_recommendations_for_undecided: {str(e)}")
        return []

# Function untuk mengambil rekomendasi berdasarkan kategori
def get_recommendations_by_category(category):
    """
    Get all recommendations for a specific category across all locations
    """
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
                        print(f"Added {new_item['name']} from {new_item['kecamatan']} to category recommendations")
                        
                    except Exception as e:
                        print(f"Error processing item: {str(e)}")
                        continue
            
            # Sort by rating (highest first)
            category_recommendations.sort(key=lambda x: float(x['rating']), reverse=True)
            print(f"Found {len(category_recommendations)} items for category {category}")
        else:
            print(f"Category {category} not found in recommendations")
        
        return category_recommendations
        
    except Exception as e:
        print(f"Error in get_recommendations_by_category: {str(e)}")
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
        'telur':'Telur',
        'bubur':'Bubur'
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
    
    context = {
        'preference': {
            'location': location_display[location],
            'breakfast_type': breakfast_display[breakfast_type],
            'price_range': price_display[price_range]
        },
        'recommendations': recommended_products,
        'is_authenticated': request.user.is_authenticated,
        'name': request.user.username if request.user.is_authenticated else None,
    }

    return render(request, 'recommendation_list.html', context)

@login_required
def edit_preferences(request):
    # Ambil preferensi pengguna yang sudah login
    user_preferences = request.user.preferences
    
    # Cek apakah metode yang digunakan adalah POST (form disubmit)
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            # Simpan perubahan preferensi
            form.save()
            return redirect('main:home')  # Redirect ke halaman home setelah preferensi disimpan
    else:
        # Inisialisasi form dengan preferensi user saat ini
        form = PreferencesForm(instance=request.user)
    
    context = {
        'form': form,
        'user_preferences': user_preferences,
    }
    return render(request, 'edit_preferences.html', context)

# views.py

def get_product_by_id(product_id):
    """
    Get product details by ID from the recommendations data
    """
    try:
        print(f"Looking for product with ID: {product_id}")  # Debug print
        all_recommendations = load_recommendations_from_excel()
        
        # Search through all categories and locations
        for category, locations in all_recommendations.items():
            for location, items in locations.items():
                for item in items:
                    # Add an ID to each item based on its position
                    item['id'] = hash(f"{item['name']}_{item['restaurant']}_{location}")
                    
                    if item['id'] == product_id:
                        # Add additional fields needed for display
                        item['category'] = category
                        item['location'] = location
                        
                        # Format price if needed
                        if 'price' in item:
                            try:
                                price = float(str(item['price']).replace(',', ''))
                                item['display_price'] = f"Rp {price:,.0f}"
                            except (ValueError, TypeError):
                                item['display_price'] = "Harga belum tersedia"
                        
                        print(f"Found product: {item['name']}")  # Debug print
                        return item
                        
        print("Product not found")  # Debug print
        return None
        
    except Exception as e:
        print(f"Error in get_product_by_id: {str(e)}")
        return None

def get_recommendations_by_category(category):
    """
    Get all recommendations for a specific category
    """
    try:
        all_recommendations = load_recommendations_from_excel()
        category_recommendations = []
        
        if category.lower() in all_recommendations:
            # Go through all locations for this category
            for location, items in all_recommendations[category.lower()].items():
                for item in items:
                    new_item = item.copy()
                    # Generate a unique ID for each item
                    new_item['id'] = hash(f"{item['name']}_{item['restaurant']}_{location}")
                    
                    # Handle price display
                    price_str = item.get('price', '0')
                    if price_str == '0' or not str(price_str).strip():
                        new_item['display_price'] = "Harga belum tersedia"
                    else:
                        try:
                            price_value = float(str(price_str).replace(',', ''))
                            new_item['display_price'] = f"Rp {price_value:,.0f}"
                        except (ValueError, TypeError):
                            new_item['display_price'] = "Harga belum tersedia"
                    
                    # Add location information
                    new_item['kecamatan'] = location
                    category_recommendations.append(new_item)
        
        print(f"Found {len(category_recommendations)} items for category {category}")
        return category_recommendations
        
    except Exception as e:
        print(f"Error in get_recommendations_by_category: {str(e)}")
        return []

def generate_product_id(name, restaurant, location):
    """
    Generate a positive integer ID from product details
    """
    # Create a string combining all the identifying information
    identifier = f"{name}_{restaurant}_{location}"
    # Create a hash of the identifier
    hash_object = hashlib.md5(identifier.encode())
    # Convert the first 8 characters of the hash to a positive integer
    return int(hash_object.hexdigest()[:8], 16)

def get_product_by_id(product_id):
    """
    Get product details by ID from the recommendations data
    Returns None if product is not found
    """
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
        print(f"Error in get_product_by_id: {str(e)}")
        return None

def get_recommendations_by_category(category):
    """
    Get all recommendations for a specific category
    Returns list of recommendations with generated IDs
    """
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
        print(f"Error in get_recommendations_by_category: {str(e)}")
        return []

def browse_category(request, category):
    """
    View function for browsing products by category
    """
    try:
        # Validate category
        valid_categories = ['nasi', 'roti', 'lontong', 'cemilan', 'minuman', 'mie', 'telur', 'bubur']
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
            'telur': 'Telur',
            'bubur': 'Bubur'
        }
        
        context = {
            'category': category_display.get(category.lower(), category.title()),
            'raw_category': category.lower(),  # For URL generation in template
            'recommendations': recommendations,
            'is_authenticated': request.user.is_authenticated,
            'name': request.user.username if request.user.is_authenticated else None,
        }
        
        return render(request, 'browse_category.html', context)
        
    except Exception as e:
        print(f"Error in browse_category view: {str(e)}")
        messages.error(request, 'Terjadi kesalahan saat memuat kategori.')
        return redirect('main:show_main')

def product_details(request, category, product_id):
    """
    View function for individual product details
    """
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
        print(f"Error in product_details view: {str(e)}")
        messages.error(request, 'Terjadi kesalahan saat memuat detail produk.')
        return redirect('main:browse_category', category=category)
