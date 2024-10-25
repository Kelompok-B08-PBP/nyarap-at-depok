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

def detail_view(request, id):
    recommendations = load_recommendations_from_excel()
    item = next((item for item in recommendations if item.get('id') == id), None)
    
    if item is None:
        return render(request, '404.html')  
    
    return render(request, 'nyarap_detailer.html', {'item': item})
