"""
Nhận dạng biển số xe máy Việt Nam từ ảnh ESP32-CAM.

Các bước:
  1. Chụp ảnh JPEG từ ESP32-CAM (http://cam-vao.local/capture).
  2. Tìm vùng biển số: dùng YOLO nếu có file mô hình (models/bien_so.pt), không có thì tìm hình chữ nhật
     nền sáng có tỉ lệ của biển xe máy (≈ 1,1–1,8) bằng OpenCV.
  3. Phóng to, tăng tương phản, đọc chữ bằng EasyOCR (mặc định) hoặc Tesseract.
  4. Ghép 2 dòng, sửa ký tự dễ nhầm theo vị trí (O↔0, B↔8, S↔5…), kiểm tra đúng dạng biển xe máy:
        59-X1 123.45   59-X1 1234   59-AB 123.45 (xe 50 cc)

Dùng thử trên ảnh hoặc camera:
    python server/nhan_dang.py anh1.jpg anh2.jpg
    python server/nhan_dang.py http://192.168.1.21/capture
    python server/nhan_dang.py --ocr tesseract anh1.jpg
Mỗi ảnh in ra biển số đọc được, độ tin cậy, thời gian; ảnh vùng biển số lưu vào server/anh/kiem_tra/.
"""
import argparse
import os
import re
import time
import urllib.request
from collections import Counter

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# ===================== CHUẨN HOÁ BIỂN SỐ =====================
TO_DIGIT = {"O": "0", "D": "0", "Q": "0", "U": "0", "I": "1", "L": "1", "J": "1", "T": "1", "Z": "2",
            "S": "5", "B": "8", "G": "6", "A": "4", "E": "8"}
TO_LETTER = {"0": "D", "8": "B", "5": "S", "2": "Z", "6": "G", "4": "A", "1": "T", "7": "T"}
SERIES_LETTERS = set("ABCDEFGHKLMNPSTUVXYZ")      # chữ cái dùng trong sê-ri biển VN (không có I, J, O, Q, R, W)


def _fix(ch, want):
    if want == "d":
        return ch if ch.isdigit() else TO_DIGIT.get(ch)
    if want == "l":
        c = ch if ch.isalpha() else TO_LETTER.get(ch)
        return c if c in SERIES_LETTERS else None
    return ch if (ch.isdigit() or ch in SERIES_LETTERS) else TO_DIGIT.get(ch)   # "x": chữ hoặc số


def chuan_hoa(text):
    """Chuỗi OCR thô -> '59-X1 123.45' hoặc None nếu không ra dạng biển xe máy."""
    s = re.sub(r"[^A-Z0-9]", "", text.upper())
    best = None
    for tail in (5, 4):                        # thử biển 5 số trước, rồi 4 số
        n = 4 + tail
        for i in range(0, max(0, len(s) - n) + 1):
            chunk = s[i:i + n]
            if len(chunk) != n:
                continue
            pattern = "ddlx" + "d" * tail
            out = [_fix(c, w) for c, w in zip(chunk, pattern)]
            # ký tự thứ 2 của sê-ri chỉ là chữ ở biển xe 50 cc (AA, AB, AK…); còn lại là số: S -> 5, B -> 8…
            if out[2] and out[2] != "A" and out[3] and out[3].isalpha():
                out[3] = TO_DIGIT.get(out[3])
            if None in out:
                continue
            fixes = sum(a != b for a, b in zip(chunk, out))
            if best is None or fixes < best[0]:
                best = (fixes, "".join(out), tail)
        if best:
            break
    if not best:
        return None
    _, p, tail = best
    num = p[4:]
    return f"{p[:2]}-{p[2:4]} {num[:3]}.{num[3:]}" if tail == 5 else f"{p[:2]}-{p[2:4]} {num}"


def khoa_bien(plate):
    """Bỏ dấu, khoảng trắng để so 2 biển số."""
    return re.sub(r"[^A-Z0-9]", "", (plate or "").upper())


def khac_nhau(a, b):
    """Số ký tự khác nhau (khoảng cách Levenshtein) giữa 2 biển số."""
    a, b = khoa_bien(a), khoa_bien(b)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# ===================== CHỤP ẢNH =====================
_LAN = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # camera trong mạng LAN: không đi qua proxy hệ thống


def chup_anh(url, timeout=1.5):
    with _LAN.open(url, timeout=timeout) as r:
        data = r.read()
    if data[:2] != b"\xff\xd8":
        raise ValueError("camera không trả ảnh JPEG")
    return data


def giai_ma(jpeg):
    img = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("ảnh hỏng")
    return img


# ===================== TÌM VÙNG BIỂN SỐ =====================
_yolo = None


def _yolo_model():
    global _yolo
    if _yolo is None:
        path = os.environ.get("YOLO_BIEN_SO", os.path.join(HERE, "models", "bien_so.pt"))
        _yolo = False
        if os.path.exists(path):
            try:
                from ultralytics import YOLO
                _yolo = YOLO(path)
                print(f"Dùng YOLO tìm biển số: {path}")
            except ImportError:
                print("Có file YOLO nhưng chưa cài ultralytics (pip install ultralytics), dùng OpenCV")
    return _yolo


def _order(pts):
    s, d = pts.sum(1), np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]], np.float32)


def _warp(img, quad, h=220):
    q = _order(quad.reshape(4, 2).astype(np.float32))
    w_top, w_bot = np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3])
    h_l, h_r = np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])
    ratio = max(w_top, w_bot) / max(1, max(h_l, h_r))
    w = int(h * ratio)
    M = cv2.getPerspectiveTransform(q, np.float32([[0, 0], [w, 0], [w, h], [0, h]]))
    return cv2.warpPerspective(img, M, (w, h))


def tim_vung_bien(img, toi_da=3):
    """Trả về danh sách (ảnh vùng biển, điểm) – tốt nhất trước. Rỗng nếu không thấy."""
    H, W = img.shape[:2]
    model = _yolo_model()
    if model:
        out = []
        for b in model(img, verbose=False)[0].boxes:
            x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
            px, py = int((x2 - x1) * 0.06), int((y2 - y1) * 0.08)
            crop = img[max(0, y1 - py):min(H, y2 + py), max(0, x1 - px):min(W, x2 + px)]
            out.append((cv2.resize(crop, (int(220 * crop.shape[1] / max(1, crop.shape[0])), 220)), float(b.conf[0])))
        return sorted(out, key=lambda t: -t[1])[:toi_da]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    cands = []
    # biển VN nền trắng: tìm vùng sáng khép kín ở nhiều ngưỡng để chịu được ánh sáng khác nhau
    for th in (None, 150, 120, 180):
        if th is None:
            _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, bw = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)
        bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)))
        for c in cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]:
            area = cv2.contourArea(c)
            if area < 0.004 * W * H or area > 0.6 * W * H:
                continue
            rect = cv2.minAreaRect(c)
            (rw, rh) = rect[1]
            if min(rw, rh) < 18:
                continue
            ang = rect[2]
            if rw < rh:
                rw, rh, ang = rh, rw, ang - 90
            ratio = rw / rh
            if not (1.05 <= ratio <= 2.0) or abs(((ang + 45) % 90) - 45) > 25:
                continue
            fill = area / (rw * rh)
            if fill < 0.72:
                continue
            box = cv2.boxPoints(rect)
            warped = _warp(img, box)
            g = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
            dark = (g < 0.6 * np.median(g)).mean()           # phần mực chữ: biển thật có 8–40 %
            if not 0.06 < dark < 0.45:
                continue
            score = fill + 0.5 * (1 - abs(ratio - 1.36) / 0.7) + min(area / (0.05 * W * H), 1) * 0.3
            cands.append((warped, score, rect[0]))
    # bỏ trùng (cùng tâm)
    out = []
    for w_, s, c in sorted(cands, key=lambda t: -t[1]):
        if all(np.hypot(c[0] - o[2][0], c[1] - o[2][1]) > 20 for o in out):
            out.append((w_, s, c))
    return [(w_, s) for w_, s, _ in out[:toi_da]]


# ===================== ĐỌC CHỮ =====================
_reader = None


def _easyocr():
    global _reader
    if _reader is None:
        import easyocr      # lần đầu chạy tự tải mô hình (~100 MB) về thư mục người dùng
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader


def _lam_ro(crop):
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
    g = cv2.resize(g, (int(g.shape[1] * 220 / g.shape[0]), 220), interpolation=cv2.INTER_CUBIC)
    g = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(g)
    return g


def _bo_vien(g):
    """Nhị phân hoá, xoá khung viền biển và vết bẩn: còn lại chữ đen trên nền trắng."""
    inv = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    h, w = inv.shape
    # khung viền là các nét thẳng dài: tách ra bằng phép mở với nhân dài rồi trừ đi, để chữ dính khung không bị xoá theo
    lines = cv2.morphologyEx(inv, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (int(w * 0.45), 1)))
    lines |= cv2.morphologyEx(inv, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(h * 0.45))))
    inv = cv2.subtract(inv, cv2.dilate(lines, np.ones((3, 3), np.uint8)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 8)
    keep = np.zeros_like(inv)
    for i in range(1, n):
        x, y, ww, hh, area = st[i]
        cham_mep = x <= 2 or y <= 2 or x + ww >= w - 2 or y + hh >= h - 2
        la_khung = ww > 0.7 * w or hh > 0.75 * h
        if la_khung or (cham_mep and (ww > 0.5 * w or hh > 0.5 * h)) or area < 0.0008 * h * w or hh < 0.12 * h:
            continue
        keep[lab == i] = 255
    return 255 - keep


def _tach_dong(bw):
    """Biển xe máy 2 dòng: cắt ở hàng trắng gần giữa nhất."""
    ink = (bw < 128).sum(1)
    h = len(ink)
    mid = range(int(h * 0.3), int(h * 0.7))
    cut = min(mid, key=lambda r: (ink[r], abs(r - h / 2)))
    return [bw[:cut], bw[cut:]]


def doc_chu(crop, ocr="easyocr"):
    """Ảnh vùng biển -> (chuỗi thô 2 dòng ghép lại, độ tin cậy 0–1)."""
    bw = _bo_vien(_lam_ro(crop))
    lines = [cv2.copyMakeBorder(l, 16, 16, 24, 24, cv2.BORDER_CONSTANT, value=255) for l in _tach_dong(bw)]
    parts, confs = [], []
    if ocr == "easyocr":
        rd = _easyocr()
        for l in lines:
            res = sorted(rd.readtext(l, allowlist="0123456789ABCDEFGHKLMNPSTUVXYZ-.", paragraph=False), key=lambda r: r[0][0][0])
            parts.append("".join(r[1] for r in res)); confs += [float(r[2]) for r in res]
    else:
        import pytesseract
        cfg = "--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHKLMNPSTUVXYZ-."
        for l in lines:
            d = pytesseract.image_to_data(l, config=cfg, output_type=pytesseract.Output.DICT)
            words = [(t, float(c)) for t, c in zip(d["text"], d["conf"]) if t.strip() and float(c) >= 0]
            parts.append("".join(t for t, _ in words)); confs += [c / 100 for _, c in words]
    return " ".join(parts), float(np.mean(confs)) if confs else 0.0


# ===================== GHÉP LẠI =====================
def nhan_dang_anh(img, ocr="easyocr", luu_vung=None):
    """Ảnh BGR -> dict(plate, conf, raw). plate = None nếu không đọc được."""
    vung = tim_vung_bien(img)
    if not vung:                                  # không thấy khung biển: thử đọc cả ảnh (biển chiếm gần hết khung)
        vung = [(img, 0.1)]
    best = {"plate": None, "conf": 0.0, "raw": ""}
    for crop, score in vung:
        raw, conf = doc_chu(crop, ocr)
        plate = chuan_hoa(raw)
        if plate and (best["plate"] is None or conf > best["conf"]):
            best = {"plate": plate, "conf": round(conf, 3), "raw": raw}
            if luu_vung:
                cv2.imwrite(luu_vung, crop)
        elif not best["raw"]:
            best["raw"] = raw
    return best


def nhan_dang_camera(url, ocr="easyocr", so_lan=3, anh_co_san=None, han_ms=3000):
    """Chụp tối đa so_lan ảnh, dừng sớm khi 2 lần đọc giống nhau hoặc 1 lần đọc rất chắc.
    Trả về dict(plate, conf, ms, jpeg, reads)."""
    t0 = time.time()
    reads, jpeg_tot = [], None
    for k in range(so_lan):
        con_lai = han_ms / 1000 - (time.time() - t0)     # ESP32 chỉ chờ 5 s: giữ cả lượt trong khoảng 3 s
        if con_lai < 0.5:
            break
        try:
            jpeg = anh_co_san if (k == 0 and anh_co_san) else chup_anh(url, timeout=min(1.5, con_lai))
        except Exception as e:
            reads.append({"plate": None, "conf": 0, "raw": f"lỗi chụp: {e}"})
            continue
        r = nhan_dang_anh(giai_ma(jpeg), ocr)
        reads.append(r)
        if r["plate"] and (jpeg_tot is None or r["conf"] >= max((x["conf"] for x in reads if x["plate"]), default=0)):
            jpeg_tot = jpeg
        if jpeg_tot is None:
            jpeg_tot = jpeg
        ok = [x["plate"] for x in reads if x["plate"]]
        if r["plate"] and r["conf"] >= 0.85:
            break
        if ok and Counter(ok).most_common(1)[0][1] >= 2:
            break
    ok = [x for x in reads if x["plate"]]
    if not ok:
        return {"plate": None, "conf": 0.0, "ms": int((time.time() - t0) * 1000), "jpeg": jpeg_tot, "reads": reads}
    plate, n = Counter(x["plate"] for x in ok).most_common(1)[0]
    conf = max(x["conf"] for x in ok if x["plate"] == plate) * (0.7 + 0.3 * n / len(reads))
    return {"plate": plate, "conf": round(conf, 3), "ms": int((time.time() - t0) * 1000), "jpeg": jpeg_tot, "reads": reads}


def main():
    ap = argparse.ArgumentParser(description="Thử nhận dạng biển số trên ảnh hoặc camera")
    ap.add_argument("nguon", nargs="+", help="file ảnh hoặc URL /capture của ESP32-CAM")
    ap.add_argument("--ocr", default=os.environ.get("OCR", "easyocr"), choices=["easyocr", "tesseract"])
    a = ap.parse_args()
    out = os.path.join(HERE, "anh", "kiem_tra"); os.makedirs(out, exist_ok=True)
    for i, src in enumerate(a.nguon):
        t = time.time()
        if src.startswith("http"):
            r = nhan_dang_camera(src, a.ocr)
            if r["jpeg"]:
                open(os.path.join(out, f"camera_{i}.jpg"), "wb").write(r["jpeg"])
            print(f"{src}: {r['plate'] or 'KHÔNG ĐỌC ĐƯỢC'}  tin cậy {r['conf']:.2f}  {r['ms']} ms  ({len(r['reads'])} lần chụp: {[x['raw'] for x in r['reads']]})")
        else:
            img = cv2.imread(src)
            if img is None:
                print(f"{src}: không mở được"); continue
            r = nhan_dang_anh(img, a.ocr, luu_vung=os.path.join(out, f"vung_{os.path.basename(src)}"))
            print(f"{src}: {r['plate'] or 'KHÔNG ĐỌC ĐƯỢC'}  tin cậy {r['conf']:.2f}  {int((time.time() - t) * 1000)} ms  (thô: {r['raw']!r})")


if __name__ == "__main__":
    main()
