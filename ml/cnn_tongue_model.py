"""
CNN-based Tongue Disease Detection
Analyzes tongue images using deep learning
"""

import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path


class TongueDiseaseDetectorCNN:
    """Tongue disease detection using CNN"""
    
    def __init__(self, model_path='ml/models/tongue_disease_model.h5'):
        self.model = None
        self.model_path = model_path
        self.class_names = [
            'normal', 'pale', 'coated', 'inflamed', 
            'fissured', 'dark', 'thrush'
        ]
        self.img_size = (224, 224)
        
        # Try to load pre-trained model
        self._load_model_if_exists()
    
    def _load_model_if_exists(self):
        """Load model if it exists"""
        if Path(self.model_path).exists():
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"✓ Tongue model loaded from {self.model_path}")
                return True
            except Exception as e:
                print(f"⚠️  Could not load tongue model: {e}")
                return False
        return False
    
    def load_model(self, model_path):
        """Explicitly load a model"""
        try:
            self.model = tf.keras.models.load_model(model_path)
            self.model_path = model_path
            print(f"✓ Tongue model loaded from {model_path}")
            return True
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    
    def analyze_tongue_image(self, image_path):
        """
        Analyze tongue image using CNN
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
                # Fallback: basic color-based analysis
                status, score, issues = self._basic_tongue_analysis(image)
                confidence = 0.0
                predicted_class = "unknown"
            
            return {
                "status": status,
                "score": score,
                "confidence": confidence,
                "prediction": predicted_class,
                "issues": issues,
                "message": f"Tongue Analysis: {status} (Confidence: {confidence:.1%})"
            }
        
        except Exception as e:
            print(f"Error in tongue analysis: {e}")
            return self._default_response(f"Analysis error: {str(e)[:50]}")
    
    def _class_to_assessment(self, predicted_class, confidence, all_predictions):
        """Convert CNN prediction to health assessment"""
        
        assessments = {
            'normal': {
                'status': 'Healthy',
                'score': 85,
                'issues': ['Tongue appears healthy', 'Good color and texture']
            },
            'pale': {
                'status': 'Pale Tongue (Anemia Risk)',
                'score': 45,
                'issues': [
                    'Low color saturation detected',
                    'May indicate anemia or nutritional deficiency',
                    'Increase iron and B12 intake'
                ]
            },
            'coated': {
                'status': 'Coated/Infected Tongue',
                'score': 40,
                'issues': [
                    'White/yellow coating detected',
                    'Possible bacterial or yeast infection',
                    'Consider antifungal treatment'
                ]
            },
            'inflamed': {
                'status': 'Inflamed Tongue',
                'score': 35,
                'issues': [
                    'Signs of inflammation detected',
                    'Possible infection or allergic reaction',
                    'Seek medical attention'
                ]
            },
            'fissured': {
                'status': 'Fissured Tongue',
                'score': 50,
                'issues': [
                    'Cracks or fissures detected',
                    'May collect bacteria or fungi',
                    'Maintain good oral hygiene'
                ]
            },
            'dark': {
                'status': 'Dark Tongue (Poor Digestion)',
                'score': 45,
                'issues': [
                    'Dark discoloration detected',
                    'May indicate poor digestion or toxin buildup',
                    'Improve diet and digestive health'
                ]
            },
            'thrush': {
                'status': 'Thrush/Candida (Fungal Infection)',
                'score': 30,
                'issues': [
                    'White patches detected - possible thrush',
                    'Fungal infection (candida)',
                    'Need antifungal medication'
                ]
            }
        }
        
        assessment = assessments.get(predicted_class, assessments['normal'])
        
        # Adjust score based on confidence
        adjusted_score = int(assessment['score'] * confidence + 75 * (1 - confidence))
        adjusted_score = max(0, min(100, adjusted_score))
        
        return assessment['status'], adjusted_score, assessment['issues']
    
    def _basic_tongue_analysis(self, image):
        """Fallback color-based analysis if CNN not available"""
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            h_mean = np.mean(h)
            s_mean = np.mean(s)
            v_mean = np.mean(v)
            
            issues = []
            
            # Pale tongue (low saturation)
            if s_mean < 60:
                issues.append("Low saturation - may indicate anemia")
                return "Pale Tongue", 45, issues
            
            # Dark tongue (low value)
            elif v_mean < 80:
                issues.append("Dark appearance - poor digestion")
                return "Dark Tongue", 45, issues
            
            # Red/inflamed (high red component in HSV)
            elif (h_mean < 10 or h_mean > 170) and s_mean > 100:
                issues.append("Red/inflamed appearance")
                return "Inflamed Tongue", 35, issues
            
            # Yellow coating
            elif h_mean > 15 and h_mean < 35 and s_mean > 80:
                issues.append("Yellow coating - possible infection")
                return "Coated Tongue", 40, issues
            
            # Normal
            else:
                return "Healthy", 85, ["Tongue appears healthy"]
        
        except Exception as e:
            return "Healthy", 75, [f"Basic analysis: {str(e)[:30]}"]
    
    def _default_response(self, message):
        """Return default response when analysis fails"""
        return {
            "status": "Healthy",
            "score": 75,
            "confidence": 0.0,
            "prediction": "unknown",
            "issues": [message],
            "message": message
        }
