from topic_extractor import extract_topics
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from collections import Counter

def debug_frequencies(text):
    text = text.lower()
    tokens = [t for t in word_tokenize(text) if len(t) > 2] # simple tokens
    
    unigrams = tokens
    bigrams = [" ".join(bg) for bg in ngrams(tokens, 2)]
    trigrams = [" ".join(tg) for tg in ngrams(tokens, 3)]
    
    freq = Counter(unigrams + bigrams + trigrams)
    
    print("--- Unigram Frequencies ---")
    for t in sorted(set(unigrams)):
        print(f"{t}: {freq[t]}")
        
    print("\n--- Bigram Frequencies ---")
    for b in sorted(set(bigrams)):
        if freq[b] > 0:
            print(f"{b}: {freq[b]}")

    print("\n--- Extracted Topics ---")
    topics = extract_topics(text)
    for t in topics:
        print(f"Topic: {t['topic']}, Importance: {t['importance']}, Frequency: {t['frequency']}")

if __name__ == "__main__":
    sample_text = """
    Merge sort is a great algorithm. I love merge sort.
    Two sum is a classic problem. Let's solve two sum.
    Binary search is fast. We use binary search.
    """
    debug_frequencies(sample_text)
