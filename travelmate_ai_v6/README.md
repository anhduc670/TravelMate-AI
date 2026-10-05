# TravelMate AI v6 — Modern UI

Bản v6 giữ nguyên toàn bộ AI, database và chức năng của v5.2,
đồng thời thêm giao diện hiện đại bằng CustomTkinter.

## Giao diện mới
- Màn hình đăng nhập chia 2 cột
- Sidebar hiện đại
- Top bar + số thông báo
- Dark / Light mode
- Dashboard hero banner + statistic cards
- Chatbot dạng bong bóng giống ứng dụng chat
- Các nút gợi ý nhanh trong chatbot
- Tour card bo góc, ảnh lớn, rating và giá nổi bật
- Menu phân tách phần người dùng / AI / quản trị

## AI được giữ nguyên
- Naive Bayes đa thức
- Phân loại Intent
- Entity Extraction
- Context hội thoại nhiều lượt
- IF–THEN
- TF-IDF
- Cosine Similarity
- Weighted Scoring
- Explainable AI
- Top-1 / Top-3 Recommendation Evaluation

## Tài khoản mặc định

Khách hàng:
- Username: khachhang
- Password: 123456

Admin:
- Username: admin
- Password: admin123

## Cách chạy dễ nhất
Nhấp đúp:
install_and_run.bat

File này tự cài:
- customtkinter
- pillow

Sau đó tự chạy app.

Hoặc chạy thủ công:
python -m pip install -r requirements.txt
python app.py

## File dự phòng
app_legacy.py là toàn bộ giao diện v5.2 cũ.
Nếu cần đối chiếu code hoặc quay lại giao diện cũ, file vẫn còn trong project.
