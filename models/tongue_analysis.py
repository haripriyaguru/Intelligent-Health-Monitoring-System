"""
Tongue Image Analysis Module
Analyzes tongue color and texture to detect health conditions
"""

import cv2
import numpy as np
from PIL import Image

class TongueAnalyzer:
    def __init__(self):
        """Initialize tongue analyzer"""
        self.color_ranges = {
            'normal': {'h_range': (0, 20), 's_range': (50, 255), 'v_range': (100, 255)},
            'pale': {'h_range': (0, 180), 's_range': (0, 50), 'v_range': (150, 255)},
            'dark': {'h_range': (0, 20), 's_range': (50, 255), 'v_range': (0, 100)}
        }

    def analyze_tongue_image(self, image_path):
        """
        Analyze uploaded tongue image
        Returns: {status: 'Normal'/'Dehydration'/'Digestion Issues', score: 0-100}
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"status": "Error", "score": 0, "message": "Could not read image"}

            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Analyze color distribution
            analysis = self._analyze_color(hsv)

            return analysis

        except Exception as e:
            return {"status": "Error", "score": 0, "message": str(e)}

    def _analyze_color(self, hsv_image):
        """Analyze tongue color from HSV image for health indicators"""

        # Get HSV channel values
        h, s, v = cv2.split(hsv_image)

        # Calculate statistics
        h_mean = np.mean(h)
        s_mean = np.mean(s)
        v_mean = np.mean(v)
        h_std = np.std(h)
        s_std = np.std(s)

        # Determine tongue status based on color
        score = 100
        status = "Healthy"
        message = "Tongue appears healthy"
        issues = []

        # ===== PALE TONGUE (Anemia, deficiency) =====
        if s_mean < 60:
            score -= 40
            status = "Pale Tongue (Deficiency)"
            issues.append("Low saturation - possible anemia or nutritional deficiency")
            message = "Low saturation detected. Increase iron and B12 intake."

        # ===== DARK/SWOLLEN TONGUE (Poor digestion, toxins) =====
        elif v_mean < 80:
            score -= 35
            status = "Dark/Swollen Tongue"
            issues.append("Dark coloration - poor digestion or metabolic issues")
            message = "Tongue appears dark. Improve diet and digestion."

        # ===== RED/INFLAMED TONGUE (Infection, inflammation) =====
        elif (h_mean < 10 or h_mean > 170) and s_mean > 100:
            # High red saturation (h=0 is red in HSV)
            score -= 45
            status = "Inflamed/Infected"
            issues.append("Red/inflamed appearance - possible infection")
            message = "Signs of inflammation detected. May indicate infection."

        # ===== YELLOWISH COATING (Infection, fever) =====
        elif h_mean > 15 and h_mean < 35 and s_mean > 80:
            score -= 40
            status = "Infected/Coated Tongue"
            issues.append("Yellow coating - possible bacterial infection")
            message = "Unusual coating detected. Consider medical consultation."

        # ===== WHITISH COATING (Candida, thrush) =====
        elif h_mean > 90 and h_mean < 130 and s_mean < 100:
            score -= 35
            status = "White Coating (Possible Thrush)"
            issues.append("White patches - possible candida infection")
            message = "White coating detected. May need antifungal treatment."

        # ===== CRACKED/FISSURED TONGUE =====
        if h_std > 40 or s_std > 80:
            score -= 20
            issues.append("Color variation indicates cracks or fissures")
            status = "Fissured Tongue" if "Fissured" not in status else status

        # Normal healthy pink tongue
        if len(issues) == 0:
            score = 85
            status = "Healthy"
            message = "Tongue color indicates good health"

        # Additional texture analysis
        texture_score = self._analyze_texture(hsv_image)
        
        if texture_score < 55:
            score = min(score, texture_score)
            issues.append(f"Abnormal texture detected (score: {texture_score})")
            if score > 60:
                status = status + " + Abnormal Texture"

        # Ensure score is in valid range
        score = max(0, min(100, score))

        return {
            "status": status,
            "score": score,
            "h_mean": float(h_mean),
            "s_mean": float(s_mean),
            "v_mean": float(v_mean),
            "issues": issues,
            "message": message
        }

    def _analyze_texture(self, hsv_image):
        """Analyze texture using edge detection"""
        v_channel = hsv_image[:, :, 2]
        edges = cv2.Canny(v_channel, 100, 200)
        edge_count = np.count_nonzero(edges)
        total_pixels = edges.size

        # Normal texture should have some edges (papillae)
        edge_ratio = edge_count / total_pixels

        if edge_ratio < 0.01:
            return 40  # Too smooth - abnormal
        elif edge_ratio > 0.15:
            return 50  # Too rough - abnormal
        else:
            return 85  # Normal texture

    def detect_conditions(self, analysis_result):
        """Provide dietary recommendations based on analysis"""
        status = analysis_result['status']
        recommendations = {}

        if "Dehydration" in status:
            recommendations['primary'] = "Dehydration"
            recommendations['advice'] = [
                "Drink at least 8-10 glasses of water daily",
                "Consume hydrating fruits: watermelon, cucumber, oranges",
                "Reduce caffeine intake",
                "Add electrolyte drinks"
            ]
        elif "Digestion" in status:
            recommendations['primary'] = "Digestion Issues"
            recommendations['advice'] = [
                "Include fiber-rich foods: whole grains, vegetables",
                "Eat slowly and chew properly",
                "Avoid spicy and fatty foods",
                "Include probiotic foods: yogurt, kimchi"
            ]
        elif "Infection" in status:
            recommendations['primary'] = "Possible Infection"
            recommendations['advice'] = [
                "Maintain oral hygiene",
                "Gargle with salt water",
                "Consume vitamin C rich foods",
                "Consult a healthcare professional"
            ]
        else:
            recommendations['primary'] = "Healthy"
            recommendations['advice'] = [
                "Maintain current dietary habits",
                "Continue regular hydration",
                "Keep oral hygiene routine"
            ]

        return recommendations
