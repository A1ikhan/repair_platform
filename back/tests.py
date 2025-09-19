from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from .models import CustomerProfile, RepairRequest
from .services import AuthService, RepairRequestService


class AuthTests(TestCase):
    def test_user_registration(self):
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'user_type': 'customer'
        }

        user = AuthService.register_user(user_data, 'customer')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(hasattr(user, 'customer_profile'))


class RepairRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testcustomer', 'customer@test.com', 'testpass')
        CustomerProfile.objects.create(user=self.user)

    def test_create_repair_request(self):
        data = {
            'title': 'Test Request',
            'description': 'Test description',
            'device_type': 'fridge',
            'address': 'Test address'
        }

        request = RepairRequestService.create_request(data, self.user)
        self.assertEqual(request.title, 'Test Request')
        self.assertEqual(request.created_by, self.user)