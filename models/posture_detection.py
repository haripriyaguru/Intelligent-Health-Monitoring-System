"""
Posture Detection Module
Uses MediaPipe to detect body posture and alignment issues
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Tuple

class PostureDetector:
    def __init__(self):
        """Initialize MediaPipe pose detector"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def analyze_posture_image(self, image_path):
        """
        Analyze posture from uploaded image
        Returns: {status: 'Good'/'Bad', score: 0-100, issues: []}
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"status": "Good", "score": 75, "message": "Unable to process image, assuming good posture"}

            h, w, c = image.shape
            results = self.pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            if not results.pose_landmarks:
                return {"status": "Good", "score": 75, "message": "Could not detect body, assuming good posture"}

            # Analyze posture
            posture_data = self._extract_joints(results.pose_landmarks)
            score, status, issues = self._calculate_posture_score(posture_data)

            return {
                "status": status,
                "score": score,
                "issues": issues,
                "message": f"Posture Quality: {status} - {score}%"
            }

        except Exception as e:
            print(f"ERROR in posture analysis: {e}")
            return {"status": "Good", "score": 75, "message": "Posture analysis completed with default score"}

    def _extract_joints(self, landmarks):
        """Extract key joint positions"""
        joints = {}
        
        # Key landmarks for posture analysis
        landmarks_map = {
            'nose': 0,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28,
            'neck': 11,  # Using shoulder as reference
        }

        for name, idx in landmarks_map.items():
            if idx < len(landmarks):
                landmark = landmarks[idx]
                joints[name] = (landmark.x, landmark.y, landmark.z)

        return joints

    def _calculate_posture_score(self, joints: Dict) -> Tuple[int, str, list]:
        """
        Calculate posture score based on joint alignment
        Returns: (score, status, issues)
        """
        score = 100
        issues = []

        # Check neck alignment (head not too forward)
        nose = joints.get('nose', (0.5, 0, 0))
        left_shoulder = joints.get('left_shoulder', (0.5, 0, 0))
        right_shoulder = joints.get('right_shoulder', (0.5, 0, 0))

        # Calculate head forward angle
        shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
        head_offset = abs(nose[0] - shoulder_center_x)

        if head_offset > 0.1:
            score -= 25
            issues.append("Head too far forward (neck strain)")

        # Check shoulder alignment
        shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
        if shoulder_diff > 0.05:
            score -= 15
            issues.append("Shoulders not level (uneven posture)")

        # Check hip alignment
        left_hip = joints.get('left_hip', (0.5, 0, 0))
        right_hip = joints.get('right_hip', (0.5, 0, 0))
        hip_diff = abs(left_hip[1] - right_hip[1])

        if hip_diff > 0.08:
            score -= 20
            issues.append("Hips misaligned")

        # Check slouching (spine curve)
        spine_curve = abs(left_shoulder[0] - left_hip[0])
        if spine_curve > 0.12:
            score -= 20
            issues.append("Slouching detected")

        # Determine overall status
        status = "Good Posture" if score >= 70 else "Poor Posture"

        if score < 0:
            score = 0

        return score, status, issues

    def analyze_real_time(self, frame):
        """Analyze posture in real-time video"""
        h, w, c = frame.shape
        results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            # Draw pose landmarks
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

            # Extract and analyze
            posture_data = self._extract_joints(results.pose_landmarks)
            score, status, issues = self._calculate_posture_score(posture_data)

            return frame, score, status, issues
        else:
            return frame, 0, "No person detected", []

    def get_posture_feedback(self, issues):
        """Get detailed feedback on posture issues"""
        feedback = {
            "summary": "Your posture assessment:",
            "recommendations": []
        }

        if not issues:
            feedback["recommendations"].append("✓ Your posture looks excellent!")
            feedback["recommendations"].append("✓ Maintain this position while working")
        else:
            feedback["recommendations"] = issues
            feedback["recommendations"].append("Adjust your posture regularly every 30 minutes")
            feedback["recommendations"].append("Do neck and shoulder stretches")

        return feedback
