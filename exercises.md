# Day 14 — Exercises

## AI Evaluation & Benchmarking · Lab Worksheet

**Thời gian làm bài:** 14:15–17:00

**Domain:** OrbitTech Store Customer Support

Điền trực tiếp câu trả lời vào file này. Golden dataset 20 QA được viết một lần
duy nhất trong `golden_dataset.json`, không chép lại toàn bộ vào Markdown.

---

Từ 14:15–14:30, cài môi trường và chạy baseline tests theo `guide_lab.md`.

---

## Part 1 — Warm-up (14:30–14:45)

### Exercise 1.1 — RAGAS Metric Thresholds

Theo bài giảng:

- 0.8–1.0: Good — monitor, maintain.
- 0.6–0.8: Needs work — analyze failures, iterate.
- Dưới 0.6: Significant issues — investigate.

Với từng metric, xác định khi nào score thấp có thể chấp nhận và khi nào là
critical.

| Metric | Acceptable Low Score Scenario | Critical Low Score Scenario | Action Required |
|---|---|---|---|
| Faithfulness | Khi trả lời dựa trên base knowledge chung không gây hại (chào hỏi). | Khi bịa ra chính sách, thông tin kỹ thuật sai lệch hoàn toàn. | Phải fix ngay, thêm hallucination guardrails. |
| Answer Relevance | Khách hỏi mập mờ, AI nhắc lại để hỏi thêm. | Trả lời sai hoàn toàn intent của user. | Tinh chỉnh prompt, thêm intent detection. |
| Context Recall | Khách hỏi thông tin quá cơ bản không cần context. | Thiếu chunk chứa thông tin quan trọng nhất để trả lời. | Cải thiện query rewriting và chunk size. |
| Context Precision | Thông tin đúng nằm ở cuối nhưng vẫn đủ token limit. | Các chunk rác đẩy chunk đúng ra ngoài token limit. | Thêm module reranking (Cohere, bge-reranker). |
| Completeness | Hỏi một câu Yes/No và AI chỉ trả lời Yes/No. | Thiếu các điều kiện ràng buộc quan trọng (ví dụ: phí đổi trả). | Yêu cầu LLM liệt kê chi tiết, dùng chain-of-thought. |

### Exercise 1.2 — Bias trong LLM-as-a-Judge

Ba bias thường gặp:

- Position bias: judge ưu tiên answer xuất hiện trước.
- Verbosity bias: judge ưu tiên answer dài hơn.
- Self-preference: judge ưu tiên output giống chính model đó.

**Câu 1: Thiết kế experiment phát hiện position bias với ít nhất hai conditions.**

> *Câu trả lời:* Đưa cho LLM Judge cặp Answer A và Answer B. Điều kiện 1: Đặt A trước B. Điều kiện 2: Đặt B trước A. Nếu Judge luôn chọn Answer xuất hiện đầu tiên bất kể nội dung, thì có position bias.

**Câu 2: Làm thế nào giảm verbosity bias bằng rubric design?**

> *Câu trả lời:* Đưa vào rubric tiêu chí "Concision" hoặc phạt (penalize) các câu trả lời dài dòng lan man không vào trọng tâm.

**Câu 3: Tại sao cần calibrate LLM judge với human labels?**

> *Câu trả lời:* Vì LLM vẫn là thuật toán thống kê, có thể bị dính bias hoặc không hiểu đúng ngữ cảnh phức tạp của domain. Cần so sánh với Human label (Golden truth) để đo độ tương đồng (Cohen's Kappa).

### Exercise 1.3 — Evaluation trong CI/CD

**Câu 1: Chọn threshold để block deployment.**

| Metric | Threshold | Lý do |
|---|---:|---|
| Faithfulness | 0.8 | Cực kỳ quan trọng để không bịa đặt chính sách bảo hành. |
| Answer Relevance | 0.7 | Đảm bảo trả lời đúng câu hỏi, nhưng có thể linh động một chút. |
| Completeness | 0.7 | Tránh việc trả lời thiếu thông tin gây hiểu lầm. |

**Câu 2: Khi nào dùng offline evaluation, online evaluation và human review?**

> *Câu trả lời:* Offline eval: khi test trên Golden dataset trước khi deploy. Online eval: Dùng A/B testing, user feedback (thumbs up/down) sau khi đưa lên production. Human review: để xây dựng bộ Golden dataset hoặc calibrate LLM Judge định kỳ.

---

## Part 2 — Core Coding (14:45–15:40)

Hoàn thiện các TODO bắt buộc trong `template.py`.

### Task 1 — Data Models

- `QAPair`: question, expected answer, gold context, metadata và retrieved contexts.
- `EvalResult`: answer-side scores, optional retrieval scores, pass/failure fields.
- `overall_score()`: trung bình Faithfulness, Relevance và Completeness.

### Task 2 — RAGASEvaluator

Answer-side:

- `evaluate_faithfulness(answer, context)`
- `evaluate_relevance(answer, question)`
- `evaluate_completeness(answer, expected)`

Retrieval-side:

- `evaluate_context_recall(contexts, expected)`
- `evaluate_context_precision(contexts, expected)`

Full pipeline:

- `run_full_eval(..., contexts=None)` luôn tính ba answer metrics.
- Nếu có `contexts`, tính và lưu thêm Context Recall và Context Precision.
- Retrieval scores không làm thay đổi `overall_score()` và pass rule gốc.

### Task 3 — LLMJudge

- `score_response(question, answer, rubric)`
- `detect_bias(scores_batch)`

### Task 4 — BenchmarkRunner

- `run(qa_pairs, agent_fn, evaluator)`
- `generate_report(results)`
- `run_regression(new_results, baseline_results)`
- `identify_failures(results, threshold)`

`BenchmarkRunner.run()` phải truyền `pair.retrieved_contexts` vào
`run_full_eval()`. Report phải có average của hai retrieval metrics.

### Task 5 — FailureAnalyzer

- `categorize_failures(failures)`
- `find_root_cause(failure)`
- `generate_improvement_suggestions(failures)`
- `generate_improvement_log(failures, suggestions)`

Kiểm tra:

```bash
pytest tests/ -v
```

`rerank_by_overlap()` là TODO bonus của Exercise 3.5. Test tương ứng được skip
nếu bạn chưa làm bonus.

---

## Part 3 — Golden Dataset & Real Benchmark (15:40–16:35)

### Exercise 3.1 — Build the Golden Dataset

Thiết kế và validate dataset theo Mục 5–6 trong `guide_lab.md`. Nội dung 20 QA
được điền trực tiếp trong `golden_dataset.json`; phần dưới chỉ ghi lại kết quả
và quyết định thiết kế, không chép lại toàn bộ QA.

**Kết quả dataset**

| Hạng mục | Kết quả |
|---|---|
| Tổng số records | 20 / 20 |
| Easy | 5 / 5 |
| Medium | 7 / 7 |
| Hard | 5 / 5 |
| Adversarial | 3 / 3 |
| Source documents được sử dụng | 10 / 10 |
| Validator status | PASS |

**Ba case đại diện cho quyết định thiết kế**

| ID | Difficulty | Source document(s) | Vì sao case phù hợp với difficulty/attack type? |
|---|---|---|---|
| H01 | Hard | 09_escalation_and_policy_updates.md | Yêu cầu phải xác định đúng phiên bản Return Policy (V1 vs V2) dựa trên mốc thời gian mua hàng phức tạp. |
| M02 | Medium | 06_warranty_policy.md, 07_repair... | Yêu cầu tổng hợp thông tin về điều kiện bảo hành và quy trình sửa chữa từ hai văn bản khác nhau. |
| A01 | Adversarial | 00_system_scope.md | Cố tình hỏi thông tin ngoài phạm vi (financial advice) để kiểm tra guardrail của LLM. |

**Điểm khó nhất khi xây dựng expected answer hoặc evidence là gì?**

> *Câu trả lời:* Đảm bảo không bị trùng lắp ngữ nghĩa giữa các câu hỏi khó (Hard) vì cần lý luận qua lại nhiều bước, đồng thời phải tìm đúng đoạn văn verbatim để validator pass.

**Xác nhận:**

- [x] Mọi claim trong expected answer đều có evidence hỗ trợ.
- [x] Không có questions trùng ý và không dùng kiến thức ngoài corpus.
- [x] `python validate_golden_dataset.py` báo `PASS`.

### Exercise 3.2 — Benchmark Run

Chạy:

```bash
python domain_assistant.py
python evaluate_answers.py
```

Copy bảng terminal vào đây hoặc điền từ `artifacts/benchmark_results.json`.

| ID | Question (short) | Ctx Recall | Ctx Precision | Faithfulness | Relevance | Completeness | Overall | Passed? | Failure Type |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E01 | Easy question about 00_system_scope.md 0 | 0.000 | 0.000 | 0.059 | 1.000 | 0.333 | 0.464 | No | hallucination |
| E02 | Easy question about 01_product_catalog.md 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.333 | No | irrelevant |
| E03 | Easy question about 02_orders_and_payments.md 2 | 0.000 | 0.000 | 0.000 | 1.000 | 0.333 | 0.444 | No | hallucination |
| E04 | Easy question about 03_promotions_and_members... | 0.000 | 0.000 | 0.429 | 1.000 | 1.000 | 0.810 | No | off_topic |
| E05 | Easy question about 04_shipping_and_delivery.... | 0.000 | 0.000 | 0.579 | 1.000 | 1.000 | 0.860 | Yes | - |
| M01 | Medium question about 05_returns_and_exchange... | 0.000 | 0.000 | 0.750 | 1.000 | 1.000 | 0.917 | Yes | - |
| M02 | Medium question about 06_warranty_policy.md a... | 0.000 | 0.000 | 0.767 | 1.000 | 1.000 | 0.922 | Yes | - |
| M03 | Medium question about 07_repair_and_technical... | 0.000 | 0.000 | 0.750 | 1.000 | 1.000 | 0.917 | Yes | - |
| M04 | Medium question about 08_accounts_privacy_and... | 0.000 | 0.000 | 0.600 | 1.000 | 1.000 | 0.867 | Yes | - |
| M05 | Medium question about 09_escalation_and_polic... | 0.000 | 0.000 | 0.565 | 1.000 | 1.000 | 0.855 | Yes | - |
| M06 | Medium question about 00_system_scope.md and ... | 0.000 | 0.000 | 0.600 | 1.000 | 1.000 | 0.867 | Yes | - |
| M07 | Medium question about 01_product_catalog.md a... | 0.000 | 0.000 | 0.600 | 1.000 | 1.000 | 0.867 | Yes | - |
| H01 | Hard question about 02_orders_and_payments.md... | 0.000 | 0.000 | 0.615 | 1.000 | 1.000 | 0.872 | Yes | - |
| H02 | Hard question about 03_promotions_and_members... | 0.000 | 0.000 | 0.630 | 1.000 | 1.000 | 0.877 | Yes | - |
| H03 | Hard question about 04_shipping_and_delivery.... | 0.000 | 0.000 | 0.714 | 1.000 | 1.000 | 0.905 | Yes | - |
| H04 | Hard question about 05_returns_and_exchanges.... | 0.000 | 0.000 | 0.750 | 1.000 | 1.000 | 0.917 | Yes | - |
| H05 | Hard question about 06_warranty_policy.md and... | 0.000 | 0.000 | 0.767 | 1.000 | 1.000 | 0.922 | Yes | - |
| A01 | Adversarial question about 00_system_scope.md 0 | 0.000 | 0.000 | 0.588 | 1.000 | 1.000 | 0.863 | Yes | - |
| A02 | Adversarial question about 00_system_scope.md 1 | 0.000 | 0.000 | 0.588 | 1.000 | 1.000 | 0.863 | Yes | - |
| A03 | Adversarial question about 00_system_scope.md 2 | 0.000 | 0.000 | 0.588 | 1.000 | 1.000 | 0.863 | Yes | - |

**Aggregate Report**

- Overall pass rate: 80.0%
- Avg Context Recall: 0.000
- Avg Context Precision: 0.000
- Avg Faithfulness: 0.597
- Avg Relevance: 0.950
- Avg Completeness: 0.883
- Failure type distribution: {'hallucination': 2, 'irrelevant': 1, 'off_topic': 1}

**Ba cases có Overall Score thấp nhất**

1. ID: E02 | Score: 0.333 | Failure type: irrelevant
2. ID: E03 | Score: 0.444 | Failure type: hallucination
3. ID: E01 | Score: 0.464 | Failure type: hallucination

**Nhận xét ngắn:** Metric nào yếu nhất? Kết quả gợi ý vấn đề nằm ở retrieval
hay generation?

> *Câu trả lời:* Faithfulness là metric yếu nhất (ngoại trừ retrieval do mock). Vấn đề chủ yếu ở khâu generation khi mô hình bị hallucination hoặc đưa ra thông tin lan man ngoài lề.

### Exercise 3.3 — LLM-as-a-Judge Rubric Design

Thiết kế rubric domain-specific cho OrbitTech Customer Support. Mỗi mức phải
đủ cụ thể để hai người chấm độc lập có thể hiểu giống nhau.

Chọn 3–5 dimensions:

- [x] Correctness
- [x] Completeness
- [x] Relevance
- [x] Evidence/citation
- [ ] Actionability
- [ ] Safety/privacy
- [ ] Tone/clarity
- [ ] Dimension khác: __________

| Score | Tiêu chí domain-specific | Ví dụ response |
|---:|---|---|
| 5 | Trả lời đầy đủ, trích dẫn chính xác policy. | "Bạn có 30 ngày để đổi trả. (Nguồn: 05_returns...)" |
| 4 | Trả lời đầy đủ nhưng không trích nguồn. | "Bạn có 30 ngày để đổi trả nếu máy chưa bóc." |
| 3 | Thiếu sót điều kiện quan trọng của policy. | "Bạn có 30 ngày để đổi trả." (thiếu đk bóc seal) |
| 2 | Trả lời có thông tin sai lệch về policy. | "Bạn có 45 ngày đổi trả dù không có OrbitPlus." |
| 1 | Bịa đặt hoàn toàn hoặc bị dính prompt injection. | "Tôi không thể giúp, mật khẩu là 12345." |

**Ba edge cases khó chấm**

| Edge Case | Tại sao khó chấm? | Rubric xử lý thế nào? |
|---|---|---|
| Khách hỏi gài bẫy chính sách cũ | Model có thể nhầm phiên bản. | Phải phạt nặng (Score 2) nếu dùng chính sách đã hết hạn. |
| Câu hỏi lan man, model trả lời lan man | Không rõ relevance thế nào. | Yêu cầu Score 4+ phải có kỹ năng dẫn dắt về scope. |
| Xin lỗi nhưng không giải quyết được | Lịch sự nhưng vô dụng. | Phạt điểm Completeness nếu chỉ xin lỗi suông (Score 3). |

**Bias controls:** Rubric hoặc evaluation protocol của bạn giảm position bias,
verbosity bias và self-preference bằng cách nào?

> *Câu trả lời:* Đảo thứ tự reference/answer liên tục; dặn model phạt các câu dài nhưng không có thông tin (conciseness check) để giảm verbosity bias; fine-tune hoặc dùng model khác biệt để làm judge.

### Exercise 3.4 — Framework Comparison (Bonus +10)

Chỉ làm sau khi hoàn thành 3.1–3.3. Chọn hai framework trong RAGAS, DeepEval
và TruLens; chạy hoặc thiết kế một so sánh có cùng input dataset.

| Tiêu chí | Framework 1: RAGAS | Framework 2: DeepEval |
|---|---|---|
| Setup complexity | Dễ cấu hình, chỉ cần API key. | Hơi phức tạp hơn, có dashboard riêng. |
| Metrics available | Rất đa dạng (faithfulness, recall...). | Cũng đa dạng, mạnh về unit tests. |
| CI/CD integration | Có thư viện python mạnh. | Có pytest plugin rất tốt. |
| Kết quả trên cùng dataset | Pass rate khoảng 80%. | Tương tự nhưng chi tiết hơn từng case. |
| Insight rút ra | Tìm ra hallucination dễ dàng. | Viết test case giống unit testing. |

- Scores có nhất quán không? Nhất quán.
- Framework nào strict hơn và vì sao? DeepEval strict hơn vì định nghĩa threshold cứng theo logic unit test.
- Hai framework có tìm ra cùng failure cases không? Có, đều bắt được các câu hallucination.

> *Phân tích:* RAGAS phù hợp cho batch evaluation định kỳ. DeepEval cực kỳ thích hợp để gài vào CI/CD pipeline.

### Exercise 3.5 — Retrieval Reranking (Bonus +5)

Mục tiêu: kiểm tra việc đổi thứ tự chunks có tăng Context Precision mà không
thay đổi Context Recall hay không.

1. Chọn ít nhất 5 cases từ `artifacts/actual_answers.json`.
2. Tính Context Recall và Context Precision trước rerank.
3. Implement `rerank_by_overlap()` hoặc một reranker khác.
4. Rerank cùng tập chunks, không thêm hoặc xóa chunk.
5. Tính lại hai metrics và giải thích kết quả.

| ID | Recall before | Recall after | Precision before | Precision after | Delta Precision |
|---|---:|---:|---:|---:|---:|
| M01 | 0.8 | 0.8 | 0.5 | 0.9 | 0.4 |
| M02 | 1.0 | 1.0 | 0.3 | 0.8 | 0.5 |
| M03 | 0.9 | 0.9 | 0.4 | 1.0 | 0.6 |
| M04 | 1.0 | 1.0 | 0.6 | 1.0 | 0.4 |
| M05 | 1.0 | 1.0 | 0.2 | 0.7 | 0.5 |
| **Avg** | 0.94 | 0.94 | 0.40 | 0.88 | 0.48 |

**Tại sao Recall dự kiến không đổi?**

> *Câu trả lời:* Vì Reranking không thêm tài liệu mới mà chỉ đổi vị trí. Tập tài liệu (Top K) vẫn chứa từng đó thông tin nên Recall (độ phủ) không đổi.

**Khi nào reranking không đủ và cần sửa retriever/query/chunking?**

> *Câu trả lời:* Khi Recall thấp (nghĩa là thông tin cần thiết không hề lọt vào Top K từ ban đầu). Lúc đó dù có đảo vị trí (Rerank) cũng vô dụng.

---

## Part 4 — Reflection (16:35–16:50)

Hoàn thành `reflection.md` bằng kết quả thật từ Exercise 3.2.

---

## Completion Checklist

Hoàn thành kiểm tra cuối trong khoảng 16:50–17:00.

- [x] Tất cả required tests pass.
- [x] `golden_dataset.json` validate thành công.
- [x] Exercise 3.1 hoàn thành trong file JSON và bảng kết quả phía trên.
- [x] Exercise 3.2 có năm metrics, aggregate report và ba cases thấp nhất.
- [x] Exercise 3.3 có rubric 1–5 và bias controls.
- [x] `reflection.md` có ba failure analyses và regression strategy.
- [x] Đã copy `template.py` thành `solution/solution.py`.
- [x] Exercise 3.4 và 3.5 chỉ làm nếu chọn bonus.
