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
from nyarap_detailer.views import load_recommendations_from_excel

def load_recommendations_from_excel():
    try:
        # Load the data from the Excel file
        df = pd.read_excel('main/data/dataset.xlsx')
        print(f"Loaded Excel file with {len(df)} rows")
        
        # Clean the data first
        df['Kategori'] = df['Kategori'].str.lower().str.strip()
        df['Kecamatan'] = df['Kecamatan']
        
        # Convert to dictionary grouped by Kategori (breakfast type) and Kecamatan (location)
        recommendations = {}
        for _, row in df.iterrows():
            try:
                kategori = row['Kategori']  # Already cleaned
                kecamatan = row['Kecamatan']  # Already cleaned
                
                # Initialize dictionary for each Kategori if not present
                if kategori not in recommendations:
                    recommendations[kategori] = {}

                # Initialize list for each Kecamatan if not present
                if kecamatan not in recommendations[kategori]:
                    recommendations[kategori][kecamatan] = []

                # Clean price data
                price = str(row['Harga'])
                if isinstance(row['Harga'], (int, float)):
                    clean_price = str(row['Harga'])
                else:
                    # Remove currency symbol, spaces, commas, and periods
                    clean_price = price.replace('Rp', '').replace(',', '').replace('.', '').replace(' ', '').strip()
                
                # Print debug info for price cleaning
                print(f"Original price: {price}, Cleaned price: {clean_price}")
                
                #Append recommendation details for each Kecamatan
                recommendations[kategori][kecamatan].append({
                    'name': str(row['Nama Produk']).strip(),
                    'restaurant': str(row['nama_restoran']).strip,
                    'rating': float(row['Rating']) if pd.notnull(row['Rating']) else 0.0,
                    'operational_hours': str(row['Jam Operasional']).strip(),
                    'location': str(row['Lokasi']).strip(),
                    'price': clean_price,
               
                })
                
            except KeyError as e:
                print(f"Missing column in row: {str(e)}")
                continue
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue

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
                
                filtered_recommendations = []
                for item in location_recommendations:
                    try:
                        # Clean price and convert to float
                        price_str = item['price']
                        price_value = float(price_str)
                        print(f"Checking price: {price_value} for {item['name']}")
                        
                        if min_price <= price_value <= max_price:
                            # Use display_price for showing to user
                      
                            filtered_recommendations.append(item)
                            print(f"Added recommendation: {item['name']} with price {item['price']}")
                    except (ValueError, KeyError) as e:
                        print(f"Error processing price for item: {item.get('name', 'unknown')}")
                        print(f"Price value causing error: {item.get('price', 'unknown')}")
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

def load_recommendations_from_excel():
    # Load the data from the Excel file
    df = pd.read_excel('main/data/dataset.xlsx')

    # Convert to dictionary grouped by Kategori (breakfast type) and Kecamatan (location)
    recommendations = {}
    for _, row in df.iterrows():
        kategori = row['Kategori'].lower() # Map Kategori to breakfast_type
        kecamatan = row['Kecamatan'] # Map Kecamatan to location

        # Initialize dictionary for each Kategori if not present
        if kategori not in recommendations:
            recommendations[kategori] = {}

        # Initialize list for each Kecamatan if not present
        if kecamatan not in recommendations[kategori]:
            recommendations[kategori][kecamatan] = []

        #Append recommendation details for each Kecamatan
        recommendations[kategori][kecamatan].append({
            'name': row['Nama Produk'],  # Map Nama Produk to product name
            'restaurant': row['nama_restoran'],  # Name of restaurant
            'rating': row['Rating'],  # Restaurant rating
            'operational_hours': row['Jam Operasional'],  # Restaurant operational hours
            'location': row['Lokasi'],  # Location (address)
            'price': str(row['Harga']),  # Map Harga to price
       
        })

    return recommendations

# Define the recommendation logic
def get_recommendations(breakfast_type, location, price_range):
    # Load recommendations from the Excel file
    recommendations = load_recommendations_from_excel()
    breakfast_type = breakfast_type.strip().lower()  # Menyesuaikan dengan lowercase
    location = location.strip().lower()  # Menyesuaikan dengan lowercase
    
    # Get recommendations based on Kategori (breakfast_type) and Kecamatan (location)
    location_recommendations = recommendations.get(breakfast_type, {}).get(location, [])
    
    # Filter by price range
    price_ranges = {
        '0-15000': (0, 15000),
        '15000-25000': (15000, 25000),
        '25000-50000': (25000, 50000),
        '50000-100000': (50000, 100000),
        '100000+': (100000, float('inf'))
    }
    
    min_price, max_price = price_ranges[price_range]
    filtered_recommendations = [
        item for item in location_recommendations
        if min_price <= float(item['price']) <= max_price
    ]
    
    return filtered_recommendations


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
