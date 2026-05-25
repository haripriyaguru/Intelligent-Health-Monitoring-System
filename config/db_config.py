"""
Database Configuration for Health Assistant
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'health_assistant'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def initialize_database():
    """Initialize database and create required tables"""
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return False

    cursor = connection.cursor()

    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                age INT,
                medical_history TEXT,
                allergies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create health records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                eye_status VARCHAR(50),
                tongue_status VARCHAR(50),
                posture_status VARCHAR(50),
                speech_status VARCHAR(50),
                health_score INT,
                predicted_condition VARCHAR(255),
                -- Nutrition fields
                height_cm DECIMAL(5,2),
                weight_kg DECIMAL(5,2),
                age_years INT,
                gender VARCHAR(10),
                activity_level VARCHAR(20),
                goal VARCHAR(20),
                maintenance_calories DECIMAL(7,2),
                target_calories DECIMAL(7,2),
                meal_plan TEXT,
                condition_recommendations JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Create diet recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diet_recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                record_id INT NOT NULL,
                breakfast TEXT,
                lunch TEXT,
                dinner TEXT,
                water_intake INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES health_records(id)
            )
        """)

        connection.commit()
        print("Database initialized successfully!")
        return True

    except Error as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    initialize_database()
