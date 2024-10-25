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

