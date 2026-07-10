from django.db import models
from django.contrib.auth.models import User

class WeatherReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.IntegerField()
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2)
    condition = models.CharField(max_length=100)
    search_date = models.DateField(auto_now_add=True)
    search_time = models.TimeField(auto_now_add=True)
    
    # Bonus details (Challenge 1)
    feels_like = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.DecimalField(max_digits=6, decimal_places=2)
    visibility = models.DecimalField(max_digits=5, decimal_places=2)
    uv_index = models.DecimalField(max_digits=3, decimal_places=1)
    
    # Raw API JSON
    raw_response = models.TextField()

    def __str__(self):
        return f"{self.city} ({self.temperature}°C) searched by {self.user.username}"
