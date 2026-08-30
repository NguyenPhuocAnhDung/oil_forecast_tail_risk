# Hướng Dẫn Thiết Lập Kiến Trúc Đám Mây Lai (Hybrid Cloud) Với 5 Dịch Vụ AWS

Tài liệu này hướng dẫn chi tiết quy trình chuẩn bị, cấu hình và vận hành hệ thống **GUM-Net Energy Risk Terminal** trên đám mây AWS sử dụng mô hình tối ưu 5 dịch vụ theo chuẩn doanh nghiệp (Production-Grade).

---

## 1. 🏛️ Thiết Kế Kiến Trúc Tổng Quan (System Architecture)

Hệ thống được vận hành theo mô hình lai (Hybrid Cloud):
* **Local Server (4 GPU)**: Đảm nhận huấn luyện sâu (retraining) ma trận 3,290 thực nghiệm walkforward. Kết quả đầu ra (Checkpoints `.pth` và file SQLite Database `forecast_storage.db`) được đẩy lên GitHub.
* **AWS Cloud (5 Services)**: Đồng bộ mã nguồn và dữ liệu từ GitHub, chạy Web Dashboard Streamlit 24/7 và thực hiện suy diễn (inference) cập nhật giá hằng ngày trên CPU.

```
                           [ Người dùng truy cập ]
                                      │
                                      ▼ (HTTPS - Cổng 443)
                         [ 5. Amazon Route 53 (DNS) ]
                                      │
                                      ▼
                       [ 4. AWS Certificate Manager ] (SSL Cert)
                                      │
                                      ▼
                        [ 1. AWS EC2 (t3.small) ] (Nginx & Docker)
                           │                  │
      (Đọc thông tin bảo mật) │                  │ (Gắn kết ổ mạng mạng)
                           ▼                  ▼
              [ 3. AWS SSM Parameter Store ]  [ 2. Amazon EFS ] (Lưu SQLite DB)
```

---

## 📋 2. Chi Tiết 5 Dịch Vụ AWS Cần Khởi Tạo

### 1. AWS EC2 (Elastic Compute Cloud)
* **Loại instance**: `t3.small` (2 vCPU, 2GB RAM) chạy hệ điều hành **Ubuntu Server 22.04 LTS**.
* **Vai trò**: Vận hành Docker container chạy Streamlit Dashboard và Nginx Reverse Proxy.
* **Security Group (Tường lửa)**:
  * **Inbound Rules**:
    * Cổng `22` (SSH): Chỉ cho phép IP của quản trị viên.
    * Cổng `80` (HTTP): Cho phép Any IPv4 (`0.0.0.0/0`).
    * Cổng `443` (HTTPS): Cho phép Any IPv4 (`0.0.0.0/0`).
  * **Outbound Rules**: Cho phép toàn bộ (`0.0.0.0/0`) để tải thư viện, cào tin tức và kết nối API.

### 2. Amazon EFS (Elastic File System)
* **Loại lưu trữ**: Elastic Network Storage (NFSv4).
* **Vai trò**: Lưu trữ tệp cơ sở dữ liệu SQLite `forecast_storage.db` độc lập khỏi bộ nhớ máy ảo.
* **Lợi ích**: Tách biệt hoàn toàn tầng dữ liệu và tầng tính toán. Nếu máy ảo EC2 bị lỗi hay cần nâng cấp, dữ liệu SQLite vẫn được bảo toàn an toàn trên EFS.

### 3. AWS Systems Manager (SSM) Parameter Store
* **Vai trò**: Quản lý và lưu trữ thông tin bảo mật. Thay thế hoàn toàn việc ghi mật khẩu ở file `.env` bằng việc mã hóa dưới dạng `SecureString`.
* **Danh sách biến cần tạo**:
  - `/oil-forecast/smtp-sender-email` (Loại: `String`)
  - `/oil-forecast/smtp-sender-password` (Loại: `SecureString`)
  - `/oil-forecast/smtp-receiver-email` (Loại: `String`)
  - `/oil-forecast/omniroute-api-key` (Loại: `SecureString`)

### 4. AWS Certificate Manager (ACM)
* **Vai trò**: Cấp phát chứng chỉ bảo mật SSL/TLS miễn phí của Amazon cho tên miền của bạn.
* **Lợi ích**: Tự động gia hạn 3 tháng/lần, đảm bảo website luôn chạy giao thức HTTPS an toàn.

### 5. Amazon Route 53
* **Vai trò**: Dịch vụ DNS quản trị tên miền toàn cầu.
* **Nhiệm vụ**: Phân giải tên miền (ví dụ: `oil-terminal.com`) thành địa chỉ IP tĩnh (Elastic IP) của máy ảo EC2.

---

## 🛠️ 3. Quy Trình Thiết Lập Từng Bước (Setup Instructions)

### Bước 3.1: Tạo Ổ Đĩa Mạng Amazon EFS và Gắn Lên EC2
1. Trên giao diện AWS Console, truy cập **EFS** -> Nhấp **Create file system**. Chọn VPC mặc định của bạn và đặt tên là `oil-forecast-efs`.
2. Tạo thư mục mount trên máy ảo EC2 và gắn kết ổ đĩa EFS thông qua cổng NFS:
   ```bash
   sudo apt-get update
   sudo apt-get install -y binutils cpp git make jq
   git clone https://github.com/aws/efs-utils
   cd efs-utils && ./build-deb.sh
   sudo apt-get install -y ./build/amazon-efs-utils*deb
   
   # Tạo thư mục lưu database
   sudo mkdir -p /mnt/forecast_storage
   # Tiến hành gắn kết EFS (Thay fs-xxxxxx bằng ID EFS thực tế của bạn)
   sudo mount -t efs -o tls fs-xxxxxx:/ /mnt/forecast_storage
   ```
3. Cấu hình tự động gắn kết EFS khi khởi động lại EC2 bằng cách thêm dòng sau vào `/etc/fstab`:
   ```text
   fs-xxxxxx:/ /mnt/forecast_storage efs defaults,_netdev,noresvport,tls 0 0
   ```

### Bước 3.2: Đẩy Thông Tin Bảo Mật Lên AWS SSM Parameter Store
Sử dụng AWS CLI trên máy cá nhân hoặc trên EC2 để đẩy các cấu hình bảo mật lên đám mây:
```bash
aws ssm put-parameter --name "/oil-forecast/smtp-sender-email" --value "sender@gmail.com" --type "String" --overwrite
aws ssm put-parameter --name "/oil-forecast/smtp-sender-password" --value "your_16_char_app_password" --type "SecureString" --overwrite
aws ssm put-parameter --name "/oil-forecast/smtp-receiver-email" --value "receiver@gmail.com" --type "String" --overwrite
aws ssm put-parameter --name "/oil-forecast/omniroute-api-key" --value "your_omniroute_key" --type "SecureString" --overwrite
```

### Bước 3.3: Gán Quyền IAM Instance Profile Cho EC2
Để EC2 có thể đọc được các biến bảo mật này mà không cần đăng nhập AWS CLI:
1. Tạo một **IAM Role** đặt tên là `EC2-Read-SSM-Parameters`.
2. Gán Policy sau cho Role:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "ssm:GetParameter",
                   "ssm:GetParameters"
               ],
               "Resource": "arn:aws:ssm:*:*:parameter/oil-forecast/*"
           }
       ]
   }
   ```
3. Chuột phải vào EC2 trên AWS Console -> **Security** -> **Modify IAM Role** -> Chọn `EC2-Read-SSM-Parameters` và lưu lại.

### Bước 3.4: Đồng Bộ Hóa Ứng Dụng Với Docker Compose
1. Di chuyển thư mục Database SQLite sang ổ đĩa EFS đã mount:
   ```bash
   # Tạo liên kết tượng trưng (symlink) để code python đọc/ghi bình thường
   ln -s /mnt/forecast_storage/forecast_storage.db /home/ubuntu/oil_forecast_tail_risk/data/processed/forecast_storage.db
   ```
2. Sửa đổi `docker-compose.yml` để Docker mount trực tiếp ổ đĩa EFS vào Container:
   ```yaml
   version: '3.8'
   services:
     streamlit-terminal:
       build: .
       container_name: gumnet_terminal
       ports:
         - "8501:8501"
       volumes:
         - /mnt/forecast_storage:/app/data/processed
       restart: always
   ```

### Bước 3.5: Viết Script Tự Động Đọc Biến Môi Trường AWS SSM
Trước khi khởi chạy script hằng ngày, Docker container sẽ gọi API AWS để lấy cấu hình bảo mật. Cập nhật đoạn code nạp cấu hình trong `daily_auto_forecast.py`:

```python
import boto3
from botocore.exceptions import NoCredentialsError

def load_aws_secrets():
    """Tự động lấy tham số bảo mật từ AWS SSM Parameter Store thông qua IAM Role"""
    ssm = boto3.client('ssm', region_name='ap-southeast-1') # Thay region của bạn
    try:
        sender = ssm.get_parameter(Name='/oil-forecast/smtp-sender-email')['Parameter']['Value']
        password = ssm.get_parameter(Name='/oil-forecast/smtp-sender-password', WithDecryption=True)['Parameter']['Value']
        receiver = ssm.get_parameter(Name='/oil-forecast/smtp-receiver-email')['Parameter']['Value']
        return sender, password, receiver
    except Exception as e:
        print("Không thể lấy cấu hình bảo mật từ AWS SSM, sử dụng fallback mặc định:", e)
        return None, None, None
```

---

## 🛡️ 4. Quy Trình Vận Hành & Bảo Trì (O&M)
* **Sao lưu dữ liệu (Backup)**: Bật tính năng **AWS Backup** tự động sao lưu ổ EFS mỗi tuần một lần, lưu trữ trong vòng 1 tháng. Chi phí sao lưu cực rẻ (chỉ ~$0.05/tháng).
* **Đồng bộ mã nguồn**: Khi bạn huấn luyện xong mô hình tối ưu trên Local Server, chỉ cần đẩy checkpoints mới lên Git. Tại AWS EC2, chạy lệnh cập nhật:
  ```bash
  git pull && docker compose restart
  ```
