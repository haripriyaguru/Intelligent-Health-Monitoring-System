"""
Diet Recommendation Module
Provides personalized diet recommendations based on health analysis
"""

class DietRecommendation:
    def __init__(self):
        """Initialize diet recommendation engine"""
        self.recommendations_database = {
            'dehydration': {
                'primary_issue': 'Dehydration Detected',
                'breakfast': [
                    'Smoothie with watermelon and strawberries',
                    'Oatmeal with citrus fruits',
                    'Herbal tea with honey'
                ],
                'lunch': [
                    'Cucumber and tomato salad with olive oil',
                    'Soup with high water content vegetables',
                    'Grilled fish with lemon and vegetables'
                ],
                'dinner': [
                    'Steamed vegetables with brown rice',
                    'Zucchini noodles with tomato sauce',
                    'Boiled vegetables with herbs'
                ],
                'water_intake': 10,
                'water_sources': [
                    'Plain water: 8-10 glasses',
                    'Herbal teas: 2-3 cups',
                    'Fruits: watermelon, cucumber, oranges',
                    'Coconut water: 1-2 glasses',
                    'Buttermilk: 1 glass'
                ],
                'avoid': ['Caffeine', 'Alcohol', 'Salty foods', 'Fried foods']
            },
            'digestion': {
                'primary_issue': 'Digestion Issues',
                'breakfast': [
                    'Whole grain toast with berries',
                    'Gram flour pancakes',
                    'Millets with milk and honey'
                ],
                'lunch': [
                    'Brown rice with lentils and vegetables',
                    'Barley soup with vegetables',
                    'Whole wheat bread with steamed vegetables'
                ],
                'dinner': [
                    'Light vegetable curry with roti',
                    'Moong dal with rice',
                    'Soup with oats and vegetables'
                ],
                'water_intake': 8,
                'fiber_recommendations': [
                    'Whole grains: rice, wheat, oats, barley',
                    'Legumes: lentils, beans, chickpeas',
                    'Vegetables: leafy greens, broccoli, carrots',
                    'Fruits: apples, pears, berries with skin',
                    'Seeds: flax seeds, chia seeds'
                ],
                'avoid': ['Spicy food', 'Fatty meats', 'Processed foods', 'Sugary drinks']
            },
            'stress': {
                'primary_issue': 'Stress Detected',
                'breakfast': [
                    'Yogurt with granola and nuts',
                    'Whole grain cereal with almonds',
                    'Egg with whole wheat toast'
                ],
                'lunch': [
                    'Grilled chicken with sweet potato',
                    'Fish with brown rice and vegetables',
                    'Nutritious salad with nuts'
                ],
                'dinner': [
                    'Steamed fish with vegetables',
                    'Vegetable stir-fry with tofu',
                    'Light curry with basmati rice'
                ],
                'water_intake': 8,
                'stress_relief_foods': [
                    'Dark chocolate (70% cocoa)',
                    'Nuts and seeds: almonds, walnuts',
                    'Green tea: 2-3 cups daily',
                    'Fatty fish: omega-3 rich',
                    'Chamomile tea: evening relaxation'
                ],
                'avoid': ['Caffeine overuse', 'Sugary foods', 'Heavy meals late night']
            },
            'fatigue': {
                'primary_issue': 'Fatigue Detected',
                'breakfast': [
                    'Iron-rich cereal with milk',
                    'Eggs with whole grain bread',
                    'Smoothie with banana and nuts'
                ],
                'lunch': [
                    'Red meat or chicken with vegetables',
                    'Lentil soup with vegetables',
                    'Fish with leafy greens'
                ],
                'dinner': [
                    'Grilled chicken with brown rice',
                    'Vegetable curry with legumes',
                    'Beans and whole grain bread'
                ],
                'water_intake': 8,
                'energy_boosting_foods': [
                    'Iron sources: red meat, spinach, lentils',
                    'Protein: chicken, fish, eggs, legumes',
                    'Complex carbs: whole grains, oats',
                    'B vitamins: fortified cereals, meat, vegetables',
                    'Fruits: bananas, dates, oranges'
                ],
                'avoid': ['Refined sugars', 'Excessive caffeine', 'Heavy fried foods']
            },
            'excellent_health': {
                'primary_issue': 'Excellent Health Status',
                'breakfast': [
                    'Mixed berries with yogurt',
                    'Whole grain toast with avocado',
                    'Protein smoothie with fruits'
                ],
                'lunch': [
                    'Balanced meal with grains, protein, and vegetables',
                    'Buddha bowl with diverse foods',
                    'Whole grain sandwich with lean protein'
                ],
                'dinner': [
                    'Grilled fish or chicken with vegetables',
                    'Vegetable and grain combination',
                    'Light curry with lean protein'
                ],
                'water_intake': 8,
                'recommendations': [
                    'Maintain current healthy eating habits',
                    'Continue balanced diet with all food groups',
                    'Stay hydrated with water',
                    'Regular physical activity: 30 mins daily',
                    'Include variety of colorful vegetables'
                ],
                'avoid': []
            }
        }

    def get_recommendations(self, analysis_results: dict):
        """
        Get diet recommendations based on health analysis
        Args:
            analysis_results: Dictionary with health analysis data
        Returns:
            Dict with personalized recommendations
        """
        
        # Determine primary health issue
        health_issue = self._determine_health_issue(analysis_results)
        
        # Get recommendations for the identified issue
        if health_issue in self.recommendations_database:
            rec_data = self.recommendations_database[health_issue]
        else:
            rec_data = self.recommendations_database['excellent_health']

        # Build detailed recommendation
        recommendations = {
            'primary_issue': rec_data['primary_issue'],
            'meal_plan': {
                'breakfast': self._select_meal(rec_data['breakfast']),
                'lunch': self._select_meal(rec_data['lunch']),
                'dinner': self._select_meal(rec_data['dinner']),
                'snacks': self._get_snacks(health_issue)
            },
            'water_intake': {
                'daily_glasses': rec_data.get('water_intake', 8),
                'recommendation': f"Drink {rec_data.get('water_intake', 8)}-10 glasses of water daily",
                'sources': rec_data.get('water_sources', rec_data.get('fiber_recommendations', []))
            },
            'key_nutrients': rec_data.get('energy_boosting_foods', 
                                         rec_data.get('stress_relief_foods',
                                                     rec_data.get('fiber_recommendations',
                                                                 rec_data.get('recommendations', [])))),
            'foods_to_avoid': rec_data.get('avoid', []),
            'tips': self._get_lifestyle_tips(health_issue)
        }

        return recommendations

    def _determine_health_issue(self, analysis_results: dict):
        """Determine the primary health issue from analysis"""
        
        eye_status = analysis_results.get('eye_status', 'Normal').lower()
        tongue_status = analysis_results.get('tongue_status', 'Healthy').lower()
        posture_status = analysis_results.get('posture_status', 'Good').lower()
        speech_status = analysis_results.get('speech_status', 'Normal').lower()
        health_score = analysis_results.get('health_score', 80)

        # Check for specific conditions
        if 'dehydration' in tongue_status or 'dehydration' in analysis_results.get('tongue_message', '').lower():
            return 'dehydration'
        elif 'digestion' in tongue_status or 'digestion' in analysis_results.get('tongue_message', '').lower():
            return 'digestion'
        elif 'stress' in speech_status or 'high stress' in speech_status:
            return 'stress'
        elif 'fatigue' in eye_status or 'strain' in eye_status:
            return 'fatigue'
        elif health_score < 60:
            return 'stress'  # Default to stress recommendations for low scores
        else:
            return 'excellent_health'

    def _select_meal(self, meal_options):
        """Select a meal from options (can be enhanced with user preferences)"""
        if meal_options:
            return meal_options[0]  # Return first option, can be rotated
        return "Balanced meal"

    def _get_snacks(self, health_issue):
        """Get snack recommendations based on health issue"""
        snacks = {
            'dehydration': [
                'Fresh watermelon or citrus fruits',
                'Cucumber slices with light dressing',
                'Herbal tea with honey'
            ],
            'digestion': [
                'Whole grain crackers with healthy spread',
                'Fruit with skin (apple, pear)',
                'Nuts without salt'
            ],
            'stress': [
                'Nuts mix with dark chocolate',
                'Yogurt with berries',
                'Herbal tea'
            ],
            'fatigue': [
                'Banana with almond butter',
                'Mix of nuts and dried fruits',
                'Peanut butter on whole grain bread'
            ],
            'excellent_health': [
                'Mixed nuts and dried fruits',
                'Fresh fruit with yogurt',
                'Whole grain crackers with cheese'
            ]
        }

        return snacks.get(health_issue, snacks['excellent_health'])

    def _get_lifestyle_tips(self, health_issue):
        """Get lifestyle tips based on health issue"""
        tips = {
            'dehydration': [
                'Drink water immediately after waking up',
                'Carry water bottle everywhere',
                'Set reminders to drink water every hour',
                'Avoid prolonged sun exposure',
                'Monitor urine color (should be pale)'
            ],
            'digestion': [
                'Eat slowly and chew thoroughly',
                'Take meals at regular times',
                'Walk 10-15 minutes after meals',
                'Avoid eating late at night',
                'Manage stress with yoga or meditation'
            ],
            'stress': [
                'Practice deep breathing exercises',
                'Meditate for 10 minutes daily',
                'Exercise regularly for 30 minutes',
                'Sleep 7-8 hours nightly',
                'Take breaks every hour'
            ],
            'fatigue': [
                'Get 7-8 hours of quality sleep',
                'Maintain consistent sleep schedule',
                'Exercise regularly (not too intense)',
                'Get sunlight in morning',
                'Manage stress levels'
            ],
            'excellent_health': [
                'Maintain current healthy habits',
                'Exercise 30 minutes daily',
                'Get 7-8 hours of sleep',
                'Continue balanced nutrition',
                'Regular health check-ups'
            ]
        }

        return tips.get(health_issue, tips['excellent_health'])

    def get_meal_plan_for_week(self, health_issue):
        """Generate a week-long meal plan"""
        rec_data = self.recommendations_database.get(health_issue, self.recommendations_database['excellent_health'])
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        week_plan = {}

        for i, day in enumerate(days):
            week_plan[day] = {
                'breakfast': rec_data['breakfast'][i % len(rec_data['breakfast'])],
                'lunch': rec_data['lunch'][i % len(rec_data['lunch'])],
                'dinner': rec_data['dinner'][i % len(rec_data['dinner'])]
            }

        return week_plan
