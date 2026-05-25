#!/usr/bin/env python
"""Test meal plan generation for 2507 calories"""

from ml.nutrition.meal_planner import MealPlanner

try:
    planner = MealPlanner()
    plan = planner.generate_meal_plan(2507, [])
    
    total = plan['total_calories']
    breakfast = sum(f['calories'] for f in plan.get('breakfast', []))
    lunch = sum(f['calories'] for f in plan.get('lunch', []))
    dinner = sum(f['calories'] for f in plan.get('dinner', []))
    snacks = sum(f['calories'] for f in plan.get('snacks', []))
    
    print("\n=== MEAL PLAN TEST RESULTS ===")
    print(f"Target: 2507 calories")
    print(f"Total Generated: {total:.0f} calories ({total-2507:+.0f})")
    print(f"\nBreakdown:")
    print(f"  Breakfast: target=752, actual={breakfast:.0f} ({breakfast-752:+.0f})")
    print(f"  Lunch: target=1003, actual={lunch:.0f} ({lunch-1003:+.0f})")
    print(f"  Dinner: target=627, actual={dinner:.0f} ({dinner-627:+.0f})")
    print(f"  Snacks: target=125, actual={snacks:.0f} ({snacks-125:+.0f})")
    print(f"\nItem counts:")
    print(f"  Breakfast: {len(plan.get('breakfast', []))} items")
    print(f"  Lunch: {len(plan.get('lunch', []))} items")
    print(f"  Dinner: {len(plan.get('dinner', []))} items")
    print(f"  Snacks: {len(plan.get('snacks', []))} items")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
