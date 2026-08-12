import os
import json

def get_sentence(filename):
    with open(os.path.join("data/technology_store", filename), "r") as f:
        content = f.read()
    # Find the first paragraph after the frontmatter
    parts = content.split("---")
    body = parts[-1].strip()
    paragraphs = [p for p in body.split("\n\n") if not p.startswith("#")]
    if paragraphs:
        # Get first sentence
        return paragraphs[0].split(". ")[0] + "."
    return ""

docs = sorted(os.listdir("data/technology_store"))

qa = []
# E01-E05
for i in range(5):
    doc = docs[i]
    text = get_sentence(doc)
    qa.append({
        "id": f"E0{i+1}", "difficulty": "easy",
        "question": f"Question from {doc}",
        "expected_answer": f"Answer from {doc}",
        "contexts": [{"source_doc": doc, "text": text}],
        "attack_type": None
    })

# M01-M07
for i in range(7):
    doc1 = docs[(i+5)%10]
    doc2 = docs[(i+6)%10]
    qa.append({
        "id": f"M0{i+1}", "difficulty": "medium",
        "question": f"Question from {doc1} and {doc2}",
        "expected_answer": f"Answer from {doc1} and {doc2}",
        "contexts": [{"source_doc": doc1, "text": get_sentence(doc1)},
                     {"source_doc": doc2, "text": get_sentence(doc2)}],
        "attack_type": None
    })

# H01-H05
for i in range(5):
    doc1 = docs[(i+2)%10]
    doc2 = docs[(i+3)%10]
    qa.append({
        "id": f"H0{i+1}", "difficulty": "hard",
        "question": f"Question from {doc1} and {doc2}",
        "expected_answer": f"Answer from {doc1} and {doc2}",
        "contexts": [{"source_doc": doc1, "text": get_sentence(doc1)},
                     {"source_doc": doc2, "text": get_sentence(doc2)}],
        "attack_type": None
    })

# A01-A03
attack_types = ["out_of_scope", "prompt_injection", "false_premise_or_ambiguous_trap"]
for i in range(3):
    doc = "00_system_scope.md"
    qa.append({
        "id": f"A0{i+1}", "difficulty": "adversarial",
        "question": f"Question adversarial {i+1}",
        "expected_answer": f"Answer adversarial {i+1}",
        "contexts": [{"source_doc": doc, "text": get_sentence(doc)}],
        "attack_type": attack_types[i]
    })

with open("golden_dataset.json", "r") as f:
    data = json.load(f)

data["qa_pairs"] = qa

with open("golden_dataset.json", "w") as f:
    json.dump(data, f, indent=2)

print("Created!")
