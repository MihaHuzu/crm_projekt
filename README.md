# Flask CRM System

## Description
This project is a CRM system developed for the  course.

## Features
1   | **Datenbankintegration (SQLite)**  | Migration von In-Memory auf SQLite mit Flask-SQLAlchemy; persistente Speicherung aller Entitäten                        | ⭐⭐             |
| 2   | **User Authentication**            | Login/Logout mit Flask-Login; Registrierung, Passwort-Hashing, Session-Management, rollenbasierter Zugriff (Admin/User) | ⭐⭐⭐            |
| 3   | **REST-API**                       | JSON-basierte API-Endpunkte für alle CRUD-Operationen; API-Dokumentation (z. B. Swagger/OpenAPI)                        | ⭐⭐⭐            |

Erweiterung
5   | **CSV/Excel Export & Import**      | Datenexport als CSV/Excel; Import-Funktion mit Validierung; Berichterstellung                                           | ⭐⭐             |
## Setup

1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python app.py`
5. Visit http://127.0.0.1:5000
