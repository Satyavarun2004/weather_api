import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Max, Min
from django.http import HttpResponse
from django.conf import settings
from .models import WeatherReport

# ==========================================
# 1. User Authentication Views
# ==========================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not username or not password:
            messages.error(request, "Username and password cannot be empty.")
            return render(request, 'weather_app/register.html')
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'weather_app/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'weather_app/register.html')
            
        try:
            # Create user and log them in
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, f"Account created! Welcome, {username}!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error registering user: {e}")
            
    return render(request, 'weather_app/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Logged in successfully. Welcome back, {username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'weather_app/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ==========================================
# 2. Main Dashboard & API Logic
# ==========================================

@login_required
def home_view(request):
    search_result = None
    api_error = None
    city_query = request.GET.get('q', '').strip()
    
    # 1. Fetch weather if user submitted a city query
    if city_query:
        api_key = getattr(settings, 'WEATHER_API_KEY', '').strip()
        
        # Check if the user is using the default placeholder or is offline
        if not api_key or api_key == "YOUR_WEATHER_API_KEY_HERE":
            # Generate premium synthetic/mock weather data for testing
            import random
            mock_conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Mist", "Patchy Rain Possible", "Thunderstorm"]
            selected_condition = random.choice(mock_conditions)
            
            # Generate realistic values based on city name hash
            city_hash = sum(ord(c) for c in city_query)
            temp = 20 + (city_hash % 15)
            humidity = 40 + (city_hash % 50)
            wind = 5 + (city_hash % 20)
            press = 1005 + (city_hash % 15)
            vis = 8.0 + ((city_hash % 3) * 1.0)
            uv = 1.0 + (city_hash % 9)
            
            data = {
                "location": {
                    "name": city_query.capitalize(),
                    "country": "India" if city_query.lower() in ['bangalore', 'mumbai', 'delhi', 'hyderabad', 'chennai', 'kolkata'] else "Global Region"
                },
                "current": {
                    "temp_c": float(temp),
                    "humidity": int(humidity),
                    "wind_kph": float(wind),
                    "condition": {"text": selected_condition},
                    "feelslike_c": float(temp + random.choice([-1, 0, 1])),
                    "pressure_mb": float(press),
                    "vis_km": float(vis),
                    "uv": float(uv)
                }
            }
            
            location = data.get("location", {})
            current = data.get("current", {})
            
            search_result = WeatherReport.objects.create(
                user=request.user,
                city=location.get("name"),
                country=location.get("country"),
                temperature=current.get("temp_c"),
                humidity=current.get("humidity"),
                wind_speed=current.get("wind_kph"),
                condition=current.get("condition", {}).get("text", "Unknown"),
                feels_like=current.get("feelslike_c"),
                pressure=current.get("pressure_mb"),
                visibility=current.get("vis_km"),
                uv_index=current.get("uv"),
                raw_response=json.dumps(data)
            )
            messages.warning(request, f"WeatherAPI key not configured. Using Mock Weather Data for {search_result.city}.")
        else:
            url = "http://api.weatherapi.com/v1/current.json"
            params = {"key": api_key, "q": city_query}
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    location = data.get("location", {})
                    current = data.get("current", {})
                    
                    # Create and save new log to MySQL database via Django model
                    search_result = WeatherReport.objects.create(
                        user=request.user,
                        city=location.get("name"),
                        country=location.get("country"),
                        temperature=current.get("temp_c"),
                        humidity=current.get("humidity"),
                        wind_speed=current.get("wind_kph"),
                        condition=current.get("condition", {}).get("text", "Unknown"),
                        feels_like=current.get("feelslike_c"),
                        pressure=current.get("pressure_mb"),
                        visibility=current.get("vis_km"),
                        uv_index=current.get("uv"),
                        raw_response=json.dumps(data)
                    )
                    messages.success(request, f"Weather retrieved for {search_result.city}!")
                elif response.status_code == 400:
                    api_error = "City not found. Please verify the name."
                elif response.status_code == 403:
                    api_error = "Invalid API Key."
                else:
                    api_error = f"API returned status code: {response.status_code}"
            except requests.exceptions.RequestException as e:
                # If connection fails, fallback to generating mock weather data so user can still test!
                import random
                mock_conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Overcast"]
                selected_condition = random.choice(mock_conditions)
                city_hash = sum(ord(c) for c in city_query)
                temp = 20 + (city_hash % 15)
                
                data = {
                    "location": {"name": city_query.capitalize(), "country": "Offline Mode"},
                    "current": {
                        "temp_c": float(temp),
                        "humidity": 60,
                        "wind_kph": 10.0,
                        "condition": {"text": selected_condition},
                        "feelslike_c": float(temp),
                        "pressure_mb": 1013.0,
                        "vis_km": 10.0,
                        "uv": 5.0
                    }
                }
                
                search_result = WeatherReport.objects.create(
                    user=request.user,
                    city=city_query.capitalize(),
                    country="Offline Mode",
                    temperature=float(temp),
                    humidity=60,
                    wind_speed=10.0,
                    condition=selected_condition,
                    feels_like=float(temp),
                    pressure=1013.0,
                    visibility=10.0,
                    uv_index=5.0,
                    raw_response=json.dumps(data)
                )
                messages.warning(request, f"Connection failed/API offline. Using Mock Weather Data for {search_result.city}.")
    
    # 2. Calculate statistics for the logged-in user
    user_reports = WeatherReport.objects.filter(user=request.user)
    total_searches = user_reports.count()
    
    hottest_report = user_reports.order_by('-temperature').first()
    coldest_report = user_reports.order_by('temperature').first()
    last_search = user_reports.order_by('-id').first()
    
    # Aggregate Stats (Bonus challenge 2)
    stats = user_reports.aggregate(
        avg_temp=Avg('temperature'),
        max_temp=Max('temperature'),
        min_temp=Min('temperature')
    )
    
    context = {
        'search_result': search_result,
        'api_error': api_error,
        'city_query': city_query,
        'total_searches': total_searches,
        'hottest_report': hottest_report,
        'coldest_report': coldest_report,
        'last_search': last_search,
        'avg_temp': stats.get('avg_temp'),
    }
    
    return render(request, 'weather_app/home.html', context)


# ==========================================
# 3. History Management & Export Views
# ==========================================

@login_required
def history_view(request):
    history_records = WeatherReport.objects.filter(user=request.user).order_by('-id')
    return render(request, 'weather_app/history.html', {'history_records': history_records})


@login_required
def delete_record_view(request, record_id):
    record = get_object_or_404(WeatherReport, id=record_id, user=request.user)
    city_name = record.city
    record.delete()
    messages.success(request, f"Removed search record for {city_name} from history.")
    return redirect('history')


@login_required
def edit_record_view(request, record_id):
    record = get_object_or_404(WeatherReport, id=record_id, user=request.user)
    
    if request.method == 'POST':
        city = request.POST.get('city', '').strip()
        country = request.POST.get('country', '').strip()
        temperature = request.POST.get('temperature', '').strip()
        humidity = request.POST.get('humidity', '').strip()
        wind_speed = request.POST.get('wind_speed', '').strip()
        condition = request.POST.get('condition', '').strip()
        feels_like = request.POST.get('feels_like', '').strip()
        pressure = request.POST.get('pressure', '').strip()
        visibility = request.POST.get('visibility', '').strip()
        uv_index = request.POST.get('uv_index', '').strip()
        
        if not city or not country or not temperature or not humidity or not wind_speed or not condition:
            messages.error(request, "Please fill in all the required fields.")
            return render(request, 'weather_app/edit.html', {'record': record})
            
        try:
            record.city = city
            record.country = country
            record.temperature = float(temperature)
            record.humidity = int(humidity)
            record.wind_speed = float(wind_speed)
            record.condition = condition
            record.feels_like = float(feels_like) if feels_like else record.feels_like
            record.pressure = float(pressure) if pressure else record.pressure
            record.visibility = float(visibility) if visibility else record.visibility
            record.uv_index = float(uv_index) if uv_index else record.uv_index
            record.save()
            
            messages.success(request, f"Weather log for {city} updated successfully.")
            return redirect('history')
        except ValueError:
            messages.error(request, "Invalid input formats. Temperature, humidity, and speed must be numbers.")
            
    return render(request, 'weather_app/edit.html', {'record': record})


@login_required
def clear_history_view(request):
    if request.method == 'POST':
        deleted_count, _ = WeatherReport.objects.filter(user=request.user).delete()
        messages.success(request, f"Successfully cleared all {deleted_count} logs from your search history.")
    return redirect('history')


@login_required
def export_history_view(request):
    user_reports = WeatherReport.objects.filter(user=request.user).order_by('id')
    
    if not user_reports.exists():
        messages.error(request, "No history records to export.")
        return redirect('history')
        
    # Generate plaintext file contents
    file_lines = []
    for report in user_reports:
        file_lines.append(f"{report.city} | {report.temperature:.0f}°C | {report.condition}")
        
    file_content = "\n\n".join(file_lines)
    
    response = HttpResponse(file_content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="weather_history.txt"'
    return response
