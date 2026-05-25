# AI-Based Human Sense Recognition Health Assistant

A comprehensive web application that uses AI and machine learning to analyze human sensory inputs (eye movement, tongue images, body posture, and speech patterns) to predict health conditions and provide personalized health recommendations.

## 🎯 Features

### 1. **User Management**
- User registration and authentication
- Secure password hashing
- Medical history and allergy tracking
- User profile management

### 2. **Health Analysis Modules**

#### Eye Analysis
- Eye strain detection using image processing
- Fatigue assessment
- Blink rate analysis
- Real-time and image-based analysis

#### Tongue Analysis
- Color analysis for health indicators
- Detection of dehydration
- Digestion issue identification
- Texture assessment

#### Posture Detection
- Full body posture evaluation using MediaPipe
- Slouching detection
- Neck and spine alignment analysis
- Real-time posture monitoring

#### Speech Analysis
- Speech speed measurement
- Stress detection from voice patterns
- Pitch variability analysis
- Voice stability assessment

### 3. **Health Prediction**
- Machine learning model (RandomForest Classifier)
- Health score calculation (0-100)
- Predicted health condition
- Historical tracking

### 4. **Diet Recommendations**
- Personalized meal plans based on health analysis
- Breakfast, lunch, and dinner suggestions
- Hydration recommendations
- Foods to avoid
- Lifestyle tips

### 5. **Hospital Locator**
- Find nearby hospitals using geolocation
- Distance calculation
- Contact information
- Hospital ratings

### 6. **Dashboard**
- Health overview with statistics
- Latest analysis results
- Quick access to all features
- Health trend visualization

## 🔧 Technology Stack

### Backend
- **Flask** - Web framework
- **Python 3.x** - Programming language
- **OpenCV** - Image processing
- **MediaPipe** - Pose detection
- **Scikit-learn** - Machine learning
- **MySQL** - Database

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling (Blue theme)
- **JavaScript** - Interactivity
- **Bootstrap 5** - Responsive framework

### APIs
- **Web Speech API** - Speech recognition
- **WebRTC** - Camera and audio access
- **Geolocation API** - Location services
- **Google Maps API** (optional) - Hospital locator

## 📋 Project Structure

```
health-assistant/
├── app.py                          # Main Flask application
├── database.py                     # Database operations
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env.example                    # Environment configuration template
│
├── config/
│   └── db_config.py               # Database configuration
│
├── models/
│   ├── eye_detection.py           # Eye analysis module
│   ├── tongue_analysis.py         # Tongue analysis module
│   ├── posture_detection.py       # Posture detection module
│   └── speech_analysis.py         # Speech analysis module
│
├── ml/
│   ├── train_model.py             # ML model training
│   ├── diet_recommendation.py     # Diet recommendation engine
│   └── health_prediction_model.pkl # Saved ML model
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom styles (Blue theme)
│   ├── js/
│   │   ├── script.js              # Main JavaScript
│   │   └── camera.js              # Camera/Audio functions
│   └── images/                    # Image assets
│
├── templates/
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   ├── register.html              # Registration page
│   ├── login.html                 # Login page
│   ├── dashboard.html             # User dashboard
│   ├── analysis.html              # Analysis page
│   └── result.html                # Results page
│
└── uploads/                       # User uploads directory
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- Git
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Clone or Download Project
```bash
cd health-assistant
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Database
1. Create MySQL database:
```bash
# Open MySQL command line
mysql -u root -p

# Create database
CREATE DATABASE health_assistant;
CREATE USER 'health_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON health_assistant.* TO 'health_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Configure Environment
1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your database credentials:
```
DB_HOST=localhost
DB_USER=health_user
DB_PASSWORD=password123
DB_NAME=health_assistant
SECRET_KEY=your-secret-key-here
```

### Step 6: Initialize Database
```bash
python -c "from config.db_config import initialize_database; initialize_database()"
```

### Step 7: Run Application
```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## 🎓 Usage Guide

### 1. Register and Login
- Visit home page and click "Get Started"
- Create account with email and password
- Login with credentials

### 2. Complete Profile
- Add medical history and allergies (optional)
- This helps personalize recommendations

### 3. Health Analysis
1. Go to "Analyze Health" from dashboard
2. Upload or capture images for:
   - Eye analysis
   - Tongue analysis
   - Posture analysis
3. Provide speech audio (record or upload)
4. Enter sleep hours and water intake
5. Click "Analyze My Health"

### 4. View Results
- Check health score and status
- Read detailed analysis for each module
- Review personalized diet recommendations
- Find nearby hospitals if needed

### 5. Track Progress
- Dashboard shows latest results
- View health statistics over time
- Compare scores across analyses

## 📊 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user

### Main Pages
- `GET /` - Home page
- `GET /dashboard` - User dashboard
- `GET /analyze` - Analysis page
- `GET /results/<record_id>` - Results page

### API Routes
- `POST /api/analyze` - Run health analysis
- `POST /api/hospitals` - Get nearby hospitals

## ⚙️ Configuration

#### Environment Variables
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` – database connection
- `SECRET_KEY` – Flask session and CSRF secret
- `SESSION_COOKIE_NAME` *(optional)* – name of session cookie (defaults to `session`).
  Added for compatibility with newer Flask versions when using server-side sessions.

### File Upload Settings
```python
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp3'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```
### Model Parameters
- **Eye Detection**: Haar Cascade Classifier
- **Posture Detection**: MediaPipe Pose (33 keypoints)
- **Speech Analysis**: Audio feature extraction
- **Health Prediction**: RandomForest (100 estimators)

## 🔒 Security Features

✅ Password hashing with werkzeug.security
✅ SQL injection prevention with parameterized queries
✅ File upload validation
✅ File size limits
✅ CSRF protection with Flask sessions
✅ Secure session management

## 🎨 UI/UX Design

### Color Scheme
- **Primary Blue**: #0d6efd
- **Dark Blue**: #0f5ad3
- **Light Blue**: #e7f1ff
- **Text Dark**: #333
- **Background**: #f5f7fa

### Responsive Design
- Mobile-first approach
- Bootstrap 5 grid system
- Touch-friendly buttons
- Optimized for tablets and desktops

### Accessibility
- ARIA labels
- Keyboard navigation
- High contrast text
- Focus indicators

## 📈 Database Schema

### Users Table
```sql
- id (PRIMARY KEY)
- name
- email (UNIQUE)
- password
- age
- medical_history
- allergies
- created_at
```

### Health Records Table
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- eye_status
- tongue_status
- posture_status
- speech_status
- health_score
- predicted_condition
- created_at
```

### Diet Recommendations Table
```sql
- id (PRIMARY KEY)
- record_id (FOREIGN KEY)
- breakfast
- lunch
- dinner
- water_intake
- created_at
```

## 🤖 Machine Learning Model

### Training Data
- Synthetic dataset: 500 samples
- Features: 6 input features
- Classes: 3 health conditions

### Model Details
```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
```

### Features Used
1. Eye Status (0-3)
2. Tongue Status (0-3)
3. Posture Status (0-3)
4. Speech Status (0-3)
5. Sleep Hours (0-10)
6. Water Intake (0-8)

## 🧪 Testing

### Manual Testing Checklist
- [x] User registration and login
- [x] Image upload and analysis
- [x] Audio recording and analysis
- [x] Health score calculation
- [x] Diet recommendations
- [x] Hospital locator
- [x] Responsive design
- [x] Error handling

## 📝 Important Notes

⚠️ **Medical Disclaimer**
- This is a demonstration/educational project
- NOT a medical diagnostic tool
- Always consult healthcare professionals
- Results are informational only

⚠️ **Data Privacy**
- User data is stored locally
- Never share medical information unnecessarily
- Keep `.env` file secure
- Use strong passwords

⚠️ **Browser Requirements**
- Modern browser with WebRTC support
- Camera and microphone access required for capture
- JavaScript must be enabled

## 🔧 Troubleshooting

### MySQL Connection Error
```
Error: 2003 - Can't connect to MySQL server
Solution: Ensure MySQL is running and credentials in .env are correct
```

### Camera Permission Denied
```
Error: Camera access denied
Solution: Check browser permissions and grant camera access
```

### Import Error: ModuleNotFoundError
```
Solution: Ensure all packages installed: pip install -r requirements.txt
```

### Port Already in Use
```
Error: Address already in use
Solution: Change port in app.py or kill process using port 5000
```

## 🚀 Deployment

### Deploying to Production
1. Set `FLASK_ENV=production`
2. Use strong `SECRET_KEY`

### Deploying to Render
1. Push your repository to GitHub.
2. Open https://dashboard.render.com and create a new Web Service.
3. Connect your GitHub account and select this repository.
4. In the Render service settings:
   - Build Command: leave blank or use the default
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Environment: add these variables:
     - `DB_HOST`
     - `DB_USER`
     - `DB_PASSWORD`
     - `DB_NAME`
     - `DB_PORT`
     - `SECRET_KEY`
     - `SESSION_COOKIE_NAME` (optional)
5. Deploy the service.
6. After deployment, Render gives you a live URL like `https://your-app.onrender.com`.

### Render Notes
- Use a managed MySQL database or remote MySQL server and set the DB credentials.
- If your app includes `.env`, do not commit sensitive values to GitHub.
- `Procfile` is already configured for Render with `gunicorn`.

### Local setup before deployment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# update .env values
python -c "from config.db_config import initialize_database; initialize_database()"
```

3. Disable `DEBUG=False`
4. Use production WSGI server (gunicorn)
5. Set up SSL/TLS
6. Configure database backups

### Requirements for Production
- Python 3.8+
- MySQL 5.7+
- Web server (Nginx, Apache)
- WSGI server (Gunicorn, uWSGI)

## 📚 Dependencies Documentation

- [Flask](https://flask.palletsprojects.com/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://mediapipe.dev/)
- [Scikit-learn](https://scikit-learn.org/)
- [Bootstrap 5](https://getbootstrap.com/)

## 👨‍💻 Development

### Adding New Features
1. Create new module in `models/` or `ml/`
2. Add routes in `app.py`
3. Create templates in `templates/`
4. Update styles in `static/css/style.css`
5. Test thoroughly

### Code Style
- Follow PEP 8 for Python
- Use meaningful variable names
- Comment complex logic
- Keep functions focused

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please:
1. Test thoroughly
2. Comment your code
3. Follow existing code style
4. Update documentation

## ❓ FAQ

**Q: Can I use this for real medical diagnosis?**
A: No, this is for educational/demonstration purposes only.

**Q: Is my data secure?**
A: Data is stored locally in MySQL. Use `.env` for sensitive info.

**Q: Can I modify the AI models?**
A: Yes, modify `ml/` and `models/` files as needed.

**Q: Does it work offline?**
A: No, requires running Flask server and MySQL database.

**Q: Can I deploy to cloud?**
A: Yes, follow deployment guidelines above.

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review error logs
3. Check browser console
4. Review Flask debug output

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Ready for Local Use
