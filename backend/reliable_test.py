from topic_extractor import extract_topics

def run_test():
    sample_text = """
    Merge sort is an algorithm. Merge sort is fast.
    Two sum is a problem. Two sum is easy.
    Binary search is efficient. Binary search is good.
    """
    topics = extract_topics(sample_text)
    
    with open("test_output.txt", "w") as f:
        f.write("--- Extracted Topics ---\n")
        for t in topics:
            f.write(f"Topic: {t['topic']}, Importance: {t['importance']}, Frequency: {t['frequency']}\n")

if __name__ == "__main__":
    run_test()
