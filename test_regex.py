import re

text = """
Brock Purdy threw a touchdown to George Kittle. The San Francisco 49ers won the game.
If The defense holds up, we win. A great play by Nick Bosa. This is a sentence.
"I love football," said Kyle Shanahan.
"""

entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
entities = re.findall(entity_pattern, text)

ignore_words = {"The", "A", "An", "And", "But", "Or", "For", "Nor", "On", "At", "To", "From", "By", "In", "I", "He", "She", "It", "They", "If", "This"}
filtered_entities = []
for ent in entities:
    words = ent.split()
    if len(words) >= 2 and words[0] not in ignore_words:
        if all(w[0].isupper() for w in words):
            filtered_entities.append(ent)

print(f"Original entities: {entities}")
print(f"Filtered entities: {filtered_entities}")

temp_p = text
for idx, ent in enumerate(sorted(set(filtered_entities), key=len, reverse=True)):
    placeholder = f"__ENT{idx}__"
    temp_p = re.sub(r'\b' + re.escape(ent) + r'\b', placeholder, temp_p)

print(f"\nReplaced text: {temp_p}")
