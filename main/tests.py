from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserPreference

class MainTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.preference = UserPreference.objects.create(
            user=self.user,
            preferred_breakfast_type='nasi',
            preferred_location='Beji',
            preferred_price_range='0-15000'
        )

    def test_login_required(self):
        """Test halaman yang membutuhkan login"""
        # Test tanpa login
        response = self.client.get(reverse('main:edit_preferences'))
        self.assertEqual(response.status_code, 302)  # Harus redirect ke login
        
        # Test dengan login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:edit_preferences'))
        self.assertEqual(response.status_code, 200)  # Harus berhasil

    def test_main_page(self):
        response = self.client.get(reverse('main:show_main'))
        self.assertEqual(response.status_code, 200)

    def test_recommendations(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:recommendation_list'))
        self.assertEqual(response.status_code, 200)