import re

with open('docs_tinhchinh.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.strip()
    
    # 1. Remove reviewer comments
    if stripped.startswith('[BỔ SUNG]') or stripped.startswith('[SỬA]') or stripped.startswith('↳'):
        continue
        
    # 2. Fix Section 4.2 text
    if "GUM-Net được tối ưu bằng AdamW với Cosine Annealing, tốc độ học khởi tạo" in stripped:
        new_text = "Thực nghiệm được triển khai trên máy chủ CPU Intel Core i9-13900K, 128 GB RAM DDR5, hai GPU NVIDIA RTX 4090 (24 GB); phần mềm gồm Ubuntu 22.04, Python 3.10, PyTorch 2.1.0, CUDA 12.1. GUM-Net được tối ưu bằng AdamW với learning rate scheduler dạng ReduceLROnPlateau (patience = 5, factor = 0.5), tốc độ học khởi tạo 10⁻³, weight decay 10⁻⁴. Quá trình huấn luyện kéo dài tối đa 200 epoch, kết hợp cơ chế Early Stopping với patience linh hoạt theo chân trời dự báo (ví dụ 25 cho H1-H5, 15 cho H10, 20 cho H60) trên tập validation nhằm tránh overfitting."
        new_lines.append(new_text + "\n")
        continue

    # 3. Fix Section 4.3 Walk-Forward protocol
    if "Chúng tôi áp dụng kiểm chứng walk-forward dạng cửa sổ mở rộng: mô hình được khởi tạo" in stripped:
        new_text = "Nghiên cứu áp dụng kiểm chứng Walk-Forward dạng cửa sổ mở rộng (Expanding-Window Walk-Forward). Mô hình được khởi tạo trên 70% dữ liệu đầu, 15% tiếp theo làm validation và 15% làm test. Trong pha kiểm tra, mô hình được dự báo trên khối dữ liệu có kích thước bằng với chân trời dự báo H, sau đó cửa sổ huấn luyện được mở rộng thêm H bước và mô hình được tái huấn luyện hoàn toàn từ đầu (train from scratch) trước khi dự báo khối kế tiếp. Việc tái huấn luyện liên tục (kích thước khối = H) đảm bảo mô hình luôn cập nhật xu hướng giá mới nhất."
        new_lines.append(new_text + "\n")
        continue
        
    # Also fix the text in 88, 91, 94, 97 which had inline [BỔ SUNG]
    if "[BỔ SUNG]" in line:
        line = re.sub(r'\[BỔ SUNG\].*?(\n|$)', '\n', line)
    
    if "[SỬA]" in line:
        line = re.sub(r'\[SỬA\].*?(\n|$)', '\n', line)
        
    new_lines.append(line)

with open('doc_content.txt', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
