import json
import os

with open("golden_dataset.json", "r") as f:
    golden = json.load(f)

answers = []

for i, q in enumerate(golden["qa_pairs"]):
    ans = {
        "id": q["id"],
        "question": q["question"],
        "retrieved_contexts": q["contexts"]
    }
    
    if i == 0:
        # Failure 1: Hallucination (low faithfulness)
        # Use words from question but entirely new words not in context
        ans["actual_answer"] = q["question"] + " But actually OrbitTech allows everything and covers all damages globally for 100 years."
    elif i == 1:
        # Failure 2: Irrelevant (low relevance)
        # Use words from context but not question
        ans["actual_answer"] = " ".join([c["text"] for c in q["contexts"]])
    elif i == 2:
        # Failure 3: Incomplete (low completeness)
        # Answer doesn't cover expected_answer
        ans["actual_answer"] = q["question"] + " Yes."
    else:
        # Pass
        ans["actual_answer"] = q["expected_answer"] + " " + q["question"] + " " + " ".join([c["text"] for c in q["contexts"]])

    answers.append(ans)

out = {
    "corpus_id": golden["corpus_id"],
    "answers": answers
}

os.makedirs("artifacts", exist_ok=True)
with open("artifacts/actual_answers.json", "w") as f:
    json.dump(out, f, indent=2)

print("actual_answers.json generated.")
