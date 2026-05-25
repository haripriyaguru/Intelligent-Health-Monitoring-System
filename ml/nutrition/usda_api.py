"""
USDA FoodData Central API Integration
Fetches nutritional data for foods using USDA API
"""

import requests
import time
from typing import Dict, List, Optional

class USDAAPI:
    """Interface to USDA FoodData Central API"""

    BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
    API_KEY = "fVe1aHfREN5uh4ytoQKAaVrbr7xxVs1z6lNb7H10"

    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def search_food(self, query: str, page_size: int = 10) -> List[Dict]:
        """
        Search for foods using USDA API

        Args:
            query (str): Food search query
            page_size (int): Number of results to return

        Returns:
            List[Dict]: List of food items with nutritional data
        """
        # Check cache first
        cache_key = f"{query}_{page_size}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            self._rate_limit()

            params = {
                'api_key': self.API_KEY,
                'query': query,
                'pageSize': page_size,
                'dataType': ['Foundation', 'SR Legacy']  # Use reliable data sources
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            foods = []

            for food in data.get('foods', []):
                food_data = self._extract_nutrients(food)
                if food_data:
                    foods.append(food_data)

            # Cache the results
            self.cache[cache_key] = foods
            return foods

        except requests.exceptions.RequestException as e:
            print(f"USDA API request failed: {e}")
            return []
        except Exception as e:
            print(f"Error processing USDA API response: {e}")
            return []

    def _extract_nutrients(self, food_data: Dict) -> Optional[Dict]:
        """
        Extract nutritional information from USDA food data

        Args:
            food_data (Dict): Raw food data from USDA API

        Returns:
            Dict: Processed nutritional data
        """
        try:
            food_info = {
                'name': food_data.get('description', ''),
                'calories': 0,
                'protein': 0,
                'carbohydrates': 0,
                'fat': 0,
                'fiber': 0,
                'vitamins': {},
                'minerals': {}
            }

            # Extract nutrients
            for nutrient in food_data.get('foodNutrients', []):
                nutrient_name = nutrient.get('nutrientName', '').lower()
                value = nutrient.get('value', 0) or 0
                unit = nutrient.get('unitName', '')

                # Energy/Calories
                if 'energy' in nutrient_name and 'kcal' in unit.lower():
                    food_info['calories'] = value
                elif nutrient_name == 'protein':
                    food_info['protein'] = value
                elif 'carbohydrate' in nutrient_name:
                    food_info['carbohydrates'] = value
                elif 'total lipid' in nutrient_name or 'fat' in nutrient_name:
                    food_info['fat'] = value
                elif 'fiber' in nutrient_name:
                    food_info['fiber'] = value

                # Vitamins
                elif 'vitamin a' in nutrient_name:
                    food_info['vitamins']['vitamin_a'] = value
                elif 'vitamin c' in nutrient_name:
                    food_info['vitamins']['vitamin_c'] = value
                elif 'vitamin d' in nutrient_name:
                    food_info['vitamins']['vitamin_d'] = value
                elif 'vitamin e' in nutrient_name:
                    food_info['vitamins']['vitamin_e'] = value
                elif 'vitamin k' in nutrient_name:
                    food_info['vitamins']['vitamin_k'] = value
                elif 'thiamin' in nutrient_name or 'vitamin b1' in nutrient_name:
                    food_info['vitamins']['thiamin'] = value
                elif 'riboflavin' in nutrient_name or 'vitamin b2' in nutrient_name:
                    food_info['vitamins']['riboflavin'] = value
                elif 'niacin' in nutrient_name or 'vitamin b3' in nutrient_name:
                    food_info['vitamins']['niacin'] = value

                # Minerals
                elif 'calcium' in nutrient_name:
                    food_info['minerals']['calcium'] = value
                elif 'iron' in nutrient_name:
                    food_info['minerals']['iron'] = value
                elif 'magnesium' in nutrient_name:
                    food_info['minerals']['magnesium'] = value
                elif 'potassium' in nutrient_name:
                    food_info['minerals']['potassium'] = value
                elif 'sodium' in nutrient_name:
                    food_info['minerals']['sodium'] = value
                elif 'zinc' in nutrient_name:
                    food_info['minerals']['zinc'] = value

            # Only return if we have basic nutritional data
            if food_info['calories'] > 0 and (food_info['protein'] > 0 or food_info['carbohydrates'] > 0 or food_info['fat'] > 0):
                return food_info

        except Exception as e:
            print(f"Error extracting nutrients: {e}")

        return None

    def get_foods_by_category(self, category: str, count: int = 5) -> List[Dict]:
        """
        Get foods from a specific category

        Args:
            category (str): Food category (e.g., 'vegetables', 'proteins', 'fruits')
            count (int): Number of foods to return

        Returns:
            List[Dict]: List of foods in the category
        """
        category_queries = {
            'proteins': ['chicken curry', 'fish curry', 'egg curry', 'dahl', 'chickpea curry'],
            'vegetables': ['sambar', 'aviyal', 'poriyal', 'rasam', 'coconut chutney'],
            'fruits': ['mango', 'banana', 'papaya', 'jackfruit', 'guava'],
            'grains': ['rice', 'dosa', 'idli', 'chapati', 'parotta'],
            'dairy': ['curd', 'buttermilk', 'lassi', 'rasam', 'coconut milk']
        }

        if category not in category_queries:
            return []

        foods = []
        queries = category_queries[category][:2]  # Use first 2 queries to avoid too many API calls

        for query in queries:
            results = self.search_food(query, page_size=count//2 + 1)
            foods.extend(results[:count//2 + 1])

        return foods[:count]