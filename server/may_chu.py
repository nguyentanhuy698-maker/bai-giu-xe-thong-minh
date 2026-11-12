"""
MÁY CHỦ THẬT cho bãi giữ xe máy thông minh (Đồ án 2 – HCMUTE).

Thay cho wokwi/server_mock.py khi đã có phần cứng: cùng topic MQTT, cùng định dạng lệnh, nên firmware ESP32
và trang quản lý không phải sửa gì. Khác bản giả lập ở chỗ biển số được đọc thật từ ESP32-CAM.

Một lượt xe:
  1. IR "xe tới" báo  {ROOT}/lane/in/arrive  -> máy chủ chụp sẵn 1 ảnh (đỡ trễ lúc quẹt thẻ)
  2. Quẹt thẻ          {ROOT}/lane/in/card    -> chụp thêm, nhận dạng biển số (bỏ phiếu nhiều ảnh)
  3. Làn vào: ghép cặp thẻ <-> biển số, lưu vào du_lieu/trong_bai.json
     Làn ra : so biển số đọc được với biển lúc vào; khác nhau -> từ chối, còi, cảnh báo đánh tráo
  4. Gửi lệnh         {ROOT}/lane/in/cmd     {"action":"open|deny","sound":..., "plate":..., "img":...}
Ảnh mỗi lượt lưu ở server/anh/<ngày>/; trang quản lý (mở qua http từ thư mục repo) hiện ảnh thật này.

Cài:  pip install -r server/requirements.txt
Chạy (Windows PowerShell, trong thư mục repo):
    $env:CAM_IN="http://192.168.1.21/capture"; $env:CAM_OUT="http://192.168.1.22/capture"; python server/may_chu.py
Chưa có camera, muốn thử trọn quy trình:  $env:GIA_LAP_CAMERA="1"; python server/may_chu.py

Biến môi trường (đều có mặc định):
    MQTT_BROKER=127.0.0.1  MQTT_PORT=1883  TOPIC_ROOT=hcmute-da2-baigiuxe
    CAM_IN=http://cam-vao.local/capture  CAM_OUT=http://cam-ra.local/capture
    OCR=easyocr | tesseract     SUC_CHUA=20     SAI_KHAC=1 (số ký tự được phép lệch khi so biển lúc ra)
    GIA_LAP_CAMERA=1 (biển số ngẫu nhiên, không cần camera)
Gõ khi đang chạy:  i = xe trong bãi | x <thẻ> = xoá 1 thẻ khỏi bãi | q = thoát
"""
import json
import os
import random
import sys
import threading
import time

import paho.mqtt.client as mqtt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

BROKER = os.environ.get("MQTT_BROKER", "127.0.0.1")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
ROOT = os.environ.get("TOPIC_ROOT", "hcmute-da2-baigiuxe")
CAMS = {"in": os.environ.get("CAM_IN", "http://cam-vao.local/capture"),
        "out": os.environ.get("CAM_OUT", "http://cam-ra.local/capture")}
OCR = os.environ.get("OCR", "easyocr")
CAPACITY = int(os.environ.get("SUC_CHUA", "20"))
MAX_DIFF = int(os.environ.get("SAI_KHAC", "1"))
FAKE_CAM = os.environ.get("GIA_LAP_CAMERA", "0") == "1"
FEE_BASE, FEE_STEP = 3000, 2000                  # 3.000 đ cho 4 giờ đầu, thêm 2.000 đ mỗi 2 giờ (giống trang quản lý)
PRECAPTURE_MAX_AGE = 4.0                         # ảnh chụp sẵn lúc xe tới chỉ dùng nếu chưa quá 4 s
DATA_DIR = os.path.join(HERE, "du_lieu")
IMG_DIR = os.path.join(HERE, "anh")
PARKED_FILE = os.path.join(DATA_DIR, "trong_bai.json")
MONTHLY_FILE = os.path.join(DATA_DIR, "the_thang.txt")   # mỗi dòng 1 UID thẻ tháng, ví dụ A3:4F:19:7C

if not FAKE_CAM:
    from nhan_dang import nhan_dang_camera, khac_nhau, chuan_hoa
else:
    from nhan_dang import khac_nhau, chuan_hoa

lock = threading.Lock()
pre = {"in": None, "out": None}                  # ảnh chụp sẵn: (thời điểm, jpeg)
busy = {"in": False, "out": False}


def log(lane, text):
    print(f"{time.strftime('%H:%M:%S')}  [{'VAO' if lane == 'in' else 'RA ' if lane == 'out' else '---'}] {text}", flush=True)


# ===================== DỮ LIỆU =====================
def load_parked():
    try:
        return json.load(open(PARKED_FILE, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_parked():
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = PARKED_FILE + ".tmp"
    json.dump(parked, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, PARKED_FILE)


def load_monthly():
    try:
        return {l.strip().upper() for l in open(MONTHLY_FILE, encoding="utf-8") if l.strip() and not l.startswith("#")}
    except OSError:
        return {"A3:4F:19:7C"}


parked = load_parked()                           # uid -> {"plate", "t_in", "img"}
monthly_cards = load_monthly()


def fee_for(uid, t_in):
    if uid in monthly_cards:
        return 0
    hours = (time.time() - t_in) / 3600
    return FEE_BASE if hours <= 4 else FEE_BASE + int(-(-(hours - 4) // 2)) * FEE_STEP


def save_image(lane, uid, jpeg):
    """Lưu ảnh, trả về đường dẫn tương đối từ thư mục repo (trang quản lý mở được qua http)."""
    if not jpeg:
        return ""
    day = time.strftime("%Y%m%d")
    d = os.path.join(IMG_DIR, day); os.makedirs(d, exist_ok=True)
    name = f"{time.strftime('%H%M%S')}_{lane}_{uid.replace(':', '')}.jpg"
    open(os.path.join(d, name), "wb").write(jpeg)
    return os.path.relpath(os.path.join(d, name), REPO).replace(os.sep, "/")


# ===================== NHẬN DẠNG =====================
LETTERS = "ABCDEFGHKLMNPSTUVXYZ"


def recognize(lane, uid):
    """-> dict(plate, conf, ms, jpeg). Ở chế độ giả lập camera: xe đã vào thì giữ đúng biển cũ khi ra."""
    if FAKE_CAM:
        time.sleep(random.uniform(0.3, 0.7))
        if lane == "out" and uid in parked:
            plate = parked[uid]["plate"]
        else:
            plate = f"{random.randint(50, 59)}-{random.choice(LETTERS)}{random.randint(1, 9)} {random.randint(100, 999)}.{random.randint(0, 99):02d}"
        return {"plate": plate, "conf": 0.95, "ms": 500, "jpeg": None, "reads": []}
    p, pre[lane] = pre[lane], None               # ảnh chụp sẵn chỉ dùng 1 lần, không để lượt sau dùng nhầm ảnh xe trước
    cached = p[1] if p and time.time() - p[0] < PRECAPTURE_MAX_AGE else None
    return nhan_dang_camera(CAMS[lane], OCR, anh_co_san=cached)


def precapture(lane):
    if FAKE_CAM:
        return
    from nhan_dang import chup_anh
    try:
        pre[lane] = (time.time(), chup_anh(CAMS[lane]))
        log(lane, "IR thấy xe tới: đã chụp sẵn ảnh")
    except Exception as e:
        log(lane, f"IR thấy xe tới nhưng chưa chụp được ảnh: {e}")


# ===================== QUYẾT ĐỊNH =====================
def decide_entry(uid, r, img):
    base = {"uid": uid, "monthly": uid in monthly_cards, "img": img, "conf": r["conf"], "ms": r["ms"]}
    with lock:
        if uid in parked:
            return "deny", "gap_bao_ve", "the dang co xe trong bai", {**base, "code": "dup", "plate": parked[uid]["plate"]}
        if len(parked) >= CAPACITY:
            return "deny", "bai_day", f"bai day {len(parked)}/{CAPACITY}", {**base, "code": "full"}
        if not r["plate"]:
            return "deny", "gap_bao_ve", "khong doc duoc bien so, cho bao ve nhap tay", {**base, "code": "ocr_fail"}
        for u, rec in parked.items():
            if khac_nhau(rec["plate"], r["plate"]) == 0:
                return "deny", "gap_bao_ve", f"bien {r['plate']} da co trong bai (the {u})", {**base, "code": "dup_plate", "plate": r["plate"]}
        t_in = time.time()
        parked[uid] = {"plate": r["plate"], "t_in": t_in, "img": img}
        save_parked()
        return "open", "moi_qua", f"ghep cap {uid} <-> {r['plate']} | trong bai {len(parked)}/{CAPACITY}", \
            {**base, "code": "in", "plate": r["plate"], "t_in": int(t_in * 1000)}


def decide_exit(uid, r, img):
    base = {"uid": uid, "monthly": uid in monthly_cards, "img": img, "conf": r["conf"], "ms": r["ms"]}
    with lock:
        rec = parked.get(uid)
        if rec is None:
            return "deny", "gap_bao_ve", "the khong co luot vao", {**base, "code": "no_entry", "plate": r["plate"] or ""}
        info = {**base, "plate_in": rec["plate"], "img_in": rec.get("img", ""), "t_in": int(rec["t_in"] * 1000)}
        if not r["plate"]:
            return "deny", "gap_bao_ve", "khong doc duoc bien so luc ra, cho bao ve doi chieu", {**info, "code": "ocr_fail"}
        d = khac_nhau(r["plate"], rec["plate"])
        if d > MAX_DIFF:
            return "deny", "khong_khop", f"the cua {rec['plate']} nhung xe la {r['plate']}", {**info, "code": "mismatch", "plate": r["plate"]}
        fee = fee_for(uid, rec["t_in"])
        del parked[uid]
        save_parked()
        what = "the thang" if fee == 0 else f"thu {fee:,}d".replace(",", ".")
        near = f" (doc {r['plate']}, lech {d} ky tu)" if d else ""
        return "open", "moi_qua", f"{rec['plate']} khop the{near}, {what} | trong bai {len(parked)}/{CAPACITY}", \
            {**info, "code": "out", "plate": rec["plate"], "fee": fee}


def send(client, lane, action, sound, msg="", info=None):
    payload = json.dumps({"action": action, "sound": sound, "msg": msg, **(info or {})}, ensure_ascii=False)
    client.publish(f"{ROOT}/lane/{lane}/cmd", payload.encode("utf-8"))
    log(lane, f"-> {action.upper()} ({sound}) {msg}")


def handle_card(client, lane, data):
    uid = str(data.get("uid", "?")).upper()
    if busy[lane]:
        log(lane, f"đang xử lý lượt trước, bỏ qua thẻ {uid}"); return
    busy[lane] = True
    t0 = time.time()
    try:
        log(lane, f"quẹt thẻ {uid}, đang nhận dạng…")
        try:
            r = recognize(lane, uid)
        except Exception as e:                    # lỗi bất ngờ: báo về để ESP32 không phải chờ hết 5 s
            log(lane, f"lỗi nhận dạng: {e}")
            r = {"plate": None, "conf": 0, "ms": int((time.time() - t0) * 1000), "jpeg": None, "reads": []}
        img = save_image(lane, uid, r.get("jpeg"))
        reads = ", ".join(x["plate"] or f"?({x['raw'][:20]})" for x in r.get("reads", []))
        log(lane, f"biển số: {r['plate'] or 'KHÔNG ĐỌC ĐƯỢC'}  tin cậy {r['conf']:.2f}  {r['ms']} ms  [{reads}]")
        action, sound, msg, info = decide_entry(uid, r, img) if lane == "in" else decide_exit(uid, r, img)
        send(client, lane, action, sound, f"{msg} | xu ly {int((time.time() - t0) * 1000)} ms", info)
    finally:
        busy[lane] = False


# ===================== MQTT =====================
def on_connect(client, userdata, flags_, reason_code, properties=None):
    log("", f"đã kết nối broker {BROKER}:{PORT}, theo dõi {ROOT}/#  |  camera: {'GIẢ LẬP' if FAKE_CAM else CAMS}  |  OCR: {OCR}")
    client.subscribe(f"{ROOT}/#")


def on_message(client, userdata, msg):
    parts = msg.topic.split("/")
    try:
        data = json.loads(msg.payload.decode())
    except ValueError:
        return
    if len(parts) == 4 and parts[1] == "lane" and parts[2] in ("in", "out"):
        lane, leaf = parts[2], parts[3]
        if leaf == "card":
            threading.Thread(target=handle_card, args=(client, lane, data), daemon=True).start()
        elif leaf == "arrive":
            if data.get("car"):
                threading.Thread(target=precapture, args=(lane,), daemon=True).start()
            elif not busy[lane]:
                pre[lane] = None                 # xe đã rời chỗ quẹt thẻ mà chưa quẹt: bỏ ảnh chụp sẵn
        elif leaf == "ir":
            log(lane, "IR: xe đã qua barie" if data.get("passed") else "IR: mở barie nhưng không có xe qua")
        elif leaf == "cmd" and data.get("manual"):
            log(lane, f"lệnh mở tay từ {data.get('by', 'trang quản lý')}")


def make_client():
    cid = f"may-chu-{random.randint(0, 99999)}"
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=cid)
    except AttributeError:
        return mqtt.Client(client_id=cid)


def warm_up():
    """Nạp mô hình OCR trước để lượt xe đầu tiên không bị chậm (EasyOCR nạp lần đầu mất vài giây)."""
    if FAKE_CAM:
        return
    import numpy as np
    from nhan_dang import doc_chu
    t = time.time()
    doc_chu(np.full((80, 110, 3), 255, np.uint8), OCR)
    log("", f"đã nạp bộ đọc chữ {OCR} ({time.time() - t:.1f} s)")


def main():
    log("", f"máy chủ bãi xe, sức chứa {CAPACITY}, đang có {len(parked)} xe trong bãi, {len(monthly_cards)} thẻ tháng")
    warm_up()
    client = make_client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(1, 10)
    client.connect(BROKER, PORT, keepalive=30)
    client.loop_start()
    print("Gõ: i = xe trong bãi | x <mã thẻ> = xoá thẻ khỏi bãi | q = thoát")
    try:
        while True:
            cmd = input().strip()
            if cmd == "i":
                for u, r in parked.items():
                    print(f"  {u:14} {r['plate']:14} vào {time.strftime('%d/%m %H:%M', time.localtime(r['t_in']))}")
                print(f"  {len(parked)}/{CAPACITY} xe")
            elif cmd.startswith("x "):
                with lock:
                    u = cmd[2:].strip().upper()
                    print("  đã xoá" if parked.pop(u, None) else "  không có thẻ này"); save_parked()
            elif cmd == "q":
                break
    except EOFError:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    except KeyboardInterrupt:
        pass
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
