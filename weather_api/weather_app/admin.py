from django.contrib import admin
from .models import WeatherReport

@admin.register(WeatherReport)
class WeatherReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'city', 'country', 'temperature', 'condition', 'search_date')
    list_filter = ('search_date', 'user', 'city')
    search_fields = ('city', 'country', 'condition', 'user__username')
