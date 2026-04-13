import requests
from django.shortcuts import render
from django.conf import settings

def index(request):
    weather_data = None
    error = None

    if request.method == 'POST':
        city = request.POST.get('city')
        api_key = settings.WEATHER_API_KEY
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
        else:
            error = 'Stadt nicht gefunden.'

    return render(request, 'weather/index.html', {'weather': weather_data, 'error': error})

