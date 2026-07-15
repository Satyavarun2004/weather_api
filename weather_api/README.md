# Weather Data Logger System

A modern Django Web Application that integrates with WeatherAPI.com to fetch, display, and log weather data to a MySQL database. Features custom glassmorphism design, session-based user authentication, complete CRUD operations, and detailed query stats.

## Features
- **User Authentication (Login/Signup):** Built using Django's session authentication with SHA-256 hashed password storage.
- **Dynamic Database Logging:** Logs location details, weather criteria, timestamps, and raw JSON payloads.
- **Advanced Statistics Dashboard:** Displays search counters, temperature averages, and hottest/coldest search queries.
- **Offline Mock Weather Fallback:** Automatically generates realistic mock data when offline or if no API key is specified, allowing offline grading.
- **Data Operations:** Full CRUD features enabling users to update or delete records, download plain text exports, and clear logs.

---

## Setup Instructions

### 1. Install Dependencies
Ensure Python is installed on your machine. Open a terminal in the project directory and run:
```bash
pip install django requests pymysql cryptography
```

### 2. Configure Credentials
The application automatically creates `weather_config.json` on start (if missing). Open the file and update it with your settings:
```json
{
    "api_key": "YOUR_WEATHER_API_KEY_HERE",
    "db_host": "localhost",
    "db_user": "root",
    "db_password": "",
    "db_port": "3306"
}
```
*Note: If no API key is entered, the app runs in **Offline Mock Fallback** mode, allowing you to test all functions without an API account.*

### 3. Run Database Migrations
Create the database tables in your local MySQL Server:
```bash
python manage.py makemigrations weather_app
python manage.py migrate
```

### 4. Run the Web Server
Launch the server:
```bash
python manage.py runserver
```
Open **`http://127.0.0.1:8000/`** in your web browser.

---

## Running Unit Tests
To execute the automated unit tests:
```bash
python manage.py test weather_app
```
