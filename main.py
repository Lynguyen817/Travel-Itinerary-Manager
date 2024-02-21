from flask import Flask, jsonify, request, render_template, redirect, url_for
#from flask_bootstrap import Bootstrap
from datamanager.sqlite_data_manager import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import secrets
import string

app = Flask(__name__, template_folder='templates')
#bootstrap = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelItineraries.db'

db.init_app(app)
with app.app_context():
    db.create_all()

data_manager = SQLiteDataManager(db)
login_manager = LoginManager(app)

activities = []
accommodations = []
transportation = []


def generate_secret_key(length=32):
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


secret_key = generate_secret_key()
print("Generated secret key:", secret_key)

app.secret_key = secret_key


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Returns homepage, alerts error when it's not open."""
    try:
        return render_template("index.html", activities=activities, accommodations=accommodations, transportation=transportation, current_user=current_user)
    except Exception as e:
        return str(e)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully.'})
    else:
        # If it's a GET request, render the register page
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
    else:
        # If it's a GET request, render the login page
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/get_destinations')
@login_required
def get_destinations():
    """Return a list of destinations for a given user_id."""
    list_of_destinations = data_manager.get_destinations(current_user.id)
    if list_of_destinations is None:
        list_of_destinations = []

    return render_template('user_destinations.html', user_id=current_user.id, list_of_destinations=list_of_destinations)


@app.route('/add_destination', methods=['GET', 'POST'])
@login_required
def add_destination():
    """Search for a destination and add it to a user's favorite destination list."""
    if request.method == 'POST':
        data = request.get_json()
        destination_data = {
            'des_name': data['des_name'],
            'poster_url': data['poster_url'],
            'activities': data['activities'],
            'accommodations': data['accommodations'],
            'transportation': data['transportation']
        }

        if not destination_data['des_name']:
            return "Please provide a destination.", 400

        data_manager.add_destination(current_user.id, destination_data)
        return redirect(url_for('get_destinations'))

    # It's GET method
    return render_template('add_destination.html', user_id=current_user.id)


@app.route('/delete_destination/<destination_id>', methods=['GET', 'POST'])
@login_required
def delete_destination(user_id, destination_id):
    """Delete a destination from the user's favorite list."""
    if request.method == 'POST':
        deleted = data_manager.delete_destination(user_id, destination_id)
        if deleted:
            return redirect(url_for('user_destinations', user_id=user_id))
        else:
            return "Destination not found"

    # Get the destination data
    list_of_destinations = data_manager.get_destinations(user_id)
    destination = next((d for d in list_of_destinations if d.id == int(destination_id)), None)

    if not destination:
        return "Destination not found."

    # It's GET request, render the delete page
    return render_template('delete_destination.html', user_id=user_id)


@app.route('/update_destination/<destination_id>', methods=['GET', 'POST'])
@login_required
def update_destination(destination_id):
    if request.method == 'POST':
        new_poster = request.form.get('new_poster')
        new_activities = request.form.get('new_activities')
        new_accommodations = request.form.get('new_accommodations')
        new_transportation = request.form.get('new_transportation')

        updated = data_manager.update_destination(
            current_user.id, destination_id, new_poster, new_activities, new_accommodations, new_transportation
        )
        if updated:
            return redirect(url_for('get_destinations'))
        else:
            return "Destination not found", 400

    return render_template('update_destination.html', user_id=current_user.id, destination_id=destination_id)


if __name__ == "__main__":
    app.run(debug=True)




# @app.route('/api/activities', methods=['GET', 'POST'])
# def handle_activities():
#     """Returns activities."""
#     if request.method == 'GET':
#         return jsonify({'activities': activities})
#     elif request.method == 'POST':
#         new_activity = request.get_json()
#         activities.append(new_activity)
#         return jsonify({'message': 'Activity added successfully'})

