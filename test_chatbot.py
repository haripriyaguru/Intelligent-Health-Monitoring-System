"""
Test script for the medical chatbot
"""

from ml.chatbot.medical_chatbot import ask_medical_llm

# Test health data
test_health_data = {
    'eye_status': 'Fatigue detected',
    'tongue_status': 'Dry',
    'posture_status': 'Poor',
    'speech_status': 'High stress',
    'health_score': 65,
    'predicted_condition': 'Fatigue'
}

# Test question
test_question = "Why do I feel tired all the time?"

if __name__ == "__main__":
    print("Testing medical chatbot...")
    print(f"Question: {test_question}")
    print(f"Health data: {test_health_data}")
    print("\nResponse:")

    try:
        response = ask_medical_llm(test_question, test_health_data)
        print(response)
    except Exception as e:
        print(f"Error: {e}")