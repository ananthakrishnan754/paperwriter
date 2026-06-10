import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperwriter.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class AuthTestCase(TestCase):
    """Base test case that provides an authenticated client."""

    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email='test@example.com',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
