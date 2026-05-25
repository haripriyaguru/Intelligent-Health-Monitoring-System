"""
Health Assistant Flask Application
Main application file
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from functools import wraps
import os
import json
from datetime import datetime
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import database and models
from database import Database
from config.db_config import initialize_database
from models.posture_detection import PostureDetector
from models.speech_analysis import SpeechAnalyzer
from ml.train_model import HealthPredictionModel
from ml.diet_recommendation import DietRecommendation
from ml.chatbot.medical_chatbot import ask_medical_llm

# Import CNN models (trained models have priority)
try:
    from ml.cnn_eye_model import EyeDiseaseDetectorCNN as EyeDetector
    from ml.cnn_tongue_model import TongueDiseaseDetectorCNN as TongueAnalyzer
    print("✓ Using trained CNN models for eye and tongue analysis")
    CNN_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  CNN models not available, falling back to rule-based detectors: {e}")
    from models.eye_detection import EyeDetector
    from models.tongue_analysis import TongueAnalyzer
    CNN_MODELS_AVAILABLE = False

# Import nutrition modules
try:
    from ml.nutrition.calorie_calculator import CalorieCalculator
    from ml.nutrition.usda_api import USDAAPI
    from ml.nutrition.meal_planner import MealPlanner
    NUTRITION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Nutrition modules not available: {e}")
    NUTRITION_AVAILABLE = False
    CalorieCalculator = None
    USDAAPI = None
    MealPlanner = None

# Import hospital locator service
try:
    from services.hospital_locator import get_nearby_hospitals, validate_coordinates
    HOSPITAL_LOCATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Hospital locator service not available: {e}")
    HOSPITAL_LOCATOR_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'health-assistant-secret-key-2024')

# Configure session
# Ensure session cookie name is set for compatibility with newer Flask versions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = os.getenv('SESSION_COOKIE_NAME', 'session')
# Flask 2.3+ removed the session_cookie_name attribute; some extensions like
# Flask-Session still access it directly.  Add it explicitly for backward
# compatibility.
app.session_cookie_name = app.config['SESSION_COOKIE_NAME']

Session(app)

# Upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp3'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize AI models
if CNN_MODELS_AVAILABLE:
    # Load trained CNN models
    eye_detector = EyeDetector('ml/models/eye_disease_model.h5')
    tongue_analyzer = TongueAnalyzer('ml/models/tongue_disease_model.h5')
    print("✓ CNN models initialized with trained weights")
else:
    # Fallback to rule-based detectors
    eye_detector = EyeDetector()
    tongue_analyzer = TongueAnalyzer()
    print("ℹ️  Using rule-based detectors (rule-based fallback)")
posture_detector = PostureDetector()
speech_analyzer = SpeechAnalyzer()
health_predictor = HealthPredictionModel()
diet_recommender = DietRecommendation()

# Initialize nutrition modules
if NUTRITION_AVAILABLE:
    calorie_calculator = CalorieCalculator()
    usda_api = USDAAPI()
    meal_planner = MealPlanner()
else:
    calorie_calculator = None
    usda_api = None
    meal_planner = None

# Load or train health prediction model
model_path = 'ml/health_prediction_model.pkl'
if not health_predictor.load_model(model_path):
    health_predictor.train_model()
    health_predictor.save_model(model_path)

# Initialize database
initialize_database()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to check login status"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not all([name, email, password, confirm_password]):
            return render_template('register.html', error='All fields are required')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')

        # Check if email already exists
        if Database.get_user_by_email(email):
            return render_template('register.html', error='Email already registered')

        # Register user
        if Database.register_user(name, email, password):
            return render_template('register.html', success='Registration successful! Please login.')
        else:
            return render_template('register.html', error='Registration failed. Try again.')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Database.login_user(email, password)

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_id = session.get('user_id')
    user = Database.get_user_by_id(user_id)
    latest_record = Database.get_latest_health_record(user_id)
    stats = Database.get_health_statistics(user_id)

    return render_template('dashboard.html', user=user, latest_record=latest_record, stats=stats)

@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Health analysis page"""
    if request.method == 'POST':
        return redirect(url_for('run_analysis'))

    return render_template('analysis.html')

@app.route('/api/analyze', methods=['POST'])
@login_required
def run_analysis():
    """Run health analysis on uploaded files"""
    user_id = session.get('user_id')
    results = {
        'eye_status': 'Normal',
        'tongue_status': 'Healthy',
        'posture_status': 'Good',
        'speech_status': 'Normal'
    }

    # Eye Analysis
    if 'eye_image' in request.files:
        eye_file = request.files['eye_image']
        if eye_file and allowed_file(eye_file.filename):
            filename = secure_filename(f"eye_{user_id}_{datetime.now().timestamp()}.png")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            eye_file.save(filepath)

            eye_result = eye_detector.analyze_eye_image(filepath)
            results['eye_status'] = eye_result.get('status', 'Normal')
            results['eye_score'] = eye_result.get('score', 75)
            results['eye_message'] = eye_result.get('message', '')

    # Tongue Analysis
    if 'tongue_image' in request.files:
        tongue_file = request.files['tongue_image']
        if tongue_file and allowed_file(tongue_file.filename):
            filename = secure_filename(f"tongue_{user_id}_{datetime.now().timestamp()}.png")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            tongue_file.save(filepath)

            tongue_result = tongue_analyzer.analyze_tongue_image(filepath)
            results['tongue_status'] = tongue_result.get('status', 'Healthy')
            results['tongue_score'] = tongue_result.get('score', 75)
            results['tongue_message'] = tongue_result.get('message', '')

    # Posture Analysis
    if 'posture_image' in request.files:
        posture_file = request.files['posture_image']
        if posture_file and allowed_file(posture_file.filename):
            filename = secure_filename(f"posture_{user_id}_{datetime.now().timestamp()}.png")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            posture_file.save(filepath)

            try:
                posture_result = posture_detector.analyze_posture_image(filepath)
                results['posture_status'] = posture_result.get('status', 'Good')
                results['posture_score'] = posture_result.get('score', 75)
                results['issues'] = posture_result.get('issues', [])
                print(f"DEBUG: Posture analysis result: {posture_result}")
            except Exception as e:
                print(f"ERROR in posture analysis: {e}")
                results['posture_status'] = 'Good'
                results['posture_score'] = 75
                results['issues'] = []

    # Speech Analysis
    if 'speech_file' in request.files:
        speech_file = request.files['speech_file']
        if speech_file and allowed_file(speech_file.filename):
            filename = secure_filename(f"speech_{user_id}_{datetime.now().timestamp()}.wav")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            speech_file.save(filepath)

            try:
                speech_result = speech_analyzer.analyze_speech_file(filepath)
                results['speech_status'] = speech_result.get('status', 'Normal')
                results['speech_score'] = speech_result.get('score', 75)
                results['stress_level'] = speech_result.get('stress_level', 0)
                print(f"DEBUG: Speech analysis result: {speech_result}")
            except Exception as e:
                print(f"ERROR in speech analysis: {e}")
                results['speech_status'] = 'Normal'
                results['speech_score'] = 75
                results['stress_level'] = 0

    # Get user input data
    sleep_hours = float(request.form.get('sleep_hours', 6))
    water_intake = int(request.form.get('water_intake', 4))

    # Get nutrition input data
    height_cm = float(request.form.get('height', 170))
    weight_kg = float(request.form.get('weight', 70))
    age_years = int(request.form.get('age', 30))
    gender = request.form.get('gender', 'male')
    activity_level = request.form.get('activity_level', 'moderate')
    goal = request.form.get('goal', 'maintain')

    # Health Prediction
    prediction_features = {
        'eye_status': results.get('eye_score', 75),
        'tongue_status': results.get('tongue_score', 75),
        'posture_status': results.get('posture_score', 75),
        'speech_status': results.get('speech_score', 75),
        'sleep_hours': sleep_hours,
        'water_intake': water_intake
    }

    prediction = health_predictor.predict_health(prediction_features)
    results['health_score'] = prediction['health_score']
    results['predicted_condition'] = prediction['prediction']

    # Calculate nutrition requirements
    if NUTRITION_AVAILABLE and calorie_calculator:
        maintenance_calories = calorie_calculator.calculate_maintenance_calories(
            weight_kg, height_cm, age_years, gender, activity_level
        )
        target_calories = calorie_calculator.adjust_calories(maintenance_calories, goal)

        results['maintenance_calories'] = maintenance_calories
        results['target_calories'] = target_calories
        results['nutrition_info'] = {
            'height': height_cm,
            'weight': weight_kg,
            'age': age_years,
            'gender': gender,
            'activity_level': activity_level,
            'goal': goal
        }

        # Detect health conditions for meal planning
        detected_conditions = []
        if results.get('eye_status') and 'fatigue' in results['eye_status'].lower():
            detected_conditions.append('eye_fatigue')
        if results.get('tongue_status') and any(term in results['tongue_status'].lower() for term in ['dry', 'dehydration', 'white']):
            detected_conditions.append('dehydration')
        if results.get('speech_status') and 'stress' in results['speech_status'].lower():
            detected_conditions.append('digestion')

        # Generate meal plan
        try:
            meal_plan = meal_planner.generate_meal_plan(target_calories, detected_conditions)
            results['meal_plan'] = meal_plan
            results['condition_recommendations'] = meal_planner.get_condition_based_recommendations(detected_conditions)
        except Exception as e:
            print(f"Error generating meal plan: {e}")
            # Fallback meal plan
            if meal_planner:
                results['meal_plan'] = meal_planner.create_fallback_meal_plan(target_calories)
            results['condition_recommendations'] = {}
    else:
        print("Nutrition modules not available - skipping meal planning")
        results['maintenance_calories'] = None
        results['target_calories'] = None
        results['nutrition_info'] = None
        results['meal_plan'] = None
        results['condition_recommendations'] = {}

    # Save health record
    record_id = Database.save_health_record(
        user_id,
        results.get('eye_status', 'Normal'),
        results.get('tongue_status', 'Healthy'),
        results.get('posture_status', 'Good'),
        results.get('speech_status', 'Normal'),
        results['health_score'],
        results['predicted_condition'],
        nutrition_info=results.get('nutrition_info'),
        maintenance_calories=results.get('maintenance_calories'),
        target_calories=results.get('target_calories'),
        meal_plan=results.get('meal_plan'),
        condition_recommendations=results.get('condition_recommendations')
    )

    print(f"DEBUG: Saved health record with ID: {record_id}")

    # Get diet recommendations
    diet_rec = diet_recommender.get_recommendations({
        'eye_status': results.get('eye_status', 'Normal'),
        'tongue_status': results.get('tongue_status', 'Healthy'),
        'tongue_message': results.get('tongue_message', ''),
        'speech_status': results.get('speech_status', 'Normal'),
        'health_score': results['health_score']
    })

    # Save diet recommendation
    if record_id:
        breakfast = ', '.join(diet_rec['meal_plan']['breakfast'])
        lunch = ', '.join(diet_rec['meal_plan']['lunch'])
        dinner = ', '.join(diet_rec['meal_plan']['dinner'])

        Database.save_diet_recommendation(
            record_id,
            breakfast,
            lunch,
            dinner,
            diet_rec['water_intake']['daily_glasses']
        )

        results['record_id'] = record_id
        print(f"DEBUG: Added record_id to results: {record_id}")
    else:
        print("DEBUG: record_id is None, not saving diet recommendations")

    # Add diet recommendations to results
    results['diet_recommendations'] = diet_rec

    return jsonify(results)

@app.route('/results/<int:record_id>')
@login_required
def results(record_id):
    """Display analysis results"""
    user_id = session.get('user_id')
    record = Database.get_health_record(record_id)
    diet_rec = Database.get_diet_recommendation(record_id)

    if not record or record['user_id'] != user_id:
        return redirect(url_for('dashboard'))

    return render_template('result.html', record=record, diet_rec=diet_rec)

@app.route('/hospitals')
@login_required
def hospitals():
    """Hospital finder page"""
    return render_template('hospitals.html')

@app.route('/api/hospitals', methods=['GET'])
@login_required
def get_hospitals():
    """Get nearby hospitals using Overpass API"""
    # Get latitude and longitude from query parameters
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)

    # Validate coordinates
    if latitude is None or longitude is None:
        return jsonify({
            'success': False,
            'error': 'Latitude and longitude parameters are required',
            'hospitals': []
        }), 400

    # Validate coordinate format
    is_valid, error_message = validate_coordinates(latitude, longitude)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error_message,
            'hospitals': []
        }), 400

    # Fetch hospitals from Overpass API
    result = get_nearby_hospitals(latitude, longitude)

    return jsonify(result)

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot():
    """AI Medical Chatbot endpoint"""
    user_id = session.get('user_id')
    data = request.json

    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    user_question = data['message'].strip()

    if not user_question:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Get user's latest health analysis
    latest_record = Database.get_latest_health_record(user_id)

    if not latest_record:
        return jsonify({'error': 'No health analysis found. Please complete a health analysis first.'}), 400

    # Prepare health data for the chatbot
    health_data = {
        'eye_status': latest_record.get('eye_status', 'Normal'),
        'tongue_status': latest_record.get('tongue_status', 'Healthy'),
        'posture_status': latest_record.get('posture_status', 'Good'),
        'speech_status': latest_record.get('speech_status', 'Normal'),
        'health_score': latest_record.get('health_score', 75),
        'predicted_condition': latest_record.get('predicted_condition', 'Good')
    }

    # Get response from medical chatbot
    try:
        response = ask_medical_llm(user_question, health_data)
        return jsonify({'reply': response})
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({'error': 'Medical assistant is currently unavailable. Please try again later.'}), 500

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
