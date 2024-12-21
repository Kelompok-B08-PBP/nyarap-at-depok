# views.py
from django.shortcuts import render
import pandas as pd
import os
from django.conf import settings

from nyarap_detailer.models import Detailer

def load_recommendations_from_excel():
    try:
        # Dapatkan path absolut file Excel
        excel_path = os.path.join(settings.BASE_DIR, 'nyarap_detailerpyth', 'data', 'dataset.xlsx')
        
        # Print path untuk debugging
        print(f"Mencoba membaca file dari: {excel_path}")
        
        # Cek apakah file exists
        if not os.path.exists(excel_path):
            print(f"File tidak ditemukan di: {excel_path}")
            return []
            
        # Baca file Excel dengan explicit engine
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        # Print kolom yang tersedia untuk debugging
        print(f"Kolom yang tersedia: {df.columns.tolist()}")
        
        # Print beberapa baris pertama untuk debugging
        print(f"Preview data:\n{df.head()}")
        
        # Konversi DataFrame ke list of dictionaries
        recommendations = []
        
        for index, row in df.iterrows():
            try:
                recommendation = {
                    'id': index,
                    'name': str(row['Nama Produk']) if pd.notnull(row['Nama Produk']) else '',
                    'restaurant': str(row['Nama Restoran']) if pd.notnull(row['Nama Restoran']) else '',
                    'location': str(row['Lokasi']) if pd.notnull(row['Lokasi']) else '',
                    'operational_hours': str(row['Jam Operasional']) if pd.notnull(row['Jam Operasional']) else '',
                    'image': str(row['Link Foto']) if pd.notnull(row['Link Foto']) else '',
                    'rating': int(float(row['Rating'])) if pd.notnull(row['Rating']) else 0,
                    'price': "{:,.0f}".format(float(row['Harga'])) if pd.notnull(row['Harga']) else "N/A",
                    'kategori': str(row['Kategori']) if pd.notnull(row['Kategori']) else ''
                }
                recommendations.append(recommendation)
                print(f"Berhasil memproses baris {index}")
            except Exception as row_error:
                print(f"Error pada baris {index}: {row_error}")
                continue
        
        print(f"Total data yang berhasil diproses: {len(recommendations)}")
        return recommendations
        
    except Exception as e:
        print(f"Error loading recommendations: {str(e)}")
        # Print traceback untuk debugging
        import traceback
        print(traceback.format_exc())
        return []

def detailer_list(request):
    recommendations = load_recommendations_from_excel()
    # Print jumlah data untuk debugging
    print(f"Jumlah data yang dikirim ke template: {len(recommendations)}")
    context = {'recommendations': recommendations}
    return render(request, 'card_list.html', context)


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