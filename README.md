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
- **Phối cảnh lắp ráp** (`lap-rap-3d.html`, mã nguồn ở `src3d/`): mô hình 1:10 dựng từ đúng linh kiện thật (kích thước mm thật), có góc nhìn xuyên vỏ cho chốt, tủ barie, cột camera, khoang điện dưới đế, đường dây và hình chiếu có kích thước.
- **Bản vẽ kỹ thuật** (`docs/ban-ve-ky-thuat.pdf`, 11 tờ A3, mã sinh bản vẽ ở `tools/ban-ve/`): lắp chung, mặt bằng toạ độ, đế và khoang điện, chốt, khai triển mica 1:1, tủ barie, cột camera, bo mạch, sơ đồ nối dây, kích thước chuẩn linh kiện, vật tư và quy trình lắp ráp.
- **Firmware phần cứng thật** (`firmware/`): bản chạy trên mạch thật (2 RC522, 2 servo, 4 IR, DFPlayer, còi), lệnh Serial để thử từng khối, file tạo âm thanh tiếng Việt và cấu hình Mosquitto. Xem `firmware/README.md`.

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

## Quên mật khẩu

- **Nhân viên quên mật khẩu:** bấm "Quên mật khẩu?" ở màn đăng nhập, chọn Nhân viên trực, nhập tên đăng nhập. Yêu cầu hiện ở mục Việc cần xử lý của quản lý và ở đầu trang Nhân viên → Hồ sơ. Quản lý bấm "Đặt mật khẩu tạm" rồi báo mật khẩu đó cho nhân viên. Lần đăng nhập tới, nhân viên phải đổi sang mật khẩu riêng (mật khẩu mới phải khác mật khẩu tạm). Tài khoản mới do quản lý tạo cũng phải đổi mật khẩu ở lần đăng nhập đầu.
- **Quản lý quên mật khẩu:** bấm "Quên mật khẩu?", chọn Quản lý, nhập tên đăng nhập, số CCCD và số điện thoại. Cả ba phải khớp hồ sơ thì mới đặt được mật khẩu mới. Trang chỉ báo "Thông tin không khớp", không nói sai ô nào. Sai 5 lần thì khóa chức năng này 15 phút cho tên đăng nhập đó. Quản lý còn lại thấy thông báo ở lần đăng nhập tới. Tài khoản nhân viên không dùng được cách này.
- Mọi lần gửi yêu cầu, đặt mật khẩu tạm, đổi mật khẩu và mọi lần xác minh sai đều ghi vào Nhật ký thao tác. Sau khi đổi mật khẩu, phiên đăng nhập cũ của tài khoản đó hết hiệu lực.
- Khóa localStorage mới: `bgx_pw_req` (yêu cầu của nhân viên), `bgx_pw_fail` (đếm lần sai), `bgx_pw_notice` (thông báo cho quản lý). Tài khoản có thêm trường `mustChange`.
- Hướng phát triển khi có máy chủ: gửi mã OTP về số điện thoại hoặc email trong hồ sơ, thay cho việc gõ lại số CCCD và SĐT.

## Tài chính: chi phí và lợi nhuận tháng (`#tai-chinh`, chỉ Quản lý)

- **Báo cáo lãi lỗ theo tháng:**
  - Doanh thu gồm phí gửi, thẻ tháng, phí mất thẻ và thu khác nhập tay.
  - Trừ lần lượt:
    - chi phí nhân sự (lấy từ Bảng lương, cộng bảo hiểm phần chủ trả theo % lương cơ bản của người có hợp đồng chính thức);
    - chi phí cố định (khoản lặp lại được tự tạo ngày 1);
    - chi phí biến đổi (điện theo chỉ số công tơ × đơn giá hoặc số trên hóa đơn, nước, vật tư, sửa chữa, phí QR theo % doanh thu QR);
    - khấu hao;
    - tiền két thiếu chưa thu hồi.
  - Ra lợi nhuận trước thuế, rồi trừ thuế (% doanh thu, mặc định 0) ra lợi nhuận ròng.
  - Mỗi dòng có số tháng này, số tháng trước và % tăng giảm. Lỗ tô đỏ, ghi "Lỗ". Tháng đang chạy có thêm phần "Dự kiến cuối tháng".
- **Chỉ số:**
  - Điểm hòa vốn (số lượt vãng lai/ngày cần có, đặt cạnh số thực tế), doanh thu mỗi chỗ đỗ, tỷ lệ lấp đầy, chi phí nhân sự trên doanh thu.
  - Biểu đồ 12 tháng: cột doanh thu và chi phí, đường lợi nhuận. Biểu đồ cơ cấu chi phí dạng thanh ngang.
  - Ô "Tính thử" không lưu gì và không đổi cài đặt.
- **Nhập liệu:**
  - Danh mục, khoản thu chi (kèm ảnh hóa đơn nén dưới 150 KB) và tài sản. Tài sản mẫu lấy từ mục Thiết bị, khấu hao mặc định 36 tháng.
  - Chi bằng tiền mặt két tạo giao dịch âm `expense`, làm giảm "tiền mặt phải có trong két" của ca đang mở.
  - Nhân viên có nút "Ghi khoản chi từ két" trong ca của mình; khoản này chờ quản lý duyệt. Nếu bị từ chối, khoản đó chuyển sang dòng tiền két thiếu.
- **Chốt tháng tài chính:**
  - Chỉ chốt được sau khi đã chốt lương tháng đó. Đã chốt thì khóa khoản thu chi của tháng và báo cáo giữ bản lưu lúc chốt.
  - Mở chốt phải có lý do. Đã chốt tài chính thì không mở chốt lương được.
  - Xuất Excel 2 sheet (Báo cáo, Chi tiết thu chi) và in A4.
- **Dữ liệu mẫu:**
  - Lịch ca và chấm công được kéo về tháng trọn vẹn đầu tiên trong 120 ngày dữ liệu. Bảng lương các tháng cũ được chốt.
  - Thẻ tháng mẫu có giao dịch gia hạn mỗi 30 ngày.
  - Có sẵn hóa đơn điện, nước, vật tư, một khoản sửa chữa và một khoản chi từ két chờ duyệt.
  - Doanh thu mẫu (khoảng 8–9 triệu/tháng) không đủ trả lương 8 người (khoảng 40 triệu), nên báo cáo hiện **lỗ**. Số liệu không bị chỉnh cho đẹp.
- **Khóa localStorage mới:** `bgx_fin_cats`, `bgx_fin_entries`, `bgx_fin_assets`, `bgx_fin_close`, `bgx_fin_auto`, `bgx_fin_seeded`, `bgx_hr_from`. Giao dịch có thêm loại `expense`.

## Đăng ký ca và xếp ca tự động (Nhân viên → Đăng ký ca, mục Của tôi)

- **Quy trình tuần:**
  - Đăng ký cho tuần sau tự mở vào thứ Hai. Hạn chót mặc định thứ Năm 20:00, sửa được ở Cài đặt → "Đăng ký ca và xếp ca tự động".
  - Nhân viên đăng ký ở mục Của tôi: bảng 7 ngày × 3 ca, mỗi ô chọn Muốn làm, Làm được hoặc Bận. Có nút "Giống tuần trước". Phải chọn đủ số ca tối thiểu mới gửi được (chính thức 5, thời vụ 4, bán thời gian 3). Quá hạn chót thì không sửa được nữa.
  - Quản lý thấy bảng tổng hợp đăng ký từng ca, ô không ai đăng ký tô đỏ, danh sách ai chưa gửi và nút Nhắc. Quản lý ghim được người vào ô; ghim phạm luật cứng thì phải ghi lý do.
  - Hết hạn thì hệ thống tự xếp, hoặc quản lý bấm "Xếp ca". Kết quả là bản nháp chỉ quản lý thấy. Quản lý chỉnh tay được; chỉnh phạm luật cứng thì có cảnh báo và phải ghi lý do. Công bố xong mới ghi vào Lịch phân ca, nên Của tôi và Chấm công dùng lịch mới.
  - Ca trống đưa lên "Ca cần người": nhân viên hợp lệ bấm "Nhận ca", ai trước được trước. Quản lý đặt được tiền thưởng cho ca đó; tiền thưởng ghi vào Thưởng – phạt của người nhận. Ca còn trống trong 24 giờ tới hiện ở Việc cần xử lý.
- **Luật cứng:**
  - Không xếp vào ô Bận, ngày nghỉ đã duyệt, người không ở trạng thái Đang làm.
  - Không 2 ca liền nhau, tính cả nối giữa hai tuần.
  - Không quá 6 ca/tuần, không quá 3 ca đêm liên tiếp.
  - Mỗi ca 1 người; không đủ người hợp lệ thì để trống.
- **Điểm khi nhiều người cùng muốn một ca:**
  - Muốn làm +10, Làm được +4.
  - +3 cho mỗi ca còn thiếu so với mục tiêu tuần (5/4/3), −5 cho mỗi ca đã vượt mục tiêu.
  - +2 cho mỗi lần bị từ chối "Muốn làm" trong 4 tuần (tối đa +8).
  - −2 cho mỗi ca khó đã làm trong 4 tuần; chỉ trừ khi người đó chọn "Làm được" cho một ca khó.
  - Hòa điểm thì người ít giờ làm hơn trong 4 tuần được ưu tiên, rồi đến người gửi đăng ký sớm hơn.
  - Mọi trọng số nằm trong Cài đặt.
- **Thuật toán:**
  - Đặt các ô ghim trước, sắp 21 ca theo số người hợp lệ tăng dần, rồi chọn người điểm cao nhất cho từng ca.
  - Sau đó thử 200 lần đổi người hoặc hoán đổi hai ô. Bộ sinh số ngẫu nhiên lấy hạt giống theo tuần, nên chạy lại cho cùng kết quả.
  - Chỉ giữ thay đổi khi hợp lệ và tốt hơn: ưu tiên lấp ô trống, rồi bớt người dưới mức tối thiểu, rồi tăng tổng điểm.
  - Mỗi ô lưu điểm và lý do bằng chữ, hiện khi rê chuột hoặc bấm "Lý do".
  - Báo cáo sau khi xếp gồm: số ca đã lấp/21, ca trống, người dưới mức tối thiểu, tỷ lệ ca "Muốn làm" được đáp ứng và số ca khó của từng người.
  - Sau khi công bố, nhân viên thấy những ca mình muốn mà không được xếp, kèm lý do.
- **Khóa localStorage mới:** `bgx_sched` (theo tuần: đăng ký, ghim, bản nháp, lịch công bố, lý do), `bgx_sched_seeded`, `bgx_open_bonus`. Cài đặt thêm các khóa `regDeadline*`, `schedMax*`, `tg*`, `min*`, `w*`, `schedIters`.

## Tổng quan theo vai trò

- **Quản lý:**
  - Hộp **"Cần tôi quyết"** gom mọi việc cần duyệt về một chỗ, duyệt hoặc từ chối ngay tại đó, không phải chuyển tab. Gồm: đơn nghỉ, đổi ca, tăng ca, khoản chi từ két, sửa biển số, quên mật khẩu, lệch tiền hoặc ca chưa kết, bản nháp lịch tuần.
  - "Việc cần xử lý" gộp việc vận hành và việc nhân sự thành một danh sách, không lặp với hộp trên.
  - **Thanh đỏ ca trực** hiện khi ca hiện tại không có ai nhận, hoặc người ca trước quá 15 phút chưa kết ca. Thanh có nút gọi số điện thoại của người theo lịch.
- **Nhân viên (màn hình chốt trực):**
  - Ô tra biển số lớn ở đầu trang: gõ vài số là thấy xe, bấm "Khách mất thẻ" ngay tại chỗ.
  - 4 nút lớn: Mở barie vào, Mở barie ra, Cảnh báo chờ (đỏ khi có cảnh báo), Chi từ két.
  - Nút "Kết ca, bàn giao" chỉ hiện ở đầu trang khi còn 30 phút là hết ca. Cần kết ca sớm thì có liên kết nhỏ phía dưới.
- **Điện thoại:** trang Xe trong bãi hiển thị mỗi xe một thẻ, nút "Khách báo mất thẻ" luôn nhìn thấy.

## Máy giữ xe (`#may-giu-xe`, nhân viên và quản lý)

- **Màn hình làm việc ở chốt,** bố cục theo phần mềm bãi xe thương mại, gồm 4 vùng:
  - thống kê (doanh thu, lượt vào/ra, xe trong bãi, người trực, đồng hồ);
  - camera biển số và camera người lái của từng làn;
  - ảnh chụp lúc quẹt thẻ (làn ra đặt ảnh lúc vào cạnh ảnh lúc ra);
  - thông tin lượt xe (mã thẻ, loại vé, biển số, giờ vào/ra, thời gian gửi, giá vé, kết quả).
- **Thao tác:** nút Mở barie, phím tắt F1/F2, nút Xử lý cảnh báo khi biển số không khớp. Có chế độ toàn màn hình cho máy tính đặt ở chốt.
- **Nguồn dữ liệu:**
  - Phần cứng thật qua MQTT: trang tự cài một trình khách MQTT nhỏ chạy trên WebSocket, không cần thư viện ngoài. Trang nghe đúng các topic mà `wokwi/sketch.ino` và `server_mock.py` đang dùng.
  - Hoặc trang mô phỏng.
  - Hoặc nút "Thử nhanh".
  - Lượt xe từ phần cứng được ghi như lượt của trang mô phỏng, nên mọi trang khác dùng chung dữ liệu.
- **Ảnh:** ảnh camera hiện là ảnh minh họa. Khi máy chủ gửi kèm đường dẫn ảnh từ ESP32-CAM thì thay vào các ô này.
- **Sửa kèm:**
  - `server_mock.py` dùng cùng topic với firmware (trước đây hai bên khác nhau) và gửi thêm thông tin lượt xe.
  - `sketch.ino` nhận lệnh mở tay từ trang quản lý.
