from django.shortcuts import render, get_object_or_404
import pandas as pd

def load_recommendations_from_excel():
    try:
        # Load the data from the Excel file
        df = pd.read_excel('main/data/dataset.xlsx')
        
        # Convert DataFrame to list of dictionaries
        recommendations = df.to_dict('records')
        
        # Format the data
        for index, item in enumerate(recommendations):
            item['id'] = index  # Menambahkan ID berdasarkan index
            item['rating'] = int(float(item['Rating'])) if pd.notnull(item['Rating']) else None
            item['price'] = "{:,.0f}".format(float(item['Harga'])) if pd.notnull(item['Harga']) else "N/A"
            item['name'] = item['Nama Produk']
            item['restaurant'] = item['Nama Restoran']
            item['operational_hours'] = item['Jam Operasional']
            item['location'] = item['Lokasi']
            item['image'] = item['Link Foto']
            item['kategori'] = item['Kategori']
        
        print(recommendations)
        
        return recommendations
    
    except Exception as e:
        print(f"Error loading recommendations: {e}")
        return []

def detailer_list(request):
    recommendations = load_recommendations_from_excel()
    return render(request, 'card_list.html', {'recommendations': recommendations})

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
