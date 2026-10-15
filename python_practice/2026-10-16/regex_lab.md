# Python Regular Expression Lab

Use the `re` module for structured text extraction.

```python
import re
text = "INFO service started; ERROR request failed"
print(re.findall(r"\b(INFO|ERROR)\b", text))
print(re.sub(r"\s+", " ", text).strip())
```

Exercises:
1. Extract dates in ISO format.
2. Find lines containing ERROR without matching lowercase variants.
3. Replace repeated whitespace with one space.
4. Explain why complex email validation is not solved reliably by one simple regex.

Test patterns against representative positive and negative examples.
