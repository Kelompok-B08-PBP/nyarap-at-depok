from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from reviews.models import Review

class ReviewTests(TestCase):
    def setUp(self):
        # Setup client dan user test
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        
        # Definisikan URL
        self.create_url = reverse('reviews:create_product_review')
        self.edit_url = lambda review_id: reverse('reviews:edit_product_review', args=[review_id])
        self.delete_url = lambda review_id: reverse('reviews:delete_product_review', args=[review_id])
        
        # Buat review contoh untuk pengujian edit dan delete
        self.review = Review.objects.create(
            user=self.user,
            restaurant_name="Test Restaurant",
            food_name="Test Food",
            rating=4,
            review="Delicious!",
        )
    
    def test_create_review(self):
        # Uji pembuatan review baru
        response = self.client.post(self.create_url, {
            'restaurant_name': 'New Restaurant',
            'food_name': 'New Food',
            'rating': 5,
            'review': 'Great food!'
        })
        
        # Pastikan redirect berhasil dan review dibuat
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(restaurant_name='New Restaurant').exists())

    def test_create_review_template(self):
        # Pastikan template create_review digunakan
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_product_review.html')

    def test_edit_review(self):
        # Uji mengedit review yang sudah ada
        response = self.client.post(self.edit_url(self.review.id), {
            'restaurant_name': 'Updated Restaurant',
            'food_name': 'Updated Food',
            'rating': 3,
            'review': 'Average food'
        })
        
        # Pastikan redirect berhasil dan perubahan tersimpan
        self.assertEqual(response.status_code, 302)
        self.review.refresh_from_db()
        self.assertEqual(self.review.restaurant_name, 'Updated Restaurant')

    def test_edit_review_template(self):
        # Pastikan template edit_review digunakan
        response = self.client.get(self.edit_url(self.review.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_product_review.html')
