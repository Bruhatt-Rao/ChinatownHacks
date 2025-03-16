from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
import classifier.run as run
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
from database import Database

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64MB max file size
app.config['MAX_CONTENT_PATH'] = None
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'}

# Initialize database with connection string if available
db = Database("postgresql://neondb_owner:npg_UkJXC78uynDd@ep-rapid-glitter-a5o753p5-pooler.us-east-2.aws.neon.tech/neondb")

login_manager = LoginManager(app)
login_manager.login_view = 'login'

GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

# Create uploads directory if it doesn't exist
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(user_id)
    return User(user_data) if user_data else None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/applied', methods=['GET', 'POST'])
def applied():
    if request.method == 'POST':
        try:
            data = dict(request.form)
            name = data.pop("restaurant_name")
            
            # Convert numeric fields to appropriate types
            numeric_fields = {
                'Years in Business': int,
                'Annual Revenue (3 Years Ago)': float,
                'Annual Revenue (2 Years Ago)': float,
                'Annual Revenue (Last Year)': float,
                'Review Rating': float,
                'Number of Reviews': int,
                'Social Media Followers': int,
                'Competitor Density': int,
                'Lease Price': float
            }
            
            # Convert string values to numbers
            for field, convert_type in numeric_fields.items():
                if field in data:
                    try:
                        data[field] = convert_type(data[field])
                    except ValueError:
                        flash(f'Invalid value for {field}. Please enter a valid number.')
                        return redirect(url_for('apply_now'))
            
            score = run.predict_from_dict(data)
            print(score)
            return render_template('prediction_result.html', 
                                restaurant_name=name, 
                                score=score)
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('apply_now'))
        except Exception as e:
            print(e)
            flash('An error occurred while processing your application.')
            return redirect(url_for('apply_now'))

    if request.method == 'GET':
        return render_template('apply_now.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = db.verify_password(username, password)
        if user_data:
            user = User(user_data)
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if db.get_user_by_username(username):
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        if db.get_user_by_email(email):
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user_id = db.create_user(username, email, password)
        if user_id:
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        else:
            flash('Error creating user')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/restaurants')
def restaurants():
    if not current_user.is_authenticated:
        flash('Please sign up to view restaurants')
        return redirect(url_for('signup'))
    return render_template('businesses.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if not current_user.is_authenticated:
        flash('Please sign up to submit an application')
        return redirect(url_for('signup'))
    return render_template('apply.html')

@app.route('/apply_now', methods=['GET', 'POST'])
def apply_now():
    return render_template('apply_now.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_size(file):
    # Check if file size is under 64MB
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    return size <= app.config['MAX_CONTENT_LENGTH']

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'GET':
        return render_template('analyze.html')
    
    # try:
    #     if 'file' not in request.files:
    #         return jsonify({'error': 'No file uploaded'}), 400
        
    #     file = request.files['file']
    #     if file.filename == '':
    #         return jsonify({'error': 'No file selected'}), 400
            
    #     if not allowed_file(file.filename):
    #         return jsonify({'error': 'File type not allowed'}), 400

        # try:
            # Create a unique filename to avoid conflicts
            # filename = secure_filename(file.filename)
            # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            # unique_filename = timestamp + filename
            
            # # Ensure the full path to the file
            # temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # # Debug print
            # print(f"Saving file to: {temp_path}")
            
            # # Make sure the directory exists
            # os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            # # Save the file
            # file.save(temp_path)
            
            # if not os.path.exists(temp_path):
            #     raise Exception(f"File failed to save at {temp_path}")

            # Return test data for now
    test_data = {
                'identified_name': 'Golden Palace Restaurant',
                'has_info': True,
                'restaurant_info': {
                    'result': {
                        'name': 'Golden Palace Restaurant',
                        'formatted_address': '123 Chinatown Street, New York, NY 10013',
                        'rating': 4.7,
                        'user_ratings_total': 856,
                        'formatted_phone_number': '(212) 555-0123',
                        'website': 'http://goldenpalaceny.com',
                        'price_level': 2,
                        'opening_hours': {
                            'open_now': True,
                            'weekday_text': [
                                'Monday: 11:00 AM - 10:00 PM',
                                'Tuesday: 11:00 AM - 10:00 PM',
                                'Wednesday: 11:00 AM - 10:00 PM',
                                'Thursday: 11:00 AM - 10:00 PM',
                                'Friday: 11:00 AM - 11:00 PM',
                                'Saturday: 11:00 AM - 11:00 PM',
                                'Sunday: 12:00 PM - 9:00 PM'
                            ]
                        },
                        'reviews': [
                            {
                                'author_name': 'John D.',
                                'rating': 5,
                                'relative_time_description': '2 days ago',
                                'text': 'Best dim sum in Chinatown! The shumai and har gow are must-tries. Very authentic and reasonable prices.'
                            },
                            {
                                'author_name': 'Sarah L.',
                                'rating': 4,
                                'relative_time_description': '1 week ago',
                                'text': 'Great traditional Chinese dishes. The service was quick and friendly. Loved the peking duck!'
                            },
                            {
                                'author_name': 'Mike R.',
                                'rating': 5,
                                'relative_time_description': '2 weeks ago',
                                'text': 'Amazing atmosphere and even better food. Their seafood is always fresh and the portions are generous.'
                            }
                        ]
                    }
                },
                'analysis_confidence': 0.92,
                'applied_status': True,  # Indicating if they've applied to the platform
                'membership_status': 'Gold Member'  # Optional membership status
    }
            
    return jsonify(test_data)

    #     except Exception as e:
    #         print(f"Error processing file: {str(e)}")  # Debug print
    #         return jsonify({
    #             'error': f'Error processing file: {str(e)}',
    #             'identified_name': None,
    #             'has_info': False
    #         }), 500
            
    #     finally:
    #         # Clean up temporary file
    #         try:
    #             if os.path.exists(temp_path):
    #                 os.remove(temp_path)
    #                 print(f"Cleaned up file: {temp_path}")  # Debug print
    #         except Exception as e:
    #             print(f"Error cleaning up file: {str(e)}")  # Debug print

    # except Exception as e:
    #     print(f"Server error: {str(e)}")  # Debug print
    #     return jsonify({
    #         'error': f'Server error: {str(e)}',
    #         'identified_name': None,
    #         'has_info': False
    #     }), 500

@app.after_request
def after_request(response):
    if request.path == '/analyze' and request.method == 'POST':
        response.headers['Content-Type'] = 'application/json'
    return response

if __name__ == '__main__':
    db.init_db()
    print(f"Upload folder is set to: {app.config['UPLOAD_FOLDER']}")  # Debug print
    app.run(debug=True, port=8080) 