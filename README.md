# Wetterapp

Eine deutschsprachige Wetteranwendung gebaut mit Django und der OpenWeather API. Die App zeigt aktuelle Wetterdaten sowie eine 5-Tage-Prognose für jede Stadt weltweit an.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-6.0-green?style=flat-square&logo=django)
![OpenWeather](https://img.shields.io/badge/API-OpenWeather-orange?style=flat-square)

---

## Features

- Aktuelle Wetterdaten für jede Stadt weltweit
- 5-Tage-Prognose mit stündlichen 3-Stunden-Slots pro Tag
- Suchverlauf: Die letzten 5 gesuchten Städte werden in der Datenbank gespeichert
- Detaillierte Metriken: Temperatur, gefühlte Temperatur, Luftfeuchtigkeit, Windgeschwindigkeit
- Vollständig deutschsprachige Benutzeroberfläche inkl. Wetterbeschreibungen
- Responsives Dark-Mode Design

---

## Technologien

| Technologie | Version | Zweck |
|---|---|---|
| Python | 3.x | Programmiersprache |
| Django | 6.0 | Web-Framework |
| OpenWeather API | 2.5 | Wetterdaten (aktuell + Prognose) |
| requests | latest | HTTP-Calls zur OpenWeather API |
| python-dotenv | latest | Laden der Umgebungsvariablen aus `.env` |
| SQLite | built-in | Datenbank für den Suchverlauf |

---

## Projektstruktur

```
wetterapp/
│
├── mysite/                      # Django-Projektkonfiguration
│   ├── settings.py              # Projekteinstellungen inkl. WEATHER_API_KEY
│   ├── urls.py                  # Haupt-URL-Konfiguration
│   ├── wsgi.py
│   └── asgi.py
│
├── weather/                     # Haupt-App
│   ├── templates/
│   │   └── weather/
│   │       ├── landing.html     # Landing Page
│   │       └── index.html       # Wettersuche & Ergebnisanzeige
│   ├── models.py                # SearchHistory Modell
│   ├── views.py                 # Business-Logik & API-Integration
│   ├── urls.py                  # App-spezifische URL-Routen
│   ├── apps.py
│   ├── admin.py
│   └── tests.py
│
├── db.sqlite3                   # SQLite-Datenbank (Suchverlauf)
├── manage.py                    # Django CLI
├── requirements.txt
├── .env                         # Umgebungsvariablen (nicht in Git!)
├── .gitignore
└── README.md
```

---

## Datenbankmodell

Die App verwendet ein einziges Modell `SearchHistory` in `weather/models.py`:

```python
class SearchHistory(models.Model):
    city = models.CharField(max_length=100)   # Name der gesuchten Stadt
    searched_at = models.DateTimeField(auto_now_add=True)  # Zeitstempel

    class Meta:
        ordering = ['-searched_at']  # Neueste Suche zuerst
```

Jede erfolgreiche Stadtsuche legt automatisch einen neuen Eintrag an. In der Ansicht werden stets die letzten 5 Einträge geladen und als Schnellzugriff-Buttons angezeigt.

---

## API-Integration

Die App kommuniziert mit zwei Endpunkten der OpenWeather API v2.5:

### Aktuelles Wetter

```
GET https://api.openweathermap.org/data/2.5/weather
    ?q={city}
    &appid={api_key}
    &units=metric
    &lang=de
```

Verwendete Felder aus der Response:

| Feld | Beschreibung |
|---|---|
| `name` | Stadtname |
| `sys.country` | Länderkürzel |
| `main.temp` | Aktuelle Temperatur in °C |
| `main.feels_like` | Gefühlte Temperatur in °C |
| `main.humidity` | Luftfeuchtigkeit in % |
| `weather[0].description` | Wetterbeschreibung (Deutsch via `lang=de`) |
| `weather[0].icon` | Icon-Code für OpenWeather Icon-CDN |
| `wind.speed` | Windgeschwindigkeit in m/s |

### 5-Tage-Prognose

```
GET https://api.openweathermap.org/data/2.5/forecast
    ?q={city}
    &appid={api_key}
    &units=metric
    &lang=de
```

Die API liefert Wetterdaten in 3-Stunden-Intervallen für 5 Tage. Die Verarbeitung in `views.py` gruppiert diese Slots nach Datum und berechnet pro Tag die Minimal- und Maximaltemperatur. Der heutige Tag wird aus der Prognose herausgefiltert. Das Icon des Tages wird anhand des 12:00-Uhr-Slots gesetzt.

---

## Views

### `landing(request)`

Rendert ausschließlich die Landing Page (`weather/landing.html`). Keine Logik.

### `index(request)`

Verarbeitet GET- und POST-Requests für die Wettersuche:

- **GET**: Zeigt das leere Suchformular sowie den Suchverlauf an.
- **POST**: Liest den Stadtnamen aus `request.POST`, ruft beide API-Endpunkte auf, verarbeitet die Daten und übergibt sie ans Template. Bei Fehler (z.B. Stadt nicht gefunden, `cod != 200`) wird eine Fehlermeldung übergeben.

Kontextvariablen die ans Template übergeben werden:

| Variable | Typ | Beschreibung |
|---|---|---|
| `weather` | dict / None | Aktuelle Wetterdaten |
| `forecast` | list | Liste mit 5 Tagesobjekten |
| `error` | str / None | Fehlermeldung |
| `history` | QuerySet | Die letzten 5 Suchanfragen |

---

## URL-Routen

### `mysite/urls.py`

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('weather.urls')),
]
```

### `weather/urls.py`

```python
urlpatterns = [
    path('', views.landing, name='landing'),
    path('wetter/', views.index, name='index'),
]
```

| URL | View | Beschreibung |
|---|---|---|
| `/` | `landing` | Landing Page |
| `/wetter/` | `index` | Wettersuche & Ergebnisanzeige |
| `/admin/` | Django Admin | Adminoberfläche |

---

## Installation

### Voraussetzungen

- Python 3.x
- pip
- OpenWeather API Key – kostenlos registrieren unter [openweathermap.org/api](https://openweathermap.org/api)

### Schritt-für-Schritt

**1. Repository klonen**

```bash
git clone https://github.com/dein-username/wetterapp.git
cd wetterapp
```

**2. Virtuelle Umgebung erstellen und aktivieren**

```bash
python -m venv myvenv
```

Windows:
```bash
myvenv\Scripts\activate
```

Mac / Linux:
```bash
source myvenv/bin/activate
```

**3. Abhängigkeiten installieren**

```bash
pip install -r requirements.txt
```

**4. Umgebungsvariablen konfigurieren**

Erstelle eine `.env` Datei im Stammverzeichnis des Projekts:

```
SECRET_KEY=dein-django-secret-key
WEATHER_API_KEY=dein-openweather-api-key
DEBUG=True
```

Wichtig: Die Variable heißt `WEATHER_API_KEY` – so wird sie in `settings.py` geladen und in `views.py` über `settings.WEATHER_API_KEY` abgerufen.

**5. Datenbank migrieren**

Erstellt die `SearchHistory`-Tabelle in der SQLite-Datenbank:

```bash
python manage.py migrate
```

**6. Entwicklungsserver starten**

```bash
python manage.py runserver
```

Die App ist erreichbar unter `http://localhost:8000`.

---

## Umgebungsvariablen

| Variable | Beschreibung | Pflicht |
|---|---|---|
| `SECRET_KEY` | Django Secret Key | Ja |
| `WEATHER_API_KEY` | API Key von openweathermap.org | Ja |
| `DEBUG` | Debug-Modus (`True` / `False`) | Nein (Standard: `False`) |

---

## .gitignore

Folgende Dateien und Ordner sind vom Git-Tracking ausgeschlossen:

```
.env
myvenv/
__pycache__/
*.pyc
db.sqlite3
```

Die `.env` Datei darf unter keinen Umständen in das Repository eingecheckt werden, da sie den geheimen API Key enthält.

---

## Requirements

```
Django>=6.0
requests
python-dotenv
```

Aktuelle Liste generieren mit:

```bash
pip freeze > requirements.txt
```

---

## Lizenz

MIT License – siehe [LICENSE](LICENSE).
