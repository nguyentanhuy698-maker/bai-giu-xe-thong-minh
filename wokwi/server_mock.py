"""
Server GIẢ LẬP cho trụ điều khiển 2 làn (Đồ án 2 – Bãi giữ xe máy thông minh).

Đóng vai server thật: nhận UID thẻ qua MQTT, "nhận dạng biển số" (giả lập bằng số ngẫu nhiên),
xác thực kép thẻ – biển số, rồi gửi lệnh mở / từ chối barie về ESP32.
Khi làm thật, chỗ giả lập nhận dạng sẽ được thay bằng: gọi ESP32-CAM lấy ảnh -> YOLOv8n -> OCR.

Cài đặt:  pip install paho-mqtt
Chạy:     python server_mock.py
Đổi broker hoặc topic không cần sửa code:  MQTT_BROKER=127.0.0.1 TOPIC_ROOT=ten-nhom python server_mock.py

Lệnh trả về ESP32 ở {ROOT}/lane/{in|out}/cmd. ESP32 chỉ đọc action, sound, msg; các trường còn lại
(uid, code, plate, plate_in, monthly, t_in, fee) để trang quản lý mục "Máy giữ xe" hiển thị.
Gõ khi đang chạy:
    s  + Enter  -> lượt RA kế tiếp giả lập xe bị đánh tráo thẻ (biển số không khớp)
    f  + Enter  -> lượt VÀO kế tiếp giả lập OCR không đọc được biển
    q  + Enter  -> thoát
"""
import json
import os
import random
import threading
import time

import paho.mqtt.client as mqtt

BROKER = os.environ.get("MQTT_BROKER", "broker.hivemq.com")    # phải trùng MQTT_HOST trong sketch.ino
PORT = int(os.environ.get("MQTT_PORT", "1883"))
ROOT = os.environ.get("TOPIC_ROOT", "hcmute-da2-baigiuxe")     # phải trùng TOPIC_ROOT trong sketch.ino và trang quản lý
CAPACITY = 3                          # sức chứa nhỏ để dễ thử tình huống bãi đầy
FEE_BASE, FEE_STEP = 3000, 2000       # 3.000đ cho 4 giờ đầu, thêm 2.000đ mỗi 2 giờ
MONTHLY_CARDS = {"A3:4F:19:7C"}       # thẻ tháng
RECOGNIZE_DELAY = (0.4, 0.9)          # giả lập thời gian chụp ảnh + nhận dạng (giây)

parked = {}                           # uid -> {"plate": str, "t_in": float}
flags = {"swap_next": False, "ocr_fail_next": False}
lock = threading.Lock()
LETTERS = "ABCDEFGHKLMNPSTUVXYZ"


def random_plate():
    return f"{random.randint(50, 59)}-{random.choice(LETTERS)}{random.randint(1, 9)} {random.randint(100, 999)}.{random.randint(0, 99):02d}"


def fee_for(uid, t_in):
    if uid in MONTHLY_CARDS:
        return 0
    hours = (time.time() - t_in) / 3600
    return FEE_BASE if hours <= 4 else FEE_BASE + int(-(-(hours - 4) // 2)) * FEE_STEP


def log(lane, text):
    print(f"{time.strftime('%H:%M:%S')}  [{'VAO' if lane == 'in' else 'RA '}] {text}", flush=True)


def send(client, lane, action, sound, msg="", info=None):
    payload = json.dumps({"action": action, "sound": sound, "msg": msg, **(info or {})})
    client.publish(f"{ROOT}/lane/{lane}/cmd", payload)
    log(lane, f"-> {action.upper()} ({sound}) {msg}")


def decide_entry(uid):
    """Trả về (action, sound, msg). Gọi sau khi đã 'chụp ảnh và nhận dạng'."""
    with lock:
        base = {"uid": uid, "monthly": uid in MONTHLY_CARDS}
        if uid in parked:
            return "deny", "gap_bao_ve", "the dang co xe trong bai", {**base, "code": "dup", "plate": parked[uid]["plate"]}
        if len(parked) >= CAPACITY:
            return "deny", "bai_day", f"bai day {len(parked)}/{CAPACITY}", {**base, "code": "full"}
        if flags["ocr_fail_next"]:
            flags["ocr_fail_next"] = False
            return "deny", "gap_bao_ve", "khong doc duoc bien so, cho bao ve nhap tay", {**base, "code": "ocr_fail"}
        plate = random_plate()
        parked[uid] = {"plate": plate, "t_in": time.time()}
        return "open", "moi_qua", f"ghep cap {uid} <-> {plate} | trong bai {len(parked)}/{CAPACITY}", {**base, "code": "in", "plate": plate, "t_in": int(time.time() * 1000)}


def decide_exit(uid):
    with lock:
        rec = parked.get(uid)
        base = {"uid": uid, "monthly": uid in MONTHLY_CARDS}
        if rec is None:
            return "deny", "gap_bao_ve", "the khong co luot vao", {**base, "code": "no_entry"}
        read_plate = rec["plate"]
        if flags["swap_next"]:
            flags["swap_next"] = False
            read_plate = random_plate()
        if read_plate != rec["plate"]:
            return "deny", "khong_khop", f"the cua {rec['plate']} nhung xe la {read_plate}", {**base, "code": "mismatch", "plate": read_plate, "plate_in": rec["plate"], "t_in": int(rec["t_in"] * 1000)}
        fee = fee_for(uid, rec["t_in"])
        del parked[uid]
        what = "the thang" if fee == 0 else f"thu {fee:,}d".replace(",", ".")
        return "open", "moi_qua", f"{read_plate} khop the, {what} | trong bai {len(parked)}/{CAPACITY}", {**base, "code": "out", "plate": read_plate, "plate_in": rec["plate"], "t_in": int(rec["t_in"] * 1000), "fee": fee}


def handle_card(client, lane, data):
    uid = data.get("uid", "?")
    t0 = time.time()
    log(lane, f"quet the {uid}")
    time.sleep(random.uniform(*RECOGNIZE_DELAY))      # giả lập chụp + nhận dạng
    action, sound, msg, info = decide_entry(uid) if lane == "in" else decide_exit(uid)
    send(client, lane, action, sound, f"{msg} | xu ly {int((time.time() - t0) * 1000)} ms", info)


def on_connect(client, userdata, flags_, reason_code, properties=None):
    print(f"Da ket noi broker {BROKER}, theo doi {ROOT}/#", flush=True)
    client.subscribe(f"{ROOT}/#")


def on_message(client, userdata, msg):
    parts = msg.topic.split("/")
    try:
        data = json.loads(msg.payload.decode())
    except ValueError:
        return
    if len(parts) == 4 and parts[1] == "lane":
        lane, leaf = parts[2], parts[3]
        if leaf == "card":
            threading.Thread(target=handle_card, args=(client, lane, data), daemon=True).start()
        elif leaf == "ir":
            log(lane, "IR: xe da qua" if data.get("passed") else "IR: mo barie nhung khong co xe qua")
    elif msg.topic.endswith("pillar/status"):
        pass  # nhịp tim của trụ, có thể in ra nếu cần


def make_client():
    try:  # paho-mqtt 2.x
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"server-mock-{random.randint(0, 99999)}")
    except AttributeError:  # paho-mqtt 1.x
        return mqtt.Client(client_id=f"server-mock-{random.randint(0, 99999)}")


def main():
    client = make_client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=30)
    client.loop_start()
    print("Go: s = lan ra ke tiep bi danh trao the | f = lan vao ke tiep OCR loi | q = thoat")
    try:
        while True:
            cmd = input().strip().lower()
            if cmd == "s":
                flags["swap_next"] = True; print("-> Luot RA ke tiep se khong khop bien so")
            elif cmd == "f":
                flags["ocr_fail_next"] = True; print("-> Luot VAO ke tiep se khong doc duoc bien")
            elif cmd == "q":
                break
    except (KeyboardInterrupt, EOFError):
        pass
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
