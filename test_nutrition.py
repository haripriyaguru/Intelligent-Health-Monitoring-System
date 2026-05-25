"""
Test Nutrition Modules
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from ml.nutrition.calorie_calculator import CalorieCalculator
    from ml.nutrition.usda_api import USDAAPI
    from ml.nutrition.meal_planner import MealPlanner
    print("✓ Successfully imported nutrition modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_calorie_calculator():
    """Test calorie calculations"""
    print("Testing Calorie Calculator...")

    calculator = CalorieCalculator()

    # Test BMR calculation
    bmr = calculator.calculate_bmr(70, 175, 30, 'male')
    print(f"BMR for 70kg, 175cm, 30yo male: {bmr} calories")

    # Test maintenance calories
    maintenance = calculator.calculate_maintenance_calories(70, 175, 30, 'male', 'moderate')
    print(f"Maintenance calories: {maintenance}")

    # Test goal adjustment
    target = calculator.adjust_calories(maintenance, 'loss')
    print(f"Target calories for weight loss: {target}")

    # Test macros
    macros = calculator.calculate_macros(target)
    print(f"Macronutrients: {macros}")

def test_usda_api():
    """Test USDA API"""
    print("\nTesting USDA API...")

    api = USDAAPI()

    # Test food search
    results = api.search_food('chicken breast', page_size=3)
    print(f"Found {len(results)} chicken breast results")
    if results:
        print(f"First result: {results[0]['name']} - {results[0]['calories']} calories")

def test_meal_planner():
    """Test meal planner"""
    print("\nTesting Meal Planner...")

    planner = MealPlanner()

    # Test meal plan generation
    meal_plan = planner.generate_meal_plan(2000, ['eye_fatigue'])
    print(f"Generated meal plan with {len(meal_plan['breakfast'])} breakfast items")
    print(f"Total calories: {meal_plan['total_calories']}")

if __name__ == "__main__":
    test_calorie_calculator()
    test_usda_api()
    test_meal_planner()
    print("\nAll tests completed!")