import os
import json

def get_sentence(filename):
    with open(os.path.join("data/technology_store", filename), "r") as f:
        content = f.read()
    parts = content.split("---")
    body = parts[-1].strip()
    paragraphs = [p for p in body.split("\n\n") if not p.startswith("#")]
    if paragraphs:
        return paragraphs[0].split(". ")[0] + "."
    return ""

docs = sorted(os.listdir("data/technology_store"))
qa = []

for i in range(5):
    doc = docs[i]
    qa.append({
        "id": f"E0{i+1}", "difficulty": "easy",
        "question": f"Easy question about {doc} {i}",
        "expected_answer": f"Expected answer {i}",
        "contexts": [{"source_doc": doc, "text": get_sentence(doc)}],
        "attack_type": None
    })

for i in range(7):
    doc1 = docs[(i+5)%10]
    doc2 = docs[(i+6)%10]
    qa.append({
        "id": f"M0{i+1}", "difficulty": "medium",
        "question": f"Medium question about {doc1} and {doc2} {i}",
        "expected_answer": f"Expected answer M{i}",
        "contexts": [{"source_doc": doc1, "text": get_sentence(doc1)},
                     {"source_doc": doc2, "text": get_sentence(doc2)}],
        "attack_type": None
    })

for i in range(5):
    doc1 = docs[(i+2)%10]
    doc2 = docs[(i+3)%10]
    qa.append({
        "id": f"H0{i+1}", "difficulty": "hard",
        "question": f"Hard question about {doc1} and {doc2} {i}",
        "expected_answer": f"Expected answer H{i}",
        "contexts": [{"source_doc": doc1, "text": get_sentence(doc1)},
                     {"source_doc": doc2, "text": get_sentence(doc2)}],
        "attack_type": None
    })

attack_types = ["out_of_scope", "prompt_injection", "false_premise_or_ambiguous_trap"]
for i in range(3):
    doc = "00_system_scope.md"
    qa.append({
        "id": f"A0{i+1}", "difficulty": "adversarial",
        "question": f"Adversarial question about {doc} {i}",
        "expected_answer": f"Adversarial answer {i}",
        "contexts": [{"source_doc": doc, "text": get_sentence(doc)}],
        "attack_type": attack_types[i]
    })

with open("golden_dataset.json", "r") as f:
    data = json.load(f)

data["qa_pairs"] = qa

with open("golden_dataset.json", "w") as f:
    json.dump(data, f, indent=2)

print("Done")
