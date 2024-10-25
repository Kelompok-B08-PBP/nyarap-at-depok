from django.shortcuts import render, redirect
from .models import Detailer, Comment
from .forms import CommentForm
import pandas as pd

def load_recommendations_from_excel():
    # Load the data from the Excel file
    df = pd.read_excel('main/data/dataset.xlsx')

    # Convert to dictionary with a list for recommendations
    recommendations = []
    for _, row in df.iterrows():
        recommendations.append({
            'name': row['Nama Produk'],  # Map Nama Produk to product name
            'restaurant': row['Nama Restoran'],  # Name of restaurant
            'rating': row['Rating'],  # Restaurant rating
            'operational_hours': row['Jam Operasional'],  # Restaurant operational hours
            'location': row['Lokasi'],  # Location (address)
            'price': str(row['Harga']),  # Map Harga to price
            'image': row['Link Foto']  # Map Link Foto to image
        })

    return recommendations

# View untuk menampilkan detail tempat makan dan mengelola form komentar
def detailer_list(request):
    detailers = Detailer.objects.all()  # Ambil semua detailer dari database
    recommendations = load_recommendations_from_excel()  # Ambil rekomendasi dari Excel

    # Mengelola form komentar
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            detailer_id = request.POST.get('detailer_id')  # Mengambil ID tempat makan dari form
            comment.detailer = Detailer.objects.get(id=detailer_id)
            comment.save()
            return redirect('detailer_list')
    else:
        form = CommentForm()

    # Kirim data tempat makan dan form ke template
    return render(request, 'main:main.html', {'detailers': detailers, 'form': form, 'recommendations': recommendations})

def preferences_summary(request):
    # Ambil preferensi dari sesi atau sumber lainnya
    preference = {
        'location': request.session.get('location', 'Depok'),
        'breakfast_type': request.session.get('breakfast_type', 'All'),
        'price_range': request.session.get('price_range', 'All'),
    }

    # Ambil data produk dari database
    detailers = Detailer.objects.all()  # Ambil semua detailer

    # Filter berdasarkan preferensi
    if preference['location']:
        detailers = detailers.filter(location=preference['location'])
    if preference['breakfast_type'] and preference['breakfast_type'] != 'All':
        detailers = detailers.filter(breakfast_type=preference['breakfast_type'])
    if preference['price_range'] and preference['price_range'] != 'All':
        detailers = detailers.filter(price_range=preference['price_range'])

    context = {
        'preference': preference,
        'detailers': detailers,
    }
    return render(request, 'main:recommendation_list.html', context)
