from groq_client import client
import os

SYSTEM_PROMPT = """
You are an intelligent tutor.

Rules:
- Answer clearly and correctly.
- Focus on the given topic.
- Use document context if provided.
- If document content is insufficient, use general knowledge.
- Avoid unnecessary academic language.
- Give examples when helpful.
"""

def topic_chat(topic, question, document_context=""):
    if not client:
        return "Error: AI Client not initialized."
        
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""
Topic: {topic}

Document Content:
{document_context}

Question:
{question}
"""}
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
