"""
CNN-based Eye Disease Detection
Analyzes eye images using deep learning
"""

import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path
import json


class EyeDiseaseDetectorCNN:
    """Eye disease detection using CNN"""
    
    def __init__(self, model_path='ml/models/eye_disease_model.h5'):
        self.model = None
        self.model_path = model_path
        self.class_names = ['normal', 'infected', 'fatigue', 'strain']
        self.img_size = (224, 224)
        
        # Try to load pre-trained model
        self._load_model_if_exists()
    
    def _load_model_if_exists(self):
        """Load model if it exists"""
        if Path(self.model_path).exists():
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"✓ Eye model loaded from {self.model_path}")
                return True
            except Exception as e:
                print(f"⚠️  Could not load eye model: {e}")
                return False
        return False
    
    def load_model(self, model_path):
        """Explicitly load a model"""
        try:
            self.model = tf.keras.models.load_model(model_path)
            self.model_path = model_path
            print(f"✓ Eye model loaded from {model_path}")
            return True
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    
    def analyze_eye_image(self, image_path):
        """
        Analyze eye image using CNN
        Returns: {status, score, confidence, issues, message}
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return self._default_response("Could not read image file")
            
            # Preprocess
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_resized = cv2.resize(image_rgb, self.img_size)
            image_normalized = image_resized.astype('float32') / 255.0
            image_batch = np.expand_dims(image_normalized, 0)
            
            # Predict using CNN if available
            if self.model:
                predictions = self.model.predict(image_batch, verbose=0)
                predicted_class_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class_idx])
                predicted_class = self.class_names[predicted_class_idx]
                
                # Convert to health assessment
                status, score, issues = self._class_to_assessment(
                    predicted_class, confidence, predictions[0]
                )
            else:
                # Fallback: basic rule-based analysis
                status, score, issues = self._basic_eye_analysis(image)
                confidence = 0.0
                predicted_class = "unknown"
            
            return {
                "status": status,
                "score": score,
                "confidence": confidence,
                "prediction": predicted_class,
                "issues": issues,
                "message": f"Eye Analysis: {status} (Confidence: {confidence:.1%})"
            }
        
        except Exception as e:
            print(f"Error in eye analysis: {e}")
            return self._default_response(f"Analysis error: {str(e)[:50]}")
    
    def _class_to_assessment(self, predicted_class, confidence, all_predictions):
        """Convert CNN prediction to health assessment with explanation"""
        
        assessments = {
            'normal': {
                'status': 'Normal',
                'score': 85,
                'issues': ['Eyes appear healthy', 'No signs of strain or infection']
            },
            'infected': {
                'status': 'Eye Infection/Inflammation',
                'score': 30,
                'issues': ['Clear signs of infection detected', 'Seek medical attention']
            },
            'fatigue': {
                'status': 'Fatigue Detected',
                'score': 50,
                'issues': ['Signs of eye fatigue', 'Take regular breaks', 'Rest eyes frequently']
            },
            'strain': {
                'status': 'Eye Strain',
                'score': 60,
                'issues': ['Mild eye strain detected', '20-20-20 rule: Every 20 min, look 20 ft away for 20 sec']
            }
        }
        
        assessment = assessments.get(predicted_class, assessments['normal'])
        
        # Adjust score based on confidence
        adjusted_score = int(assessment['score'] * confidence + 75 * (1 - confidence))
        adjusted_score = max(0, min(100, adjusted_score))
        
        return assessment['status'], adjusted_score, assessment['issues']
    
    def _basic_eye_analysis(self, image):
        """Fallback rule-based analysis if CNN not available"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        issues = []
        
        if mean_brightness < 40:
            return "Severe Fatigue", 35, ["Very dark - possible severe fatigue"]
        elif mean_brightness < 70:
            issues.append("Fatigue detected - dark appearance")
            return "Fatigue", 50, issues
        elif mean_brightness < 100:
            issues.append("Mild eye strain")
            return "Eye Strain", 60, issues
        else:
            return "Normal", 85, ["Eyes appear healthy"]
    
    def _default_response(self, message):
        """Return default response when analysis fails"""
        return {
            "status": "Normal",
            "score": 75,
            "confidence": 0.0,
            "prediction": "unknown",
            "issues": [message],
            "message": message
        }
