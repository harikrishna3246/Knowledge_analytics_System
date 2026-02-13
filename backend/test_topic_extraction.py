from topic_extractor import extract_topics

def test_extraction():
    sample_text = """
    Python is an interpreted, high-level, general-purpose programming language. 
    Python's design philosophy emphasizes code readability with its notable use of significant whitespace. 
    Its language constructs and object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.
    Python is dynamically-typed and garbage-collected. It supports multiple programming paradigms, including structured (particularly, procedural), object-oriented, and functional programming.
    Python is often described as a "batteries included" language due to its comprehensive standard library.
    Python is a popular language for data science and machine learning.
    Python, Python, Python, language, code, code, code, code.
    """
    
    topics = extract_topics(sample_text)
    
    print("--- Extracted Topics ---")
    for item in topics:
        print(f"Topic: {item['topic']}, Importance: {item['importance']}, Frequency: {item['frequency']}")

if __name__ == "__main__":
    test_extraction()
