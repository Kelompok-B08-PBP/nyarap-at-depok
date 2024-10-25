from django.shortcuts import render, redirect
from .models import Detailer, Comment
from .forms import CommentForm

# View untuk menampilkan detail tempat makan dan mengelola form komentar
def detailer_list(request):
    detailers = Detailer.objects.all()

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
    return render(request, 'nyarap_detailer.html', {'detailers': detailers, 'form': form})
