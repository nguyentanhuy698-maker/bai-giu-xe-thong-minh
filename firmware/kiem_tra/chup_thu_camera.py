"""Thử 2 ESP32-CAM từ laptop: chụp ảnh, đo thời gian, lưu file để xem biển số có rõ không.

    python firmware/kiem_tra/chup_thu_camera.py                       # dùng tên mDNS cam-vao.local, cam-ra.local
    python firmware/kiem_tra/chup_thu_camera.py 192.168.1.21 192.168.1.22   # hoặc ghi IP (Windows hay không phân giải được .local)

Đạt: mỗi ảnh về dưới 1 s, nặng 20–80 kB, nhìn rõ đủ ký tự biển số khi mở file.
"""
import sys, time, urllib.request, pathlib

hosts = sys.argv[1:] or ["cam-vao.local", "cam-ra.local"]
out = pathlib.Path("anh_thu"); out.mkdir(exist_ok=True)
for h in hosts:
    for i in range(3):
        t = time.time()
        try:
            data = urllib.request.urlopen(f"http://{h}/capture", timeout=5).read()
        except Exception as e:
            print(f"{h}: LỖI {e}  -> kiểm tra Wi-Fi, IP trong Serial Monitor của ESP32-CAM, nguồn 5 V"); break
        ms = (time.time() - t) * 1000
        f = out / f"{h.split('.')[0]}_{i + 1}.jpg"; f.write_bytes(data)
        ok = data[:2] == b"\xff\xd8" and 15_000 < len(data) < 120_000 and ms < 1000
        print(f"{h}: ảnh {i + 1} {len(data) / 1024:.0f} kB trong {ms:.0f} ms -> {'ĐẠT' if ok else 'XEM LẠI'}  ({f})")
print("Mở thư mục anh_thu để xem biển số có rõ không.")
