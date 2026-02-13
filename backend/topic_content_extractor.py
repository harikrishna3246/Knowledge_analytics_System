def extract_topic_content(text, topic):
    import re
    # Split into sentences for finer granularity
    # Uses a lookbehind/lookahead to split at punctuation followed by space
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    topic_low = topic.lower()
    related_sentences = []

    # Patterns that suggest a definition
    definition_patterns = [
        f"{topic_low} is",
        f"{topic_low} refers to",
        f"{topic_low} means",
        f"{topic_low} can be defined as",
        f"{topic_low} is a technique"
    ]

    for sent in sentences:
        sent_clean = sent.strip().replace("\n", " ")
        if len(sent_clean) < 30 or len(sent_clean) > 400:
            continue
            
        if topic_low in sent_clean.lower():
            # Scoring: Definition match gets higher priority
            score = 1
            if any(p in sent_clean.lower() for p in definition_patterns):
                score = 10
            
            # Penalize list-like sentences (too many commas or slashes often indicate lists)
            if sent_clean.count(',') > 4 or sent_clean.count('&') > 1:
                score -= 5
                
            related_sentences.append((sent_clean, score))

    # Sort by score descending
    related_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 3 distinct points
    unique_points = []
    for s, score in related_sentences:
        if s not in unique_points and score > 0:
            unique_points.append(s)
        if len(unique_points) >= 3:
            break
            
    return unique_points
