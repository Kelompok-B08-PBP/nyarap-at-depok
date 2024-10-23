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

# views.py

def recommendations(request):
    context = {
        'is_authenticated': request.user.is_authenticated,
        'name': request.user.username if request.user.is_authenticated else None,
        'form': PreferencesForm()  # Updated form name
    }
    
    if request.method == 'POST':
        form = PreferencesForm(request.POST)  # Updated form name
        if form.is_valid():
            location = form.cleaned_data['preferred_location']
            breakfast_type = form.cleaned_data['preferred_breakfast_type']
            price_range = form.cleaned_data['preferred_price_range']
            
            if request.user.is_authenticated:
                UserPreference.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'preferred_location': location,
                        'preferred_breakfast_type': breakfast_type,
                        'preferred_price_range': price_range
                    }
                )
                messages.success(request, 'Preferensi kamu telah disimpan!')
            
            return redirect('main:recommendation_list')
        else:
            context['form'] = form
    
    return render(request, 'recommendations.html', context)

def create_preference_entry(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST)  # Updated form name
        if form.is_valid():
            preference = form.save(commit=False)
            preference.user = request.user
            preference.save()
            return redirect('main:recommendation_list')
    else:
        form = PreferencesForm()  # Updated form name
    
    context = {'form': form}
    return render(request, "create_preference.html", context)

def recommendation_list(request):
    context = {
        'user_preferences': []
    }
    
    if request.user.is_authenticated:
        # Get user's preference history
        context['user_preferences'] = UserPreference.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
    return render(request, 'recommendation_list.html', context)
