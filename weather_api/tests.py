from django.test import TestCase
from django.contrib.auth.models import User
from .models import WeatherReport

class WeatherReportModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_report_creation(self):
        # Test inserting a weather report
        report = WeatherReport.objects.create(
            user=self.user,
            city="Hyderabad",
            country="India",
            temperature=30.0,
            humidity=60,
            wind_speed=12.0,
            condition="Sunny",
            feels_like=31.0,
            pressure=1013.0,
            visibility=10.0,
            uv_index=6.0,
            raw_response="{}"
        )
        self.assertEqual(report.city, "Hyderabad")
        self.assertEqual(report.user.username, "testuser")
        self.assertEqual(str(report), "Hyderabad (30.00°C) searched by testuser")


class WeatherViewsTest(TestCase):
    def test_login_page_renders(self):
        # Verify login URL loads and renders template
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather_app/login.html')

    def test_register_page_renders(self):
        # Verify registration URL loads and renders template
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather_app/register.html')
