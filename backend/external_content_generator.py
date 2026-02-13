import json
from groq_client import client

def generate_external_content(topic):
    """
    Generates academic/professional insights for a given topic using Groq.
    Returns a structured dictionary with academic knowledge and real-world examples.
    """
    if not client:
        return {
            "academic_knowledge": ["API client not initialized."],
            "real_world_example": "Feature unavailable."
        }

    prompt = f"""
    You are a subject matter expert. Provide a structured technical analysis of the topic: '{topic}'.
    
    Rules:
    - Provide exactly 3 high-quality academic or professional points.
    - Provide 1 clear real-world application or example.
    - Be technically accurate and informative.
    - Return ONLY valid JSON.
    
    JSON Format:
    {{
      "academic_knowledge": [
        "Simple string explanation 1",
        "Simple string explanation 2",
        "Simple string explanation 3"
      ],
      "real_world_example": "A simple string describing a real-world example"
    }}
    
    CRITICAL: The values in 'academic_knowledge' MUST be simple strings, NOT objects.
    CRITICAL: 'real_world_example' MUST be a simple string, NOT an object.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional knowledge generator."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        return data
        
    except Exception as e:
        print(f"Error generating external content for {topic}: {e}")
        return {
            "academic_knowledge": [
                f"{topic.title()} involves systematic problem solving.",
                "It requires careful analysis of constraints.",
                "It is a core concept in modern computing."
            ],
            "real_world_example": "Applied in various high-performance software systems."
        }
