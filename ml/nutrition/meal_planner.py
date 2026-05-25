"""
Meal Planner Module
Generates personalized meal plans based on calorie needs and health conditions
"""

import random
from typing import Dict, List, Optional
from .calorie_calculator import CalorieCalculator
from .usda_api import USDAAPI

class MealPlanner:
    """Generate personalized meal plans using USDA nutritional data"""

    def __init__(self):
        self.calculator = CalorieCalculator()
        self.usda_api = USDAAPI()

    def _calculate_total_calories(self, meal_plan: Dict) -> float:
        """Calculate total calories in meal plan"""
        total = 0

        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            if meal_type in meal_plan:
                for food in meal_plan[meal_type]:
                    total += food.get('calories', 0)

        return round(total, 2)

    def _calculate_nutritional_summary(self, meal_plan: Dict) -> Dict:
        """
        Calculate comprehensive nutritional summary for the meal plan

        Args:
            meal_plan (Dict): Complete meal plan

        Returns:
            Dict: Nutritional summary with vitamins and minerals
        """
        summary = {
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'total_fiber': 0,
            'vitamins': {},
            'minerals': {}
        }

        # Aggregate nutrients from all meals
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            if meal_type in meal_plan:
                for food in meal_plan[meal_type]:
                    summary['total_calories'] += food.get('calories', 0)
                    summary['total_protein'] += food.get('protein', 0)
                    summary['total_carbs'] += food.get('carbohydrates', 0)
                    summary['total_fat'] += food.get('fat', 0)
                    summary['total_fiber'] += food.get('fiber', 0)

                    # Aggregate vitamins
                    for vitamin, amount in food.get('vitamins', {}).items():
                        if vitamin not in summary['vitamins']:
                            summary['vitamins'][vitamin] = 0
                        summary['vitamins'][vitamin] += amount

                    # Aggregate minerals
                    for mineral, amount in food.get('minerals', {}).items():
                        if mineral not in summary['minerals']:
                            summary['minerals'][mineral] = 0
                        summary['minerals'][mineral] += amount

        return summary

    def generate_meal_plan(self, target_calories: float, conditions: List[str] = None) -> Dict:
        """
        Generate a detailed daily meal plan with comprehensive nutritional information

        Args:
            target_calories (float): Daily calorie target
            conditions (List[str]): Health conditions detected by AI

        Returns:
            Dict: Detailed meal plan with breakfast, lunch, dinner, snacks
        """
        if conditions is None:
            conditions = []

        # Calculate meal calorie distribution
        meal_distribution = {
            'breakfast': target_calories * 0.30,  # 30%
            'lunch': target_calories * 0.40,      # 40%
            'dinner': target_calories * 0.25,     # 25%
            'snacks': target_calories * 0.05      # 5%
        }

        # Get detailed foods for each meal type
        meal_plan = {}

        # Breakfast
        meal_plan['breakfast'] = self._plan_breakfast(meal_distribution['breakfast'], conditions)

        # Lunch
        meal_plan['lunch'] = self._plan_lunch(meal_distribution['lunch'], conditions)

        # Dinner
        meal_plan['dinner'] = self._plan_dinner(meal_distribution['dinner'], conditions)

        # Snacks
        meal_plan['snacks'] = self._plan_snacks(meal_distribution['snacks'], conditions)

        # Calculate totals
        meal_plan['total_calories'] = self._calculate_total_calories(meal_plan)
        meal_plan['macros'] = self.calculator.calculate_macros(target_calories)
        meal_plan['nutritional_summary'] = self._calculate_nutritional_summary(meal_plan)

        return meal_plan

    def _plan_breakfast(self, calories: float, conditions: List[str]) -> List[Dict]:
        """Plan detailed breakfast meal with comprehensive nutritional data"""
        breakfast_foods = []
        current_calories = 0

        # Define breakfast food categories with specific items
        breakfast_options = {
            'proteins': [
                'egg curry', 'chicken keema', 'fish fry', 'prawn masala', 'mutton curry'
            ],
            'grains': [
                'idli', 'dosa', 'pongal', 'upma', 'poori', 'chapati', 'parotta'
            ],
            'fruits': [
                'banana', 'mango', 'papaya', 'jackfruit', 'guava', 'pineapple'
            ],
            'dairy': [
                'curd', 'buttermilk', 'lassi', 'milk', 'coconut milk'
            ],
            'vegetables': [
                'sambar', 'aviyal', 'poriyal', 'rasam', 'coconut chutney'
            ]
        }

        # Add condition-specific foods
        if 'eye_fatigue' in conditions:
            breakfast_options['eye_health'] = ['carrots', 'spinach', 'eggs', 'sweet potato']
        if 'dehydration' in conditions:
            breakfast_options['hydration'] = ['watermelon', 'orange juice', 'cucumber', 'celery']
        if 'digestion' in conditions:
            breakfast_options['digestive'] = ['oatmeal', 'banana', 'yogurt', 'papaya']

        # Select foods to reach calorie target - allow slight overshoot
        max_attempts = 25
        attempts = 0
        
        while current_calories < calories and attempts < max_attempts:
            category = random.choice(list(breakfast_options.keys()))
            food_query = random.choice(breakfast_options[category])
            results = self.usda_api.search_food(food_query, page_size=5)
            if results:
                # Filter foods that stay close to target (within 5% overshoot allowed)
                remaining = calories - current_calories
                suitable = [f for f in results if 50 <= f.get('calories', 0) <= remaining * 1.05]
                if suitable:
                    # Sort by calories descending to fit larger foods when possible
                    suitable.sort(key=lambda x: x.get('calories', 0), reverse=True)
                    food = suitable[0]  # Take the largest suitable food
                    breakfast_foods.append(food)
                    current_calories += food['calories']
            attempts += 1

        return breakfast_foods

    def _plan_lunch(self, calories: float, conditions: List[str]) -> List[Dict]:
        """Plan detailed lunch meal with comprehensive nutritional data"""
        lunch_foods = []
        current_calories = 0

        # Define lunch food categories with specific items
        lunch_options = {
            'proteins': [
                'chicken curry', 'mutton curry', 'fish curry', 'prawn masala', 'egg curry',
                'chicken biryani', 'mutton biryani', 'fish biryani'
            ],
            'vegetables': [
                'sambar', 'aviyal', 'poriyal', 'rasam', 'coconut chutney', 'pickle',
                'mixed vegetable curry', 'bhindi masala', 'aloo gobi'
            ],
            'grains': [
                'rice', 'biryani rice', 'jeera rice', 'pulao', 'chapati', 'naan', 'parotta'
            ],
            'dairy': [
                'curd', 'buttermilk', 'lassi', 'raita'
            ],
            'legumes': [
                'dahl', 'chana masala', 'rajma', 'moong dahl', 'toor dahl'
            ]
        }

        # Add condition-specific foods
        if 'eye_fatigue' in conditions:
            lunch_options['eye_health'] = ['salmon', 'spinach', 'sweet potato', 'carrots', 'kale']
        if 'dehydration' in conditions:
            lunch_options['hydration'] = ['cucumber', 'celery', 'lettuce', 'watermelon', 'tomato']
        if 'digestion' in conditions:
            lunch_options['digestive'] = ['yogurt', 'fermented foods', 'fiber rich vegetables', 'beans']

        # Select foods to reach calorie target - allow slight overshoot
        max_attempts = 30
        attempts = 0
        
        while current_calories < calories and attempts < max_attempts:
            category = random.choice(list(lunch_options.keys()))
            food_query = random.choice(lunch_options[category])
            results = self.usda_api.search_food(food_query, page_size=5)
            if results:
                # Filter foods that stay close to target (within 5% overshoot allowed)
                remaining = calories - current_calories
                suitable = [f for f in results if 50 <= f.get('calories', 0) <= remaining * 1.05]
                if suitable:
                    # Sort by calories descending to fit larger foods when possible
                    suitable.sort(key=lambda x: x.get('calories', 0), reverse=True)
                    food = suitable[0]  # Take the largest suitable food
                    lunch_foods.append(food)
                    current_calories += food['calories']
            attempts += 1

        return lunch_foods

    def _plan_dinner(self, calories: float, conditions: List[str]) -> List[Dict]:
        """Plan detailed dinner meal with comprehensive nutritional data"""
        dinner_foods = []
        current_calories = 0

        # Define dinner food categories with specific items
        dinner_options = {
            'proteins': [
                'chicken curry', 'mutton curry', 'fish curry', 'prawn masala', 'egg curry',
                'chicken fry', 'mutton fry', 'fish fry'
            ],
            'vegetables': [
                'sambar', 'aviyal', 'poriyal', 'rasam', 'coconut chutney', 'pickle',
                'mixed vegetable curry', 'bhindi masala', 'aloo gobi', 'cabbage thoran'
            ],
            'grains': [
                'rice', 'jeera rice', 'pulao', 'chapati', 'naan', 'parotta', 'appam'
            ],
            'dairy': [
                'curd', 'buttermilk', 'lassi', 'raita'
            ],
            'legumes': [
                'dahl', 'chana masala', 'rajma', 'moong dahl', 'toor dahl'
            ]
        }

        # Add condition-specific foods
        if 'eye_fatigue' in conditions:
            dinner_options['eye_health'] = ['salmon', 'kale', 'sweet potato', 'carrots', 'spinach']
        if 'dehydration' in conditions:
            dinner_options['hydration'] = ['cucumber', 'celery', 'lettuce', 'watermelon', 'tomato']
        if 'digestion' in conditions:
            dinner_options['digestive'] = ['fermented foods', 'fiber rich vegetables', 'probiotic rich foods']

        # Select foods to reach calorie target - allow slight overshoot
        max_attempts = 30
        attempts = 0
        
        while current_calories < calories and attempts < max_attempts:
            category = random.choice(list(dinner_options.keys()))
            food_query = random.choice(dinner_options[category])
            results = self.usda_api.search_food(food_query, page_size=5)
            if results:
                # Filter foods that stay close to target (within 5% overshoot allowed)
                remaining = calories - current_calories
                suitable = [f for f in results if 50 <= f.get('calories', 0) <= remaining * 1.05]
                if suitable:
                    # Sort by calories descending to fit larger foods when possible
                    suitable.sort(key=lambda x: x.get('calories', 0), reverse=True)
                    food = suitable[0]  # Take the largest suitable food
                    dinner_foods.append(food)
                    current_calories += food['calories']
            attempts += 1

        return dinner_foods

    def _plan_snacks(self, calories: float, conditions: List[str]) -> List[Dict]:
        """Plan detailed snacks with comprehensive nutritional data"""
        snack_foods = []
        current_calories = 0

        # Define snack food categories with specific items
        snack_options = {
            'fruits': [
                'banana', 'mango', 'papaya', 'jackfruit', 'guava', 'pineapple',
                'orange', 'apple', 'grapes'
            ],
            'nuts_seeds': [
                'peanuts', 'cashews', 'almonds', 'pistachios', 'coconut'
            ],
            'dairy': [
                'curd', 'buttermilk', 'lassi', 'yogurt', 'milk'
            ],
            'vegetables': [
                'cucumber', 'carrot', 'beetroot', 'tomato'
            ],
            'traditional': [
                'murukku', 'mixture', 'chips', 'banana chips', 'jaggery'
            ]
        }

        # Add condition-specific foods
        if 'eye_fatigue' in conditions:
            snack_options['eye_health'] = ['carrots', 'berries', 'eggs']
        if 'dehydration' in conditions:
            snack_options['hydration'] = ['watermelon', 'cucumber', 'orange']
        if 'digestion' in conditions:
            snack_options['digestive'] = ['banana', 'yogurt', 'papaya']

        # Select foods to reach calorie target - stay within exact target
        max_attempts = 25
        attempts = 0
        
        while current_calories < calories and attempts < max_attempts:
            category = random.choice(list(snack_options.keys()))
            food_query = random.choice(snack_options[category])
            results = self.usda_api.search_food(food_query, page_size=3)
            if results:
                # Filter foods that stay close to target (within 5% overshoot allowed)
                remaining = calories - current_calories
                suitable = [f for f in results if 50 <= f.get('calories', 0) <= remaining * 1.05]
                if suitable:
                    # Sort by calories descending to fit larger foods when possible
                    suitable.sort(key=lambda x: x.get('calories', 0), reverse=True)
                    food = suitable[0]  # Take the largest suitable food
                    snack_foods.append(food)
                    current_calories += food['calories']
            attempts += 1

        return snack_foods

    def _select_best_food(self, foods: List[Dict], category: str) -> Optional[Dict]:
        """
        Select the most nutritionally complete food from a list of options

        Args:
            foods (List[Dict]): List of food options
            category (str): Food category for selection criteria

        Returns:
            Dict: Best food choice or None
        """
        if not foods:
            return None

        # Define scoring criteria based on category
        category_criteria = {
            'proteins': lambda f: f.get('protein', 0) * 2 + f.get('calories', 0) * 0.1,
            'vegetables': lambda f: f.get('fiber', 0) * 3 + len(f.get('vitamins', {})) + len(f.get('minerals', {})),
            'fruits': lambda f: len(f.get('vitamins', {})) * 2 + f.get('fiber', 0),
            'grains': lambda f: f.get('fiber', 0) * 2 + f.get('protein', 0),
            'healthy_fats': lambda f: f.get('fat', 0) + len(f.get('vitamins', {})),
            'dairy': lambda f: f.get('protein', 0) + f.get('calories', 0) * 0.1 + len(f.get('minerals', {})),
            'nuts_seeds': lambda f: f.get('fat', 0) + f.get('protein', 0) + len(f.get('minerals', {})),
            'eye_health': lambda f: (f.get('vitamins', {}).get('vitamin_a', 0) + f.get('vitamins', {}).get('vitamin_c', 0)) * 2,
            'hydration': lambda f: f.get('calories', 0) * 0.05,  # Lower calorie foods for hydration
            'digestive': lambda f: f.get('fiber', 0) * 3 + f.get('protein', 0)
        }

        # Score each food
        scored_foods = []
        for food in foods:
            score = 0
            if category in category_criteria:
                try:
                    score = category_criteria[category](food)
                except:
                    score = food.get('calories', 0) * 0.1  # Fallback scoring

            # Bonus for having vitamins and minerals
            vitamins_count = len(food.get('vitamins', {}))
            minerals_count = len(food.get('minerals', {}))
            score += vitamins_count * 0.5 + minerals_count * 0.5

            scored_foods.append((food, score))

        # Return the highest scoring food
        if scored_foods:
            scored_foods.sort(key=lambda x: x[1], reverse=True)
            return scored_foods[0][0]

        return foods[0]  # Fallback to first food

    def get_condition_based_recommendations(self, conditions: List[str]) -> Dict[str, List[str]]:
        """
        Get food recommendations based on detected conditions

        Args:
            conditions (List[str]): Detected health conditions

        Returns:
            Dict[str, List[str]]: Condition-based food recommendations
        """
        recommendations = {}

        if 'eye_fatigue' in conditions:
            recommendations['eye_fatigue'] = [
                'Carrots (Vitamin A)',
                'Spinach (Lutein)',
                'Salmon (Omega-3)',
                'Eggs (Lutein)',
                'Sweet potatoes (Vitamin A)'
            ]

        if 'dehydration' in conditions:
            recommendations['dehydration'] = [
                'Watermelon (high water content)',
                'Cucumber (hydrating)',
                'Oranges (electrolytes)',
                'Coconut water (electrolytes)',
                'Celery (water-rich)'
            ]

        if 'digestion' in conditions:
            recommendations['digestion'] = [
                'Oatmeal (fiber)',
                'Brown rice (fiber)',
                'Broccoli (fiber)',
                'Beans (fiber)',
                'Yogurt (probiotics)'
            ]

        return recommendations

    def create_fallback_meal_plan(self, target_calories: float) -> Dict:
        """
        Create a fallback meal plan when API is unavailable

        Args:
            target_calories (float): Daily calorie target

        Returns:
            Dict: Basic meal plan
        """
        return {
            'breakfast': [
                {'name': 'Oatmeal with banana', 'calories': target_calories * 0.15, 'protein': 5, 'carbohydrates': 30, 'fat': 3},
                {'name': 'Greek yogurt', 'calories': target_calories * 0.10, 'protein': 15, 'carbohydrates': 5, 'fat': 5},
                {'name': 'Orange', 'calories': target_calories * 0.05, 'protein': 1, 'carbohydrates': 15, 'fat': 0}
            ],
            'lunch': [
                {'name': 'Grilled chicken breast', 'calories': target_calories * 0.20, 'protein': 30, 'carbohydrates': 0, 'fat': 5},
                {'name': 'Brown rice', 'calories': target_calories * 0.15, 'protein': 3, 'carbohydrates': 35, 'fat': 1},
                {'name': 'Broccoli', 'calories': target_calories * 0.05, 'protein': 3, 'carbohydrates': 5, 'fat': 0}
            ],
            'dinner': [
                {'name': 'Baked salmon', 'calories': target_calories * 0.15, 'protein': 25, 'carbohydrates': 0, 'fat': 15},
                {'name': 'Sweet potato', 'calories': target_calories * 0.08, 'protein': 2, 'carbohydrates': 20, 'fat': 0},
                {'name': 'Green beans', 'calories': target_calories * 0.02, 'protein': 2, 'carbohydrates': 5, 'fat': 0}
            ],
            'snacks': [
                {'name': 'Apple', 'calories': target_calories * 0.03, 'protein': 0, 'carbohydrates': 15, 'fat': 0},
                {'name': 'Handful of almonds', 'calories': target_calories * 0.02, 'protein': 3, 'carbohydrates': 3, 'fat': 8}
            ],
            'total_calories': target_calories,
            'macros': self.calculator.calculate_macros(target_calories)
        }