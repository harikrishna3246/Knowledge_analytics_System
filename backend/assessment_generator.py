import json
from groq_client import client

def generate_topic_quiz(topic):
    """
    Generates a 10-question assessment using Groq (LLaMA 3.1).
    Difficulty: 3 Easy, 4 Medium, 3 Hard.
    Includes MCQs and Problem-solving/Coding questions.
    """
    if not client:
        return {"error": "AI Client not initialized."}

    prompt = f"""
    You are an expert assessment generator.
    Generate a 10-question quiz for the topic: '{topic}'.
    
    Difficulty Distribution:
    - 3 Easy MCQs (Basic definitions/concepts)
    - 4 Medium MCQs (Application/Conceptual understanding)
    - 3 Hard Questions (Deep technical analysis, coding snippets, or complex problem-solving)

    Rules:
    - MCQs must have 4 options and 1 correct answer.
    - Coding/Hard questions should require a text-based solution.
    - Ensure questions are unique and challenging.
    - Return ONLY valid JSON.

    Format:
    {{
      "questions": [
        {{
          "id": 1,
          "type": "mcq",
          "difficulty": "easy",
          "question": "What is...",
          "options": ["A", "B", "C", "D"],
          "correct_answer": 0
        }},
        {{
          "id": 8,
          "type": "problem",
          "difficulty": "hard",
          "question": "Write a function to...",
          "sample_answer": "Expected approach or code snippet"
        }}
      ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional assessment creator."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error generating quiz for {topic}: {e}")
        return {"error": "Failed to generate assessment. Please try again."}
