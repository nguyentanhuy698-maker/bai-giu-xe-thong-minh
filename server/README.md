# Máy chủ nhận dạng biển số (chạy trên laptop ở chốt)

`may_chu.py` thay cho `wokwi/server_mock.py` khi đã có phần cứng. Topic MQTT và định dạng lệnh giữ nguyên, nên firmware ESP32 và trang quản lý không phải sửa. Khác bản giả lập ở chỗ biển số được đọc thật từ 2 ESP32-CAM.

| File | Nội dung |
| --- | --- |
| `may_chu.py` | Nhận thẻ qua MQTT, chụp ảnh, nhận dạng, quyết định mở/từ chối, lưu ảnh và danh sách xe trong bãi |
| `nhan_dang.py` | Tìm vùng biển số, đọc chữ, chuẩn hoá biển xe máy VN. Chạy riêng được để thử trên ảnh hoặc camera |
| `requirements.txt` | Thư viện Python cần cài |
| `du_lieu/trong_bai.json` | Xe đang trong bãi (tự tạo; tắt máy chủ mở lại vẫn nhớ) |
| `du_lieu/the_thang.txt` | Danh sách UID thẻ tháng, mỗi dòng một thẻ (tự tạo nếu cần) |
| `anh/<ngày>/` | Ảnh chụp mỗi lượt quẹt thẻ (trang quản lý hiện ảnh này) |

## Cài đặt (Windows)

```
pip install -r server/requirements.txt
```

Lần chạy đầu EasyOCR tự tải mô hình đọc chữ (khoảng 100 MB) nên cần mạng. Lần đầu nạp mất 5–10 giây, sau đó mỗi lượt nhận dạng khoảng 0,3–1 giây trên CPU laptop.

## Chạy

Trong thư mục repo, PowerShell:

```
mosquitto -c firmware/mosquitto/mosquitto.conf -v                  # cửa sổ 1
$env:CAM_IN="http://192.168.1.21/capture"; $env:CAM_OUT="http://192.168.1.22/capture"
python server/may_chu.py                                            # cửa sổ 2
python -m http.server 8000                                          # cửa sổ 3, rồi mở http://localhost:8000/quan-ly.html
```

IP của 2 camera xem trong Serial Monitor khi ESP32-CAM khởi động. Trong trang quản lý, mục **Máy giữ xe → Cài đặt kết nối**:

- Broker: `ws://127.0.0.1:9001`
- Xem trực tiếp camera: `http://192.168.1.21:81/stream`, `http://192.168.1.22:81/stream`

**Chưa có camera** mà muốn thử trọn quy trình thẻ – barie – trang quản lý:

```
$env:GIA_LAP_CAMERA="1"; python server/may_chu.py
```

| Biến môi trường | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `MQTT_BROKER`, `MQTT_PORT` | `127.0.0.1`, `1883` | Broker Mosquitto |
| `TOPIC_ROOT` | `hcmute-da2-baigiuxe` | Trùng `TOPIC_ROOT` trong firmware |
| `CAM_IN`, `CAM_OUT` | `http://cam-vao.local/capture`… | Địa chỉ chụp ảnh của 2 camera |
| `OCR` | `easyocr` | `tesseract` nếu đã cài Tesseract-OCR và `pytesseract` |
| `SUC_CHUA` | `20` | Số xe tối đa trong bãi |
| `SAI_KHAC` | `1` | Lúc ra, biển đọc được được phép lệch bao nhiêu ký tự so với lúc vào (0 = phải khớp hoàn toàn) |
| `GIA_LAP_CAMERA` | `0` | `1` = biển số ngẫu nhiên, không cần camera |

Gõ khi máy chủ đang chạy: `i` xem xe trong bãi, `x <mã thẻ>` xoá một thẻ khỏi bãi (khi bảo vệ đã xử lý tay), `q` thoát.

## Cách nhận dạng

1. IR "xe tới" báo lên thì máy chủ **chụp sẵn** 1 ảnh, để lúc quẹt thẻ đỡ chờ. Ảnh chụp sẵn chỉ dùng 1 lần và chỉ trong 4 giây.
2. Khi quẹt thẻ, máy chủ chụp thêm nếu cần, **tối đa 3 ảnh trong 3 giây**. Nó dừng sớm khi 2 ảnh đọc ra cùng biển số hoặc 1 ảnh đọc rất chắc. Kết quả là biển số được nhiều ảnh đọc ra nhất. Cả lượt luôn xong trước 5 giây ESP32 chờ.
3. **Tìm vùng biển số.** Máy chủ tìm hình chữ nhật nền sáng có tỉ lệ của biển xe máy (khoảng 1,1–1,8), có phần mực chữ hợp lý, rồi nắn thẳng phối cảnh. Nếu có mô hình YOLO tự huấn luyện ở `server/models/bien_so.pt` (cài thêm `ultralytics`) thì dùng YOLO thay cho bước này.
4. **Làm rõ ảnh.** Phóng ảnh lên cao 220 px, tăng tương phản, xoá khung viền biển, tách thành 2 dòng.
5. **Đọc chữ.** Dùng EasyOCR. Sau đó sửa những ký tự dễ nhầm theo vị trí: ở chỗ phải là số thì O→0, B→8, S→5; ở chỗ phải là chữ thì 8→B. Cuối cùng kiểm tra đúng dạng `59-X1 123.45`, `59-X1 1234` hoặc `59-AB 123.45`.

Kết quả thử trên 40 ảnh tổng hợp có cùng góc nhìn với mô hình (lệch 30–40°, chúc 10–18°, ảnh 800 × 600, có nhiễu và mờ), dùng bộ đọc Tesseract yếu hơn EasyOCR:

- Tìm đúng vùng biển: 40/40 ảnh.
- Đọc đúng cả biển với 1 lần chụp: 36/40 ảnh. Bỏ phiếu nhiều ảnh còn sửa thêm các lần đọc sai ngẫu nhiên.
- Mỗi ảnh xử lý khoảng 0,2 giây.

Ảnh thật sẽ khác ảnh tổng hợp. Khi có phần cứng, hãy đo lại theo bước 9 trong `firmware/README.md` và đưa số liệu đó vào báo cáo.

## Mẹo để đọc chuẩn trên mô hình

- **In biển số:** cỡ 22 × 16 mm, nền trắng, chữ đen đậm (Arial Black hoặc DIN), viền đen mảnh, 2 dòng `59-X1` / `123.45`. In laser trên giấy mờ (không bóng) để không bị loá.
- **Thử nhanh khi căn camera:** `python server/nhan_dang.py http://<IP camera>/capture` in ra biển đọc được, độ tin cậy và thời gian. Ảnh được lưu ở `server/anh/kiem_tra/`.
- **Đọc sai nhiều:** xem ảnh trong `server/anh/`. Ảnh tối thì chỉnh đèn LED chiếu biển; mờ thì vặn nhẹ ống kính OV2640 để lấy nét gần (khoảng 15 cm); biển quá nhỏ trong ảnh thì đưa camera lại gần hoặc đổi `FRAME` sang `FRAMESIZE_UXGA` trong firmware camera.
