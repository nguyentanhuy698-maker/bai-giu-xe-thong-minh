# Mô phỏng Wokwi – trụ điều khiển 2 làn

Firmware ESP32 cho trụ điều khiển giữa 2 làn (vào / ra), chạy thử trên [Wokwi](https://wokwi.com) trước khi làm phần cứng thật.

| File | Nội dung |
| --- | --- |
| `sketch.ino` | Firmware: đọc thẻ, gửi UID lên server qua MQTT, chờ lệnh, điều khiển barie, cảm biến IR an toàn. 2 làn chạy song song, không dùng `delay()`. |
| `diagram.json` | Sơ đồ mạch Wokwi: ESP32, 2 servo, 2 nút quẹt thẻ, 2 nút IR, 2 LED trạng thái |
| `libraries.txt` | Thư viện cần cho Wokwi |
| `server_mock.py` | Server giả lập trên laptop: nhận thẻ, "nhận dạng" biển số, xác thực kép, trả lệnh mở / từ chối |

## Chạy trên Wokwi

1. Vào wokwi.com → **New Project** → **ESP32**.
2. Dán nội dung `sketch.ino` vào tab `sketch.ino`, dán `diagram.json` vào tab `diagram.json`.
3. Bấm dấu **+** cạnh các tab → **New file…** → đặt tên `libraries.txt`, dán nội dung file `libraries.txt`.
4. Mở `sketch.ino`, đổi `TOPIC_ROOT` thành một chuỗi riêng của nhóm (để không trùng người khác dùng chung broker công cộng). Đổi y hệt trong `server_mock.py`.
5. Trên laptop: `pip install paho-mqtt` rồi `python server_mock.py`.
6. Bấm ▶ trên Wokwi, chờ Serial Monitor báo `Ket noi MQTT ... OK`.

Muốn thử nhanh **không cần server**: đặt `#define OFFLINE_DEMO 1` (ESP32 tự quyết định, sức chứa demo 3 xe).

## Cách thao tác

| Linh kiện | Ý nghĩa |
| --- | --- |
| Nút xanh bên phải / trái | Quẹt thẻ ở làn vào / làn ra (mỗi lần bấm là một thẻ, theo thứ tự) |
| Nút vàng | Cảm biến IR dưới cần barie. **Giữ** nút = có xe đang đi qua, **thả** = xe qua hẳn |
| Servo | Cần barie |
| LED | Xanh dương: đang chờ server · xanh lá: mời qua · đỏ: từ chối |
| Serial Monitor | Nhật ký và câu loa sẽ đọc (phần cứng thật dùng DFPlayer) |

Trong cửa sổ `server_mock.py`, gõ `s` + Enter để lượt ra kế tiếp bị **đánh tráo thẻ**, `f` + Enter để lượt vào kế tiếp **không đọc được biển số**.

## Tình huống nên thử

1. Xe vào → giữ rồi thả nút IR → barie hạ.
2. Vào 3 xe → xe thứ 4 bị từ chối vì **bãi đầy**.
3. Xe ra bình thường → server tính phí; gõ `s` rồi cho xe ra → **không khớp**, barie không mở.
4. **An toàn**: khi cần barie đang hạ, bấm nút IR → cần nâng lên lại.
5. **Mất server**: tắt `server_mock.py` rồi quẹt thẻ → sau 5 s barie vẫn đóng (an toàn khi mất mạng).
6. Mở barie mà không bấm IR → sau 15 s tự hạ.
7. Quẹt thẻ ở 2 làn gần như cùng lúc → mỗi làn xử lý độc lập.

## Khác biệt so với phần cứng thật

| Mô phỏng | Phần cứng thật |
| --- | --- |
| Nút xanh GPIO32 / 33 | RC522 ×2 chung SPI: SCK 18, MISO 19, MOSI 23, SS 5 / 4, RST 27 |
| In câu loa ra Serial | DFPlayer Mini UART2 (GPIO16 / 17) + loa 3 W |
| Broker công cộng `broker.hivemq.com` | Mosquitto chạy trên laptop, IP tĩnh |
| Server giả lập | Server thật gọi ESP32-CAM lấy ảnh → YOLOv8n → OCR |
