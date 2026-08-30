# Original User Request

## Initial Request — 2026-07-17T08:54:11Z

Polishing and refining the GUM-Net Geopolitical Tail Risk paper draft files in the newly migrated repository `/data/quyhv/oil_forecast_tail_risk` based on senior reviewer feedback.

Working directory: /data/quyhv/oil_forecast_tail_risk
Integrity mode: benchmark

## Requirements

### R1. Mathematical Notation Standardization
Standardize the Directional Accuracy (DA) notation in the LaTeX math formulas by removing programming-style comparison operators `==` and replacing them with standard mathematical equality `=` or equivalence:
$$\mathbb{I}\left(\text{sgn}(P_{t+h} - P_t) = \text{sgn}(\hat{P}_{t+h} - P_t)\right)$$

### R2. Ablation Study Delta Clarification
In the Ablation Study table of `docs/Evaluation_Scenarios_Draft.md`, add a clear explanatory note immediately below the table:
"Ghi chú: Delta DA được tính bằng điểm phần trăm tuyệt đối (percentage points - ppt), Delta MAPE được tính bằng tỷ lệ phần trăm tăng thêm so với mô hình GUM-Net gốc."

### R3. Diebold-Mariano Statistical Significance
Insert a standard econometric justification sentence in the discussion sections (e.g. `docs/Evaluation_Scenarios_Draft.md` or `docs/Part_4_Experiments.md`):
"Để đảm bảo tính vững chãi thống kê, chúng tôi đã tiến hành kiểm định Diebold-Mariano (DM test) đối với các chuỗi sai số dự báo. Kết quả cho thấy sự bứt phá của GUM-Net trước tất cả các mô hình đối chứng đều có ý nghĩa thống kê ở mức $p < 0.01$ trên mọi cửa sổ rủi ro đuôi."

### R4. Comprehensive Consistency & Integrity Verification
Perform a complete scan of the draft files in `docs/` to check:
- Accurate case-sensitive baseline model naming.
- Reviewer-mandated author affiliations and corresponding email format.
- Complete compatibility of LaTeX math formulas.

## Acceptance Criteria

### Mathematical & Notational Accuracy
- [ ] No occurrences of `==` in mathematical LaTeX definitions for Directional Accuracy (DA).
- [ ] The Ablation Study table contains the explanatory footnote clarifying absolute percentage points (ppt) for Delta DA and relative percentage change for Delta MAPE.

### Statistical Justification
- [ ] The Diebold-Mariano test significance statement is correctly integrated into the discussion sections.

### Structural Verification
- [ ] Author affiliations and emails follow the reviewer-mandated format exactly.
- [ ] The dry run test or build check passes successfully on the repository.

## Follow-up — 2026-07-17T16:11:34+07:00

Dự án này nhằm mục đích tinh chỉnh các bản thảo bài báo khoa học cho mô hình dự báo giá dầu GUM-Net bằng cách cập nhật các ký hiệu toán học, bổ sung phản biện của reviewer về chỉ số delta trong nghiên cứu cắt bỏ (ablation study) và ý nghĩa thống kê, đồng thời thiết kế một khung lập luận khoa học và kịch bản đánh giá đa khía cạnh (trung thực, không bịa đặt số liệu) để phân tích hiệu năng của GUM-Net trên 5 cửa sổ rủi ro địa chính trị đuôi (2014, 2020, 2022, 2024, và 2026 kéo dài đến tháng 5/2026) so với 10 mô hình SOTA, đảm bảo GUM-Net đạt hiệu năng vững chãi vượt trội trên cả 5 cửa sổ này.

Thư mục làm việc: /data/quyhv/oil_forecast_tail_risk
Chế độ liêm chính (Integrity mode): development

## Yêu cầu (Requirements)

### R1. Chuẩn hóa ký hiệu và bổ sung hiệu chỉnh nhỏ của Reviewer
- Trong file `docs/Evaluation_Scenarios_Draft.md`, xác nhận công thức tính Directional Accuracy (DA) ở Mục 1.1 đã đổi dấu từ `==` thành `=`.
- Trong file `docs/Evaluation_Scenarios_Draft.md` (hoặc các phần liên quan của `docs/Part_4_Experiments.md`), đảm bảo bảng Nghiên cứu cắt bỏ (Ablation Study) có ghi chú chân trang làm rõ:
  `*Ghi chú: Delta DA được tính bằng điểm phần trăm tuyệt đối (percentage points - ppt), Delta MAPE được tính bằng tỷ lệ phần trăm tăng thêm so với mô hình GUM-Net gốc (Ví dụ: Nếu DA của GUM-Net là 80%, biến thể giảm 11.35% nghĩa là còn 68.65%).*`
- Đảm bảo có đoạn văn ở cuối Mục 3 trong file `docs/Evaluation_Scenarios_Draft.md` khẳng định đã thực hiện kiểm định Diebold-Mariano (DM test) cho thấy sự bứt phá của GUM-Net trước tất cả các mô hình đối chứng đều có ý nghĩa thống kê ở mức $p < 0.01$ trên mọi cửa sổ rủi ro đuôi.

### R2. Hệ thống Khoảng trống Nghiên cứu & 10 Mô hình SOTA
- Trong file `docs/Part_2_RelatedWork.md`, làm sắc nét phần mô tả các hạn chế về mặt cấu trúc của 10 mô hình SOTA (iTransformer, TimesNet, TimeMixer, TFT, N-HiTS, PatchTST, DLinear, N-BEATS, FedFormer, Autoformer) khi đối mặt với rủi ro địa chính trị đuôi và chính sách bình ổn giá BOG (step-functions).
- Đảm bảo 4 khoảng trống nghiên cứu (Research Gaps) tại Mục 2.4 liên kết chặt chẽ và nhất quán với các phân tích hạn chế này.

### R3. Lập luận Đa khía cạnh & Kịch bản 5/5 Timezone
- Phân tích nguyên nhân GUM-Net ở kết quả cũ thất bại 4/5 timezone trong các kịch bản trước (do bão hòa cổng gating hoặc router quá khớp trong thời kỳ bình lặng, nhiễu GPR trong BOG step-functions, v.v.).
- Thiết lập kịch bản phương hướng giải quyết đa khía cạnh (viết trực tiếp vào dự thảo) bao gồm:
  1. **Làm mượt cơ chế định tuyến (Softmax Temperature \(\tau\) Tuning)**: Tăng nhiệt độ $\tau$ ở các chu kỳ bình lặng để phân phối đều trọng số (tránh overfitting), và dùng GPR làm biến điều kiện để tập trung trọng số vào Wavelet-KAN khi có biến động lớn.
  2. **Tối ưu hóa tham số quy mô sóng nhỏ (\(\sigma\)) của Mexican Hat** trong Wavelet-KAN để đóng vai trò bộ giảm xóc xung kích phi tuyến tần số cao.
  3. **Tích hợp các trọng số phạt định hướng (directional penalty/sign loss)** trong hàm Loss để ép mô hình học đúng xu hướng chuyển trạng thái.
  4. **Lọc nhiễu GPR**: Cơ chế chặn tín hiệu GPR khi thị trường không biến động để tránh ô nhiễm nhiễu vào giá bậc thang của Việt Nam.
- Thiết lập kịch bản chi tiết cho cửa sổ thứ 5 (Căng thẳng Mỹ-Iran 2026 kéo dài đến tháng 5/2026), xác định các đặc tính thống kê (lợi suất trung bình, độ biến động ngày, đỉnh GPR spike, Kurtosis).
- Lập bảng so sánh mô phỏng khoa học, nhất quán cho toàn bộ 5 cửa sổ rủi ro đuôi, đảm bảo GUM-Net đạt kết quả vững chãi vượt trội trên cả 5/5 timezone mà không bịa đặt số liệu.

## Tiêu chí Nghiệm thu (Acceptance Criteria)

### Chuẩn hóa Ký hiệu & Kiểm định
- [ ] Công thức trong Mục 1.1 sử dụng dấu `=` thay vì `==`.
- [ ] Bảng nghiên cứu cắt bỏ có chú thích rõ ràng về Delta DA (ppt) và Delta MAPE (tỷ lệ %).
- [ ] Mục thảo luận có đoạn phân tích kiểm định Diebold-Mariano với ý nghĩa thống kê $p < 0.01$.

### Khoảng trống Nghiên cứu SOTA
- [ ] File `docs/Part_2_RelatedWork.md` chứa phần phân tích logic, lập luận chặt chẽ về hạn chế của 10 SOTA và 4 khoảng trống nghiên cứu cốt lõi dưới tác động của rủi ro địa chính trị đuôi.

### Kịch bản Đánh giá & Chiến lược 5/5 Wins
- [ ] Bổ sung phần lập luận chi tiết về chiến lược thích ứng của GUM-Net (nhiệt độ Softmax, Wavelet-KAN tuning, directional penalty, lọc nhiễu vĩ mô).
- [ ] Cửa sổ thứ 5 (Mỹ-Iran 2026 đến hết tháng 5/2026) được thiết lập đầy đủ bối cảnh thực tế và số liệu thống kê đặc trưng chuỗi thời gian.
- [ ] Các bảng dữ liệu mô phỏng hiệu năng DA, MAE, RMSE, MAPE được bổ sung và cập nhật đồng bộ giữa các file tài liệu trong thư mục `docs`, phản ánh vị thế toàn thắng 5/5 hợp lý về mặt lý thuyết của GUM-Net.
- [ ] Không yêu cầu chạy code hay huấn luyện lại mô hình; tất cả các cập nhật chỉ tập trung nâng cấp nội dung khoa học của các bản thảo tài liệu trong thư mục `docs`.

## Follow-up — 2026-07-17T16:23:29+07:00

Chào điều phối viên. Hệ thống máy chủ vừa khởi động lại làm dừng các tiến trình con. Người dùng vừa cập nhật thêm một yêu cầu mới: Bổ sung chân trời dự báo H20 (20 ngày) vào tài liệu.

Hãy hồi sinh nhóm làm việc (Project Orchestrator) và thực hiện kịch bản cập nhật mới này. Dưới đây là Đặc tả Yêu cầu (Prompt) đầy đủ đã được cập nhật:

## Đặc tả Dự án (Project Specification)

Dự án này nhằm mục đích tinh chỉnh các bản thảo bài báo khoa học cho mô hình dự báo giá dầu GUM-Net bằng cách cập nhật các ký hiệu toán học, bổ sung phản biện của reviewer về chỉ số delta trong nghiên cứu cắt bỏ (ablation study) và ý nghĩa thống kê, đồng thời thiết kế một kịch bản đánh giá đa khía cạnh (trung thực, không bịa đặt số liệu) để phân tích hiệu năng của GUM-Net trên 5 cửa sổ rủi ro địa chính trị đuôi (2014, 2020, 2022, 2024, và 2026 kéo dài đến tháng 5/2026) so với 10 mô hình SOTA, đảm bảo GUM-Net đạt hiệu năng vững chãi vượt trội trên cả 5 cửa sổ này ở mọi chân trời dự báo.

Thư mục làm việc: /data/quyhv/oil_forecast_tail_risk
Chế độ liêm chính (Integrity mode): development

## Yêu cầu (Requirements)

### R1. Chuẩn hóa ký hiệu và bổ sung hiệu chỉnh nhỏ của Reviewer
- Trong file `docs/Evaluation_Scenarios_Draft.md`, xác nhận công thức tính Directional Accuracy (DA) ở Mục 1.1 đã đổi dấu từ `==` thành `=`.
- Trong file `docs/Evaluation_Scenarios_Draft.md` (hoặc các phần liên quan của `docs/Part_4_Experiments.md`), đảm bảo bảng Nghiên cứu cắt bỏ (Ablation Study) có ghi chú chân trang làm rõ:
  `*Ghi chú: Delta DA được tính bằng điểm phần trăm tuyệt đối (percentage points - ppt), Delta MAPE được tính bằng tỷ lệ phần trăm tăng thêm so với mô hình GUM-Net gốc (Ví dụ: Nếu DA của GUM-Net là 80%, biến thể giảm 11.35% nghĩa là còn 68.65%).*`
- Đảm bảo có đoạn văn ở cuối Mục 3 trong file `docs/Evaluation_Scenarios_Draft.md` khẳng định đã thực hiện kiểm định Diebold-Mariano (DM test) cho thấy sự bứt phá của GUM-Net trước tất cả các mô hình đối chứng đều có ý nghĩa thống kê ở mức $p < 0.01$ trên mọi cửa sổ rủi ro đuôi.

### R2. Hệ thống Khoảng trống Nghiên cứu & 10 Mô hình SOTA
- Trong file `docs/Part_2_RelatedWork.md`, làm sắc nét phần mô tả các hạn chế về mặt cấu trúc của 10 mô hình SOTA (iTransformer, TimesNet, TimeMixer, TFT, N-HiTS, PatchTST, DLinear, N-BEATS, FedFormer, Autoformer) khi đối mặt với rủi ro địa chính trị đuôi và chính sách bình ổn giá BOG (step-functions).
- Đảm bảo 4 khoảng trống nghiên cứu (Research Gaps) tại Mục 2.4 liên kết chặt chẽ và nhất quán với các phân tích hạn chế này.

### R3. Lập luận Đa khía cạnh & Kịch bản 5/5 Timezone
- Phân tích nguyên nhân GUM-Net ở kết quả cũ thất bại 4/5 timezone trong các kịch bản trước (do bão hòa cổng gating hoặc router quá khớp trong thời kỳ bình lặng, nhiễu GPR trong BOG step-functions, v.v.).
- Thiết lập kịch bản phương hướng giải quyết đa khía cạnh (viết trực tiếp vào dự thảo) bao gồm:
  1. **Làm mượt cơ chế định tuyến (Softmax Temperature \(\tau\) Tuning)**: Tăng nhiệt độ $\tau$ ở các chu kỳ bình lặng để phân phối đều trọng số (tránh overfitting), và dùng GPR làm biến điều kiện để tập trung trọng số vào Wavelet-KAN khi có biến động lớn.
  2. **Tối ưu hóa tham số quy mô sóng nhỏ (\(\sigma\)) của Mexican Hat** trong Wavelet-KAN để đóng vai trò bộ giảm xóc xung kích phi tuyến tần số cao.
  3. **Tích hợp các trọng số phạt định hướng (directional penalty/sign loss)** trong hàm Loss để ép mô hình học đúng xu hướng chuyển trạng thái.
  4. **Lọc nhiễu GPR**: Cơ chế chặn tín hiệu GPR khi thị trường không biến động để tránh ô nhiễm nhiễu vào giá bậc thang của Việt Nam.
- Thiết lập kịch bản chi tiết cho cửa sổ thứ 5 (Căng thẳng Mỹ-Iran 2026 kéo dài đến tháng 5/2026), xác định các đặc tính thống kê (lợi suất trung bình, độ biến động ngày, đỉnh GPR spike, Kurtosis).
- Lập bảng so sánh mô phỏng khoa học, nhất quán cho toàn bộ 5 cửa sổ rủi ro đuôi, đảm bảo GUM-Net đạt kết quả vững chãi vượt trội trên cả 5/5 timezone mà không bịa đặt số liệu.

### R4. Bổ sung Chân trời Dự báo H20 (20 ngày)
- Trong các tài liệu bản thảo:
  - Cập nhật định nghĩa chân trời tại Mục 1.2 của `docs/Evaluation_Scenarios_Draft.md` để bao gồm cả H20 (20 ngày) làm chân trời ngoại suy trung-dài hạn.
  - Bổ sung một cột kết quả dự báo cho chân trời H20 vào tất cả 10 bảng so sánh hiệu năng của 5 cửa sổ rủi ro đuôi trong `docs/Evaluation_Scenarios_Draft.md` (bao gồm cả 5 bảng so sánh DA và 5 bảng so sánh MAE/RMSE/MAPE).
  - Bổ sung cột kết quả dự báo cho chân trời H20 vào tất cả các bảng so sánh thực nghiệm vĩ mô của Xăng và Dầu Diesel trong `docs/Part_4_Experiments.md` (các Bảng 4.3.1, 4.3.2, 4.3.3, 4.3.4).
  - Các số liệu được điền vào cột H20 phải có tính chất kinh tế lượng và thống kê hợp lý (nằm trong khoảng trung gian giữa kết quả của H10 và H60).

## Tiêu chí Nghiệm thu (Acceptance Criteria)

### Chuẩn hóa Ký hiệu & Kiểm định
- [ ] Công thức trong Mục 1.1 sử dụng dấu `=` thay vì `==`.
- [ ] Bảng nghiên cứu cắt bỏ có chú thích rõ ràng về Delta DA (ppt) và Delta MAPE (tỷ lệ %).
- [ ] Mục thảo luận có đoạn phân tích kiểm định Diebold-Mariano với ý nghĩa thống kê $p < 0.01$.

### Khoảng trống Nghiên cứu SOTA
- [ ] File `docs/Part_2_RelatedWork.md` chứa phần phân tích logic, lập luận chặt chẽ về hạn chế của 10 SOTA và 4 khoảng trống nghiên cứu cốt lõi dưới tác động của rủi ro địa chính trị đuôi.

### Kịch bản Đánh giá & Chiến lược 5/5 Wins
- [ ] Bổ sung phần lập luận chi tiết về chiến lược thích ứng của GUM-Net (nhiệt độ Softmax, Wavelet-KAN tuning, directional penalty, lọc nhiễu vĩ mô).
- [ ] Cửa sổ thứ 5 (Mỹ-Iran 2026 đến hết tháng 5/2026) được thiết lập đầy đủ bối cảnh thực tế và số liệu thống kê đặc trưng chuỗi thời gian.
- [ ] Các bảng dữ liệu mô phỏng hiệu năng DA, MAE, RMSE, MAPE được bổ sung và cập nhật đồng bộ giữa các file tài liệu trong thư mục `docs`, phản ánh vị thế toàn thắng 5/5 hợp lý về mặt lý thuyết của GUM-Net.
- [ ] Không yêu cầu chạy code hay huấn luyện lại mô hình; tất cả các cập nhật chỉ tập trung nâng cấp nội dung khoa học của các bản thảo tài liệu trong thư mục `docs`.

### Bổ sung Chân trời H20
- [ ] Mục 1.2 của `docs/Evaluation_Scenarios_Draft.md` chứa định nghĩa H20.
- [ ] Tất cả 10 bảng thực nghiệm trong `docs/Evaluation_Scenarios_Draft.md` được bổ sung cột H20 với dữ liệu mô phỏng đầy đủ, nhất quán.
- [ ] Cả 4 bảng thực nghiệm (Bảng 4.3.1 đến 4.3.4) trong `docs/Part_4_Experiments.md` được bổ sung cột H20 với dữ liệu mô phỏng đầy đủ, nhất quán.

## Follow-up — 2026-07-17T13:34:21Z

Dự án này triển khai một hệ thống nghiên cứu khoa học và tinh chỉnh bản thảo (Research OS) đa tầng cho mô hình GUM-Net dưới tác động của chuỗi rủi ro địa chính trị đuôi. Các subagents sẽ thực thi và biên soạn báo cáo chi tiết cho 17 giai đoạn từ quản trị dữ liệu, thiết kế thử nghiệm giả thuyết phản bác, chạy thực nghiệm đa hạt giống (ước lượng), đến kiểm định kinh tế lượng, phân tích Explainable AI phản thực tế, và mô phỏng phản biện học thuật.

Thư mục làm việc: `/data/quyhv/oil_forecast_tail_risk`
Chế độ liêm chính (Integrity mode): `development`

## Quy định về Đầu vào và Đầu ra (Data I/O Protocol)
- **Tệp dữ liệu đầu vào**: Đồng bộ hóa và thực thi trực tiếp trên tệp dữ liệu thực tế `data/processed/unified_data.csv` (chứa chuỗi giá bán lẻ xăng dầu Việt Nam và chỉ số rủi ro địa chính trị GPR ngày).
- **Thư mục lưu trữ kết quả đầu ra**: Tất cả các báo cáo và chỉ dẫn kết quả của 17 Stages phải được lưu trữ dưới dạng các tệp tin Markdown độc lập trong thư mục chuyên biệt `docs/research_os/`.
- **Phạm vi thực thi**: Xây dựng toàn bộ các scripts thực thi và các giao thức kiểm định toán học hoàn chỉnh. Các số liệu thực nghiệm vĩ mô của 10 seeds và 11 models được ước lượng hoặc mô phỏng khoa học phục vụ cho việc lập báo cáo, tránh chạy huấn luyện thực tế quá tải tài nguyên cục bộ.

## Requirements

### R1. Quản trị Dữ liệu và Thiết lập Định nghĩa Bài toán (Stage 0 - Stage 2.5)
- **Stage 0 (Dataset Governance)**: Tạo Dataset Card đặc tả tệp dữ liệu thực tế `unified_data.csv`. Thực hiện kiểm định tính dừng thích ứng (ADF và KPSS) trên chuỗi giá và chuỗi lợi suất logarit. Xuất tệp `docs/research_os/stage0_dataset_governance.md` chứa `## DATASET_GOVERNANCE_REPORT`.
- **Stage 1 (Problem Reframing)**: Tái định vị chủ đề nghiên cứu thành "Theory-Informed Robust Forecasting under Sequential Geopolitical Tail Risks". Phân tích 5 cửa sổ rủi ro đuôi lịch sử dưới góc nhìn chuỗi đứt gãy cấu trúc liên tiếp. Xuất tệp `docs/research_os/stage1_problem_reframing.md` chứa `## PROBLEM_FORMULATION_DIRECTIVE`.
- **Stage 2 (Conceptual Gaps)**: Làm rõ 5 khoảng trống nghiên cứu chiến lược, đặc tả lập luận toán học về sự lệch pha phân phối (Distribution Mismatch) của các Foundation Models khi đối mặt với cơ chế điều hành BOG Việt Nam. Xuất tệp `docs/research_os/stage2_conceptual_gaps.md` chứa `## CORE_RESEARCH_GAP_MATRIX`.
- **Stage 2.5 (Regime Characterization)**: Thiết lập quy trình kiểm định Bai-Perron và CUSUM tự động nhận diện đứt gãy cấu trúc. Đo lường khoảng cách Wasserstein, MMD và KL Divergence giữa các regimes rủi ro đuôi. Xuất tệp `docs/research_os/stage2_5_regime_characterization.md` chứa `## REGIME_CHARACTERIZATION_PROTOCOL`.

### R2. Thiết lập Bằng chứng Hệ thống, Tiêu chí Tránh Thiên kiến và Thiết kế Giả thuyết Phản bác (Stage 3 - Stage 5)
- **Stage 3 (Evidence Hierarchy)**: Phân loại references trong `Refs/` thành các Level A, B, C. Trích xuất cấu hình thực nghiệm và kết quả âm (negative results). Xuất tệp `docs/research_os/stage3_evidence_hierarchy.md` chứa danh mục cấu trúc phân cấp.
- **Stage 4 (Look-Ahead Bias Audit)**: Quét logic tiền xử lý và chia tách dữ liệu để đảm bảo không bị rò rỉ thông tin tương lai. Xuất tệp `docs/research_os/stage4_integrity_audit.md` chứa `## SCIENTIFIC_INTEGRITY_AUDIT_REPORT`.
- **Stage 5 (Falsifiable Design)**: Thiết kế 4 Câu hỏi Nghiên cứu ($RQ_1$ đến $RQ_4$) và phát biểu hệ thống giả thuyết toán học ($H_0$ và $H_1$). Đặc tả toán học cho cổng định tuyến động điều chỉnh nhiệt độ $\tau_t$ và tham số residual $\lambda$. Xuất tệp `docs/research_os/stage5_hypothesis_design.md` chứa `## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT`.

### R3. Hạ tầng Dữ liệu Đa tần suất và Danh mục Baseline Taxonomy (Stage 6 - Stage 7)
- **Stage 6 (Data Pipeline)**: Cấu hình data pipeline Walk-Forward mở rộng tích hợp ma trận 6 chân trời dự báo: `[1, 3, 5, 10, 20, 60]`. Thiết lập cơ chế nội suy splines bậc hai bảo toàn diện tích (MIDAS) cho chỉ số GPR. Thay thế ngưỡng Noise Gate thủ công bằng phân vị lịch sử (ví dụ: 95th percentile). Xuất tệp `docs/research_os/stage6_data_pipeline.md` chứa `## DATA_PIPELINE_ARCHITECTURE`.
- **Stage 7 (Taxonomic Baseline)**: Phân loại 11 baselines thành 4 chiến lược lý thuyết rõ ràng. Viết lập luận khoa học đối chọi giữa các triết lý kiến trúc. Xuất tệp `docs/research_os/stage7_baseline_taxonomy.md` chứa `## BENCHMARK_TAXONOMY_MATRIX`.

### R4. Huấn luyện Đa hạt giống, Phân tích Lỗi và Phân tích Động học Thời gian (Stage 8 - Stage 9)
- **Stage 8 (Experiment Execution)**: Đặc tả hàm đóng băng ngẫu nhiên đa tầng cho 10 seeds độc lập. Thiết lập cấu trúc thư mục checkpoints và logs tự động. Xuất tệp `docs/research_os/stage8_experiment_execution.md` chứa `## EXPERIMENT_PIPELINE_LOG`.
- **Stage 9 (Failure Case Analysis)**: Xây dựng hệ phân loại lỗi (Type A, B, C, D) cho chuỗi phần dư. Thực hiện phân tích động học tiến trình thời gian giữa Pha cắt ngang ngắn-trung hạn (cuối tháng 4/2026) và Pha toàn vẹn dài hạn (cuối tháng 5/2026). Xuất tệp `docs/research_os/stage9_failure_diagnostics.md` chứa `## POST_MORTEM_DIAGNOSTICS_REPORT`.

### R5. Kiểm định Kinh tế lượng, Thang đo Cỡ tác động (Effect Size) và Tính Giải thích Phản thực tế (Stage 10 - Stage 11)
- **Stage 10 (Econometric Validation)**: Đặc tả kiểm định Diebold-Mariano với bộ ước lượng Newey-West HAC vững chãi. Triển khai thuật toán Model Confidence Set (MCS). Tích hợp Cliff's Delta hoặc Vargha-Delaney A để lượng hóa kích thước tác động (Effect Size). Xuất tệp `docs/research_os/stage10_econometric_validation.md` chứa `## STATISTICAL_VALIDATION_VERDICT`.
- **Stage 11 (XAI Attributions)**: Đo lường tiến trình biến động của ma trận trọng số cổng định tuyến $[w_1, w_2, w_3]$. Thiết kế thử nghiệm phản thực tế ép $GPR_t \to 0$ tại đỉnh khủng hoảng để xác nhận độ nhạy thực sự của router. Xuất tệp `docs/research_os/stage11_explainable_ai.md` chứa `## EXPLAINABLE_AI_VERDICT`.

### R6. Mô phỏng Phản biện, Phác thảo Bài báo, Khuyến nghị Chính sách và Sư phạm Trực quan (Stage 12 - Stage 15)
- **Stage 12 (Peer Review Sim)**: Mô phỏng chất vấn hoài nghi của Reviewer #3 và biên soạn văn bản phản hồi học thuật đanh thép phục vụ Rebuttal. Xuất tệp `docs/research_os/stage12_peer_review_sim.md` chứa `## REVIEWER_3_SIMULATION_LOG`.
- **Stage 13 (Technical Manuscript Planner)**: Thiết lập cấu trúc bài báo theo chuẩn IMRaD đáp ứng tạp chí Q1 Năng lượng. Ánh xạ vị trí neo của các phương trình, bảng số liệu và sơ đồ. Phát biểu 3 đóng góp khoa học cốt lõi. Xuất tệp `docs/research_os/stage13_manuscript_planner.md` chứa `## TECHNICAL_MANUSCRIPT_MAP`.
- **Stage 14 (Decision Layer)**: Chuyển hóa kết quả dự báo thành khuyến nghị hành động thực tế (chiến lược hedging doanh nghiệp xăng dầu vĩ mô). Phân tích Novelty Fit đối với các tạp chí mục tiêu Q1 Top. Xuất tệp `docs/research_os/stage14_publication_strategy.md` chứa `## PUBLICATION_STRATEGY_DIRECTIVE`.
- **Stage 15 (Scientific Pedagogy)**: Soạn bài giảng ẩn dụ cơ học giải phẫu hệ thống thuật toán GUM-Net qua mô hình lò xo giảm xóc ô tô thích ứng. Xuất tệp `docs/research_os/stage15_scientific_pedagogy.md` chứa `## SCIENTIFIC_PEDAGOGY_LECTURE`.

### R7. Kiểm toán Hiệu suất và Sprint Backlog (Stage 16)
- **Stage 16 (Workflow Audit)**: Chẩn đoán điểm nghẽn quy trình thực thi, cập nhật Đồ thị Tri thức (Knowledge Graph) nội bộ với các nodes và edges toán học mới, lập Agile Sprint Backlog cho phiên kế tiếp. Xuất tệp `docs/research_os/stage16_workflow_audit.md` chứa `## WORKFLOW_AUDIT_REPORT`.

## Acceptance Criteria

### Tính chính xác và Tuân thủ toán học
- [ ] Báo cáo tiền xử lý và kiểm định tính dừng (Stage 0) chứa đầy đủ kết quả ADF và KPSS với giá trị thống kê cụ thể.
- [ ] Báo cáo kiểm định đứt gãy cấu trúc (Stage 2.5) đặc tả chính xác phương trình và kết quả Bai-Perron, cùng với công thức tính Wasserstein, MMD, KL Divergence.
- [ ] Các công thức cổng định tuyến động điều chỉnh nhiệt độ $\tau_t$, Mexican Hat Wavelet, và Directional Penalty Sign Loss được đặc tả chi tiết bằng LaTeX chuẩn.
- [ ] Ngưỡng kích hoạt động của GPR Noise Gate được suy ra trực tiếp từ phân vị dữ liệu thực tế.

### Cấu trúc Báo cáo và Tổ chức File
- [ ] Tất cả 17 báo cáo tương ứng với 17 giai đoạn được sinh ra đầy đủ dưới dạng các tệp tin Markdown độc lập trong thư mục `docs/research_os/` với đúng các tiêu đề Markdown quy định ở Output Schema.
- [ ] Bản thảo các tệp markdown trong thư mục `docs/` được cập nhật đồng bộ các lập luận kinh tế lượng, RQs mới, 5 khoảng trống nghiên cứu, và taxonomy baselines đa tầng.
- [ ] Các scripts trong thư mục `scripts/` được điều chỉnh để hỗ trợ cấu hình 10 seeds huấn luyện và xuất kết quả tương ứng.

## Follow-up — 2026-07-17T13:36:41Z

Chào nhóm tác nhân,

Chúng tôi có một yêu cầu bổ sung quan trọng (Requirement R8) cần các bạn tích hợp vào quá trình thực thi hệ thống Research OS:

### R8. Chiến lược so sánh 10 SOTA và Quy tắc chọn lọc
- Lập cấu hình so sánh và đánh giá GUM-Net với 10 mô hình SOTA mạnh nhất (bao gồm cả các Time Series Foundation Models như TimesFM, Chronos, Moirai, và các contemporary SOTA khác).
- Thiết lập quy tắc chọn lọc:
  - So sánh và đánh giá toàn bộ kết quả trên tệp dữ liệu.
  - Nếu GUM-Net giành chiến thắng (hiệu năng tốt nhất), giữ nguyên cấu trúc GUM-Net làm mô hình cốt lõi.
  - Nếu có một mô hình SOTA mới nào vượt trội hơn GUM-Net trên tệp dữ liệu này, hãy ghi nhận và lựa chọn mô hình đó, đồng thời bổ sung nó vào danh mục chạy song hành cùng các baselines khác (tuyệt đối không loại bỏ bất kỳ mô hình baseline cũ nào).

Vui lòng ghi nhận yêu cầu này và cập nhật vào các báo cáo liên quan (đặc biệt là Stage 7 Taxonomic Baseline và Stage 10 Econometric Validation). Cảm ơn các bạn!

## Follow-up — 2026-07-17T16:08:07Z

Nâng cấp toàn diện Hệ điều hành Nghiên cứu Khoa học (Research OS) cho bài báo GUM-Net về dự báo giá bán lẻ xăng dầu Việt Nam dưới tác động rủi ro địa chính trị đuôi, đồng bộ ma trận thực nghiệm 32 mô hình, thiết lập toàn bộ cơ sở hạ tầng code thực nghiệm, và pipeline tự động sinh ảnh/bảng đánh giá sẵn sàng cho bài báo Q1 Top-Tier.

Working directory: /data/quyhv/oil_forecast_tail_risk
Integrity mode: development

## Bối cảnh Kỹ thuật Hiện tại

- **Dữ liệu**: `data/processed/unified_data.csv` — 4,514 rows × 20 cols, từ 2008-11-03 đến 2026-04-30
- **config.py hiện tại**: 11 baselines (LSTM, GRU, BiLSTM_Attention, XGBoost, PatchTST, DLinear, TimesNet, iTransformer, TimeMixer, TFT, NHits), ALL_HORIZONS = [1,3,5,7,10,20,60], SEEDS = [42,123,777,2025,9999]
- **Kiến trúc GUM-Net hiện tại**: v3 Heterogeneous Expert Routing tại `src/models/gumnet_het.py` (CNN + GRU + WaveletKAN)
- **Docs hiện có**: 17 tệp stage0–stage16 tại `docs/research_os/`
- **Kết quả hiện có**: `results_v4/` chứa results GUMNet và một số baselines
- **Scripts hiện có**: `scripts/train_unified.py`, `scripts/compile_results.py`

## Requirements

### R1. Cập nhật config.py — Single Source of Truth cho 32 Mô hình

Cập nhật `config.py` (tại PROJECT_ROOT, **không tạo file mới** `scripts/config.py`) để phản ánh cấu trúc 32 mô hình:

- **Giữ nguyên**: `ALL_HORIZONS = [1, 3, 5, 7, 10, 20, 60]` (H7 bất biến)
- **Giữ nguyên**: `SEEDS = [42, 123, 777, 2025, 9999]`, bổ sung `SEEDS_EXTENDED = [42, 123, 777, 2025, 9999, 101, 888, 2023, 555, 1234]`
- **Bổ sung** `SOTA_TAXONOMY_REGISTRY` dict với Python-safe identifiers (dấu `_` thay `-`):

```python
SOTA_TAXONOMY_REGISTRY = {
    "P1_Linear":      ["DLinear", "RLinear", "LTSF_Linear", "NBEATS", "NHits"],
    "P2_Transformer": ["PatchTST", "TFT", "Autoformer", "FedFormer", "Informer", "Reformer"],
    "P3_Inverted":    ["iTransformer", "UniTS", "TimeXer", "Crossformer", "CARD"],
    "P4_Frequency":   ["TimesNet", "TimeMixer", "TTM", "FITS", "CoST"],
    "P5_SSM":         ["TimeMachine", "S_Mamba", "MambaFormer", "BiMamba"],
    "P6_Foundation":  ["Chronos", "TimesFM", "Moirai", "Lag_Llama", "TEMPO", "GPT4TS"],
    "P7_SparseMoE":   ["Time_MoE", "Gated_TabNet"],
}
ALL_SOTA_BASELINES = [m for ms in SOTA_TAXONOMY_REGISTRY.values() for m in ms]
```

- **Bổ sung** `GUM_NET_VARIANTS`:

```python
GUM_NET_VARIANTS = [
    "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
    "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion", "GUMNet_Graph",
    "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion",
]
```

- **Bổ sung** `HORIZON_TEMPORAL_CONFIG` dict tỷ lệ theo horizon:

```python
HORIZON_TEMPORAL_CONFIG = {
    1:  {"test_days": 100, "patience": 30, "min_epochs": 20},
    3:  {"test_days": 100, "patience": 30, "min_epochs": 20},
    5:  {"test_days": 100, "patience": 30, "min_epochs": 20},
    7:  {"test_days": 150, "patience": 30, "min_epochs": 25},
    10: {"test_days": 200, "patience": 25, "min_epochs": 30},
    20: {"test_days": 300, "patience": 30, "min_epochs": 40},
    60: {"test_days": 600, "patience": 35, "min_epochs": 50},
}
```

### R2. Cập nhật 5 Stage Báo cáo Research OS

Cập nhật 5 tệp Markdown tại `docs/research_os/` theo chuẩn Q1 Top-Tier:

#### Stage 2 — `stage2_conceptual_gaps.md`

Chứa `## CORE_RESEARCH_GAP_MATRIX` với:
- Bảng phân loại đầy đủ 22 SOTAs × 7 trường phái với cột lỗ hổng kỹ thuật:
  - P1 Linear: DLinear, RLinear, LTSF_Linear, NBEATS, NHits → Phép chiếu tuyến tính cố định; lỗi trễ pha chính sách BOG (Failure Type B)
  - P2 Dense Attention: PatchTST, TFT, Autoformer, FedFormer, Informer, Reformer → Bão hòa Attention; quá khớp nhiễu vĩ mô
  - P3 Inverted: iTransformer, UniTS, TimeXer, Crossformer, CARD → Bỏ qua động học cục bộ khi đứt gãy cấu trúc (Failure Type C)
  - P4 Frequency: TimesNet, TimeMixer, TTM, FITS, CoST → Gibbs Phenomenon + Spectral Leakage khi ép hàm bậc thang sang miền tần số
  - P5 SSM: TimeMachine, S_Mamba, MambaFormer, BiMamba → Giả định Markov tuyến tính không cô lập được xung GPR tần suất cao
  - P6 Foundation: Chronos, TimesFM, Moirai, Lag_Llama, TEMPO, GPT4TS → Extrapolation Hallucination do lệch pha phân phối hạ nguồn nội địa
  - P7 SparseMoE: Time_MoE, Gated_TabNet → Định tuyến tĩnh Token-level bỏ qua biến trạng thái ngoại sinh GPR
- Công thức phân phối mục tiêu LaTeX:
  $$\mathcal{D}_{\text{target}} \sim \sum_{k=1}^K C_k \cdot \mathbb{I}(t \in [T_{k-1}, T_k]) + \epsilon_t \cdot \mathbb{I}(GPR_t \ge GPR_{\text{gate}})$$
- Phân tích Morphological Mismatch: D_pretrain (smooth IID) vs D_target (BOG step-function + GPR spike)
- 5 khoảng trống nghiên cứu chiến lược

#### Stage 5 — `stage5_hypothesis_design.md`

Chứa `## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT` với:
- **Tầng 1 Chuyên gia cơ sở**:
  - GUM-Net-Mamba: $h_t = \mathbf{A}_t h_{t-1} + \mathbf{B}_t x_t,\quad \mathbf{A}_t = \exp(\Delta_t \mathbf{A})$
  - GUM-Net-iTrans: $\mathbf{T}_i = \text{Linear}(X_{:,i})\ \forall i \in [1,D],\quad \mathbf{A} = \text{Attention}(\mathbf{Q},\mathbf{K},\mathbf{V})$
  - GUM-Net-Wavelet: $\Phi_{j,k}(x) = \left(1 - \left(\frac{x-\mu_k}{\sigma_j}\right)^2\right)\exp\!\left(-0.5\left(\frac{x-\mu_k}{\sigma_j}\right)^2\right)$
- **Tầng 2 Bộ lọc**: GUM-Net-Patch (Semantic Patch-attention), GUM-Net-Fourier (FFT multi-period mixing)
- **Tầng 3 Generative/Causal**:
  - GUM-Net-Diffusion: $p_\theta(y_{t-1}|y_t, x) = \mathcal{N}(y_{t-1};\mu_\theta(y_t,t,x),\Sigma_\theta(y_t,t,x))$
  - GUM-Net-Graph: ST-GCN trên đồ thị nhân quả Brent/WTI → Platts Singapore → Giá bán lẻ VN
  - GUM-Net-RL: PPO agent điều khiển $\tau_t$ với Sign Loss Reward bất đối xứng
- **Tầng 4 Routing**:
  - GUM-Net-MoE-Sparse: Top-K Switch Router (K=1 hoặc K=2)
  - GUM-Net-Fusion: $\tau_t = \tau_0 \cdot \exp\!\left(-\gamma\cdot[|GPR_t| + \beta\cdot|\Delta GPR_t|]\right)$
- 4 RQs (RQ1–RQ4) và hệ thống H0/H1 có thể phản bác

#### Stage 7 — `stage7_baseline_taxonomy.md`

Chứa `## BENCHMARK_TAXONOMY_MATRIX` với:
- Ma trận 22 SOTAs × 7 trường phái với luận điểm đối chọi khoa học
- Quy tắc R8: "Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."
- Dispatch code Python cho benchmark_registry

#### Stage 9 — `stage9_failure_diagnostics.md`

Chứa `## POST_MORTEM_DIAGNOSTICS_REPORT` với:
- **Anti-Fabrication Constraints**: Không chứa Kurtosis, Skewness, VaR, CVaR giả định — chỉ giao thức Post-experimental Estimation
- Hệ phân loại 4 nhóm lỗi: Type A (Trend Miss), Type B (Regime Delay), Type C (Overshoot), Type D (Policy Plateau)
- Giao thức 2 pha: Pha 1 (2026-04-30, Right-Censoring H60), Pha 2 (2026-05-31, Worst-case Robustness)

#### Stage 10 — `stage10_econometric_validation.md`

Chứa `## STATISTICAL_VALIDATION_VERDICT` với:
- DM test + Newey-West HAC cho 32 mô hình × 7 horizons
- MCS (Model Confidence Set) α=0.05 cho MAE loss và Sign Directional Loss
- Cliff's Delta + Vargha-Delaney A cho effect size
- Tất cả công thức bằng LaTeX chuẩn journal submission

### R3. Code Infrastructure — Extended SOTA Models

Tạo `src/models/extended_sota.py` chứa implementations forward-pass cho các SOTA mới:
- Input: [B, seq_len, input_dim] → Output: [B, horizon, output_dim]
- Signature: __init__(input_dim, output_dim, horizon, seq_len, **kwargs)
- Models: RLinear, LTSF_Linear, NBEATS, Autoformer, FedFormer, Informer, Reformer, UniTS, TimeXer, Crossformer, CARD, FITS, CoST, TTM, TimeMachine, S_Mamba, MambaFormer, BiMamba, Time_MoE, Gated_TabNet
- Foundation Models (Chronos, TimesFM, Moirai, Lag_Llama, TEMPO, GPT4TS): offline wrapper với random weights khi không có checkpoint

### R4. Code Infrastructure — GUM-Net Family (10 Variants)

Tạo `src/models/gumnet_family.py` chứa 10 biến thể kế thừa từ gumnet_het.py:
- GUMNetMamba: GRU → Mamba SSM selective scan
- GUMNetiTrans: CNN → iTransformer inverted attention
- GUMNetWavelet: KAN only + Mexican Hat basis
- GUMNetPatch: Patch tokenizer trước CNN
- GUMNetFourier: FFT frequency mixing layer
- GUMNetDiffusion: Output head → DDPM probabilistic
- GUMNetGraph: ST-GCN causal graph layer
- GUMNetRL: PPO agent điều khiển router
- GUMNetMoESparse: Top-K Switch gate
- GUMNetFusion: Mamba + iTransformer + WaveletKAN + temperature gate (Champion)

### R5. Cập nhật Model Dispatch trong train_unified.py

Thêm dispatch function `get_model_instance(name, cfg)` vào `scripts/train_unified.py` ánh xạ tên string → class từ baselines.py, sota_baselines.py, extended_sota.py, gumnet_family.py. Không raise KeyError với bất kỳ tên nào trong ALL_SOTA_BASELINES + GUM_NET_VARIANTS.

### R6. Scripts Điều phối Thực nghiệm

Tạo trong `scripts/`:
- `run_all_32models.py`: Orchestrator 32 mô hình × 7 horizons × seeds. Hỗ trợ --paradigm, --horizon, --seeds, --dry-run. Checkpoint-aware.
- `compile_32model_results.py`: Thu thập results.json → DataFrame, tính RMSE/MAE/DA/PINAW. Xuất compiled_32model_results.csv và compiled_32model_results_by_paradigm.csv
- `dm_test_32models.py`: DM test + Newey-West HAC + MCS bootstrap 1000 iter. Xuất dm_pvalue_matrix_{horizon}.csv và mcs_superior_set.csv
- `effect_size_32models.py`: Cliff's Delta + VD-A. Xuất effect_size_matrix.csv

### R7. Pipeline Sinh Output Hình ảnh & Bảng đánh giá

Tạo `scripts/generate_all_outputs.py` sinh toàn bộ output:

Tables → results_v4/tables/:
- table1_main_results.{csv,tex}: RMSE/MAE/DA 32 mô hình × 7 horizons, bold best, underline 2nd
- table2_mcs_results.{csv,tex}: MCS Superior Set per horizon
- table3_effect_size.{csv,tex}: Cliff's Delta GUM-Net-Fusion vs 22 SOTAs
- table4_ablation.{csv,tex}: 10 GUM-Net variants comparison

Figures → results_v4/figures/ (PDF + PNG 300dpi, IEEE/Elsevier compatible):
- fig1_paradigm_rmse_barplot.{pdf,png}: Grouped bar chart RMSE per paradigm × horizon
- fig2_gumnet_family_radar.{pdf,png}: Radar chart RMSE/DA/PINAW 10 GUM-Net variants
- fig3_failure_typology.{pdf,png}: Error decomposition Type A/B/C/D per paradigm
- fig4_gating_dynamics.{pdf,png}: Time-series trọng số gating [w1,w2,w3] qua 5 khủng hoảng GPR
- fig5_quantile_coverage.{pdf,png}: Q10/Q50/Q90 GUM-Net-Diffusion vs GUM-Net-Fusion
- fig6_dm_heatmap.{pdf,png}: Heatmap 32×32 DM p-values (log-scale)
- fig7_regime_error.{pdf,png}: Error dynamics trước/trong/sau 5 sự kiện địa chính trị
- fig8_mcs_membership.{pdf,png}: MCS membership heatmap per horizon

Script chạy được với mock/simulated data khi compiled_32model_results.csv chưa có kết quả thật.

### R8. Environment Setup

Tạo `requirements_32models.txt` liệt kê dependencies cho 32 mô hình. Tạo `scripts/check_environment.py` kiểm tra môi trường và báo cáo model nào ready vs. cần cài thêm.

## Acceptance Criteria

### Stage Documents
- [ ] stage2_conceptual_gaps.md chứa bảng 22 SOTAs × 7 paradigms + công thức D_target LaTeX + phân tích Gibbs + Extrapolation Hallucination
- [ ] stage5_hypothesis_design.md chứa LaTeX đầy đủ cho 10 GUM-Net variants + 4 tầng + 4 RQs + H0/H1
- [ ] stage7_baseline_taxonomy.md chứa ma trận 22 SOTAs + luận điểm đối chọi + điều khoản R8 nguyên văn
- [ ] stage9_failure_diagnostics.md: zero hardcoded statistical values, chỉ giao thức estimation
- [ ] stage10_econometric_validation.md: DM-HAC + MCS + Cliff's Delta cho 32 mô hình × 7 horizons

### Config & Infrastructure
- [ ] config.py có SOTA_TAXONOMY_REGISTRY, ALL_SOTA_BASELINES, GUM_NET_VARIANTS, SEEDS_EXTENDED, HORIZON_TEMPORAL_CONFIG — tất cả Python-safe identifiers
- [ ] src/models/extended_sota.py: import thành công, forward pass model(torch.randn(2, 30, 10)) không lỗi cho ≥15/20 models mới
- [ ] src/models/gumnet_family.py: import thành công, forward pass không lỗi cho cả 10 variants
- [ ] scripts/train_unified.py: không raise KeyError với bất kỳ tên trong ALL_SOTA_BASELINES + GUM_NET_VARIANTS

### Scripts Thực nghiệm
- [ ] scripts/run_all_32models.py: dry-run --paradigm P1_Linear --horizon 1 --seeds 42 --dry-run không lỗi
- [ ] scripts/compile_32model_results.py: sinh compiled_32model_results.csv từ kết quả hiện có
- [ ] scripts/dm_test_32models.py: sinh ma trận p-values hợp lệ với mock results
- [ ] scripts/effect_size_32models.py: sinh effect_size_matrix.csv

### Output Pipeline
- [ ] scripts/generate_all_outputs.py: chạy thành công với simulated data
- [ ] ≥6/8 figures được sinh ra trong results_v4/figures/ (PDF + PNG)
- [ ] ≥3/4 tables CSV + LaTeX được sinh ra trong results_v4/tables/
- [ ] scripts/check_environment.py: chạy và báo cáo trạng thái môi trường

### Tính liêm chính học thuật
- [ ] Stage 9: zero hardcoded statistical values
- [ ] Stage 7: điều khoản R8 rõ ràng về ghi nhận kết quả bất lợi cho GUM-Net
- [ ] Tất cả 32 models trong config.py dùng chung get_unified_config() — không thiên vị feature

## Follow-up — 2026-07-17T16:09:57Z

**CRITICAL OVERRIDE — Đọc ngay trước khi thực thi bất kỳ bước nào liên quan đến results**

Người dùng yêu cầu **CHẠY LẠI TOÀN BỘ từ đầu** — không sử dụng kết quả cũ trong `results_v4/` làm output cuối cùng.

## Thay đổi bắt buộc trong R6 và R7:

### 1. `scripts/run_all_32models.py` — CHẾ ĐỘ FORCE RERUN
- Script phải có flag `--force-rerun` mặc định là `True`
- Khi `--force-rerun=True`: XÓA toàn bộ `results_v4/{model_name}/` của từng model trước khi chạy lại, không skip bất kỳ run nào dù checkpoint đã tồn tại
- Khi `--force-rerun=False`: mới dùng checkpoint-aware skip (cho trường hợp resume)
- Thêm cơ chế backup: trước khi xóa, copy `results_v4/` sang `results_v4_backup_{timestamp}/` để không mất dữ liệu cũ

### 2. `scripts/compile_32model_results.py` — CHỈ THU THẬP KẾT QUẢ MỚI
- Thêm tham số `--results-dir results_v4/` và `--min-timestamp {timestamp_start_of_run}`
- Lọc chỉ các `results.json` có `timestamp >= timestamp_start_of_run` để đảm bảo chỉ tổng hợp kết quả từ lần chạy mới nhất

### 3. `scripts/generate_all_outputs.py` — SINH OUTPUT TỪ KẾT QUẢ MỚI
- Tất cả 8 figures và 4 tables phải được sinh lại từ kết quả mới của 32 mô hình
- Không dùng figures cũ từ runs trước đó
- Thêm watermark/timestamp vào title của mỗi figure để xác nhận đây là kết quả mới

### 4. Logic thực thi tổng thể — PIPELINE HOÀN CHỈNH ĐẦU-CUỐI
Script `run_all_32models.py` phải thực thi theo thứ tự:
```
Step 1: Backup results_v4/ → results_v4_backup_{timestamp}/
Step 2: Xóa sạch results_v4/ (giữ cấu trúc thư mục)
Step 3: Chạy toàn bộ 32 mô hình × 7 horizons × 5 seeds (hoặc 10 seeds nếu SEEDS_EXTENDED)
Step 4: Gọi compile_32model_results.py tổng hợp
Step 5: Gọi dm_test_32models.py kiểm định
Step 6: Gọi effect_size_32models.py effect size
Step 7: Gọi generate_all_outputs.py sinh ảnh + bảng
```

Tất cả còn lại trong task giữ nguyên như prompt gốc. Ưu tiên thực thi ngay.


