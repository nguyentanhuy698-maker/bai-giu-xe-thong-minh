"""
Tạo 5 file âm thanh tiếng Việt cho DFPlayer Mini.

Chạy trên laptop (cần Internet vì dùng giọng đọc của Google):
    pip install gTTS
    python tao_am_thanh.py
Kết quả nằm trong thư mục sd/mp3/. Chép nguyên thư mục mp3 vào thư mục gốc của thẻ microSD
(định dạng FAT32), để có đường dẫn /mp3/0001.mp3 ... /mp3/0005.mp3.

Số thứ tự phải khớp bảng SOUNDS trong tru_dieu_khien.ino.
"""
import os
from gtts import gTTS

CAU_LOA = [
    (1, "moi_qua", "Mời qua"),
    (2, "bai_day", "Bãi đã đầy, vui lòng quay lại sau"),
    (3, "gap_bao_ve", "Vui lòng gặp bảo vệ"),
    (4, "khong_khop", "Thẻ và biển số không khớp, vui lòng gặp bảo vệ"),
    (5, "loi_ket_noi", "Hệ thống đang bận, vui lòng gặp bảo vệ"),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sd", "mp3")
os.makedirs(out, exist_ok=True)
for so, ten, cau in CAU_LOA:
    duong_dan = os.path.join(out, f"{so:04d}.mp3")
    gTTS(cau, lang="vi").save(duong_dan)
    print(f"{so:04d}.mp3  ({ten})  {cau}")
print(f"\nXong. Chép thư mục {out} vào thẻ nhớ thành /mp3")
