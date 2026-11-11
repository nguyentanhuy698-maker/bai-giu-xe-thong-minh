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

## Cập nhật: thiết bị, nhận dạng, mở barie tay, xe cần chú ý, nhật ký

- Thiết bị: trạng thái máy chủ, broker, ESP32, đầu đọc, camera, barie, cảm biến; cảnh báo đầu trang khi mất kết nối; nhật ký sự cố.
- Lịch sử gửi xe: bấm vào lượt gửi để xem ảnh biển số và người lái lúc vào, lúc ra; sửa biển số khi camera đọc sai (giữ lại biển gốc).
- Nhận dạng: tỉ lệ đọc đúng, số lần phải nhập tay, độ trễ trung bình và p95, phân bố độ trễ, xuất Excel cho Chương 4.
- Mở barie bằng tay có chọn lý do và ghi tên người mở; trang mô phỏng nhận lệnh và mở barie.
- Danh sách xe cần chú ý (báo mất cắp, cấm gửi, nợ phí): xe trong danh sách ở trong bãi hoặc vừa vào là có cảnh báo.
- Nhật ký thao tác: đăng nhập, nhận ca, kết ca, đổi giá, sửa lịch ca, khóa thẻ, mở barie, sửa biển số.

## Bản 3 của trang quản lý (quan-ly.html)

Vẫn là một tệp HTML, JavaScript thuần, dữ liệu lưu trong trình duyệt (localStorage), mở trực tiếp hoặc qua GitHub Pages. Đăng nhập chỉ mang tính mô hình; hệ thống thật kiểm tra tài khoản ở máy chủ FastAPI và lưu trong SQLite.

**Tài khoản mẫu** (vai trò lấy theo tài khoản, không chọn ở màn đăng nhập)

| Tài khoản | Mật khẩu | Vai trò |
|---|---|---|
| nguyentanhuy, votruongthuyduong | admin123 | Quản lý |
| phanquochuy, nguyenthanhphat, lytuananh, dinhphamphuhung, nguyenhoangquan, nguyentanan | 123456 | Nhân viên trực |

**Quy ước chung**
- "Ngày" là ngày làm việc từ 6:00 đến 6:00 hôm sau. Ca sáng 6–14, ca chiều 14–22, ca đêm 22–6.
- Mọi khoản tiền (gửi xe, mất thẻ, thẻ tháng, nộp quản lý) nằm trong bảng giao dịch `bgx_transactions`; tiền theo ca, doanh thu ở Tổng quan và Thống kê đều tính từ bảng này.
- Phiên đăng nhập có token, hết hạn sau 12 giờ. Quyền được kiểm tra trong JavaScript trước mỗi thao tác.
- Mọi thao tác thay đổi dữ liệu ghi vào Nhật ký thao tác, kèm giá trị trước và sau; nhật ký không xóa được.

**Vận hành bãi xe**
- Nhận ca tính từ lúc nhận; khoảng chưa ai trực ghi riêng "Không có người trực". Kết ca: đếm tiền, nộp quản lý, đếm xe thực tế, bàn giao.
- Mất thẻ: tách phí gửi và phí mất thẻ, chọn tiền mặt hoặc QR, đóng lượt gửi, có thể cấp thẻ tháng mới giữ hạn cũ.
- Thẻ tháng gia hạn theo tháng lịch, tiền ghi vào ca đang mở. Thẻ hết hạn tính như vãng lai, thẻ báo mất bị từ chối.
- Phụ thu qua đêm chỉ tính khi xe còn trong bãi lúc 6:00 sáng. Biểu giá có ngày hiệu lực; lượt gửi dùng giá lúc xe vào.
- Mở barie tay làn ra phải chọn xe và thu phí; làn vào tạo lượt gửi "không thẻ". Cảnh báo không khớp có trạng thái Chờ xử lý / Cho qua / Giữ xe.
- Xe mất cắp hoặc cấm gửi trong bãi: gửi lệnh giữ barie làn ra cho trang mô phỏng. So số xe đếm bằng cảm biến IR với số lượt mở theo RFID.

**Nhân sự (mục Nhân viên, 10 tab)**
Tổng quan nhân sự, Hồ sơ (8 nhân sự theo bảng thông tin nhân sự), Lịch phân ca (tự phân ca, sao chép tuần trước, in), Chấm công tháng (chỉnh tay có lý do, in A4 ngang), Giao ca (tạo khoản trừ khi thiếu tiền), Nghỉ phép và đổi ca, Tăng ca (tự đề xuất khi kết ca trễ quá 15 phút hoặc làm ca ngoài lịch), Thưởng – phạt, Bảng lương (chốt và mở chốt, in phiếu A5), Hiệu suất. Nhân viên có mục "Của tôi" và chỉ xem được dữ liệu của mình.

Bảng lương chỉ để tham khảo, chưa tính bảo hiểm xã hội và thuế thu nhập cá nhân.

## Báo cáo kiểm thử

[docs/bao-cao-kiem-thu.pdf](docs/bao-cao-kiem-thu.pdf): 29 tình huống kiểm thử trang quản lý (đăng nhập, ca trực, vận hành bãi xe, nhân sự, đồng bộ và giao diện điện thoại), mỗi tình huống có các bước, kết quả mong đợi, kết quả thực tế và ảnh chụp màn hình. Kết quả: đạt 29/29, chạy trên bản commit 8d2f273. Cuối báo cáo có bảng các lỗi đã tìm ra và cách sửa.
