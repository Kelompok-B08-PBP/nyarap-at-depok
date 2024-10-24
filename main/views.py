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


def show_main(request):
    preference_entries = UserPreference.objects.all()

    context = {
        'name': request.user.username,
        'class': 'PBP D',
        'npm': '2306123456',
        'mood_entries': preference_entries,
        'last_login': request.COOKIES['last_login'],
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

def recommendation_list(request):
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    
    # Dictionary untuk convert nilai dari form ke display value
    breakfast_display = {
        'masih_bingung': 'Masih Bingung',
        'nasi': 'Nasi',
        'roti': 'Roti',
        'lontong': 'Lontong',
        'cemilan': 'Cemilan',
        'minuman': 'Minuman',
    }

    location_display = {
        'beji': 'Beji',
        'bojongsari': 'Bojongsari',
        'cilodong': 'Cilodong',
        'cimanggis': 'Cimanggis',
        'cinere': 'Cinere',
        'cipayung': 'Cipayung',
        'limo': 'Limo',
        'pancoran_mas': 'Pancoran Mas',
        'sawangan': 'Sawangan',
        'sukmajaya': 'Sukmajaya',
        'tapos': 'Tapos',
    }

    price_display = {
        '0-15000': 'Dibawah Rp 15.000',
        '15000-25000': 'Rp 15.000 - Rp 25.000',
        '25000-50000': 'Rp 25.000 - Rp 50.000',
        '50000-100000': 'Rp 50.000 - Rp 100.000',
        '100000+': 'Diatas Rp 100.000',
    }
    
    if request.user.is_authenticated:
        try:
            # Ambil preferensi terbaru dari user yang login
            latest_preference = UserPreference.objects.filter(user=request.user).latest('created_at')
            print("Fetched preference:", latest_preference.preferred_breakfast_type, latest_preference.preferred_location, latest_preference.preferred_price_range)  # Debug
            
            context['preference'] = {
                'breakfast_type': breakfast_display.get(latest_preference.preferred_breakfast_type),
                'location': location_display.get(latest_preference.preferred_location),
                'price_range': price_display.get(latest_preference.preferred_price_range)
            }
        except UserPreference.DoesNotExist:
            context['preference'] = {
                'breakfast_type': 'Belum dipilih',
                'location': 'Belum dipilih',
                'price_range': 'Belum dipilih'
            }
    else:
        # Untuk user yang tidak login, ambil dari session
        breakfast_type = request.session.get('preferred_breakfast_type', '')
        location = request.session.get('preferred_location', '')
        price_range = request.session.get('preferred_price_range', '')
        
        context['preference'] = {
            'breakfast_type': breakfast_display.get(breakfast_type, 'Belum dipilih'),
            'location': location_display.get(location, 'Belum dipilih'),
            'price_range': price_display.get(price_range, 'Belum dipilih')
        }

    return render(request, 'recommendation_list.html', context)

def recommendations(request):
    context = {
        'is_authenticated': request.user.is_authenticated,
        'name': request.user.username if request.user.is_authenticated else None,
    }
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                existing_preference = UserPreference.objects.get(user=request.user)
                form = PreferencesForm(request.POST, instance=existing_preference)
            except UserPreference.DoesNotExist:
                form = PreferencesForm(request.POST)
        else:
            form = PreferencesForm(request.POST)
        
        if form.is_valid():
            if request.user.is_authenticated:
                preference = form.save(commit=False)
                preference.user = request.user
                preference.save()
                messages.success(request, 'Preferensi kamu telah diperbarui!')
                print("Updated preference:", preference.preferred_breakfast_type, preference.preferred_location, preference.preferred_price_range)  # Debug
            else:
                # Simpan ke session untuk user yang tidak login
                request.session['preferred_location'] = form.cleaned_data['preferred_location']
                request.session['preferred_breakfast_type'] = form.cleaned_data['preferred_breakfast_type']
                request.session['preferred_price_range'] = form.cleaned_data['preferred_price_range']
                print("Saved to session:", form.cleaned_data)  # Debug
            
            return redirect('main:recommendation_list')
    else:
        # GET request - tampilkan form dengan data yang ada
        if request.user.is_authenticated:
            try:
                existing_preference = UserPreference.objects.get(user=request.user)
                form = PreferencesForm(instance=existing_preference)
            except UserPreference.DoesNotExist:
                form = PreferencesForm()
        else:
            # Pre-fill form dari session untuk user yang tidak login
            initial_data = {
                'preferred_location': request.session.get('preferred_location', ''),
                'preferred_breakfast_type': request.session.get('preferred_breakfast_type', ''),
                'preferred_price_range': request.session.get('preferred_price_range', ''),
            }
            form = PreferencesForm(initial=initial_data)
    
    context['form'] = form
    return render(request, 'recommendations.html', context)
