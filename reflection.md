# Day 14 — Reflection

## Evaluation Report & Failure Analysis

Dùng kết quả thật trong `artifacts/benchmark_results.json` và kiểm tra lại
answer/context trace trong `artifacts/actual_answers.json` trước khi kết luận.

---

## 1. Benchmark Results Summary

**Overall pass rate:** 80.0%

| Metric | Average | Min | Max | Nhận xét |
|---|---:|---:|---:|---|
| Context Recall | 0.000 | 0.000 | 0.000 | Context recall đánh giá tài liệu truy xuất có chứa expected answer không. Ở đây tất cả đều là 0 do format. |
| Context Precision | 0.000 | 0.000 | 0.000 | Context precision đánh giá tài liệu tốt ở vị trí cao, hiện tại kết quả là 0.0. |
| Faithfulness | 0.597 | 0.000 | 1.000 | Độ trung thực của câu trả lời so với context là 59.7% trung bình. |
| Relevance | 0.950 | 0.000 | 1.000 | Độ liên quan của câu trả lời rất cao (95%). |
| Completeness | 0.883 | 0.000 | 1.000 | Câu trả lời bao phủ được expected_answer khá tốt (88.3%). |
| Overall Score | 0.810 | 0.333 | 0.922 | Điểm tổng quát khá cao nhờ completeness và relevance gánh. |

**Score interpretation**

- Metrics/cases ở mức Good (0.8–1.0): 16 cases
- Metrics/cases ở mức Needs Work (0.6–0.8): 1 case
- Metrics/cases ở mức Significant Issues (<0.6): 3 cases

**Failure type distribution**

| Failure Type | Count | Percentage |
|---|---:|---:|
| hallucination | 2 | 50% |
| irrelevant | 1 | 25% |
| off_topic | 1 | 25% |
| incomplete | 0 | 0% |
| refusal | 0 | 0% |

**Chẩn đoán tổng quan:** Vấn đề chính nằm ở retrieval, generation hay cả hai?
Dùng ít nhất hai metrics để bảo vệ kết luận.

> *Câu trả lời:* Vấn đề chủ yếu nằm ở generation, đặc biệt là hallucination (faithfulness thấp). Context recall và precision cũng thấp cho thấy phần retrieval gặp khó khăn (tuy nhiên trong mock data là do không lấy được tokens phù hợp).

---

## 2. Top 3 Worst Failures — 5 Whys

Phân loại failure trước khi đề xuất fix. Với mỗi case, kiểm tra cả gold evidence
và retrieved chunks; không suy luận chỉ từ một score.

### Failure 1

**ID và question:**

> *Điền:* E02: Easy question about 01_product_catalog.md 1

**Expected answer:**

> *Điền:* Expected answer 1

**Actual answer:**

> *Điền:* OrbitTech sells four primary fictional devices.

**Scores:** Context Recall: 0.0 | Context Precision: 0.0 | Faithfulness: 1.0 |
Relevance: 0.0 | Completeness: 0.0 | Overall: 0.333

**Evidence inspection:** Retriever lấy đúng/thiếu/thừa chunks nào?

> *Câu trả lời:* Retriever lấy đúng văn bản nhưng câu trả lời generation không sử dụng một từ nào từ câu hỏi hoặc từ câu trả lời mong đợi.

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | relevance = 0.0 |
| Why 1 | Tại sao symptom xảy ra? | Answer không chứa keyword của câu hỏi. |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Generator phớt lờ câu hỏi và chỉ bưng nguyên một câu từ context ra. |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | System prompt không yêu cầu trả lời đúng trọng tâm. |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Prompting yếu. |
| Why 5 | Root cause có thể hành động được là gì? | Cải thiện prompt để yêu cầu bám sát câu hỏi. |

**Root cause từ `find_root_cause()`:**

> *Paste output:* Multiple issues detected — review full pipeline

**Bạn đồng ý hay không? Dẫn evidence từ trace:**

> *Câu trả lời:* Đồng ý. Điểm relevance và completeness đều 0, chứng tỏ toàn bộ pipeline (đặc biệt generation) có vấn đề trong case này.

**Proposed fix cụ thể:**

> *Câu trả lời:* Tinh chỉnh LLM prompt (add few-shot examples) để nó biết cách trả lời trúng đích hơn.

### Failure 2

**ID và question:**

> *Điền:* E03: Easy question about 02_orders_and_payments.md 2

**Expected answer:**

> *Điền:* Expected answer 2

**Actual answer:**

> *Điền:* Easy question about 02_orders_and_payments.md 2 Yes.

**Scores:** Context Recall: 0.0 | Context Precision: 0.0 | Faithfulness: 0.0 |
Relevance: 1.0 | Completeness: 0.333 | Overall: 0.444

**Evidence inspection:**

> *Câu trả lời:* Faithfulness bằng 0 chứng tỏ câu trả lời tạo ra chứa toàn từ không có trong context (trừ các stop word).

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | faithfulness = 0.0, bị đánh dấu hallucination |
| Why 1 | Tại sao symptom xảy ra? | Model bịa ra câu trả lời ("Yes") |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Model không dựa vào context để trả lời. |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | Không có cơ chế ràng buộc hallucination. |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Retrieval không mang đủ ngữ cảnh, khiến model phải đoán. |
| Why 5 | Root cause có thể hành động được là gì? | Context is missing or irrelevant — improve retrieval |

**Root cause và proposed fix:**

> *Câu trả lời:* Cải thiện thuật toán tìm kiếm và thêm module check hallucination trước khi trả về.

### Failure 3

**ID và question:**

> *Điền:* E01: Easy question about 00_system_scope.md 0

**Expected answer:**

> *Điền:* Expected answer 0

**Actual answer:**

> *Điền:* Easy question about 00_system_scope.md 0 But actually OrbitTech allows everything and covers all damages globally for 100 years.

**Scores:** Context Recall: 0.0 | Context Precision: 0.0 | Faithfulness: 0.059 |
Relevance: 1.0 | Completeness: 0.333 | Overall: 0.464

**Evidence inspection:**

> *Câu trả lời:* Model hoàn toàn bịa ra thông tin sai lệch ("covers all damages globally").

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | hallucination nghiêm trọng. |
| Why 1 | Tại sao symptom xảy ra? | Câu trả lời không bám sát policy. |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Model hallucinate. |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | Hệ thống thiếu guardrail chặn thông tin sai lệch về chính sách. |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | LLM tự do sáng tạo. |
| Why 5 | Root cause có thể hành động được là gì? | Áp dụng self-reflection / NLI để check mâu thuẫn chính sách. |

**Root cause và proposed fix:**

> *Câu trả lời:* Implement hallucination checker to filter unsupported claims.

---

## 3. Failure Clustering

Một root cause có thể tạo ra nhiều failures. Nhóm theo nguyên nhân có thể sửa,
không chỉ nhóm theo tên metric.

| Cluster | Root Cause | Failure IDs | Priority |
|---|---|---|---|
| 1 | Hallucination due to weak context/guardrails | E01, E03 | High |
| 2 | Irrelevant response generation | E02 | Medium |
| 3 | Off-topic | E04 | Low |

**Nếu chỉ được sửa một cluster, bạn chọn cluster nào và vì sao?**

> *Câu trả lời:* Chọn Cluster 1 (Hallucination) vì trong dịch vụ khách hàng (Customer Support), việc bịa đặt ra chính sách sai lệch (ví dụ "bảo hành mọi hỏng hóc toàn cầu 100 năm") sẽ gây hậu quả pháp lý và tài chính nghiêm trọng hơn rất nhiều so với việc trả lời không đúng trọng tâm.

---

## 4. Improvement Log

Paste output của `generate_improvement_log()`:

```text
| Failure ID | Type | Root Cause | Suggested Fix | Status |
|------------|------|------------|---------------|--------|
| E01 | hallucination | Context is missing or irrelevant — improve retrieval | Implement hallucination checker to filter unsupported claims | Open |
| E02 | irrelevant | Multiple issues detected — review full pipeline | Add few-shot examples showing complete answers to improve completeness | Open |
| E03 | hallucination | Context is missing or irrelevant — improve retrieval | Improve intent detection to handle out-of-scope questions | Open |
| E04 | off_topic | Context is missing or irrelevant — improve retrieval |  | Open |
```

**Ba improvement suggestions ưu tiên**

1. Implement hallucination checker to filter unsupported claims
2. Add few-shot examples showing complete answers to improve completeness
3. Improve intent detection to handle out-of-scope questions

Với mỗi suggestion, nêu metric dự kiến thay đổi và cách đo lại.

| Suggestion | Target metric | Verification method |
|---|---|---|
| Hallucination checker | Faithfulness | Chạy lại batch eval, kỳ vọng số lượng failure "hallucination" giảm |
| Few-shot examples | Relevance, Completeness | So sánh trung bình Relevance score trước và sau khi thêm prompt |
| Intent detection | Relevance | Test riêng các câu out-of-scope xem có bị off-topic nữa không |

---

## 5. Regression Testing Strategy

**Câu 1: Khi nào chạy `run_regression()` trong production workflow?**

> *Câu trả lời:* Trước mỗi lần merge PR (trong CI/CD pipeline) có sửa đổi code liên quan đến RAG pipeline (prompt, chunking, retrieval model).

**Câu 2: Threshold drop 0.05 có phù hợp OrbitTech Customer Support không? Vì sao?**

> *Câu trả lời:* Phù hợp vì nó cho phép một biên độ dao động nhỏ (5%) do tính chất ngẫu nhiên của LLM, nhưng vẫn đủ nhạy để bắt các phiên bản làm suy giảm đáng kể chất lượng phản hồi cho khách hàng.

**Câu 3: Metric/failure nào phải block deployment, metric nào chỉ alert?**

> *Câu trả lời:* Faithfulness drop hoặc failure type = "hallucination" phải block deploy vì đưa sai chính sách là rủi ro cực kỳ lớn. Completeness drop nhẹ có thể chỉ cần alert.

**Câu 4: Điền evaluation stages vào flow.**

```text
Code/prompt/retrieval change → [Unit Tests] → [Golden Dataset Eval] → [A/B Testing] → Deploy
```

> *Giải thích:* Unit tests đảm bảo logic chạy đúng; Golden Dataset đảm bảo không bị regression; A/B testing đo lường tác động thực tế trên production.

---

## 6. Continuous Improvement Loop

```text
Evaluate → Analyze → Improve → Augment benchmark → Repeat
```

| Priority | Action | Metric dự kiến cải thiện | Expected impact |
|---:|---|---|---|
| 1 | Thêm guardrail chặn hallucination | Faithfulness | Rất cao |
| 2 | Tuning chunk size cho retrieval | Context Precision | Trung bình |
| 3 | Tối ưu prompt với few-shot | Completeness | Trung bình |

**Hai hoặc ba failure cases nào cần thêm vào benchmark ở vòng tiếp theo?**

> *Câu trả lời:* Cần thêm các câu hỏi phức tạp hơn yêu cầu tổng hợp từ 3 tài liệu trở lên, và các câu hỏi gài bẫy (adversarial) mô phỏng chính xác lỗi hallucination E01 và E03.

---

## 7. Final Reflection

**Điều gì trong kết quả benchmark trái với dự đoán ban đầu của bạn?**

> *Câu trả lời:* Điểm Context Precision và Recall có thể bằng 0.0 do cách tính word-overlap không phản ánh đúng ý nghĩa ngữ nghĩa (nếu context dùng từ đồng nghĩa với expected answer thì điểm sẽ rất thấp).

**Word-overlap heuristics trong lab có giới hạn gì? Nếu đưa hệ thống vào
production, bạn sẽ thay hoặc bổ sung metric nào?**

> *Câu trả lời:* Giới hạn lớn nhất là không hiểu được semantic similarity (ví dụ "điện thoại" và "smartphone" sẽ bị tính là khác nhau hoàn toàn). Khi lên production, nên dùng LLM-as-a-judge (như class LLMJudge đã implement) hoặc các embedding-based metrics (như BERTScore) để đánh giá.
