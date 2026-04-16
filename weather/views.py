import requests
from datetime import datetime
from django.shortcuts import render
from django.conf import settings
from .models import SearchHistory


def landing(request):
    return render(request, 'weather/landing.html')


def index(request):
    weather_data = None
    forecast_data = []
    error = None

    if request.method == 'POST':
        city = request.POST.get('city')
        api_key = settings.WEATHER_API_KEY

        # Aktuelles Wetter
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=de'
        response = requests.get(url)
        data = response.json()

        if data.get('cod') == 200:
            weather_data = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind': round(data['wind']['speed']),
            }
            SearchHistory.objects.create(city=data['name'])

            # 5-Tage-Prognose
            forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=de'
            forecast_response = requests.get(forecast_url)
            forecast_json = forecast_response.json()

            day_names = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            today = datetime.now().strftime('%Y-%m-%d')
            days = {}

            for item in forecast_json.get('list', []):
                date = item['dt_txt'][:10]
                if date == today:
                    continue
                if date not in days:
                    dt = datetime.strptime(date, '%Y-%m-%d')
                    days[date] = {
                        'day': day_names[dt.weekday()],
                        'temps': [],
                        'icon': item['weather'][0]['icon'],
                        'slots': [],
                    }
                days[date]['temps'].append(item['main']['temp'])
                if '12:00:00' in item['dt_txt']:
                    days[date]['icon'] = item['weather'][0]['icon']
                days[date]['slots'].append({
                    'time': item['dt_txt'][11:16],
                    'temp': round(item['main']['temp']),
                    'icon': item['weather'][0]['icon'],
                    'description': item['weather'][0]['description'],
                    'humidity': item['main']['humidity'],
                    'wind': round(item['wind']['speed']),
                })

            for day in list(days.values())[:5]:
                forecast_data.append({
                    'day': day['day'],
                    'icon': day['icon'],
                    'max': round(max(day['temps'])),
                    'min': round(min(day['temps'])),
                    'slots': day['slots'],
                })

        else:
            error = 'Stadt nicht gefunden.'

    # Die letzten 5 Suchen laden
    history = SearchHistory.objects.all()[:5]

    return render(request, 'weather/index.html', {
        'weather': weather_data,
        'forecast': forecast_data,
        'error': error,
        'history': history,
    })

