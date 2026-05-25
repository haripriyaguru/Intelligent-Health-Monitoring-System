"""
Medical Chatbot Module
Handles communication with Ollama Llama3 model for medical Q&A
"""

import ollama
from .prompt_builder import build_health_prompt

def ask_medical_llm(question, health_data):
    """
    Send a question to the Ollama Llama3 model with health context

    Args:
        question (str): User's question
        health_data (dict): Health analysis data

    Returns:
        str: AI response or error message
    """

    try:
        # Build the prompt with health context
        prompt = build_health_prompt(question, health_data)

        # Send to Ollama Llama3 model
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract the response content
        if response and "message" in response and "content" in response["message"]:
            return response["message"]["content"]
        else:
            return "Medical assistant is currently unavailable. Please try again later."

    except Exception as e:
        # Handle various errors (Ollama not running, model not available, etc.)
        error_message = str(e).lower()

        if "connection" in error_message or "connect" in error_message:
            return "Medical assistant is currently unavailable. Please ensure Ollama is running and try again later."
        elif "model" in error_message:
            return "Medical assistant model is not available. Please ensure Llama3 model is installed in Ollama."
        else:
            print(f"Chatbot error: {e}")
            return "Medical assistant is currently unavailable. Please try again later."