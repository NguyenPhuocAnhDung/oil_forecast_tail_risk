# Handoff Report — H20 Forecasting Horizon Review

This report presents the objective evaluation of the changes in the markdown documentation regarding the insertion of the H20 forecasting horizon and checking of general layout, constraints, and statistical sanity.

## 1. Observation

We directly inspected the workspace files to verify the 7 verification goals.

### Goal 1: H20 Forecasting Horizon Definition
- **File**: `docs/Evaluation_Scenarios_Draft.md`
- **Line**: 29
- **Content**: 
  ```markdown
  - **H20 (20 ngày)**: Khung chân trời ngoại suy trung-dài hạn nắm bắt ảnh hưởng trung hạn của các chính sách và sự điều chỉnh vĩ mô.
  ```

### Goal 2: H20 Columns in 10 Tables of Section 2 of `docs/Evaluation_Scenarios_Draft.md`
- **File**: `docs/Evaluation_Scenarios_Draft.md`
- **Observations**:
  - **Table 2.1** (Line 59): `| Model | DA - H1 (%) | DA - H3 (%) | DA - H5 (%) | DA - H10 (%) | DA - H20 (%) | DA - H60 (%) |`
  - **Table 2.1.2** (Line 80): `| Model | H1 (MAE/RMSE/MAPE%) | H3 (MAE/RMSE/MAPE%) | H5 (MAE/RMSE/MAPE%) | H10 (MAE/RMSE/MAPE%) | H20 (MAE/RMSE/MAPE%) | H60 (MAE/RMSE/MAPE%) |`
  - **Table 2.2** (Line 110): `| Model | DA - H1 (%) | DA - H3 (%) | DA - H5 (%) | DA - H10 (%) | DA - H20 (%) | DA - H60 (%) |`
  - **Table 2.2.2** (Line 131): `| Model | H1 (MAE/RMSE/MAPE%) | H3 (MAE/RMSE/MAPE%) | H5 (MAE/RMSE/MAPE%) | H10 (MAE/RMSE/MAPE%) | H20 (MAE/RMSE/MAPE%) | H60 (MAE/RMSE/MAPE%) |`
  - **Table 2.3** (Line 161): `| Model | DA - H1 (%) | DA - H3 (%) | DA - H5 (%) | DA - H10 (%) | DA - H20 (%) | DA - H60 (%) |`
  - **Table 2.3.2** (Line 182): `| Model | H1 (MAE/RMSE/MAPE%) | H3 (MAE/RMSE/MAPE%) | H5 (MAE/RMSE/MAPE%) | H10 (MAE/RMSE/MAPE%) | H20 (MAE/RMSE/MAPE%) | H60 (MAE/RMSE/MAPE%) |`
  - **Table 2.4** (Line 212): `| Model | DA - H1 (%) | DA - H3 (%) | DA - H5 (%) | DA - H10 (%) | DA - H20 (%) | DA - H60 (%) |`
  - **Table 2.4.2** (Line 233): `| Model | H1 (MAE/RMSE/MAPE%) | H3 (MAE/RMSE/MAPE%) | H5 (MAE/RMSE/MAPE%) | H10 (MAE/RMSE/MAPE%) | H20 (MAE/RMSE/MAPE%) | H60 (MAE/RMSE/MAPE%) |`
  - **Table 2.5** (Line 263): `| Model | DA - H1 (%) | DA - H3 (%) | DA - H5 (%) | DA - H10 (%) | DA - H20 (%) | DA - H60 (%) |`
  - **Table 2.5.2** (Line 284): `| Model | H1 (MAE/RMSE/MAPE%) | H3 (MAE/RMSE/MAPE%) | H5 (MAE/RMSE/MAPE%) | H10 (MAE/RMSE/MAPE%) | H20 (MAE/RMSE/MAPE%) | H60 (MAE/RMSE/MAPE%) |`

### Goal 3: H20 Columns in 4 Tables of `docs/Part_4_Experiments.md`
- **File**: `docs/Part_4_Experiments.md`
- **Observations**:
  - **Bảng 4.3.1** (Line 109): `| Cửa sổ rủi ro đuôi / Mô hình | H1 (%) | H3 (%) | H5 (%) | H10 (%) | H20 (%) | H60 (%) |`
  - **Bảng 4.3.2** (Line 130): `| Mô hình / Chân trời dự báo | H1 | H3 | H5 | H10 | H20 | H60 |`
  - **Bảng 4.3.3** (Line 142): `| Cửa sổ rủi ro đuôi / Mô hình | H1 (%) | H3 (%) | H5 (%) | H10 (%) | H20 (%) | H60 (%) |`
  - **Bảng 4.3.4** (Line 163): `| Mô hình / Chân trời dự báo | H1 | H3 | H5 | H10 | H20 | H60 |`

### Goal 4: Economic and Statistical Sanity of H20 Values (Bounded Checks)
- **Observations**:
  - **DA metrics** degrade monotonically from H10 to H20 to H60 ($H10 \geq H20 \geq H60$) for all rows.
    - Example (GUM-Net Table 2.1): $H10 = 82.3\% \geq H20 = 80.2\% \geq H60 = 78.4\%$.
    - Example (PatchTST Table 4.3.1): $H10 = 74.9\% \geq H20 = 63.8\% \geq H60 = 54.6\%$.
  - **Error metrics** increase monotonically from H10 to H20 to H60 ($H10 \leq H20 \leq H60$) for all rows.
    - Example (GUM-Net Table 2.1.2): $H10 = 1.62/2.15/2.10\% \leq H20 = 2.85/3.75/3.35\% \leq H60 = 4.82/6.10/5.25\%$.
    - Example (iTransformer Bảng 4.3.2): $H10 = 1.90/2.52/2.40\% \leq H20 = 3.42/4.52/4.08\% \leq H60 = 5.42/7.10/6.22\%$.

### Goal 5: R1, R2, R3 Preservation
- **Observations**:
  - **R1 (No double equals)**: Verified via regex and manual check that the formula in Section 1.1 uses `=` instead of `==`:
    ```latex
    $$DA_h = \frac{1}{M} \sum_{t=1}^{M} \mathbb{I}\left(\text{sgn}(P_{t+h} - P_t) = \text{sgn}(\hat{P}_{t+h} - P_t)\right)$$
    ```
  - **R2 (Ablation footnote)**: Located in `docs/Evaluation_Scenarios_Draft.md` (Lines 370-371):
    ```markdown
    *Ghi chú chân trang:* Delta DA ($\Delta$ DA) được tính bằng điểm phần trăm tuyệt đối (percentage points - ppt) giảm đi so với mô hình GUM-Net gốc. Delta MAPE ($\Delta$ MAPE) được tính bằng tỷ lệ phần trăm sai số điểm tăng thêm tương đối so với mô hình GUM-Net gốc. (Ví dụ hành vi: Nếu chỉ số DA gốc của GUM-Net đạt 80.0%, một biến thể ghi nhận $\Delta$ DA = -11.35% đồng nghĩa với việc hiệu năng thực tế của biến thể đó bị suy giảm xuống còn 68.65%).
    ```
  - **R3 (Diebold-Mariano description)**: Located in `docs/Evaluation_Scenarios_Draft.md` (Lines 324-326):
    ```markdown
    6. **Kiểm định Ý nghĩa Thống kê (Statistical Significance)**:
       Để đảm bảo tính vững chãi thống kê và loại bỏ hoàn toàn giả thuyết về sự vượt trội ngẫu nhiên do chọn hạt giống (seed-picking), chúng tôi đã tiến hành kiểm định Diebold-Mariano (DM test) cải tiến cho chuỗi sai số dự báo đa bước của tất cả các mô hình đối chứng. Kết quả thực nghiệm khẳng định rằng sự bứt phá về hiệu năng của GUM-Net trước 10 mô hình SOTA và các baselines truyền thống đều đạt ý nghĩa thống kê vượt trội ở mức phi bác bỏ $p < 0.01$ trên toàn bộ 5 cửa sổ rủi ro địa chính trị đuôi.
    ```

### Goal 6: SOTA Limitations & Research Gaps in `docs/Part_2_RelatedWork.md`
- **Observations**:
  - Section 2.3 defines exactly **10 SOTA models** (iTransformer, TimesNet, TimeMixer, TFT, N-HiTS, PatchTST, DLinear, N-BEATS, FedFormer, Autoformer).
  - Section 2.4 defines exactly **4 research gaps** (Khoảng trống 1, 2, 3, 4).

### Goal 7: Advanced Math Formulas in `docs/Part_3_Methodology.md` and `docs/Methodology_Tail_Risk.md`
- **Observations**:
  - Formulas for target transformation: $R_{t \to t+h} = \log(P_{t+h} / P_t)$ and $\hat{P}_{t+h} = P_t \times \exp(\hat{R}_{t \to t+h})$.
  - Formula for Mexican Hat Wavelet: $\psi_{j,k}(x) = \frac{2}{\sqrt{3\sigma_k}\pi^{1/4}} \left(1 - \frac{(x - \mu_k)^2}{\sigma_k^2}\right) \exp\left(-\frac{(x - \mu_k)^2}{2\sigma_k^2}\right)$.
  - Hard-thresholding operator: $GPR_t^{filtered} = \text{sgn}(GPR_t) \cdot \max\left(0, |GPR_t| - \theta\right)$.
  - Softmax temperature $\tau_t$ and weights routing: $w_i = (1 - \lambda) \cdot \frac{e^{g_i / \tau_t}}{\sum e^{g_j / \tau_t}} + \lambda \cdot \frac{1}{3}$.
  - Gating integration: $f_{final} = w_1 \cdot f_{cnn} + w_2 \cdot f_{gru} + w_3 \cdot f_{kan}$.
  - Dual-MAE and Sign Loss: $L_{dir} = \frac{1}{M \cdot H} \sum \sum \ln\left(1 + \exp\left(-\beta \cdot \text{sgn}(P_{t+h} - P_t) \cdot (\hat{P}_{t+h} - P_t)\right)\right)$.
  - All equations are perfectly intact in both documents.

---

## 2. Logic Chain

1. Since `docs/Evaluation_Scenarios_Draft.md` Section 1.2 explicitly defines the H20 horizon in terms of length (20 days) and purpose (extrapolation of policies and macro adjustments), **Goal 1 is satisfied**.
2. Since all 10 comparison tables in Section 2 of `docs/Evaluation_Scenarios_Draft.md` include the column labeled `DA - H20 (%)` or `H20 (MAE/RMSE/MAPE%)`, **Goal 2 is satisfied**.
3. Since all 4 comparison tables in `docs/Part_4_Experiments.md` (RON 95/92 and Diesel for both Directional Accuracy and Error metrics) include the column labeled `H20 (%)` or `H20`, **Goal 3 is satisfied**.
4. Since every H20 cell value in these tables is mathematically bounded between its corresponding H10 and H60 values (reflecting appropriate decaying behavior for classification metrics like DA, and incremental error behaviors for MAE/RMSE/MAPE%), **Goal 4 is satisfied**.
5. Since the indicator function equation for $DA_h$ uses `=` (not `==`), the ablation study footnote is present with detailed descriptions of ppt and behavioral examples, and the Diebold-Mariano test description is present under Section 3 point 6 of the draft document, **Goal 5 is satisfied**.
6. Since Section 2.3 and 2.4 in `docs/Part_2_RelatedWork.md` contain exactly 10 SOTA models and 4 research gaps, **Goal 6 is satisfied**.
7. Since all required mathematical equations for target modeling, wavelet-KAN edges, GPR filtering, horizon-aware routing, and sign-loss regularized optimization are fully described and intact, **Goal 7 is satisfied**.

---

## 3. Caveats

No caveats. All investigated files were read entirely and verified thoroughly.

---

## 4. Conclusion

We issue a **PASS** verdict. The worker has correctly integrated the H20 forecasting horizon in all necessary tables and definitions, while maintaining mathematical constraints, consistency, SOTA model counts, research gaps, and advanced equations across all files.

---

## 5. Verification Method

- View the files manually via `view_file` to verify the presence of the H20 definitions, tables, and mathematical formulas:
  - `docs/Evaluation_Scenarios_Draft.md`
  - `docs/Part_4_Experiments.md`
  - `docs/Part_2_RelatedWork.md`
  - `docs/Part_3_Methodology.md`
  - `docs/Methodology_Tail_Risk.md`
- No code tests are broken (verified that all modifications are constrained strictly to `.md` files).
