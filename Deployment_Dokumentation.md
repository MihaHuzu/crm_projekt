# Deployment-Dokumentation – Flask CRM System

## Übersicht

Das Flask CRM System wurde auf **PythonAnywhere** deployed und ist unter folgender Adresse öffentlich erreichbar:

**URL:** https://mihaela.pythonanywhere.com/login

PythonAnywhere ist eine cloudbasierte Plattform, die Python-Webanwendungen kostenlos hostet. Im Gegensatz zu GitHub, wo nur der Quellcode gespeichert wird, läuft die Anwendung auf PythonAnywhere tatsächlich als Webserver und ist für jeden im Internet zugänglich.

---

## Unterschied: GitHub vs. Deployment

| | GitHub | PythonAnywhere |
|---|---|---|
| **Zweck** | Quellcode speichern | Anwendung live betreiben |
| **Zugriff** | Nur Entwickler | Alle Internetnutzer |
| **Läuft die App?** | Nein | Ja |
| **URL** | github.com/... | mihaela.pythonanywhere.com |

---

## Voraussetzungen

- GitHub-Konto mit dem Projektrepository
- PythonAnywhere-Konto (kostenlos)
- Projekt läuft lokal fehlerfrei

---

## Deployment-Schritte

### Schritt 1: Code auf GitHub aktualisieren

Vor dem Deployment muss der aktuelle Code auf GitHub verfügbar sein.

```bash
git add .
git commit -m "Beschreibung der Änderungen"
git push
```

### Schritt 2: Bash Console auf PythonAnywhere öffnen

Im PythonAnywhere Dashboard unter **Consoles** eine neue Bash Console öffnen.

### Schritt 3: Repository klonen

Beim ersten Deployment wird das Repository von GitHub geklont:

```bash
cd ~
git clone https://github.com/MihaHuzu/crm_projekt.git crm_app
cd crm_app
```

### Schritt 4: Abhängigkeiten installieren

Alle benötigten Python-Pakete werden installiert:

```bash
source /home/Mihaela/venv/bin/activate
pip install -r requirements.txt
```

Die `requirements.txt` enthält folgende Pakete:

```
Flask
Werkzeug
flask-restx
flask-login
flask-sqlalchemy
openpyxl
```

### Schritt 5: WSGI-Datei konfigurieren

PythonAnywhere verwendet eine WSGI-Konfigurationsdatei, um die Flask-Anwendung zu starten. Die Datei befindet sich unter `/var/www/mihaela_pythonanywhere_com_wsgi.py` und enthält folgenden Code:

```python
import sys
import os

# Projektpfad hinzufügen
path = '/home/Mihaela/crm_app'
if path not in sys.path:
    sys.path.insert(0, path)

os.chdir(path)

from app import app as application
```

**Erklärung:**
- `sys.path.insert` – teilt Python mit, wo sich der Projektcode befindet
- `os.chdir` – wechselt in das Projektverzeichnis
- `from app import app as application` – importiert die Flask-Anwendung

### Schritt 6: Web App neu starten

Im Tab **Web** auf PythonAnywhere den Button **Reload** drücken, um die Änderungen zu aktivieren.

---

## Updates deployen

Wenn Änderungen am Code vorgenommen wurden, müssen diese folgendermaßen auf PythonAnywhere übertragen werden:

```bash
# 1. Lokal: Code auf GitHub pushen
git add .
git commit -m "Update"
git push

# 2. Auf PythonAnywhere: Bash Console öffnen
cd /home/Mihaela/crm_app
git pull origin main

# 3. Web App neu laden (Tab "Web" → Reload)
```

---

## Konfiguration für die Produktionsumgebung

Für den produktiven Betrieb wurden folgende Anpassungen vorgenommen:

**Secret Key:** In der Produktionsumgebung sollte ein sicherer, zufälliger Schlüssel verwendet werden:
```python
app.secret_key = 'sicherer-zufälliger-schlüssel'
```

**Debug-Modus:** Der Debug-Modus ist in der Produktion deaktiviert, da er Sicherheitsrisiken birgt:
```python
app.run(debug=False)
```

**Datenbank:** Die SQLite-Datenbankdatei `crm.db` wird automatisch beim ersten Start erstellt und befindet sich im Verzeichnis `/home/Mihaela/crm_app/instance/`.

---

## Projektstruktur auf PythonAnywhere

```
/home/Mihaela/
├── crm_app/                    → Projektverzeichnis (von GitHub geklont)
│   ├── app.py                  → Hauptanwendung
│   ├── models.py               → Datenbankmodelle
│   ├── api.py                  → REST API
│   ├── export_import.py        → Export/Import
│   ├── requirements.txt        → Abhängigkeiten
│   ├── instance/
│   │   └── crm.db              → Datenbankdatei
│   ├── static/                 → CSS, JavaScript
│   └── templates/              → HTML-Templates
└── venv/                       → Virtuelle Python-Umgebung

/var/www/
└── mihaela_pythonanywhere_com_wsgi.py  → WSGI-Konfiguration
```

---

## Erreichbare URLs

| URL | Beschreibung |
|---|---|
| https://mihaela.pythonanywhere.com/login | Login-Seite |
| https://mihaela.pythonanywhere.com/customers | Kundenliste |
| https://mihaela.pythonanywhere.com/leads | Lead-Liste |
| https://mihaela.pythonanywhere.com/api/docs | Swagger API-Dokumentation |

---

## Fehlerbehebung

Falls die Anwendung nicht erreichbar ist, können die Log-Dateien auf PythonAnywhere eingesehen werden:

- **Error log:** Zeigt Python-Fehler und Import-Fehler
- **Server log:** Zeigt Server-Fehler
- **Access log:** Zeigt alle HTTP-Anfragen

Die Log-Dateien sind im Tab **Web** unter **Log files** erreichbar.

**Häufige Fehler:**

| Fehler | Ursache | Lösung |
|---|---|---|
| `ModuleNotFoundError` | Paket nicht installiert | `pip install paketname` |
| `500 Internal Server Error` | Fehler im Python-Code | Error log prüfen |
| `404 Not Found` | Route nicht gefunden | URL prüfen |

---

## Zugangsdaten (Testumgebung)

| Username | Passwort | Rolle |
|---|---|---|
| admin | admin123 | Administrator |
| user | user123 | Normaler Benutzer |
