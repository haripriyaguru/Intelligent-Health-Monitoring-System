"""
Eye Detection and Analysis Module
Detects eye strain, fatigue, and blink rate
"""

import cv2
import numpy as np
from datetime import datetime

class EyeDetector:
    def __init__(self):
        """Initialize eye cascade classifier"""
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.blink_count = 0
        self.eye_closed_frames = 0
        self.last_analysis = None

    def analyze_eye_image(self, image_path):
        """
        Analyze uploaded eye image
        Returns: {status: 'Normal'/'Eye Strain'/'Fatigue', score: 0-100}
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"status": "Error", "score": 0, "message": "Could not read image"}

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                return {"status": "No face detected", "score": 0}

            # Get the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face

            # Analyze eye region
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)

            if len(eyes) < 2:
                return {"status": "Eye Strain", "score": 35}

            # Analyze eye characteristics
            score, status = self._calculate_eye_health(roi_gray, eyes)

            return {
                "status": status,
                "score": score,
                "eyes_detected": len(eyes),
                "message": f"Detected {len(eyes)} eyes. Status: {status}"
            }

        except Exception as e:
            return {"status": "Error", "score": 0, "message": str(e)}

    def _calculate_eye_health(self, roi_gray, eyes):
        """Calculate eye health based on detected features"""
        # Analyze brightness, contrast, and color for health indicators
        mean_brightness = np.mean(roi_gray)
        std_brightness = np.std(roi_gray)

        # Convert to BGR for color analysis if possible
        score = 100
        status = "Normal"
        issues = []

        # Check brightness levels
        if mean_brightness < 40:
            score -= 35
            issues.append("Severe darkness (fatigue/exhaustion)")
            status = "Severe Fatigue"
        elif mean_brightness < 70:
            score -= 20
            issues.append("Dark circle/fatigue detected")
            status = "Fatigue"
        elif mean_brightness < 100:
            score -= 10
            issues.append("Mild eye strain")
            status = "Eye Strain"

        # Check contrast (high contrast = healthy, low = fatigue/dryness)
        if std_brightness < 20:
            score -= 15
            issues.append("Low contrast (possible dryness or tiredness)")
            status = "Dry Eyes" if score > 50 else status

        # Check for redness by analyzing color distribution
        # In grayscale, redness from blood vessels shows as darker regions with specific patterns
        # This is a simple heuristic - real detection would use color images
        histogram = cv2.calcHist([roi_gray], [0], None, [256], [0, 256])
        
        # Redness in eyes often shows as higher pixel intensity in mid-range
        mid_range_pixels = np.sum(histogram[100:200])
        high_range_pixels = np.sum(histogram[200:256])
        
        if mid_range_pixels > np.sum(histogram) * 0.5:
            score -= 25
            issues.append("Possible redness/infection detected")
            status = "Possible Infection/Inflammation"
        
        if high_range_pixels < np.sum(histogram) * 0.2:
            score -= 10
            issues.append("Light intensity abnormal")

        # Ensure score is in valid range
        score = max(0, min(100, score))

        return score, status

        # Check for low contrast (fatigue)
        if std_brightness < 20:
            score -= 10

        return max(0, score), status

    def detect_blink(self, frame):
        """Detect blink in real-time video frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)

            # Simple blink detection based on eye detection
            if len(eyes) == 0:
                self.eye_closed_frames += 1
            else:
                if self.eye_closed_frames > 5:
                    self.blink_count += 1
                self.eye_closed_frames = 0

        return self.blink_count

    def get_fatigue_level(self):
        """Get fatigue level based on blink rate"""
        # Normal blink rate: 15-20 blinks per minute
        # High blink rate indicates fatigue

        if self.blink_count < 10:
            return {"status": "Good", "score": 90}
        elif self.blink_count < 25:
            return {"status": "Normal", "score": 75}
        else:
            return {"status": "Fatigue", "score": 50}

    def reset_counters(self):
        """Reset blink counters"""
        self.blink_count = 0
        self.eye_closed_frames = 0
