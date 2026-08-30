# Robust Forecasting under Tail Geopolitical Risk in the Retail Petroleum Market

Huong Bui^1, Phuoc Anh Dung Nguyen^1, Van Quy Hoang^{2*}
^1 Faculty of Information Technology, HUTECH University, Ho Chi Minh City, Vietnam
^2 Thuy Loi University (TLU), Hanoi, Vietnam

* Corresponding author.
E-mail addresses: bd.huong@hutech.edu.vn (H. Bui), anhdungnguyen955@gmail.com (P.A.D. Nguyen), hoangvanquy@tlu.edu.vn (V.Q. Hoang)

---

## ABSTRACT

**Background.** Giá bán lẻ xăng dầu là một biến số tài chính vĩ mô mang tính chiến lược, ảnh hưởng sâu sắc đến động lực lạm phát toàn cầu, chính sách tiền tệ quốc gia và an ninh năng lượng rộng lớn hơn. Tuy nhiên, dưới tác động của rủi ro địa chính trị đuôi (tail geopolitical risk), thị trường năng lượng thường xuyên phải đối mặt với các đứt gãy cấu trúc (structural breaks), độ biến động cực cao (high volatility) và phân phối đuôi béo (fat tails). Bất chấp tầm quan trọng vô song này, các mô hình học sâu thời gian tiên tiến (SOTA) hiện nay như iTransformer, TimesNet, TimeMixer, TFT, N-HiTS, PatchTST, DLinear, N-BEATS, FedFormer, và Autoformer thường gặp thất bại thảm hại trong các cửa sổ rủi ro đuôi (tail risk windows). Sự thất bại này là do các mô hình trên thiếu cơ chế thích ứng phi tuyến chuyên biệt để hấp thụ các cú sốc địa chính trị cực đoan và xử lý tính không đồng nhất thống kê giữa các sản phẩm xăng dầu (nhóm xăng có tính dừng và nhóm diesel không dừng).

**Objective.** Nghiên cứu này đề xuất GUM-Net (Gated Unified Mixture Network), một kiến trúc Mixture-of-Experts (MoE) chuyên biệt được thiết kế để dự báo vững chãi (robust forecasting) bốn sản phẩm nhiên liệu bán lẻ của Việt Nam (Xăng RON95, Xăng RON92, Diesel DO 0.05% và DO 0.001%) trên phổ dự báo đa chân trời đầy thách thức (H1, H3, H5, H10, H20, và H60).

**Method.** GUM-Net giới thiệu một cơ chế định tuyến động nhận thức chân trời (Horizon-Aware Dynamic Router) để kết hợp thông minh các biểu diễn từ ba chuyên gia thời gian chuyên biệt: một 1D-CNN đa tỷ lệ giãn (Multi-Scale Dilated 1D-CNN) bắt động lượng ngắn hạn; một GRU kết hợp Multi-Head Self-Attention bắt xu hướng dài hạn; và một mạng Wavelet-Kolmogorov-Arnold (Wavelet-KAN) đột phá thay thế B-splines bằng các kích hoạt wavelet Mexican Hat cục bộ để hấp thụ trực tiếp Chỉ số Rủi ro Địa chính trị (GPR). GUM-Net tối ưu hóa việc phân bổ trọng số thông qua công thức định tuyến động gating dạng LaTeX: \(f_{final} = w_1 \cdot f_{cnn} + w_2 \cdot f_{gru} + w_3 \cdot f_{kan}\) (hoặc biểu diễn plain-text: f_final = w₁·f_cnn + w₂·f_gru + w₃·f_kan). Nghiên cứu cũng chính thức hóa một Chiến lược Mô hình Hóa Tách rời (Decoupled Modelling) dựa trên kiểm định thống kê Augmented Dickey-Fuller (ADF) để xử lý riêng biệt xăng và diesel, và tối ưu hóa qua hàm mất mát Joint Quantile Pinball Loss để cung cấp dự báo phân vị hiệu quả.

**Results.** Được đánh giá trên tập dữ liệu thực tế khổng lồ gồm 4.517 ngày làm việc kéo dài đến tháng 5/2026 bằng giao thức Walk-Forward expanding-window phi rò rỉ dữ liệu, kết quả thực nghiệm chỉ ra sự ưu việt của GUM-Net. Trong các cửa sổ rủi ro đuôi cực đoan, trong khi các mô hình SOTA sụp đổ hiệu năng nghiêm trọng (ví dụ R² âm ở H60), GUM-Net duy trì độ ổn định vượt trội nhờ cơ chế Residual Scaling hoạt động như một bộ hãm sai số thuật toán, giới hạn chặt chẽ sai số MAPE dưới mức 7.5%. Hơn nữa, GUM-Net mang lại một lợi thế vượt trội về Độ chính xác định hướng (Directional Accuracy - DA), cải thiện đáng kể khả năng nhận biết xu hướng biến động giá phục vụ hoạch định chính sách và quản trị rủi ro tồn kho.

**Keywords:** Robust Forecasting; Tail Geopolitical Risk; Retail Petroleum Market; Mixture-of-Experts (MoE); Wavelet-KAN; Decoupled Modelling.

---

## 1. GIỚI THIỆU (INTRODUCTION)

Thị trường năng lượng toàn cầu đóng vai trò như hệ tuần hoàn của nền kinh tế hiện đại. Trong đó, giá bán lẻ nhiên liệu đại diện cho một biến số kinh tế vĩ mô mang tính chiến lược [1]. Mọi sự biến động của giá bán lẻ xăng dầu đều lan truyền trực tiếp và nhanh chóng vào cấu trúc chi phí của các ngành công nghiệp cốt lõi, ảnh hưởng sâu sắc đến chỉ số giá tiêu dùng (CPI) và lạm phát [2]. Tuy nhiên, trong kỷ nguyên bất ổn vĩ mô hiện nay, thị trường năng lượng ngày càng chịu chi phối mạnh mẽ bởi **Rủi ro địa chính trị đuôi (Tail Geopolitical Risk)**. Các sự kiện cực đoan như cuộc chiến Nga-Ukraine, khủng hoảng vận tải Biển Đỏ hay xung đột leo thang tại Trung Đông tạo ra các cú sốc cung-cầu phi tuyến tính khốc liệt. Các cú sốc này biểu hiện dưới dạng các đứt gãy cấu trúc (structural breaks), độ biến động cực đại (high volatility) và hiện tượng đuôi béo (fat tails) trong phân phối lợi suất giá [3]-[4] trước các biến động dị thường này [13].

Bất chấp tầm quan trọng vĩ mô này, các nghiên cứu dự báo chuỗi thời gian hiện tại chủ yếu tập trung vào thị trường dầu thô thượng nguồn (như dầu WTI hay Brent) [5], bỏ qua tính chất thống kê đặc thù và các quy định chính sách của thị trường bán lẻ hạ nguồn. Tại các nền kinh tế đang phát triển như Việt Nam, Nhà nước điều hành giá bán lẻ xăng dầu trần định kỳ thông qua các chu kỳ điều chỉnh (hiện tại là chu kỳ 7 ngày). Sự can thiệp chính sách này tạo ra các độ trễ truyền dẫn (policy lags) và biến chuỗi thời gian thành các hàm bậc thang (step-functions) rất khó dự báo. 

Khi các mô hình học sâu thời gian tiên tiến (SOTA) hiện nay — bao gồm cả các Transformer phân mảnh và mạng tuyến tính như **iTransformer, TimesNet, TimeMixer, TFT, N-HiTS, PatchTST, DLinear, N-BEATS, FedFormer, và Autoformer** — được áp dụng vào thị trường bán lẻ xăng dầu trong các cửa sổ rủi ro đuôi cực đoan, chúng thường gặp thất bại thảm hại. Sự suy sụp hiệu năng này bắt nguồn từ ba nguyên nhân cốt lõi:
1. **Thiếu cơ chế giảm chóc phi tuyến chuyên biệt**: Các mô hình SOTA sử dụng các hàm kích hoạt tĩnh (ReLU, GeLU) hoặc các phép biến đổi tuyến tính toàn cục, hoàn toàn bất lực trước các cú sốc xung kích đột ngột của chỉ số GPR.
2. **Ô nhiễm chéo tín hiệu học (Cross-contamination of learning signals)**: Việc ép chung các nhóm sản phẩm có đặc trưng thống kê đối lập — xăng mang tính dừng (stationary) mạnh mẽ và diesel mang tính không dừng có xu hướng (non-stationary, trend-dominated) — vào cùng một ma trận dự báo chung khiến các mô hình SOTA bị triệt tiêu động lượng cục bộ.
3. **Ảo giác ngoại suy dài hạn (Extrapolation Hallucination)**: Ở các chân trời xa như H60, các mô hình tự hồi quy hoặc Transformer thuần túy có xu hướng phóng đại sai số, dẫn đến sự chệch hướng hoàn toàn của dự báo so với thực tế vĩ mô.

Để giải quyết triệt để các hạn chế trên, chúng tôi giới thiệu hệ thống **GUM-Net (Gated Unified Mixture Network)**. Thiết kế của GUM-Net dựa trên triết lý Hỗn hợp Chuyên gia (Mixture-of-Experts - MoE) thích ứng theo chân trời dự báo. GUM-Net phân phối dữ liệu đầu vào song song cho ba chuyên gia thời gian độc lập: một chuyên gia CNN đa tỷ lệ giãn (Multi-Scale Dilated 1D-CNN) bắt động lượng ngắn hạn, một chuyên gia GRU kết hợp cơ chế Tự chú ý (Multi-Head Self-Attention) bắt xu hướng dài hạn, và một chuyên gia Wavelet-KAN đột phá. Bằng cách thay thế hàm B-splines tiêu chuẩn bằng các hàm sóng nhỏ Mexican Hat (Mexican Hat Wavelet) trực tiếp trên các cạnh của mạng Kolmogorov-Arnold, chuyên gia Wavelet-KAN đóng vai trò như một bộ giảm xóc thuật toán, hấp thụ trực tiếp Chỉ số Rủi ro Địa chính trị (GPR Index) để thích ứng với các đứt gãy cấu trúc địa chính trị cực đoan.

Trọng tâm điều tiết của GUM-Net là Bộ định tuyến động nhận thức chân trời (Horizon-Aware Dynamic Router). Bộ định tuyến này tự động ước lượng trọng số đóng góp mềm \(w_1, w_2, w_3\) thông qua công thức định tuyến cổng gating:
\(f_{final} = w_1 \cdot f_{cnn} + w_2 \cdot f_{gru} + w_3 \cdot f_{kan}\) (hoặc biểu diễn plain-text: f_final = w₁·f_cnn + w₂·f_gru + w₃·f_kan)

Trong đó, các trọng số định tuyến được tối ưu hóa năng động dựa trên nhúng vị trí chân trời dự báo \(H\). Ngoài ra, chúng tôi áp dụng Chiến lược Mô hình Hóa Tách rời (Decoupled Modelling) dựa trên kiểm định ADF và cơ chế Residual Scaling để kiểm soát sai số ngoại suy dài hạn.

Nghiên cứu của chúng tôi đóng góp bốn giá trị khoa học then chốt:
1. **Thiết lập Khung Dự báo vững chãi dưới rủi ro địa chính trị đuôi** đầu tiên cho thị trường xăng dầu bán lẻ hạ nguồn được điều tiết chính sách.
2. **Đề xuất Wavelet-KAN MoE** như một cơ chế hấp thụ sốc phi tuyến vượt trội, khắc phục triệt để sự suy sụp của 10 mô hình SOTA phổ biến (iTransformer, TimesNet, TimeMixer, TFT, N-HiTS, PatchTST, DLinear, N-BEATS, FedFormer, và Autoformer).
3. **Chứng minh tầm quan trọng của Độ chính xác định hướng (Directional Accuracy - DA)** như thước đo hiệu quả kinh tế hàng đầu trong việc hỗ trợ quyết định quản lý quỹ BOG và tồn kho doanh nghiệp đầu mối.
4. **Cung cấp một bộ benchmark hoàn chỉnh**, được kiểm chứng qua kiểm định thống kê Diebold-Mariano phi rò rỉ thông tin trên chuỗi dữ liệu kéo dài đến tháng 5/2026.

Cấu trúc của bài báo được tổ chức như sau: Phần 2 trình bày tổng quan các nghiên cứu liên quan và các khoảng trống học thuật. Phần 3 mô tả chi tiết phương pháp luận toán học của GUM-Net và các cửa sổ rủi ro đuôi. Phần 4 thảo luận về thiết lập thực nghiệm và phân tích kết quả. Phần 5 kết luận và đưa ra các hàm ý chính sách vĩ mô.
