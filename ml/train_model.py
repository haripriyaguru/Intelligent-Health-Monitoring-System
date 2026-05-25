"""
Health Prediction Model Training
Trains and saves ML model for health prediction
"""

import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os

class HealthPredictionModel:
    def __init__(self):
        """Initialize health prediction model"""
        self.model = None
        self.is_trained = False
        self.feature_names = [
            'eye_status',
            'tongue_status',
            'posture_status',
            'speech_status',
            'sleep_hours',
            'water_intake'
        ]

    def generate_training_data(self, num_samples=500):
        """Generate synthetic training data"""
        np.random.seed(42)

        # Feature encoding
        status_encoding = {
            'normal': 3,
            'healthy': 3,
            'good': 3,
            'good_posture': 3,
            'excellent': 3,
            'eye_strain': 1,
            'fatigue': 1,
            'dehydration': 1,
            'digestion': 1,
            'bad_posture': 1,
            'stress': 1,
            'moderate': 2,
        }

        X = []
        y = []

        for _ in range(num_samples):
            # Generate random features
            eye = np.random.choice([1, 2, 3])  # 1=bad, 2=moderate, 3=good
            tongue = np.random.choice([1, 2, 3])
            posture = np.random.choice([1, 2, 3])
            speech = np.random.choice([1, 2, 3])
            sleep = np.random.uniform(4, 10)
            water = np.random.uniform(0, 8)

            features = [eye, tongue, posture, speech, sleep, water]
            X.append(features)

            # Calculate health condition based on features
            avg_score = (eye + tongue + posture + speech) / 4
            sleep_score = min(3, sleep / 3)
            water_score = min(3, water / 3)

            # Combined health assessment
            overall_score = (avg_score * 0.5 + sleep_score * 0.25 + water_score * 0.25)

            if overall_score >= 2.5:
                y.append("Excellent Health")
            elif overall_score >= 1.8:
                y.append("Good Health")
            else:
                y.append("Needs Attention")

        return np.array(X), np.array(y)

    def train_model(self):
        """Train the random forest model"""
        # Generate training data
        X, y = self.generate_training_data(500)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"Model trained with accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        self.is_trained = True

    def predict_health(self, features: dict):
        """
        Predict health condition using both ML model and rule-based assessment
        Args:
            features: {
                'eye_status': int (score 0-100),
                'tongue_status': int (score 0-100),
                'posture_status': int (score 0-100),
                'speech_status': int (score 0-100),
                'sleep_hours': float,
                'water_intake': int (glasses per day)
            }
        """
        # Get raw scores
        eye_score = features.get('eye_status', 75)
        tongue_score = features.get('tongue_status', 75)
        posture_score = features.get('posture_status', 75)
        speech_score = features.get('speech_status', 75)
        sleep = features.get('sleep_hours', 6)
        water = features.get('water_intake', 4)

        # ===== RULE-BASED ASSESSMENT (more accurate than ML on synthetic data) =====
        issues = []
        health_warnings = []

        # Check eye health
        if eye_score < 40:
            issues.append("Serious eye condition")
            health_warnings.append("⚠️ Eye Problem: Possible infection/inflammation")
        elif eye_score < 60:
            issues.append("Eye strain detected")
            health_warnings.append("⚠️ Eye Issue: Strain or fatigue")
        
        # Check tongue health
        if tongue_score < 40:
            issues.append("Serious tongue condition")
            health_warnings.append("⚠️ Tongue Problem: Possible infection/disease")
        elif tongue_score < 60:
            issues.append("Tongue issue detected")
            health_warnings.append("⚠️ Tongue Issue: Coated or inflamed")
        
        # Check posture
        if posture_score < 40:
            issues.append("Poor posture")
            health_warnings.append("⚠️ Posture: Significant alignment issues")
        elif posture_score < 60:
            issues.append("Posture could be improved")
            health_warnings.append("⚠️ Posture: Minor misalignment")
        
        # Check speech/stress
        if speech_score < 40:
            issues.append("High stress indicators")
            health_warnings.append("⚠️ Speech: Signs of high stress")
        
        # Check sleep
        if sleep < 5:
            issues.append("Insufficient sleep")
            health_warnings.append("⚠️ Sleep: Less than 5 hours per night")
        elif sleep < 7:
            issues.append("Sleep could be improved")
            health_warnings.append("⚠️ Sleep: Less than recommended 7-9 hours")
        
        # Check water intake
        if water < 4:
            issues.append("Dehydration risk")
            health_warnings.append("⚠️ Hydration: Less than 4 glasses daily")

        # ===== CALCULATE OVERALL HEALTH SCORE =====
        # Direct weighted average of all factors
        health_score = int(
            (eye_score * 0.20) +          # Eyes 20%
            (tongue_score * 0.20) +       # Tongue 20%
            (posture_score * 0.15) +      # Posture 15%
            (speech_score * 0.15) +       # Speech/Stress 15%
            (min(sleep, 9) / 9 * 100 * 0.15) +    # Sleep 15%
            (min(water, 8) / 8 * 100 * 0.15)      # Water 15%
        )

        # ===== DETERMINE HEALTH STATUS =====
        if health_score >= 85:
            prediction = "Excellent Health"
        elif health_score >= 70:
            prediction = "Good Health"
        elif health_score >= 55:
            prediction = "Moderate Health - Attention Needed"
        elif health_score >= 40:
            prediction = "Poor Health - Significant Concerns"
        else:
            prediction = "Critical Health Issues - Medical Attention Needed"

        return {
            'prediction': prediction,
            'health_score': max(0, min(100, health_score)),
            'issues': issues,
            'warnings': health_warnings,
            'detailed_scores': {
                'eye': eye_score,
                'tongue': tongue_score,
                'posture': posture_score,
                'speech': speech_score,
                'sleep': min(sleep, 9),
                'water': min(water, 8)
            },
            'recommendation_level': self._get_recommendation_level(health_score)
        }

    def _normalize_score(self, score):
        """Normalize score to 1-3 scale"""
        if score > 50:
            return 3
        elif score > 30:
            return 2
        else:
            return 1

    def _get_recommendation_level(self, health_score):
        """Get recommendation level based on health score"""
        if health_score >= 80:
            return "Maintain current lifestyle"
        elif health_score >= 60:
            return "Minor improvements recommended"
        elif health_score >= 40:
            return "Significant lifestyle changes recommended"
        else:
            return "Urgent health attention needed"

    def save_model(self, filepath):
        """Save trained model to disk"""
        if not self.is_trained:
            self.train_model()

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"Model saved to {filepath}")

    def load_model(self, filepath):
        """Load trained model from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.model = pickle.load(f)
            self.is_trained = True
            print(f"Model loaded from {filepath}")
            return True
        else:
            print(f"Model file not found: {filepath}")
            return False
