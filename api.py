# api.py
# Alle REST API Routen - getrennt von app.py

from flask import request
from flask_restx import Api, Resource, fields
from flask_login import login_required, current_user
from models import db, Customer, Lead, Contact

# ---------------------------------------------------------------
# Funktion, die die API in der Flask-Anwendung registriert
# Wird von app.py aufgerufen
# ---------------------------------------------------------------

def create_api(app):
    """
    Erstellt und konfiguriert die API.
    Empfängt die Flask-Anwendung und fügt die API-Routen hinzu.
    """

    api = Api(
        app,
        version='1.0',
        title='CRM API',
        description='REST API für das CRM System',
        doc='/api/docs'  # Swagger-Dokumentation ist unter dieser Adresse erreichbar
    )

    # ---------------------------------------------------------------
    # NAMESPACE
    # Ein Namespace ist eine Gruppe zusammengehöriger Routen
    # Ähnlich wie ein Blueprint in Flask
    # ---------------------------------------------------------------

    customers_ns = api.namespace('api/customers', description='Kunden-Operationen')
    leads_ns     = api.namespace('api/leads',     description='Lead-Operationen')
    contacts_ns  = api.namespace('api/contacts',  description='Kontakt-Operationen')

    # ---------------------------------------------------------------
    # MODELLE - definieren die JSON-Struktur
    # Werden von Swagger für die Dokumentation verwendet
    # ---------------------------------------------------------------

    # Modell für Customer - welche Felder hat ein Kunde im JSON
    customer_model = api.model('Customer', {
        'id':         fields.Integer(description='Eindeutige ID'),
        'name':       fields.String(required=True, description='Name des Kunden'),
        'email':      fields.String(required=True, description='E-Mail'),
        'company':    fields.String(required=True, description='Unternehmen'),
        'phone':      fields.String(required=True, description='Telefon'),
        'status':     fields.String(description='Status: prospect/active/inactive'),
        'created_at': fields.String(description='Erstellungsdatum')
    })

    # Modell für Lead
    lead_model = api.model('Lead', {
        'id':      fields.Integer(description='Eindeutige ID'),
        'name':    fields.String(required=True, description='Name'),
        'email':   fields.String(required=True, description='E-Mail'),
        'company': fields.String(required=True, description='Unternehmen'),
        'value':   fields.Float(description='Deal-Wert'),
        'source':  fields.String(description='Lead-Quelle'),
        'status':  fields.String(description='Status: new/contacted/qualified/lost')
    })

    # Modell für Contact
    contact_model = api.model('Contact', {
        'id':           fields.Integer(description='Eindeutige ID'),
        'customer_id':  fields.Integer(required=True, description='Kunden-ID'),
        'contact_type': fields.String(required=True, description='Typ: phone/email/meeting/note'),
        'notes':        fields.String(required=True, description='Notizen'),
        'date':         fields.String(description='Kontaktdatum')
    })

    # ---------------------------------------------------------------
    # Hilfsfunktionen - wandeln ein Objekt in ein Dictionary um
    # ---------------------------------------------------------------

    def customer_to_dict(c):
        return {
            'id':         c.id,
            'name':       c.name,
            'email':      c.email,
            'company':    c.company,
            'phone':      c.phone,
            'status':     c.status,
            'created_at': str(c.created_at)
        }

    def lead_to_dict(l):
        return {
            'id':      l.id,
            'name':    l.name,
            'email':   l.email,
            'company': l.company,
            'value':   l.value,
            'source':  l.source,
            'status':  l.status
        }

    def contact_to_dict(c):
        return {
            'id':           c.id,
            'customer_id':  c.customer_id,
            'contact_type': c.contact_type,
            'notes':        c.notes,
            'date':         str(c.date)
        }

    # ---------------------------------------------------------------
    # CUSTOMER ENDPUNKTE
    # ---------------------------------------------------------------

    @customers_ns.route('/')
    class CustomerList(Resource):
        """Route für /api/customers/"""

        @customers_ns.doc('list_customers')
        @customers_ns.marshal_list_with(customer_model)
        def get(self):
            """Gibt alle Kunden zurück - GET /api/customers/"""
            customers = Customer.query.all()
            return [customer_to_dict(c) for c in customers]

        @customers_ns.doc('create_customer')
        @customers_ns.marshal_with(customer_model, code=201)
        def post(self):
            """Fügt einen neuen Kunden hinzu - POST /api/customers/"""
            data = request.get_json()

            # Validierung
            if not data:
                api.abort(400, 'Keine Daten übermittelt')

            required = ['name', 'email', 'company', 'phone']
            for field in required:
                if field not in data:
                    api.abort(400, f'Feld {field} ist erforderlich')

            # Prüfen ob E-Mail bereits existiert
            if Customer.query.filter_by(email=data['email']).first():
                api.abort(400, 'E-Mail existiert bereits')

            # Kunden erstellen
            new_customer = Customer(
                name=data['name'],
                email=data['email'],
                company=data['company'],
                phone=data['phone'],
                status=data.get('status', 'prospect')
            )
            db.session.add(new_customer)
            db.session.commit()

            return customer_to_dict(new_customer), 201


    @customers_ns.route('/<int:customer_id>')
    class CustomerDetail(Resource):
        """Route für /api/customers/<id>"""

        @customers_ns.doc('get_customer')
        @customers_ns.marshal_with(customer_model)
        def get(self, customer_id):
            """Gibt einen Kunden nach ID zurück - GET /api/customers/1"""
            customer = Customer.query.get(customer_id)
            if not customer:
                api.abort(404, 'Kunde nicht gefunden')
            return customer_to_dict(customer)

        @customers_ns.doc('update_customer')
        @customers_ns.marshal_with(customer_model)
        def put(self, customer_id):
            """Aktualisiert einen Kunden - PUT /api/customers/1"""
            customer = Customer.query.get(customer_id)
            if not customer:
                api.abort(404, 'Kunde nicht gefunden')

            data = request.get_json()
            if not data:
                api.abort(400, 'Keine Daten übermittelt')

            # Nur die übermittelten Felder aktualisieren
            if 'name'    in data: customer.name    = data['name']
            if 'email'   in data: customer.email   = data['email']
            if 'company' in data: customer.company = data['company']
            if 'phone'   in data: customer.phone   = data['phone']
            if 'status'  in data: customer.status  = data['status']

            db.session.commit()
            return customer_to_dict(customer)

        @customers_ns.doc('delete_customer')
        def delete(self, customer_id):
            """Löscht einen Kunden - DELETE /api/customers/1"""
            customer = Customer.query.get(customer_id)
            if not customer:
                api.abort(404, 'Kunde nicht gefunden')

            db.session.delete(customer)
            db.session.commit()
            return {'message': 'Kunde wurde gelöscht'}, 200


    # ---------------------------------------------------------------
    # LEAD ENDPUNKTE
    # ---------------------------------------------------------------

    @leads_ns.route('/')
    class LeadList(Resource):

        @leads_ns.marshal_list_with(lead_model)
        def get(self):
            """Gibt alle Leads zurück - GET /api/leads/"""
            return [lead_to_dict(l) for l in Lead.query.all()]

        @leads_ns.marshal_with(lead_model, code=201)
        def post(self):
            """Fügt einen neuen Lead hinzu - POST /api/leads/"""
            data = request.get_json()
            if not data:
                api.abort(400, 'Keine Daten übermittelt')

            required = ['name', 'email', 'company', 'source']
            for field in required:
                if field not in data:
                    api.abort(400, f'Feld {field} ist erforderlich')

            new_lead = Lead(
                name=data['name'],
                email=data['email'],
                company=data['company'],
                value=data.get('value', 0.0),
                source=data['source']
            )
            db.session.add(new_lead)
            db.session.commit()
            return lead_to_dict(new_lead), 201


    @leads_ns.route('/<int:lead_id>')
    class LeadDetail(Resource):

        @leads_ns.marshal_with(lead_model)
        def get(self, lead_id):
            """Gibt einen Lead nach ID zurück - GET /api/leads/1"""
            lead = Lead.query.get(lead_id)
            if not lead:
                api.abort(404, 'Lead nicht gefunden')
            return lead_to_dict(lead)

        def delete(self, lead_id):
            """Löscht einen Lead - DELETE /api/leads/1"""
            lead = Lead.query.get(lead_id)
            if not lead:
                api.abort(404, 'Lead nicht gefunden')
            db.session.delete(lead)
            db.session.commit()
            return {'message': 'Lead wurde gelöscht'}, 200


    # ---------------------------------------------------------------
    # KONTAKT ENDPUNKTE
    # ---------------------------------------------------------------

    @contacts_ns.route('/customer/<int:customer_id>')
    class ContactList(Resource):

        @contacts_ns.marshal_list_with(contact_model)
        def get(self, customer_id):
            """Gibt alle Kontakte eines Kunden zurück - GET /api/contacts/customer/1"""
            contacts = Contact.query.filter_by(customer_id=customer_id).all()
            return [contact_to_dict(c) for c in contacts]

        @contacts_ns.marshal_with(contact_model, code=201)
        def post(self, customer_id):
            """Fügt einen Kontakt hinzu - POST /api/contacts/customer/1"""
            data = request.get_json()
            if not data:
                api.abort(400, 'Keine Daten übermittelt')

            required = ['contact_type', 'notes']
            for field in required:
                if field not in data:
                    api.abort(400, f'Feld {field} ist erforderlich')

            new_contact = Contact(
                customer_id=customer_id,
                contact_type=data['contact_type'],
                notes=data['notes']
            )
            db.session.add(new_contact)
            db.session.commit()
            return contact_to_dict(new_contact), 201

    return api