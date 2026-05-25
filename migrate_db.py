"""
Database Migration Script
Add nutrition columns to health_records table
"""

from config.db_config import get_db_connection

def migrate_database():
    """Add nutrition columns to health_records table"""
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False

    cursor = connection.cursor()

    try:
        # Check current columns
        cursor.execute("DESCRIBE health_records")
        current_columns = [col[0] for col in cursor.fetchall()]
        print(f"📋 Current columns: {current_columns}")

        # Add missing nutrition columns
        nutrition_columns = [
            ("height_cm", "DECIMAL(5,2)"),
            ("weight_kg", "DECIMAL(5,2)"),
            ("age_years", "INT"),
            ("gender", "VARCHAR(10)"),
            ("activity_level", "VARCHAR(20)"),
            ("goal", "VARCHAR(20)"),
            ("maintenance_calories", "DECIMAL(7,2)"),
            ("target_calories", "DECIMAL(7,2)"),
            ("meal_plan", "JSON"),
            ("condition_recommendations", "JSON")
        ]

        added_columns = []
        for col_name, col_type in nutrition_columns:
            if col_name not in current_columns:
                try:
                    cursor.execute(f"ALTER TABLE health_records ADD COLUMN {col_name} {col_type}")
                    added_columns.append(col_name)
                    print(f"✅ Added column: {col_name}")
                except Exception as e:
                    print(f"❌ Failed to add {col_name}: {e}")

        connection.commit()
        print(f"🎉 Migration completed! Added {len(added_columns)} columns: {added_columns}")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_database()