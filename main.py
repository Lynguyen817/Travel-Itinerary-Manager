import os
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from datamanager.sqlite_data_manager import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_babel import Babel
import secrets
import string
import logging
import requests

app = Flask(__name__, template_folder='templates')
bootstrap = Bootstrap(app)
babel = Babel(app)

app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logging.StreamHandler())

babel_logger = logging.getLogger('flask_babel')
babel_logger.setLevel(logging.DEBUG)
babel_logger.addHandler(logging.StreamHandler())

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelItineraries.db'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(app.root_path, 'translations')
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'it': 'Italian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ru': 'Russian'
}


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


@app.before_request
def before_request():
    # Set the language for each request based on the session
    session_language = session.get('language', 'en')
    babel.locale = session_language
    print("Session Language:", session_language)


@app.context_processor
def utility_processor():
    def get_user_locale():
        # Get the language from the session, or use the default language
        return session.get('language', 'en')

    # Return a dictionary containing the functions to make it available in templates
    return dict(get_user_locale=get_user_locale)


@app.route('/set_language/<language>')
def set_language(language):
    # Store the selected language in the session
    session['language'] = language
    print("Session data after setting language:", session)
    print("Referrer URL", request.referrer)

    return redirect(request.referrer or url_for('index'))

#
# @app.route('/')
# def translate():
#     text_to_translate = request.args.get('text', default='', type=str)
#     target_language = request.args.get('target_language', default='', type=str)
#
#     if text_to_translate and target_language:
#         API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
#         url = url_for('translate', _external=True, text=text_to_translate,target_language=target_language)
#         #url = f'https://translation.googleapis.com/language/translate/v2?key={API_KEY}&q={text_to_translate}&target={target_language}'
#
#         translated_text = translate_text(text_to_translate, target_language, API_KEY, url)
#         if translated_text:
#             return f"Translated text: {translated_text}"
#         else:
#             return "Translation request failed", 500
#     else:
#         return "Please provide text and target_language parameters", 400
#
#
# def translate_text(text, target_language, API_KEY, url):
#     params = {
#         'key': API_KEY,
#         'q': text,
#         'target': target_language
#     }
#     response = requests.post(url, params=params)
#     if response.status_code == 200:
#         translated_text = response.json()['data']['translations'][0]['translatedText']
#         return translated_text
#     else:
#         print(f"Translation request failed: {response.text}")
#         return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Returns homepage, alerts error when it's not open."""
    print("Session data in index route:", session)
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

        return redirect(url_for('login'))
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
    try:
        list_of_destinations = data_manager.get_destinations(current_user.id)
        if list_of_destinations is None:
            list_of_destinations = []

        # Retrieve the current user
        user = current_user

        # Iterate through destinations and replace newline characters with <br> tags
        for destination in list_of_destinations:
            destination.activities = destination.activities.replace("\n", "<br>")
            destination.accommodations = destination.accommodations.replace("\n", "<br>")
            destination.transportation = destination.transportation.replace("\n", "<br>")

        return render_template('user_destinations.html', user=user, list_of_destinations=list_of_destinations)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 500


@app.route('/add_destination', methods=['GET', 'POST'])
@login_required
def add_destination():
    """Search for a destination and add it to a user's favorite destination list."""
    if request.method == 'POST':
        # Print out the form data to inspect it
        print("From Data:", request.form)

        # Extract the destination data from the form
        destination_data = {
            'des_name': request.form['des_name'],
            'poster_url': request.form['poster_url'],
            'activities': request.form['activities'],
            'accommodations': request.form['accommodations'],
            'transportation': request.form['transportation']
        }

        if not destination_data['des_name']:
            return "Please provide a destination.", 400

        data_manager.add_destination(current_user.id, destination_data)
        return redirect(url_for('get_destinations'))

    # It's GET method
    return render_template('add_destination.html', user_id=current_user.id)


@app.route('/delete_destination/<int:user_id>/<int:destination_id>', methods=['GET', 'POST'])
@login_required
def delete_destination(user_id, destination_id):
    """Delete a destination from the user's favorite list."""
    try:
        if request.method == 'POST':
            deleted = data_manager.delete_destination(user_id, destination_id)
            if deleted:
                # After deleting, redirect to the get_destinations route
                print("Redirecting to get_destinations route")
                return redirect(url_for('get_destinations'))
            else:
                print("Destination not found.")
                return "Destination not found", 404
    except Exception as e:
        print(f"An error occurred:")
        return f"An error occurred: {str(e)}", 500


@app.route('/update_destination/<int:destination_id>', methods=['GET', 'POST'])
@login_required
def update_destination(destination_id):
    print(f"Updating destination with ID: {destination_id}")

    # Fetch the destination by user ID and destination ID
    destination = data_manager.get_destination_by_id(destination_id)
    if not destination:
        return jsonify({'message': "Destination not found."}), 404

    if request.method == 'POST':
        print("Form data:", request.form)

        # Check if the form data is empty
        if not request.form:
            print("No data received from the form.")
        else:
            print("Received form data.")

        # Extract updated data from the form
        updated_data = {
            'poster_url': request.form.get('poster_url', '').strip(),
            'activities': request.form.get('activities', '').strip(),
            'accommodations': request.form.get('accommodations', '').strip(),
            'transportation': request.form.get('transportation', '').strip()
        }

        print("Updated data:", updated_data)

        if not updated_data['poster_url']:
            print("New Poster URL is empty.")
            return "New Poster URL cannot be empty.", 400

        try:
            updated = data_manager.update_destination(destination_id, updated_data)
            if updated:
                return redirect(url_for('get_destinations'))
            else:
                return "Failed to update destination.", 404
        except ValueError as e:
            return str(e), 400

    return render_template('update_destination.html', destination=destination)


if __name__ == "__main__":
    app.run(debug=True)






