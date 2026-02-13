from topic_content_extractor import extract_topic_content

def test_content_extraction():
    sample_text = """
    Python is an interpreted, high-level, general-purpose programming language. 
    Python's design philosophy emphasizes code readability with its notable use of significant whitespace. 
    Its language constructs and object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.
    Python is dynamically-typed and garbage-collected. It supports multiple programming paradigms, including structured (particularly, procedural), object-oriented, and functional programming.
    Python is often described as a "batteries included" language due to its comprehensive standard library.
    Python is a popular language for data science and machine learning.
    """
    
    topic = "Python"
    explanation = extract_topic_content(sample_text, topic)
    
    print(f"--- Extracted Content for Topic: {topic} ---")
    print(explanation)

if __name__ == "__main__":
    test_content_extraction()
