from topic_extractor import extract_topics

def test_bigram_detection():
    sample_text = """
    Sliding window is a powerful technique. 
    A sliding window can optimize array problems. 
    Dynamic programming is also useful. 
    We use sliding window along with dynamic programming.
    The sliding window approach is better than dynamic programming here.
    Sliding window, sliding window, sliding window, sliding window.
    """
    
    topics = extract_topics(sample_text)
    
    print("--- Detected Topics (Looking for Bigrams) ---")
    topics_list = [t['topic'] for t in topics]
    for topic in topics_list:
        print(f"Topic: {topic}")
    
    if "sliding window" in topics_list:
        print("\n✅ Bigram 'sliding window' successfully detected!")
    else:
        print("\n❌ Bigram 'sliding window' NOT detected.")

    if "dynamic programming" in topics_list:
        print("✅ Bigram 'dynamic programming' successfully detected!")

if __name__ == "__main__":
    test_bigram_detection()
