import sys
import os

# Add the current directory to path so we can import topic_extractor
sys.path.append(os.getcwd())

from topic_extractor import extract_topics

test_text = """
The space complexity of an algorithm measures the amount of memory it uses. 
Space complexity is often analyzed alongside time complexity. 
When we talk about space complexity, we look at both auxiliary space and total space.
In competitive programming, space complexity is just as important as time complexity.
Often, we try to optimize space complexity by reusing variables.
Many students forget that space complexity includes the stack space for recursive calls.
The space complexity of merge sort is O(n).
Understanding space complexity helps in building efficient systems.
"""

print("--- Testing Topic Extraction ---")
topics = extract_topics(test_text)

for t in topics:
    print(f"Topic: {t['topic']} | Importance: {t['importance']} | Freq: {t['frequency']}")

found_phrase = any(t['topic'] == 'space complexity' for t in topics)
if found_phrase:
    print("\n✅ SUCCESS: 'space complexity' was detected as a merged topic!")
else:
    print("\n❌ FAILED: 'space complexity' was NOT detected as a merged topic.")
