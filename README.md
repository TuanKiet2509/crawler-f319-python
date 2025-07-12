# F319 Crawler - Enhanced Multi-User Web Interface
## Tính năng nổi bật

### 🚀 Enhanced Full Content Control
- **Kiểm soát thông minh**: Chọn số lượng posts lấy full content thay vì tất cả
- **Tùy chọn linh hoạt**: 10, 20, 50, 100 posts hoặc tất cả
- **Tối ưu hiệu suất**: Tránh quá tải với dữ liệu lớn

### 👥 Multi-User Crawling
- Crawl nhiều users cùng lúc
- File kết quả riêng cho từng user + file combined
- Báo cáo chi tiết từng user

### ⚡ Search-Based Approach
- Nhanh chóng và hiệu quả
- Sử dụng search API của f319.com
- Tự động phân trang

## Cách sử dụng

### 1. Cài đặt
```bash
pip install -r requirements.txt
python app.py
```

### 2. Truy cập Web Interface
- Mở trình duyệt: `http://localhost:5000`
- Nhập username.userid (vd: `csdn.699927`)
- Chọn tùy chọn full content phù hợp

### 3. Tùy chọn Full Content

#### 🎯 Khuyến nghị sử dụng:
- **10 posts**: Để test và kiểm tra chất lượng
- **20-50 posts**: Phù hợp cho hầu hết trường hợp
- **100 posts**: Với users có nhiều posts chất lượng
- **Tất cả**: Chỉ với users có ít posts (<50)

#### ⚠️ Lưu ý:
- Full content mất thời gian hơn (3-5 giây/post)
- Với >100 posts, khuyến nghị giới hạn để tránh timeout
- Snippet content thường đã đủ chi tiết cho phân tích

### 4. Multi-User Mode
```
# Nhập nhiều users (cách nhau bằng dấu phẩy)
csdn.699927, lamnguyenphu.493993, user2.123456
```

## Cấu hình trong config.py

```python
# Full content settings
MAX_FULL_CONTENT_POSTS = 0  # 0 = tất cả, -1 = không lấy
FULL_CONTENT_DELAY = 3      # Delay giữa các requests (giây)
SKIP_LONG_POSTS = True      # Bỏ qua posts dài >5000 chars
LONG_POST_THRESHOLD = 5000  # Ngưỡng độ dài
```

## Tính năng mới

### ✨ Intelligent Content Control
- Tự động skip posts quá dài để tránh timeout
- Hiển thị progress real-time
- Báo cáo chi tiết về từng bước

### 🔧 Advanced Configuration
- Kiểm soát delay giữa requests
- Tùy chỉnh ngưỡng độ dài posts
- Tối ưu hiệu suất crawling

### 📊 Enhanced Reporting
- Thống kê chi tiết posts/user
- Hiển thị thời gian crawl
- Kích thước file output

## Troubleshooting

### Vấn đề thường gặp:
1. **Timeout**: Giảm số lượng full content posts
2. **Quá chậm**: Tăng `FULL_CONTENT_DELAY` hoặc chọn snippet mode
3. **Không tìm thấy posts**: Kiểm tra username.userid có chính xác

### Tips tối ưu:
- Với users >100 posts: Chọn 20-50 posts full content
- Với users <20 posts: Có thể chọn tất cả
- Test với 10 posts trước khi crawl số lượng lớn

## Kết quả

- **File CSV**: Dữ liệu posts với đầy đủ thông tin
- **Multi-user**: File riêng cho từng user + combined
- **Encoding**: UTF-8 với BOM (mở được bằng Excel)

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. File `enhanced_crawler.log` để xem chi tiết lỗi
2. Đảm bảo username.userid đúng format
3. Kết nối internet ổn định

---

**Phiên bản**: Enhanced Multi-User v2.0
**Tác giả**: F319 Crawler Team
**Cập nhật**: 2024 # crawer-f319
# crawler-f319-python
# crawler-f319-python
