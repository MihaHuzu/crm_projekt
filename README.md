# Flask CRM System

## Projektbeschreibung

Dieses Projekt ist ein **Customer Relationship Management (CRM) System**, das mit dem Python-Framework **Flask** entwickelt wurde. Es ermöglicht die Verwaltung von Kunden, Leads und Kontakthistorien. Das Projekt wurde im Rahmen des SWPOMO-Kurses entwickelt und umfasst vier Sprints.

---

## Projektstruktur

```
crm_init/
├── app.py                  → Hauptanwendung (Controller, Routen)
├── models.py               → Datenbankmodelle (SQLAlchemy)
├── api.py                  → REST API Endpunkte (Flask-RESTX)
├── export_import.py        → CSV/Excel Export & Import
├── requirements.txt        → Abhängigkeiten
├── instance/
│   └── crm.db              → SQLite Datenbankdatei (automatisch erstellt)
├── static/
│   ├── css/style.css       → Styling
│   └── js/script.js        → JavaScript
└── templates/
    ├── base.html           → Grundgerüst (Navbar, Flash-Nachrichten)
    ├── index.html          → Dashboard
    ├── login.html          → Login-Seite
    ├── register.html       → Registrierungsseite
    ├── customers.html      → Kundenliste
    ├── customer_detail.html→ Kundendetails & Kontakthistorie
    ├── add_customer.html   → Kunde hinzufügen
    ├── edit_customer.html  → Kunde bearbeiten
    ├── leads.html          → Lead-Liste
    ├── lead_detail.html    → Lead-Details
    ├── add_lead.html       → Lead hinzufügen
    ├── import.html         → Import-Seite
    ├── 404.html            → Fehlerseite 404
    └── 500.html            → Fehlerseite 500
```

---

## Architektur: MVC-Muster

Das Projekt folgt dem **Model-View-Controller (MVC)** Muster:

| Schicht | Datei | Beschreibung |
|---|---|---|
| **Model** | `models.py` | Datenbankstruktur (User, Customer, Lead, Contact) |
| **View** | `templates/` | HTML-Templates mit Jinja2 |
| **Controller** | `app.py` | Routen, Logik, Request-Verarbeitung |

---

## Features

### Feature 1: SQLite Datenbankintegration ⭐⭐

Migration von In-Memory-Speicherung (Python-Listen) auf eine persistente SQLite-Datenbank mit Flask-SQLAlchemy.

**Was wurde implementiert:**
- Alle Entitäten (Customer, Lead, Contact) als SQLAlchemy-Modelle
- Persistente Datenspeicherung in `crm.db`
- CRUD-Operationen über `db.session`
- Automatische Tabellenerstellung beim ersten Start

**Technologie:** Flask-SQLAlchemy, SQLite

---

### Feature 2: Benutzerauthentifizierung ⭐⭐⭐

Vollständiges Login/Logout-System mit rollenbasiertem Zugriff.

**Was wurde implementiert:**
- Login und Logout mit Flask-Login
- Passwort-Hashing mit Werkzeug (keine Klartextpasswörter)
- Session-Management (Cookie-basiert)
- Zwei Rollen: `admin` und `user`
- `@login_required` Decorator auf allen Routen
- Admin kann neue Benutzer registrieren

**Zugangsdaten für Tests:**

| Username | Passwort | Rolle |
|---|---|---|
| admin | admin123 | Administrator |
| user | user123 | Normaler Benutzer |

**Rollenunterschiede:**

| Aktion | Admin | User |
|---|---|---|
| Kunden anzeigen | ✅ | ✅ |
| Kunden hinzufügen | ✅ | ✅ |
| Kunden bearbeiten | ✅ | ✅ |
| Kunden löschen | ✅ | ❌ |
| Neue Benutzer erstellen | ✅ | ❌ |

**Technologie:** Flask-Login, Werkzeug Security

---

### Feature 3: REST API ⭐⭐⭐

JSON-basierte API-Endpunkte für alle CRUD-Operationen mit automatischer Swagger-Dokumentation.

**Endpunkte:**

| Method | URL | Beschreibung |
|---|---|---|
| GET | `/api/customers/` | Alle Kunden abrufen |
| POST | `/api/customers/` | Neuen Kunden erstellen |
| GET | `/api/customers/{id}` | Einen Kunden abrufen |
| PUT | `/api/customers/{id}` | Kunden aktualisieren |
| DELETE | `/api/customers/{id}` | Kunden löschen |
| GET | `/api/leads/` | Alle Leads abrufen |
| POST | `/api/leads/` | Neuen Lead erstellen |
| GET | `/api/leads/{id}` | Einen Lead abrufen |
| DELETE | `/api/leads/{id}` | Lead löschen |
| GET | `/api/contacts/customer/{id}` | Kontakte eines Kunden |
| POST | `/api/contacts/customer/{id}` | Kontakt hinzufügen |

**Swagger-Dokumentation:** `http://127.0.0.1:5000/api/docs`

**Technologie:** Flask-RESTX, Swagger/OpenAPI

---

### Erweiterung: CSV/Excel Export & Import ⭐⭐

Export und Import von Kundendaten als CSV- oder Excel-Datei.

**Was wurde implementiert:**
- Export aller Kunden als `.csv`
- Export aller Kunden als `.xlsx` (mit formatierter Kopfzeile)
- Import von Kunden aus `.csv` oder `.xlsx`
- Validierung beim Import (Pflichtfelder, E-Mail-Format, Duplikaterkennung)

**Export-Format (Spalten):**
```
id, name, email, company, phone, status, created_at
```

**Import-Format (Pflichtfelder):**
```
name, email, company, phone, status
```

**Zugang:** Customers-Seite → Buttons "Export CSV" / "Export Excel" / "Import"

**Technologie:** Python csv-Modul, openpyxl

---

## Datenbankstruktur (ERD)

```
users
├── id (PK)
├── username (unique)
├── email (unique)
├── password_hash
├── role (admin/user)
└── created_at

customers
├── id (PK)
├── name
├── email (unique)
├── company
├── phone
├── status (prospect/active/inactive)
└── created_at

leads
├── id (PK)
├── name
├── email
├── company
├── value
├── source
├── status (new/contacted/qualified/lost)
└── created_at

contacts
├── id (PK)
├── customer_id (FK → customers.id)
├── contact_type (phone/email/meeting/note)
├── notes
└── date
```

---

## Setup & Installation

### Voraussetzungen
- Python 3.10+
- Git

### Installation

**1. Repository klonen:**
```bash
git clone https://github.com/MihaHuzu/crm_projekt.git
cd crm_projekt
```

**2. Virtuelle Umgebung erstellen:**
```bash
python -m venv venv
```

**3. Virtuelle Umgebung aktivieren:**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

**4. Abhängigkeiten installieren:**
```bash
pip install -r requirements.txt
```

**5. Anwendung starten:**
```bash
python app.py
```

**6. Im Browser öffnen:**
```
http://127.0.0.1:5000/login
```

---

## Verwendete Technologien

| Technologie | Version | Zweck |
|---|---|---|
| Python | 3.10+ | Programmiersprache |
| Flask | 3.x | Web-Framework |
| Flask-SQLAlchemy | 3.x | Datenbankanbindung |
| Flask-Login | 0.6.x | Authentifizierung |
| Flask-RESTX | 1.x | REST API + Swagger |
| Werkzeug | 3.x | Passwort-Hashing |
| openpyxl | 3.x | Excel Export/Import |
| SQLite | built-in | Datenbank |
| Jinja2 | built-in | HTML-Templates |

---

## Deployment (Lokal)

Die Anwendung läuft lokal auf `http://127.0.0.1:5000`. Für eine produktive Umgebung müssen folgende Änderungen vorgenommen werden:

**1. Secret Key ändern** (in `app.py`):
```python
app.secret_key = 'sicherer-zufälliger-schlüssel'
```

**2. Debug-Modus deaktivieren** (in `app.py`):
```python
app.run(debug=False)
```

**3. `.gitignore` sicherstellen:**
```
instance/
*.db
__pycache__/
venv/
```

---

## Sprint-Übersicht

| Sprint | Fokus | Deliverables |
|---|---|---|
| Sprint 0 | Setup & Planning | Jira eingerichtet, GitHub Repo geklont |
| Sprint 1 | Requirements & Design | Use-Case-Diagramm, ERD, Sequenzdiagramm |
| Sprint 2 | Implementierung Kern | SQLite + Authentication implementiert |
| Sprint 3 | Erweiterung & Finalisierung | REST API, CSV/Excel Export/Import, Dokumentation |

---

## Testdaten

Nach dem ersten Start werden automatisch Testdaten angelegt:

**Kunden:** John Doe, Jane Smith, Bob Wilson

**Leads:** Alice Brown, Charlie Davis

**Login:** `admin / admin123` oder `user / user123`
