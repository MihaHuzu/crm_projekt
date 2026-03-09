from flask_sqlalchemy import SQLAlchemy   
from flask_login import UserMixin         
from werkzeug.security import generate_password_hash, check_password_hash  
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

 
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  
    role          = db.Column(db.String(20), default='user')   
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Customer(db.Model):
    __tablename__ = 'customers'


    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    company    = db.Column(db.String(100), nullable=False)
    phone      = db.Column(db.String(50), nullable=False)
    status     = db.Column(db.String(20), default='prospect')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contacts = db.relationship(
        'Contact',
        backref='customer',
        cascade='all, delete-orphan',
        lazy=True
    )

    def __init__(self, name, email, company, phone, status="prospect"):
        self.name = name
        self.email = email
        self.company = company
        self.phone = phone
        self.status = status

    @classmethod
    def add_customer(cls, name, email, company, phone, status="prospect"):
        customer = cls(name=name, email=email,
                       company=company, phone=phone, status=status)
        db.session.add(customer)
        db.session.commit()
        return customer

    @classmethod
    def get_all_customers(cls):
        return cls.query.all()

    @classmethod
    def get_customer_by_id(cls, customer_id):
        return cls.query.get(customer_id)

    @classmethod
    def update_customer(cls, customer_id, name, email, company, phone, status):
        customer = cls.get_customer_by_id(customer_id)
        if customer:
            customer.name    = name
            customer.email   = email
            customer.company = company
            customer.phone   = phone
            customer.status  = status
            db.session.commit()   
            return True
        return False

    @classmethod
    def delete_customer(cls, customer_id):
        customer = cls.get_customer_by_id(customer_id)
        if customer:
            db.session.delete(customer)
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<Customer {self.id}: {self.name} ({self.company})>'

class Lead(db.Model):
    __tablename__ = 'leads'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    company    = db.Column(db.String(100), nullable=False)
    value      = db.Column(db.Float, default=0.0)
    source     = db.Column(db.String(50), nullable=False)
    status     = db.Column(db.String(20), default='new') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def add_lead(cls, name, email, company, value, source):
        lead = cls(name=name, email=email,
                   company=company, value=value, source=source)
        db.session.add(lead)
        db.session.commit()
        return lead

    @classmethod
    def get_all_leads(cls):
        return cls.query.all()

    @classmethod
    def get_lead_by_id(cls, lead_id):
        return cls.query.get(lead_id)

    @classmethod
    def delete_lead(cls, lead_id):
        lead = cls.get_lead_by_id(lead_id)
        if lead:
            db.session.delete(lead)
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<Lead {self.id}: {self.name} (€{self.value})>'

class Contact(db.Model):
    """Istoricul interactiunilor cu un client"""

    __tablename__ = 'contacts'

    id           = db.Column(db.Integer, primary_key=True)
    customer_id  = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    contact_type = db.Column(db.String(50), nullable=False)   
    notes        = db.Column(db.Text, nullable=False)
    date         = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def add_contact(cls, customer_id, contact_type, notes):
        contact = cls(customer_id=customer_id,
                      contact_type=contact_type,
                      notes=notes)
        db.session.add(contact)
        db.session.commit()
        return contact

    @classmethod
    def get_contacts_by_customer(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id).all()

    def __repr__(self):
        return f'<Contact {self.id}: {self.contact_type}>'
