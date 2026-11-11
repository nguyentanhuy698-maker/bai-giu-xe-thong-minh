# Bãi giữ xe máy thông minh – mô phỏng

Đồ án 2 · HCMUTE – Khoa Điện – Điện tử
Sinh viên: Nguyễn Tấn Huy (23161021) · Võ Trương Thùy Dương (23161013)
GVHD: ThS. Nguyễn Văn Phúc

Hệ thống bãi giữ xe máy xác thực kép **thẻ RFID + biển số**, một trụ điều khiển ESP32 cho hai làn vào/ra, nhận dạng biển số trên server.

## Trang web

- **Mô phỏng hoạt động** (`index.html`): bấm cho xe vào/ra, xem barie mở, màn hình chốt bảo vệ, tình huống thẻ bị đánh tráo, bãi đầy.
- **Trang quản lý** (`quan-ly.html`): tổng quan trong ngày, xe trong bãi và tra cứu khi mất thẻ, lịch sử gửi xe, thống kê theo ngày / tuần / tháng / quý, xuất Excel, quản lý thẻ tháng, cảnh báo, cài đặt giá vé. Số liệu hôm nay lấy từ trang mô phỏng nếu đã chạy mô phỏng trên cùng trình duyệt; các ngày trước là dữ liệu mẫu.
- **Phối cảnh 3D** (`phoi-canh-3d.html`): xoay mô hình, các góc nhìn và hình chiếu kỹ thuật.

- **Mô phỏng Wokwi** (`wokwi/`): firmware ESP32 cho trụ điều khiển 2 làn và server giả lập Python, chạy thử trên wokwi.com.

Hai trang web là HTML độc lập, mở trực tiếp bằng trình duyệt, không cần cài đặt.

> Đây là mô phỏng giao diện và luồng xử lý để minh họa, chưa kết nối phần cứng thật.

## Cập nhật: phương án chọn sau khi đối chiếu phần mềm bãi xe thương mại

- Mỗi làn chụp 2 ảnh: biển số và người lái (ESP32-CAM thứ hai).
- Thẻ và biển số không khớp: còi 5 V và đèn đỏ nháy cho tới khi nhân viên quyết định.
- Phí vãng lai theo lượt, giá ngày / đêm, phụ thu mỗi đêm gửi qua; vẫn chọn được tính theo giờ trong trang quản lý.
- Quy trình mất thẻ: tra theo biển số, đối chiếu ảnh lúc vào, khóa thẻ, thu phí, ghi nhật ký.
- Thống kê theo ca trực, vai trò quản lý / nhân viên (nhân viên không xem doanh thu tổng và cài đặt), lọc xe gửi quá 24 giờ.

## Cập nhật: đăng nhập, quản lý nhân viên, giao ca

- Vào trang quản lý phải đăng nhập, chọn vai trò Quản lý hoặc Nhân viên. Tài khoản mẫu: `quanly` / admin123, `nv01` đến `nv04` / 123456. Đây là bản mô hình chạy trên trình duyệt; hệ thống thật kiểm tra mật khẩu ở máy chủ.
- Quản lý: mục Nhân viên gồm danh sách tài khoản (thêm, sửa, đổi mật khẩu, khóa), lịch phân ca theo tuần, nhật ký giao ca và chấm công, hiệu suất từng người. Tổng quan có doanh thu hôm nay và doanh thu từng ca.
- Lịch sử gửi xe chọn được đúng một ngày.
- Nhân viên: nhận ca khi đăng nhập, chỉ thấy doanh thu ca đang làm, kết ca bằng cách đếm tiền mặt, hệ thống tính chênh lệch, chọn người nhận bàn giao và ghi chú.
