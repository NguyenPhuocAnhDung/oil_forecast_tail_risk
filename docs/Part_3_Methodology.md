# 3. PHƯƠNG PHÁP NGHIÊN CỨU VÀ KIẾN TRÚC HỆ THỐNG (METHODOLOGY)

## 3.1. Thiết lập Bài toán và Xử lý Tiền dữ liệu (Problem Setup & Data Preprocessing)
Bài toán đặt ra là dự báo giá bán lẻ xăng dầu trần của 4 mặt hàng chủ lực tại Việt Nam (Xăng RON95, Xăng RON92, Diesel DO 0.05%, Diesel DO 0.001%) dựa trên một tập hợp phong phú các biến ngoại sinh đa chiều. Dữ liệu đầu vào bao gồm:
- Các biến giá trị thị trường quốc tế: Giá giao ngay Platt’s Singapore (Platt's Singapore Spot Prices), Hợp đồng tương lai dầu WTI và Brent.
- Các biến vĩ mô và địa chính trị: Chỉ số sức mạnh đồng đô la Mỹ (US Dollar Index - DXY), Chỉ số Rủi ro Địa chính trị (Geopolitical Risk Index - GPR).
- Lịch sử giá bán lẻ nội địa của Việt Nam (Nguồn gốc trực tiếp từ các quyết định điều hành của Liên Bộ Tài chính - Công Thương).

Một điểm tối quan trọng trong việc thiết lập môi trường dữ liệu là ngăn chặn triệt để hiện tượng rò rỉ thông tin tương lai (Look-ahead bias). Do thị trường xăng dầu đóng cửa vào cuối tuần và các ngày lễ, dữ liệu thường bị khuyết (missing values). Thay vì sử dụng các phương pháp nội suy (interpolation) vốn sử dụng thông tin của các ngày tương lai để lấp đầy ngày quá khứ, chúng tôi áp dụng nguyên tắc Forward Fill tuyệt đối (ffill) (chỉ dùng giá của ngày gần nhất trước đó để điền vào ngày trống) nhằm bảo toàn tính nhân quả tuyệt đối của thời gian.

## 3.2. Chiến lược Mô hình Hóa Tách rời dựa trên Tính dừng (Stationarity-Aware Decoupled Modelling)
Tính chất thống kê của dữ liệu chuỗi thời gian đóng vai trò sống còn đối với khả năng học của các mạng nơ-ron. Để định lượng tính dừng của các mặt hàng đồng phân phối (co-products), chúng tôi thực hiện kiểm định thống kê Augmented Dickey-Fuller (ADF Test) trên toàn bộ dữ liệu lịch sử. Kết quả kiểm định ADF xác nhận một cách khách quan rằng: Nhóm mặt hàng Xăng (RON95, RON92) mang tính dừng (stationary) mạnh mẽ; trong khi nhóm mặt hàng Dầu Diesel (DO 0.05%, DO 0.001%) lại mang tính không dừng (non-stationary) và bị chi phối bởi xu hướng (trend-dominated).

Phát hiện thống kê này là nền tảng cho Chiến lược Mô hình Hóa Tách rời (Decoupled Modelling) của chúng tôi. Thay vì ép một mạng nơ-ron đa biến khổng lồ học chung một hàm ánh xạ cho toàn bộ 4 mặt hàng, chúng tôi cô lập chúng thành hai cụm độc lập: Cụm Xăng và Cụm Diesel. Sự phân tách này bảo vệ cấu trúc bên trong của mạng khỏi sự ô nhiễm chéo tín hiệu (signal cross-contamination) giữa các sản phẩm không đồng nhất.

[INJECT_IMAGE_SYSTEM]

## 3.3. Định dạng Mục tiêu: Lợi suất Tích lũy Trực tiếp (Direct Cumulative Log-Return Target)
Trong dự báo đa chân trời (multi-horizon forecasting), phương pháp tự hồi quy (recursive forecasting) thường dẫn đến sự tích lũy sai số theo cấp số nhân khi chân trời H càng lớn. Để giải quyết triệt để rủi ro này, chúng tôi áp dụng chiến lược dự báo trực tiếp (direct forecasting) vào biến mục tiêu là Lợi suất Tích lũy (Cumulative Log-Return) thay vì dự báo giá tuyệt đối.

Cho trước giá tại thời điểm hiện tại $P_t$ và giá tại thời điểm tương lai $P_{t+h}$, biến mục tiêu dự báo $R_{t \to t+h}$ được định nghĩa bằng phương trình toán học sau:
$$R_{t \to t+h} = \log(P_{t+h} / P_t)$$

Trong giai đoạn suy luận thực tế (inference phase), giá bán lẻ tuyệt đối được khôi phục ngược lại thông qua hàm mũ tự nhiên (exponential function):
$$\hat{P}_{t+h} = P_t \times \exp(\hat{R}_{t \to t+h})$$

## 3.4. Kiến trúc Mạng GUM-Net (Gated Unified Mixture Network)
Kiến trúc cốt lõi của hệ thống được xây dựng dựa trên nguyên lý Hỗn hợp Chuyên gia Dị thể (Heterogeneous Mixture-of-Experts). Đầu vào lịch sử đa biến $X$ được phân chia thành các tập con đặc trưng chuyên biệt trước khi truyền song song vào ba mạng chuyên gia thời gian.

[INJECT_IMAGE_NETWORK]

### 3.4.1. Chuyên gia Động lượng Ngắn hạn: CNN Đa tỷ lệ (Multi-Scale 1D-CNN)
Thị trường xăng dầu có những động lượng cục bộ ngắn hạn rất mạnh. Để nắm bắt được các chu kỳ vi mô này, chúng tôi thiết kế một chuyên gia sử dụng Mạng nơ-ron Tích chập 1 Chiều với các kích thước hạt nhân song song $k \in \{3, 7, 15\}$ tương ứng với padding $p = k // 2$:
$$out_k = \text{ReLU}(\text{Conv1D}_k(x^{\text{CNN}}))$$
$$out_{\text{concat}} = \text{Concat}(out_3, out_7, out_{15})$$
$$f_{\text{CNN}} = \text{TemporalAttention}(\text{LayerNorm}(\text{Proj}(out_{\text{concat}})))$$
Đầu ra đại diện cho các biến động tần số cao (3 ngày), tuần (7 ngày) và đa tuần (15 ngày).

### 3.4.2. Chuyên gia Xu hướng Vĩ mô: GRU-Attention
Để duy trì ký ức dài hạn về các chu kỳ vĩ mô kéo dài (như chu kỳ suy thoái kinh tế hay chu kỳ siêu tăng giá hàng hóa), chúng tôi sử dụng Đơn vị Hồi quy có Cổng (GRU - Gated Recurrent Unit) 2 lớp kết hợp với cơ chế Tự chú ý Đa đầu (Multi-Head Self-Attention) và chú ý thời gian:
$$h_t = \text{GRU}(x^{\text{GRU}}_t, h_{t-1})$$
$$A = \text{SelfAttention}(H, H, H) \quad \text{với } H = [h_1, h_2, \dots, h_L]$$
$$f_{\text{GRU}} = \text{TemporalAttention}(A)$$
Cơ chế này giúp mô hình tự động nhận diện và gán trọng số cao cho những ngày giao dịch quan trọng trong quá khứ.

### 3.4.3. Chuyên gia Chống sốc Phi tuyến: Wavelet-KAN
Đây là đóng góp kiến trúc đột phá nhất của nghiên cứu. Thay vì sử dụng MLP truyền thống, chúng tôi tích hợp Mạng Kolmogorov-Arnold (KAN) cải tiến sử dụng hàm sóng nhỏ Mexican Hat làm kích hoạt trên cạnh để học trực tiếp các quan hệ phi tuyến tính biên độ lớn:
$$x_i^{\text{norm}} = \frac{x_i - t_i}{s_i}$$
$$\psi(x_i^{\text{norm}}) = (1 - (x_i^{\text{norm}})^2) \cdot e^{-0.5 (x_i^{\text{norm}})^2}$$
$$\phi(x_i) = \text{SiLU}(W_{\text{base}} x_i) + W_{\text{wavelet}} \psi(x_i^{\text{norm}})$$
$$f_{\text{KAN}} = \text{TemporalAttention}(\Phi(X))$$
Trong đó, $t_i$ và $s_i$ là các tham số dịch chuyển và co giãn quy mô sóng nhỏ khả học để điều chỉnh dải thông tần số đáp ứng cục bộ.

## 3.5. Bộ Định tuyến Động dị thể (Heterogeneous Dynamic Router)
Mỗi chân trời dự báo (H=1 so với H=60) đòi hỏi sự kết hợp trọng số chuyên gia hoàn toàn khác nhau. Bộ định tuyến nhận đầu vào là $[f_{\text{CNN}} \parallel f_{\text{GRU}} \parallel f_{\text{KAN}} \parallel \text{Pos}_h \parallel x_{\text{ctx}}]$ với $x_{\text{ctx}}$ là đặc trưng bối cảnh toàn cục (Mean và Std) và $\text{Pos}_h$ là nhúng vị trí bước chân trời. Trọng số định tuyến động $w_h = [w_1, w_2, w_3]$ được tính bằng:
$$g_h = \text{MLP}([f_{\text{CNN}} \parallel f_{\text{GRU}} \parallel f_{\text{KAN}} \parallel \text{Pos}_h \parallel x_{\text{ctx}}])$$
$$w_h = \text{Softmax}(g_h)$$

Biểu diễn tích hợp cuối cùng $f_{\text{final}}$ được xác định bằng công thức gating tuyến tính mềm:
$$f_{\text{final}} = w_1 \cdot f_{\text{CNN}} + w_2 \cdot f_{\text{GRU}} + w_3 \cdot f_{\text{KAN}}$$

## 3.6. Giới hạn Sai số Ngoại suy bằng Residual Scaling (Error Bounding)
Ở các chân trời cực xa như H60, sự bất định là vô cùng lớn. Các mô hình mạng nơ-ron sâu thường bị hoang tưởng (hallucination), tạo ra các dự báo lệch pha hoàn toàn. Để khắc phục, GUM-Net áp dụng cơ chế Hãm phần dư (Residual Scaling). Đầu ra thô của mô hình sẽ được nhân với một hệ số hãm đi qua hàm Sigmoid $\sigma$, đảm bảo rằng sai số tuyệt đối luôn bị giới hạn trong một hành lang an toàn (bounded-risk corridor):
$$\hat{R} = \text{Raw\_Output} \times \sigma(r_h)$$
Trong đó $r_h$ là tham số hãm phần dư khả học cho từng bước chân trời dự báo.

## 3.7. Tối ưu hóa với Hàm mất mát Huber-Quantile & Load Balancing Loss
Mô hình được huấn luyện đồng thời trên 3 phân vị ($q \in \{0.1, 0.5, 0.9\}$) sử dụng hàm Huber-Quantile Loss để chống nhiễu béo đuôi (fat-tailed noise) kết hợp hình phạt cân bằng tải chuyên gia (load-balancing regularization) nhằm ép định tuyến phân bổ đồng đều, tránh sụp đổ cổng (gating collapse):
$$L_{\text{total}} = L_{\text{Huber-Quantiles}} + \alpha_{\text{lb}} \cdot L_{\text{lb}}$$

Hàm mất mát phân vị Huber được định nghĩa:
$$L_{\text{Huber-Quantiles}} = \frac{1}{M \cdot H} \sum_{t=1}^M \sum_{h \in \mathcal{H}} \sum_{q} \rho_q (y_{t+h} - \hat{y}_{t+h})$$
$$\rho_q(e) = \begin{cases} q \cdot \text{Huber}_{\delta}(e) & \text{nếu } e \ge 0 \\ (1-q) \cdot \text{Huber}_{\delta}(e) & \text{nếu } e < 0 \end{cases}$$
$$\text{Huber}_{\delta}(e) = \begin{cases} 0.5 \cdot e^2 & \text{nếu } |e| \le \delta \\ \delta \cdot |e| - 0.5 \cdot \delta^2 & \text{nếu } |e| > \delta \end{cases}$$
Với $\delta = 0.02$.

Hình phạt cân bằng tải để điều phối gating:
$$L_{\text{lb}} = \sum_{i=1}^3 \left( \bar{w}_i - \frac{1}{3} \right)^2$$
Với $\bar{w}_i$ là trọng số trung bình của chuyên gia $i$ trong batch, và hệ số cân bằng tải $\alpha_{\text{lb}} = 0.01$.
