"""
Database Module
Handles all database operations
"""

from config.db_config import get_db_connection
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Database:
    @staticmethod
    def execute_query(query, params=None, fetch=False):
        """Execute database query"""
        connection = get_db_connection()
        if not connection:
            return None

        cursor = connection.cursor(dictionary=True) if fetch else connection.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch:
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount

            return result

        except Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def register_user(name, email, password, age=None, medical_history=None, allergies=None):
        """Register a new user"""
        hashed_password = generate_password_hash(password)

        query = """
            INSERT INTO users (name, email, password, age, medical_history, allergies)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = (name, email, hashed_password, age, medical_history, allergies)
        result = Database.execute_query(query, params)

        return result > 0 if result is not None else False

    @staticmethod
    def login_user(email, password):
        """Verify user login"""
        query = "SELECT id, name, email, password FROM users WHERE email = %s"
        result = Database.execute_query(query, (email,), fetch=True)

        if result and len(result) > 0:
            user = result[0]
            if check_password_hash(user['password'], password):
                return {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email']
                }

        return None

    @staticmethod
    def get_user_by_id(user_id):
        """Get user information by ID"""
        query = "SELECT id, name, email, age, medical_history, allergies FROM users WHERE id = %s"
        result = Database.execute_query(query, (user_id,), fetch=True)

        return result[0] if result else None

    @staticmethod
    def get_user_by_email(email):
        """Check if email already exists"""
        query = "SELECT id FROM users WHERE email = %s"
        result = Database.execute_query(query, (email,), fetch=True)

        return len(result) > 0 if result else False

    @staticmethod
    def save_health_record(user_id, eye_status, tongue_status, posture_status, 
                          speech_status, health_score, predicted_condition,
                          nutrition_info=None, maintenance_calories=None, 
                          target_calories=None, meal_plan=None, condition_recommendations=None):
        """Save health analysis record"""
        query = """
            INSERT INTO health_records 
            (user_id, eye_status, tongue_status, posture_status, speech_status, health_score, predicted_condition,
             height_cm, weight_kg, age_years, gender, activity_level, goal, maintenance_calories, target_calories, meal_plan, condition_recommendations)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Extract nutrition info
        height_cm = nutrition_info.get('height') if nutrition_info else None
        weight_kg = nutrition_info.get('weight') if nutrition_info else None
        age_years = nutrition_info.get('age') if nutrition_info else None
        gender = nutrition_info.get('gender') if nutrition_info else None
        activity_level = nutrition_info.get('activity_level') if nutrition_info else None
        goal = nutrition_info.get('goal') if nutrition_info else None

        # Convert meal_plan and condition_recommendations to JSON strings
        import json
        meal_plan_json = json.dumps(meal_plan) if meal_plan else None
        condition_recommendations_json = json.dumps(condition_recommendations) if condition_recommendations else None

        params = (user_id, eye_status, tongue_status, posture_status, 
                 speech_status, health_score, predicted_condition,
                 height_cm, weight_kg, age_years, gender, activity_level, goal,
                 maintenance_calories, target_calories, meal_plan_json, condition_recommendations_json)

        connection = get_db_connection()
        if not connection:
            return None

        cursor = connection.cursor()

        try:
            cursor.execute(query, params)
            connection.commit()
            
            # Get the last inserted ID from the same connection
            last_id = cursor.lastrowid
            return last_id if last_id > 0 else None

        except Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def save_diet_recommendation(record_id, breakfast, lunch, dinner, water_intake):
        """Save diet recommendation"""
        query = """
            INSERT INTO diet_recommendations 
            (record_id, breakfast, lunch, dinner, water_intake)
            VALUES (%s, %s, %s, %s, %s)
        """

        params = (record_id, breakfast, lunch, dinner, water_intake)
        result = Database.execute_query(query, params)

        return result > 0 if result is not None else False

    @staticmethod
    def get_health_history(user_id, limit=10):
        """Get user's health history"""
        query = """
            SELECT * FROM health_records 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """

        return Database.execute_query(query, (user_id, limit), fetch=True)

    @staticmethod
    def get_health_record(record_id):
        """Get specific health record"""
        query = "SELECT * FROM health_records WHERE id = %s"
        result = Database.execute_query(query, (record_id,), fetch=True)

        if result:
            record = result[0]
            # Parse JSON fields
            import json
            if record.get('meal_plan'):
                try:
                    record['meal_plan'] = json.loads(record['meal_plan'])
                except:
                    record['meal_plan'] = None
            
            if record.get('condition_recommendations'):
                try:
                    record['condition_recommendations'] = json.loads(record['condition_recommendations'])
                except:
                    record['condition_recommendations'] = None
            
            return record
        return None

    @staticmethod
    def get_diet_recommendation(record_id):
        """Get diet recommendation for a health record"""
        query = "SELECT * FROM diet_recommendations WHERE record_id = %s"
        result = Database.execute_query(query, (record_id,), fetch=True)

        return result[0] if result else None

    @staticmethod
    def get_latest_health_record(user_id):
        """Get latest health record for user"""
        query = """
            SELECT * FROM health_records 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """

        result = Database.execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def update_user_info(user_id, age=None, medical_history=None, allergies=None):
        """Update user information"""
        updates = []
        params = []

        if age is not None:
            updates.append("age = %s")
            params.append(age)

        if medical_history is not None:
            updates.append("medical_history = %s")
            params.append(medical_history)

        if allergies is not None:
            updates.append("allergies = %s")
            params.append(allergies)

        if not updates:
            return False

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"

        result = Database.execute_query(query, params)
        return result > 0 if result is not None else False

    @staticmethod
    def get_health_statistics(user_id):
        """Get health statistics for user"""
        query = """
            SELECT 
                COUNT(*) as total_records,
                AVG(health_score) as avg_health_score,
                MAX(health_score) as best_score,
                MIN(health_score) as worst_score
            FROM health_records 
            WHERE user_id = %s
        """

        result = Database.execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None
