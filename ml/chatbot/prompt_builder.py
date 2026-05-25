"""
Prompt Builder for Medical Chatbot
Builds structured prompts for the AI medical assistant
"""

def build_health_prompt(user_question, health_data):
    """
    Build a structured prompt for the medical chatbot using health analysis data

    Args:
        user_question (str): The user's question
        health_data (dict): Health analysis results from the database

    Returns:
        str: Formatted prompt for the AI model
    """

    # Extract health data with defaults
    eye_status = health_data.get('eye_status', 'Normal')
    tongue_status = health_data.get('tongue_status', 'Healthy')
    posture_status = health_data.get('posture_status', 'Good')
    speech_status = health_data.get('speech_status', 'Normal')
    health_score = health_data.get('health_score', 75)
    predicted_condition = health_data.get('predicted_condition', 'Good')

    # Build the prompt
    prompt = f"""You are an AI healthcare assistant providing general health information and guidance.

IMPORTANT SAFETY INSTRUCTIONS:
- You are NOT a doctor and cannot provide medical diagnosis or prescriptions
- Always recommend consulting healthcare professionals for medical concerns
- Provide only general health information and lifestyle suggestions
- Never give specific medical advice or treatment recommendations

USER HEALTH REPORT:
Eye condition: {eye_status}
Tongue condition: {tongue_status}
Posture status: {posture_status}
Speech stress level: {speech_status}
Overall health score: {health_score}/100
Predicted condition: {predicted_condition}

Based on the user's health analysis, provide helpful general guidance about:
- Possible causes of detected conditions
- General lifestyle improvements
- Basic wellness tips
- When to seek professional medical advice

USER QUESTION:
{user_question}

Please provide a helpful, informative response based on the health data above."""

    return prompt