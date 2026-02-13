from topic_extractor import extract_topics

def test_merge_sort_split():
    sample_text = """
    Merge sort is a divide and conquer algorithm. 
    Merge sort is efficient. 
    We should use merge sort for large datasets.
    Sort the array using merge sort.
    Merge sort is better than quick sort.
    Merge sort, merge sort, merge sort.
    """
    
    topics = extract_topics(sample_text)
    
    print("--- Detected Topics ---")
    topics_list = [t['topic'] for t in topics]
    for t in topics:
        print(f"Topic: {t['topic']}, Importance: {t['importance']}, Frequency: {t['frequency']}")
    
    has_merge_sort = "merge sort" in topics_list
    has_merge = "merge" in topics_list
    has_sort = "sort" in topics_list
    
    if has_merge_sort:
        print("\n✅ Bigram 'merge sort' detected.")
    
    if has_merge:
        print("⚠️ Unigram 'merge' also detected!")
    
    if has_sort:
        print("⚠️ Unigram 'sort' also detected!")

if __name__ == "__main__":
    test_merge_sort_split()
