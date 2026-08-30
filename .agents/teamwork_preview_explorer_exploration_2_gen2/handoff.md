# Handoff Report

This report summarizes the read-only exploration and analysis of the draft papers in `docs/` regarding the Ablation Study table footnotes, the Diebold-Mariano test significance paragraph, and the structural limitations of 10 State-of-the-Art (SOTA) models mapped to the 4 research gaps in Section 2.4.

---

## 1. Observation

### 1.1. Placement of the Ablation Study Table Explanatory Footnote/Notes
- **File**: `docs/Evaluation_Scenarios_Draft.md`
- **Location**: Section 4, lines 330–347.
- **Specific Footnote Line**: Line 339.
- **Verbatim Text**:
  ```markdown
  330: ## 4. Nghiên cứu Cắt bỏ (Ablation Study)
  331: 
  332: Để đánh giá định lượng đóng góp của từng thành phần kiến trúc trong GUM-Net đối với sự vững chãi trước rủi ro địa chính trị đuôi, chúng tôi thực hiện nghiên cứu cắt bỏ trên 3 biến thể cấu trúc:
  333: 1. **w/o Wavelet-KAN**: Loại bỏ hoàn toàn chuyên gia Wavelet-KAN và chỉ giữ lại nhánh CNN + GRU.
  334: 2. **w/o GRU-Attention**: Loại bỏ nhánh GRU và cơ chế Tự chú ý đa đầu để đánh giá năng lực lưu giữ ký ức dài hạn.
  335: 3. **w/o Dynamic Gating (Equal Weight)**: Thay thế bộ định tuyến động Softmax bằng cơ chế cộng gộp trung bình trọng số cố định (\(w_i = 1/3\)).
  336: 
  337: Bảng dưới đây thống kê sự suy giảm hiệu năng (Delta DA và Delta MAPE) trung bình của các biến thể so với GUM-Net đầy đủ trên toàn bộ 5 cửa sổ rủi ro đuôi ở chân trời dự báo dài H60:
  338: 
  339: *Ghi chú: Delta DA được tính bằng điểm phần trăm tuyệt đối (percentage points - ppt), Delta MAPE được tính bằng tỷ lệ phần trăm tăng thêm so với mô hình GUM-Net gốc (Ví dụ: Nếu DA của GUM-Net là 80%, biến thể giảm 11.35% nghĩa là còn 68.65%).*
  340: 
  341: | Biến thể cấu trúc | Delta DA XĂNG (%) | Delta MAPE XĂNG (%) | Delta DA DẦU (%) | Delta MAPE DẦU (%) | Luận điểm khoa học & Vai trò kiến trúc |
  342: | :--- | :---: | :---: | :---: | :---: | :--- |
  343: | **GUM-Net (Gốc)** | **0.0 (Reference)** | **0.0 (Reference)** | **0.0 (Reference)** | **0.0 (Reference)** | Kiến trúc tích hợp đầy đủ tối ưu. |
  344: | w/o Wavelet-KAN | -8.45% | +1.85% | -9.12% | +2.10% | Khẳng định Wavelet-KAN là chuyên gia chính chịu trách nhiệm hấp thụ xung kích phi tuyến GPR. Khi loại bỏ, mô hình mất hoàn toàn bộ giảm xóc cục bộ. |
  345: | w/o GRU-Attention | -5.20% | +1.20% | -6.50% | +1.45% | Chứng minh tầm quan trọng của GRU và cơ chế Attention trong việc ghi nhớ xu hướng vĩ mô dài hạn tại H60. |
  346: | w/o Dynamic Gating | -11.35% | +2.65% | -12.40% | +2.95% | Thất bại thảm hại nhất. Cho thấy định tuyến cổng Softmax động là trái tim của MoE, giúp mô hình linh hoạt chuyển dịch tham số thích ứng theo từng bối cảnh sốc. |
  ```
- **Note**: The file `docs/Part_4_Experiments.md` does not contain the word "Ablation" or "cắt bỏ" (Grep search returned 0 results).

### 1.2. Placement of the Diebold-Mariano Test Significance Paragraph
- **File**: `docs/Evaluation_Scenarios_Draft.md`
- **Location**: Section 3, item 6, lines 324–326.
- **Verbatim Text**:
  ```markdown
  324: 6. **Kiểm định Ý nghĩa Thống kê (Statistical Significance)**:
  325:    Để đảm bảo tính vững chãi thống kê, chúng tôi đã tiến hành kiểm định Diebold-Mariano (DM test) đối với các chuỗi sai số dự báo. Kết quả cho thấy sự bứt phá của GUM-Net trước tất cả các mô hình đối chứng đều có ý nghĩa thống kê ở mức \(p < 0.01\) trên mọi cửa sổ rủi ro đuôi.
  ```
- **Note**: The file `docs/Part_4_Experiments.md` does not contain references to "Diebold", "Mariano", or "DM test" (Grep searches returned 0 results). However, references to Diebold-Mariano do exist in `Part_1_Intro.md` (line 48) and `Part_2_RelatedWork.md` (line 35), and the literature reference is located in `Part_5_Conclusion_Refs.md` (line 59).

### 1.3. Structural Limitations of the 10 SOTA Models
As described in `docs/Part_2_RelatedWork.md` (lines 9–20), the 10 SOTA models exhibit structural limitations under extreme tail risk events and price stabilization policies (BOG step-functions):
- **iTransformer**: Performs self-attention variable-wise (as tokens) which captures cross-variable correlations well but ignores non-linear temporal dependencies and is highly sensitive to local shocks.
- **TimesNet**: Transforms 1D series to 2D tensors based on Fast Fourier Transform (FFT) to extract periodic features. Fails during geopolitical crises because tail risk events are sudden, non-periodic, and unique, causing phase-shift errors.
- **TimeMixer**: Employs multi-scale mixing across sampling rates but lacks dynamic activation functions (e.g., wavelets) to suppress/absorb exogenous GPR spikes.
- **TFT**: Combines self-attention and variable selection. Its massive parameter count makes it prone to overfitting to short-term shock volatility, losing robustness in long-term predictions.
- **N-HiTS**: Relies on multi-rate interpolation and pooling. The linear pooling/downsampling acts as a low-pass filter, smoothing out sharp GPR shocks and underestimating tail risk severity.
- **PatchTST**: Splits series into patches to preserve local information. Under extreme structural breaks at long horizons (H60), historical patches do not contain analog scenarios, causing complete performance collapse (negative $R^2$).
- **DLinear**: A simple linear architecture decomposing series into trend/seasonal components. Highly stable under normal conditions but cannot capture non-linear, non-additive interactions between GPR shocks and local price stabilization.
- **N-BEATS**: Uses backward/forward residual connections. Built primarily as a univariate model, it lacks native mechanisms to effectively integrate multi-dimensional exogenous variables like GPR.
- **FedFormer**: Uses frequency-domain attention (Fourier/Wavelet). Representing features globally in the frequency domain loses time-localization, causing delayed reactions to abrupt structural breaks.
- **Autoformer**: Replaces self-attention with auto-correlation to find repeating historical patterns. Utterly helpless against black swan tail events that have no historical precedent.

---

## 2. Logic Chain

To synthesize these findings and explain how the SOTA models' structural limitations link to the 4 Research Gaps defined in Section 2.4 of `docs/Part_2_RelatedWork.md`, we apply step-by-step logical reasoning:

### 2.1. Gap 1: Lack of Decoupled Modelling Strategy (Vietnam-Specific Regulated Market)
- **Premise**: Augmented Dickey-Fuller (ADF) tests show that xăng (RON95, RON92) is stationary, whereas diesel (DO 0.05%, DO 0.001%) is non-stationary and trend-dominated (`Part_3_Methodology.md`, lines 11-15).
- **SOTA Defect**: SOTA models process all variables uniformly within a single model architecture or joint representation space.
- **Logical Connection**: Under the price-stabilization BOG step-functions, xăng and diesel are subject to different regulatory weights, tax structures, and price adjustments. Modeling them jointly in SOTA models causes "signal cross-contamination" (e.g., diesel's strong trend corrupting gasoline's mean-reverting features), degrading accuracy.

### 2.2. Gap 2: Inability of SOTA Models to Handle Geopolitical Tail Risk
- **Premise**: Geopolitical shocks (represented by the GPR Index) are sudden, non-periodic, highly non-linear, and lack historical precedents (black swans).
- **SOTA Defect**: SOTA architectures either rely on global frequency/auto-correlation (TimesNet, FedFormer, Autoformer), assume linearity (DLinear), downsample and smooth out peaks (N-HiTS), lack multivariate integration (N-BEATS), or suffer from historical patch dependency (PatchTST) and parameter overfitting (TFT).
- **Logical Connection**: SOTA models do not possess a localized, non-linear shock-absorbing component. GUM-Net addresses this gap by incorporating a **Wavelet-KAN** expert utilizing Mexican Hat wavelets, which have dual time-frequency localization and fast decay properties to absorb GPR spikes locally.

### 2.3. Gap 3: Lack of Horizon-Aware Dynamic Routing
- **Premise**: Short-term forecasting (H1) is dominated by local price momentum and step-function flat periods, where GPR index fluctuations act as noise. Long-term forecasting (H60) is dominated by cumulative macroeconomic trends and geopolitical risks (`Evaluation_Scenarios_Draft.md`, lines 39-47; `Part_4_Experiments.md`, lines 89-96).
- **SOTA Defect**: SOTA models apply static architectures with fixed weights regardless of whether they predict H1 or H60.
- **Logical Connection**: Because SOTA models cannot adapt their structural priorities across horizons, they suffer from either overfitting to GPR noise in H1 (which DLinear avoids) or catastrophic cumulative error collapse in H60 (which PatchTST suffers from). A horizon-aware routing mechanism is necessary to dynamically shift weights between local (CNN), trend (GRU), and shock (Wavelet-KAN) experts as $h$ changes.

### 2.4. Gap 4: Lack of Reliable Evaluation Protocols and Directional Metrics on Regulated Markets
- **Premise**: BOG price stabilization produces flat prices (high sparsity in returns) and step-like jumps. Traditional point metrics (MAE, RMSE, MAPE) on standard random splits fail to measure directional accuracy (DA) or guard against time-leakage.
- **SOTA Defect**: SOTA models are optimized for point errors and evaluated under standard splits, hiding their failures in directional forecasting during crises.
- **Logical Connection**: Without a Walk-Forward expanding window validation and statistical tests (like the Diebold-Mariano test) applied specifically to extreme tail-risk windows, it is impossible to evaluate whether a model's predictive superiority under tail-risk shocks is statistically significant.

---

## 3. Caveats

- **No Code Implementation**: In compliance with the "Read-only investigation" constraint, no changes were applied to the markdown files in `docs/` or the source code.
- **Exclusion of Codebase verification**: The analysis is based purely on the documents inside `docs/` and results in `results_v4/`. The exact implementation of these models was not audited.
- **Assumption on Model Descriptions**: The structural limitations of SOTA models listed in Section 2.2 of `Part_2_RelatedWork.md` are assumed to be accurate representations of their theoretical characteristics as described in literature.

---

## 4. Conclusion

1. **Ablation Footnote Placement**: Located at line 339 of `docs/Evaluation_Scenarios_Draft.md` under Section 4. It should be integrated or kept alongside the ablation table if merged with `docs/Part_4_Experiments.md`.
2. **Diebold-Mariano Paragraph Placement**: Located at lines 324-326 (item 6) of `docs/Evaluation_Scenarios_Draft.md` under Section 3. It should be placed at the end of the results discussion section if merged with `docs/Part_4_Experiments.md`.
3. **SOTA Limitations & Gaps Link**: The 10 SOTA models collapse under tail risk and price-stabilization rules due to rigid uniform processing (violating Gap 1), global/linear/smoothed structures lacking shock absorption (violating Gap 2), horizon-insensitive pathways (violating Gap 3), and standard point-error evaluations that ignore directional accuracy under step-functions (violating Gap 4).

---

## 5. Verification Method

- **Inspection of Files**:
  - Open `docs/Evaluation_Scenarios_Draft.md` and check lines 330–347 to verify the Ablation Study table and footnote placement.
  - Open `docs/Evaluation_Scenarios_Draft.md` and check lines 324–326 to verify the DM test significance paragraph.
  - Open `docs/Part_2_RelatedWork.md` and check lines 9–20 to verify the SOTA limitations, and lines 29–36 to verify the 4 Research Gaps.
- **Code Execution Verification**: Since this is a read-only exploration task, no code execution or test suite execution is required.
