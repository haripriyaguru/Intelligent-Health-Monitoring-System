"""
Calorie Calculator Module
Calculates Basal Metabolic Rate (BMR) and maintenance calories using Mifflin-St Jeor equation
"""

class CalorieCalculator:
    """Calculate daily calorie needs based on user profile"""

    # Activity level multipliers
    ACTIVITY_LEVELS = {
        'sedentary': 1.2,      # Little or no exercise
        'light': 1.375,        # Light exercise 1-3 days/week
        'moderate': 1.55,      # Moderate exercise 3-5 days/week
        'active': 1.725,       # Hard exercise 6-7 days/week
        'very_active': 1.9     # Very hard exercise & physical job
    }

    @staticmethod
    def calculate_bmr(weight_kg, height_cm, age_years, gender):
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation

        Args:
            weight_kg (float): Weight in kilograms
            height_cm (float): Height in centimeters
            age_years (int): Age in years
            gender (str): 'male' or 'female'

        Returns:
            float: BMR in calories per day
        """
        if gender.lower() == 'male':
            # BMR = (10 × weight) + (6.25 × height) − (5 × age) + 5
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) + 5
        elif gender.lower() == 'female':
            # BMR = (10 × weight) + (6.25 × height) − (5 × age) − 161
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) - 161
        else:
            raise ValueError("Gender must be 'male' or 'female'")

        return round(bmr, 2)

    @staticmethod
    def calculate_maintenance_calories(weight_kg, height_cm, age_years, gender, activity_level):
        """
        Calculate Total Daily Energy Expenditure (maintenance calories)

        Args:
            weight_kg (float): Weight in kilograms
            height_cm (float): Height in centimeters
            age_years (int): Age in years
            gender (str): 'male' or 'female'
            activity_level (str): Activity level key

        Returns:
            float: Maintenance calories per day
        """
        bmr = CalorieCalculator.calculate_bmr(weight_kg, height_cm, age_years, gender)

        if activity_level not in CalorieCalculator.ACTIVITY_LEVELS:
            raise ValueError(f"Invalid activity level. Must be one of: {list(CalorieCalculator.ACTIVITY_LEVELS.keys())}")

        activity_multiplier = CalorieCalculator.ACTIVITY_LEVELS[activity_level]
        maintenance_calories = bmr * activity_multiplier

        return round(maintenance_calories, 2)

    @staticmethod
    def adjust_calories(maintenance_calories, goal):
        """
        Adjust maintenance calories based on weight goal

        Args:
            maintenance_calories (float): Maintenance calories
            goal (str): 'loss', 'maintain', or 'gain'

        Returns:
            float: Target calories per day
        """
        if goal.lower() == 'loss':
            # Weight loss: subtract 500 calories
            target_calories = maintenance_calories - 500
        elif goal.lower() == 'maintain':
            # Maintain weight: use maintenance calories
            target_calories = maintenance_calories
        elif goal.lower() == 'gain':
            # Weight gain: add 500 calories
            target_calories = maintenance_calories + 500
        else:
            raise ValueError("Goal must be 'loss', 'maintain', or 'gain'")

        # Ensure minimum safe calorie intake (1200 for safety)
        return max(round(target_calories, 2), 1200)

    @staticmethod
    def calculate_macros(calories):
        """
        Calculate macronutrient distribution in grams

        Standard ratio: 25% protein, 50% carbs, 25% fat

        Args:
            calories (float): Daily calorie target

        Returns:
            dict: Macronutrient grams
        """
        # Protein: 25% of calories, 4 calories per gram
        protein_grams = (calories * 0.25) / 4

        # Carbohydrates: 50% of calories, 4 calories per gram
        carbs_grams = (calories * 0.50) / 4

        # Fat: 25% of calories, 9 calories per gram
        fat_grams = (calories * 0.25) / 9

        return {
            'protein': round(protein_grams, 1),
            'carbohydrates': round(carbs_grams, 1),
            'fat': round(fat_grams, 1)
        }