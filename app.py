from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Customer, Lead, Contact
from api import create_api
from export_import import export_import

app = Flask(__name__)
app.secret_key = 'secretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'  # creeaza fisierul crm.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # leaga db-ul de aplicatie
app.register_blueprint(export_import)

# ---------------------------------------------------------------
# NOU: Configurare Flask-Login
# ---------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # daca nu esti logat, te trimite la /login
login_manager.login_message = 'You must be logged in to access this page.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    # Flask-Login apeleaza asta la fiecare request ca sa stie cine e logat
    return User.query.get(int(user_id))

# ---------------------------------------------------------------
# MODIFICAT: init_sample_data -> init_db
# Acum salveaza in baza de date, nu in liste Python
# ---------------------------------------------------------------
def init_db():
    with app.app_context():
        db.create_all()  # creeaza tabelele daca nu exista

        # adaugam date de test doar daca DB e goala
        if User.query.count() == 0:

            # cream userii
            admin = User(username='admin', email='admin@crm.com', role='admin')
            admin.set_password('admin123')

            user = User(username='user', email='user@crm.com', role='user')
            user.set_password('user123')

            db.session.add_all([admin, user])

            # cream clientii de test (la fel ca inainte, dar cu db.session)
            c1 = Customer(name='John Doe', email='john@example.com',
                          company='Acme Corp', phone='555-0001', status='active')
            c2 = Customer(name='Jane Smith', email='jane@example.com',
                          company='Tech Solutions', phone='555-0002', status='prospect')
            c3 = Customer(name='Bob Wilson', email='bob@example.com',
                          company='Global Industries', phone='555-0003', status='inactive')

            db.session.add_all([c1, c2, c3])

            # cream lead-urile de test
            l1 = Lead(name='Alice Brown', email='alice@example.com',
                      company='StartUp Inc', value=50000, source='Website')
            l2 = Lead(name='Charlie Davis', email='charlie@example.com',
                      company='Enterprise Ltd', value=100000, source='Referral')

            db.session.add_all([l1, l2])
            db.session.commit()  # salveaza totul in baza de date

            print('Database initialized!')
            print('Login: admin / admin123  or  user / user123')

# ---------------------------------------------------------------
# NOU: Rute pentru autentificare
# ---------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    # daca esti deja logat, mergi direct la dashboard
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # cautam userul in baza de date
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)  # salveaza userul in sesiune
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Wrong username or password!', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()  # sterge userul din sesiune
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    no_users_yet = User.query.count() == 0

    # blocam accesul daca nu esti admin (exceptie: primul user din sistem)
    if not no_users_yet:
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Only admins can create new accounts.', 'error')
            return redirect(url_for('login'))

    if request.method == 'POST':
        username         = request.form.get('username')
        email            = request.form.get('email')
        password         = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role             = request.form.get('role', 'user')

        # validari
        if not all([username, email, password, confirm_password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken!', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        # primul user devine automat admin
        if no_users_yet:
            role = 'admin'

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Account {username} created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------------------------------------------------------
# MODIFICAT: Rutele tale originale
# Singura schimbare: @login_required adaugat pe fiecare ruta
# + metodele folosesc acum SQLAlchemy in loc de liste
# ---------------------------------------------------------------

@app.route('/')
@login_required  # NOU: protejat
def index():
    # MODIFICAT: .count() in loc de len()
    total_customers = Customer.query.count()
    total_leads = Lead.query.count()
    return render_template('index.html',
                           total_customers=total_customers,
                           total_leads=total_leads)


@app.route('/customers')
@login_required  # NOU
def customers():
    # MODIFICAT: .query.all()
    return render_template('customers.html', customers=Customer.query.all())


@app.route('/customers/add', methods=['GET', 'POST'])
@login_required  # NOU
def add_customer():
    if request.method == 'POST':
        name    = request.form.get('name')
        email   = request.form.get('email')
        company = request.form.get('company')
        phone   = request.form.get('phone')
        status  = request.form.get('status', 'prospect')

        if not all([name, email, company, phone]):
            flash('All fields are required!', 'error')
            return redirect(url_for('add_customer'))

        # MODIFICAT: folosim db.session in loc de Customer.add_customer()
        new_customer = Customer(name=name, email=email,
                                company=company, phone=phone, status=status)
        db.session.add(new_customer)
        db.session.commit()

        flash(f'Customer {name} added successfully!', 'success')
        return redirect(url_for('customers'))
    return render_template('add_customer.html')


@app.route('/customers/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        flash('Customer not found!', 'error')
        return redirect(url_for('customers'))
    contacts = Contact.query.filter_by(customer_id=customer_id).all()  # NOU
    return render_template('customer_detail.html', 
                           customer=customer, contacts=contacts)  # NOU

@app.route('/customers/<int:customer_id>/contact/add', methods=['POST'])
@login_required
def add_contact(customer_id):
    contact_type = request.form.get('contact_type')
    notes = request.form.get('notes')
    if contact_type and notes:
        Contact.add_contact(customer_id, contact_type, notes)
        flash('Contact saved!', 'success')
    return redirect(url_for('customer_detail', customer_id=customer_id))


@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required  # NOU
def edit_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        flash('Customer not found!', 'error')
        return redirect(url_for('customers'))

    if request.method == 'POST':
        # MODIFICAT: modificam direct atributele si facem commit
        customer.name    = request.form.get('name')
        customer.email   = request.form.get('email')
        customer.company = request.form.get('company')
        customer.phone   = request.form.get('phone')
        customer.status  = request.form.get('status')
        db.session.commit()

        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customer_detail', customer_id=customer_id))

    return render_template('edit_customer.html', customer=customer)


@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required  # NOU
def delete_customer(customer_id):
    # NOU: doar adminii pot sterge
    if not current_user.is_admin():
        flash('You do not have permission to delete customers!', 'error')
        return redirect(url_for('customers'))

    customer = Customer.query.get(customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()

    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers'))


@app.route('/leads')
@login_required  # NOU
def leads():
    return render_template('leads.html', leads=Lead.query.all())


@app.route('/leads/add', methods=['GET', 'POST'])
@login_required  # NOU
def add_lead():
    if request.method == 'POST':
        name    = request.form.get('name')
        email   = request.form.get('email')
        company = request.form.get('company')
        value   = request.form.get('value')
        source  = request.form.get('source')

        if not all([name, email, company, value, source]):
            flash('All fields are required!', 'error')
            return redirect(url_for('add_lead'))

        try:
            # MODIFICAT: folosim db.session in loc de Lead.add_lead()
            new_lead = Lead(name=name, email=email, company=company,
                            value=float(value), source=source)
            db.session.add(new_lead)
            db.session.commit()
            flash(f'Lead {name} added successfully!', 'success')
        except ValueError:
            flash('Deal value must be a number!', 'error')

        return redirect(url_for('leads'))
    return render_template('add_lead.html')


@app.route('/leads/<int:lead_id>')
@login_required  # NOU
def lead_detail(lead_id):
    lead = Lead.query.get(lead_id)
    if not lead:
        flash('Lead not found!', 'error')
        return redirect(url_for('leads'))
    return render_template('lead_detail.html', lead=lead)


@app.route('/leads/<int:lead_id>/delete', methods=['POST'])
@login_required  # NOU
def delete_lead(lead_id):
    # NOU: doar adminii pot sterge
    if not current_user.is_admin():
        flash('You do not have permission to delete leads!', 'error')
        return redirect(url_for('leads'))

    lead = Lead.query.get(lead_id)
    if lead:
        db.session.delete(lead)
        db.session.commit()

    flash('Lead deleted successfully!', 'success')
    return redirect(url_for('leads'))


# ---------------------------------------------------------------
# Neschimbat: Error handlers
# ---------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# ---------------------------------------------------------------
# MODIFICAT: init_sample_data() -> init_db()
# ---------------------------------------------------------------
create_api(app)
if __name__ == '__main__':
    init_db()  
    app.run(debug=True, host='127.0.0.1', port=5000)