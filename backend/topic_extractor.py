import json
from groq_client import client

def extract_topics(text):
    """
    Extracts important topics from document text using AI (Groq).
    Returns a list of topic dicts with: topic, priority, and reason.
    """
    if not text or not text.strip():
        return []

    if not client:
        return [
            {"topic": "Error", "priority": "LOW", "reason": "AI Client not initialized"}
        ]

    # Limit text length to avoid token limits, but keep enough context
    context_text = text[:15000] 

    prompt = f"""
    You are an AI system that analyzes documents and extracts knowledge.

    TASK:
    1. Read the document text carefully.
    2. Identify ALL meaningful topics and concepts present in the document (aim for top 15-20).
    3. Topics must be complete phrases, not single words.
    4. Merge related words into proper conceptual terms.
    5. Do NOT restrict topics to any specific domain. Extract what is actually important in THIS text.

    For each topic:
    - Decide its importance based ONLY on how strongly it is discussed in the document.
    - Assign priority as:
      - High: Core or heavily emphasized concepts
      - Medium: Supporting or moderately discussed concepts
      - Low: Briefly mentioned or peripheral concepts
    - Provide a concise reason WHY this priority was assigned based on document context.

    DOCUMENT TEXT:
    {context_text}

    OUTPUT FORMAT (STRICT JSON ONLY):
    {{
      "topics": [
        {{
          "topic": "Concept Name",
          "priority": "High | Medium | Low",
          "reason": "Explanation based on document emphasis"
        }}
      ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a technical knowledge analyzer."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        topics = data.get("topics", [])

        # Normalize and sort results by priority: High > Medium > Low
        results = []
        for t in topics:
            p = t.get("priority", "Low").upper()
            results.append({
                "topic": t.get("topic", "Unknown").title(),
                "priority": p,
                "reason": t.get("reason", "Identified as a relevant concept."),
                "importance": p.lower()
            })

        priority_map = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        results.sort(key=lambda x: priority_map.get(x["priority"], 4))
            
        return results

    except Exception as e:
        print(f"Error extracting topics with AI: {e}")
        # Fallback to a very basic extraction or empty list
        return []
