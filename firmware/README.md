# Firmware phần cứng thật – trụ điều khiển 2 làn

`tru_dieu_khien/tru_dieu_khien.ino` là bản chạy trên mạch thật của firmware trong `wokwi/sketch.ino`. Logic 2 làn, máy trạng thái, MQTT và quy tắc an toàn giữ nguyên; chỉ thay nút giả lập bằng linh kiện thật.

| Thư mục | Nội dung |
| --- | --- |
| `tru_dieu_khien/` | Firmware ESP32 DevKit V1 ở trụ giữa 2 làn |
| `camera_bien_so/` | Firmware 2 ESP32-CAM chụp biển số (`/capture`, xem trực tiếp `:81/stream`) |
| `kiem_tra/chup_thu_camera.py` | Thử chụp ảnh từ 2 camera trên laptop |
| `am_thanh/tao_am_thanh.py` | Tạo 5 file mp3 tiếng Việt cho DFPlayer |
| `mosquitto/mosquitto.conf` | Broker MQTT chạy trên laptop ở chốt bảo vệ (cổng 1883 cho ESP32, 9001 cho trang quản lý) |

## Nối chân

| Thiết bị | Chân thiết bị | Chân ESP32 | Nguồn | Ghi chú |
| --- | --- | --- | --- | --- |
| RC522 làn vào | SDA (SS) | GPIO5 | 3,3 V | Không cấp 5 V cho RC522 |
| RC522 làn ra | SDA (SS) | GPIO4 | 3,3 V | |
| RC522 cả 2 | SCK / MOSI / MISO / RST | GPIO18 / 23 / 19 / 27 | | Chung bus SPI, chung chân RST |
| Servo làn vào / ra | Tín hiệu | GPIO25 / 26 | 5 V riêng ≥ 3 A | Tụ 1000 µF sát nguồn servo |
| IR xe tới làn vào / ra | OUT | GPIO34 / 36 | 3,3 V | LOW = có xe |
| IR an toàn làn vào / ra | OUT | GPIO35 / 39 | 3,3 V | LOW = có vật dưới cần |
| DFPlayer Mini | TX → / RX ← | GPIO16 / GPIO17 (qua 1 kΩ) | 5 V | Loa 3 W ở SPK1, SPK2 |
| Module còi chủ động (3 chân) | I/O | GPIO14 | **3,3 V** | Module có sẵn transistor, kêu khi I/O = LOW (`BUZZER_ACTIVE_LOW 1`). Cấp 3,3 V chứ không cấp 5 V: ở 5 V, mức HIGH 3,3 V của ESP32 không tắt được còi |
| 2 LED WS2812 | DIN | GPIO13 | 5 V | Làn vào là LED thứ nhất |

**LED WS2812 cấp 5 V nhưng tín hiệu DIN của ESP32 chỉ 3,3 V** (WS2812 cần ≥ 0,7 × VDD = 3,5 V): đa số con vẫn chạy, nhưng nếu LED nháy sai màu hoặc không sáng thì cấp chân 5V của WS2812 qua 1 diode 1N4007 (còn ≈ 4,3 V), mức 3,3 V lúc đó đủ nhận. Có thể hàn sẵn diode từ đầu cho chắc.

**Tất cả GND nối chung.** GPIO34–39 chỉ đọc vào và không có điện trở kéo lên trong; module IR loại FC-51 đã có sẵn trên board nên nối thẳng được.

## Nạp firmware

1. Arduino IDE → Boards Manager → cài **esp32** (Espressif). Chọn board **ESP32 Dev Module**.
2. Library Manager → cài: **MFRC522** (GithubCommunity), **PubSubClient**, **ArduinoJson** 7.x, **ESP32Servo**, **Adafruit NeoPixel**, **DFRobotDFPlayerMini**.
3. Mở `tru_dieu_khien.ino`, sửa phần CẤU HÌNH: `WIFI_SSID`, `WIFI_PASS`, `MQTT_HOST` (IP laptop, xem bằng `ipconfig`).
4. Nạp, mở Serial Monitor **115200**, chọn kiểu xuống dòng **Newline**.

## Thử từng khối (chưa cần server)

Lúc khởi động, firmware tự kiểm tra và in ra:

```
RC522 LAN VAO: version 0x92 -> OK
RC522 LAN RA: version 0x92 -> OK
DFPlayer: OK
```

`0x00` hoặc `0xFF` nghĩa là RC522 chưa nối đúng (dây SPI, chân SS, nguồn 3,3 V). Sau đó gõ lệnh vào Serial Monitor:

| Lệnh | Thử khối nào |
| --- | --- |
| `i` | In trạng thái: RC522, IR xe tới, IR an toàn, góc servo, Wi-Fi, MQTT |
| `mv` / `mr` | Mở barie làn vào / ra (servo + IR an toàn: che IR rồi bỏ ra, cần phải hạ sau 0,8 s) |
| `s1` … `s5` | Phát thử 5 câu loa |
| `b` | Còi kêu 3 tiếng (nếu kêu liên tục từ lúc bật nguồn, đổi `BUZZER_ACTIVE_LOW` thành 0) |
| `v` / `r` | Giả quẹt thẻ ở làn vào / ra (không cần thẻ thật) |

Quẹt thẻ thật lên RC522: Serial in `Quet the 6D:41:3E:C8` và LED chuyển xanh dương.

Muốn chạy trọn quy trình mà chưa có laptop: đặt `#define OFFLINE_DEMO 1`, ESP32 tự quyết định (sức chứa thử 3 xe).

## Âm thanh

```
pip install gTTS
python am_thanh/tao_am_thanh.py
```

Chép thư mục `am_thanh/sd/mp3` vào thẻ microSD (FAT32) thành `/mp3/0001.mp3` … `/mp3/0005.mp3`.

| File | Mã server gửi | Câu đọc |
| --- | --- | --- |
| 0001 | `moi_qua` | Mời qua |
| 0002 | `bai_day` | Bãi đã đầy, vui lòng quay lại sau |
| 0003 | `gap_bao_ve` | Vui lòng gặp bảo vệ |
| 0004 | `khong_khop` | Thẻ và biển số không khớp, vui lòng gặp bảo vệ (kèm còi 3 tiếng) |
| 0005 | `loi_ket_noi` | Hệ thống đang bận, vui lòng gặp bảo vệ |

## Chạy cùng server và trang quản lý

1. Cài [Mosquitto](https://mosquitto.org/download/) trên laptop, chạy `mosquitto -c firmware/mosquitto/mosquitto.conf -v`. Cho phép cổng 1883 và 9001 qua Windows Firewall.
2. `MQTT_BROKER=127.0.0.1 python wokwi/server_mock.py` (Windows PowerShell: `$env:MQTT_BROKER="127.0.0.1"; python wokwi/server_mock.py`).
3. Mở trang quản lý **bằng http trên laptop**, không mở bản GitHub Pages (trang https không được nối broker ws://):
   `python -m http.server 8000` trong thư mục repo, rồi vào `http://localhost:8000/quan-ly.html`.
4. Máy giữ xe → Cài đặt kết nối → địa chỉ `ws://localhost:9001`, gốc topic `hcmute-da2-baigiuxe` → Kết nối phần cứng.
5. Quẹt thẻ: Serial, cửa sổ server và trang quản lý đều hiện lượt xe.

## Khác với bản Wokwi

| Wokwi | Bản thật |
| --- | --- |
| Nút GPIO32 / 33 giả quẹt thẻ, mỗi lần bấm 1 UID trong danh sách | RC522 đọc UID thật; thẻ để yên trên đầu đọc không bị tính 2 lần (3 s) |
| Câu loa in ra Serial | DFPlayer phát mp3 |
| Không có còi | Còi 3 tiếng khi thẻ và biển số không khớp |
| Không có IR xe tới | IR GPIO34 / 36 gửi `lane/{in\|out}/arrive` `{"car":true}` để server chụp sẵn ảnh; đặt `REQUIRE_CAR_FOR_CARD 1` để chỉ nhận thẻ khi có xe |
| Broker HiveMQ công cộng | Mosquitto trên laptop, có thể bật tài khoản (`MQTT_USER`, `MQTT_PASS`) |
| Nhịp tim: rssi, uptime, trạng thái làn | Thêm `rfid_in`, `rfid_out`, `audio` để biết linh kiện nào chưa chạy |

Cả hai bản đặt `mqtt.setBufferSize(512)`: lệnh của server kèm biển số, giờ vào và phí dài khoảng 240–280 byte, vượt bộ đệm 256 byte mặc định của PubSubClient, nên trước đây ESP32 bỏ lệnh và báo hết giờ chờ server.

## Lỗi thường gặp

| Hiện tượng | Nguyên nhân hay gặp |
| --- | --- |
| ESP32 khởi động lại liên tục khi servo chạy | Servo lấy nguồn từ chân 5 V của ESP32; phải dùng nguồn 5 V riêng và nối chung GND |
| RC522 báo `0x00` / `0xFF` | Sai chân SS, thiếu dây MISO, cấp 5 V làm hỏng module |
| Chỉ 1 trong 2 RC522 đọc được | Hai module cùng chân SS, hoặc dây SPI quá dài (giữ dưới 20 cm) |
| `DFPlayer: KHONG THAY` | Thẻ nhớ không phải FAT32, đảo dây TX/RX, thiếu điện trở 1 kΩ |
| `Ket noi MQTT ... loi -2` | Sai IP laptop, Mosquitto chưa chạy, tường lửa chặn cổng 1883 |
| Quẹt thẻ, chờ 5 s rồi "He thong dang ban" | `server_mock.py` chưa chạy hoặc khác `TOPIC_ROOT` |
| Nạp code báo `Failed to connect to ESP32` | Giữ nút BOOT trên ESP32 lúc IDE bắt đầu nạp |

## Camera biển số (2 ESP32-CAM)

1. Board **AI Thinker ESP32-CAM**. Nạp bằng đế **ESP32-CAM-MB** (cắm micro USB là nạp được).
2. Mở `camera_bien_so/camera_bien_so.ino`, sửa `WIFI_SSID`, `WIFI_PASS`. Con làn vào để `CAM_NAME = "cam-vao"`, nạp; đổi thành `"cam-ra"`, nạp con thứ hai.
3. Serial Monitor 115200 in ra IP. Mở `http://<IP>:81/stream` trên trình duyệt để căn góc camera theo thước 35,8° / 15° (rập tờ 7).
4. Trên laptop: `python firmware/kiem_tra/chup_thu_camera.py <IP cam vào> <IP cam ra>` rồi mở thư mục `anh_thu` xem biển số có rõ không.

Báo lỗi `Brownout detector was triggered` là nguồn 5 V yếu hoặc dây dài: cấp từ mạch hạ áp, dây ≥ 22 AWG, thêm tụ 470 µF ở chân 5V của camera.

## Quy trình test sau khi lắp ráp

Làm theo thứ tự, khối trước đạt mới sang khối sau. Mỗi bước ghi lại kết quả (ảnh chụp Serial Monitor, video) để đưa vào báo cáo.

| Bước | Làm gì | Đạt khi |
| --- | --- | --- |
| 1. Nguồn | Chưa cắm ESP32, DFPlayer, servo. Cấp 12 V, chỉnh XY-3606 | J1 = 5,0–5,3 V; đo 3,3 V sau khi cắm ESP32 |
| 2. ESP32 + RC522 | Cắm ESP32, nạp firmware với `OFFLINE_DEMO 1`, mở Serial | In `RC522 LAN VAO ... OK`, `RC522 LAN RA ... OK`; quẹt thẻ thật in ra UID ở đúng làn |
| 3. IR | Gõ `i`, lần lượt che 4 cảm biến bằng tay hoặc xe mô hình | Đúng cảm biến báo `CO XE` / `CO VAT`; chỉnh biến trở trên FC-51 cho khoảng 2–4 cm |
| 4. Servo | Gõ `mv`, `mr` | Cần nâng 90°, tự hạ sau 15 s; che IR an toàn lúc đang hạ thì cần nâng lại. Chỉnh `ANGLE_CLOSED/OPEN` nếu cần lệch |
| 5. Loa, còi, LED | `s1`…`s5`, `b`; quan sát LED | Nghe rõ 5 câu; còi 3 tiếng (kêu liên tục từ lúc bật nguồn thì đổi `BUZZER_ACTIVE_LOW`); LED xanh lam khi chờ |
| 6. Chạy OFFLINE | Quẹt thẻ ở cả 2 làn, cho xe mô hình đi qua | Vào 3 xe thì xe thứ 4 nghe "Bãi đã đầy"; ra khi bãi trống bị từ chối |
| 7. Camera | Theo mục Camera ở trên | 2 camera trả ảnh dưới 1 s, biển số rõ |
| 8. Toàn hệ thống | Đặt `OFFLINE_DEMO 0`, chạy Mosquitto + server + trang quản lý (mục ở trên) | Trang quản lý hiện trụ "trực tuyến"; quẹt thẻ thấy lượt xe hiện ngay; tắt Wi-Fi laptop thì barie giữ đóng và loa báo "Hệ thống đang bận" sau 5 s |
| 9. Đo đạc cho báo cáo | Quẹt thẻ 20 lần mỗi làn, ghi thời gian từ quẹt thẻ đến lúc cần bắt đầu nâng | Thời gian phản hồi trung bình, số lần đọc hỏng; đưa vào chương kết quả |
