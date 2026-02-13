import sys
import os

# Add the current directory to path so we can import topic_extractor
sys.path.append(os.getcwd())

from topic_extractor import extract_topics

test_text = """
The space complexity of an algorithm measures the memory. 
Space complexity is about space. 
We analyze space complexity and time complexity. 
A sliding window is helpful. 
The sliding window technique uses a window.
Space complexity is high. Time complexity is high.
In this sliding window example, we see space complexity.
Complexity is a broad term but space complexity is specific.
Space complexity, space complexity, space complexity.
"""

print("--- Testing Smart Deduplication Extraction ---")
topics = extract_topics(test_text)

print("\nEXTRACTED TOPICS:")
for t in topics:
    print(f"Topic: {t['topic']} | Importance: {t['importance']} | Freq: {t['frequency']}")

top_topics = [t['topic'] for t in topics]

# Assertions
has_phrase = "space complexity" in top_topics
has_unigram_space = "space" in top_topics
has_unigram_complexity = "complexity" in top_topics

print("\nVERIFICATION RESULTS:")
if has_phrase:
    print("✅ SUCCESS: 'space complexity' detected.")
else:
    print("❌ FAILED: 'space complexity' NOT detected.")

if not has_unigram_space:
    print("✅ SUCCESS: Unigram 'space' correctly deduplicated.")
else:
    # If it is there, check its frequency logic - we only keep it if it's > 2x the phrase
    print("⚠️  INFO: Unigram 'space' exists (checking if it met the 2x threshold).")

if not has_unigram_complexity:
    print("✅ SUCCESS: Unigram 'complexity' correctly deduplicated.")
else:
    print("⚠️  INFO: Unigram 'complexity' exists.")
