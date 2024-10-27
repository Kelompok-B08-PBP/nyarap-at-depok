import os
from django.core.wsgi import get_wsgi_application

# Pastikan nama proyeknya benar
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyarap_at_depok.settings')

application = get_wsgi_application()
