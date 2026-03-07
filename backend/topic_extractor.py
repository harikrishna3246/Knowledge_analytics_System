import json
from groq_client import client

def get_subject_profile(subject):
    """Generates a subject profile with key topics and concepts using AI."""
    if not subject:
        return {}
    
    prompt = f"""
    Given the subject '{subject}', list the core concepts, keywords, and important areas 
    used in academics and professional applications.
    Include key techniques, fundamental theories, and common sub-topics.
    
    OUTPUT FORMAT (STRICT JSON ONLY):
    {{
      "core_topics": ["Topic 1", "Topic 2", ...],
      "importance_keywords": ["Keyword 1", "Keyword 2", ...]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a subject matter expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error generating subject profile: {e}")
        return {"core_topics": [], "importance_keywords": []}

def extract_topics(text, subject=None, headings=None):
    """
    Extracts important topics from document text using AI (Groq).
    Focuses on headings and is aware of the subject domain.
    Returns a list of topic dicts with: topic, priority, and reason.
    """
    if not text or not text.strip():
        return []

    if not client:
        return [
            {"topic": "Error", "priority": "LOW", "reason": "AI Client not initialized"}
        ]

    # Get subject profile if subject is provided
    subject_profile = get_subject_profile(subject) if subject else {}
    
    # Prepare context: focus on headings if available, otherwise use text preview
    context_headings = "\n".join(headings[:50]) if headings else ""
    context_text = text[:10000] # Reduced text context because we emphasize headings

    prompt = f"""
    You are an AI system that analyzes documents and extracts knowledge for the subject: {subject or 'General'}.
    
    SUBJECT PREVIEW (Core Concepts):
    {json.dumps(subject_profile.get('core_topics', []), indent=2)}

    TASK:
    1. Identify topics ONLY from document headings and emphasized titles.
       Headings found in document:
       {context_headings}
    
    2. Merge related words into proper conceptual terms (e.g., merging individual keywords into their full technical phrase if they appear as separate headings).
    3. Use the subject profile to decide priority.
    
    PRIORITY CRITERIA:
    - HIGH: Matches core '{subject}' concepts or heavily emphasized in headings.
    - MEDIUM: Supporting concepts or secondary headings.
    - LOW: Brief mentions or peripheral topics.

    DOCUMENT CONTEXT (First 10k chars):
    {context_text}

    OUTPUT FORMAT (STRICT JSON ONLY):
    {{
      "topics": [
        {{
          "topic": "Concept Name",
          "priority": "High | Medium | Low",
          "reason": "Explanation based on subject relevance and heading level"
        }}
      ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"You are an expert in {subject or 'academic subjects'} and technical knowledge analysis."},
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
        return []
