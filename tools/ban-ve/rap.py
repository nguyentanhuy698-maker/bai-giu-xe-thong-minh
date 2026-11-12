# Rập cắt 1:1 khổ A4 dọc (210 × 297 mm) – in 100 %, dán lên vật liệu rồi cắt theo nét liền
import os, sys, asyncio
from html import escape
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = 'DejaVu Sans, Arial, sans-serif'
PAGES = []

class Page:
    def __init__(self, title, subtitle=''):
        self.o = []; self.title = title; self.subtitle = subtitle
        PAGES.append(self)
    def t(self, x, y, s, size=3, anchor='start', w='normal', rot=0, fill='#000'):
        tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
        self.o.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}" font-weight="{w}" fill="{fill}"{tr}>{escape(s)}</text>')
    def line(self, x1, y1, x2, y2, sw=0.2, dash=None, col='#000'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.o.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{sw}"{d}/>')
    def rect(self, x, y, w, h, sw=0.3, dash=None, fill='none', rx=0, col='#000'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.o.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{col}" stroke-width="{sw}"{d}/>')
    def circ(self, cx, cy, r, sw=0.3, dash=None, fill='none'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="#000" stroke-width="{sw}"{d}/>')
    def center(self, cx, cy, r=0):  # dấu tâm khoan: chữ thập + chấm
        L = max(2.5, r + 2)
        self.line(cx - L, cy, cx + L, cy, 0.15); self.line(cx, cy - L, cx, cy + L, 0.15)
        self.o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="0.35" fill="#000"/>')
    def svg(self, no, total):
        h = [f'<rect width="210" height="297" fill="#fff"/>']
        h.append(f'<text x="10" y="11" font-family="{FONT}" font-size="4" font-weight="bold">{escape(self.title)}</text>')
        if self.subtitle: h.append(f'<text x="10" y="16" font-family="{FONT}" font-size="2.8">{escape(self.subtitle)}</text>')
        h.append(f'<text x="200" y="11" font-family="{FONT}" font-size="3.2" text-anchor="end" font-weight="bold">Tờ {no}/{total}</text>')
        h.append(f'<text x="200" y="5.5" font-family="{FONT}" font-size="2.2" text-anchor="end">Rập 1:1 · Bãi giữ xe máy thông minh · ĐA2</text>')
        # ô kiểm tra tỉ lệ in 50 × 50
        x0, y0 = 150, 270
        h.append(f'<rect x="{x0}" y="{y0}" width="50" height="12" fill="none" stroke="#000" stroke-width="0.3"/>')
        for i in range(0, 51, 5):
            L = 3 if i % 10 == 0 else 1.6
            h.append(f'<line x1="{x0+i}" y1="{y0}" x2="{x0+i}" y2="{y0+L}" stroke="#000" stroke-width="0.2"/>')
        h.append(f'<text x="{x0+25}" y="{y0+9}" font-family="{FONT}" font-size="3.2" text-anchor="middle" font-weight="bold">50 mm</text>')
        h.append(f'<text x="{x0-3}" y="{y0+4.5}" font-family="{FONT}" font-size="2.6" text-anchor="end" font-weight="bold">KIỂM TRA: khung bên phải dài đúng 50 mm →</text>')
        h.append(f'<text x="{x0-3}" y="{y0+9}" font-family="{FONT}" font-size="2.3" text-anchor="end">Sai lệch quá 0,5 mm: in lại ở 100 %, tắt "Vừa trang"</text>')
        h.append(f'<text x="10" y="292" font-family="{FONT}" font-size="2.4">Nét liền đậm: cắt · Chữ thập: tâm khoan (chấm dùi trước) · Nét gạch: chỉ đánh dấu, không cắt · Kích thước ghi bằng mm</text>')
        return '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">' + ''.join(h) + ''.join(self.o) + '</svg>'

def part(pg, x, y, w, h, name, qty, mat, feats=(), note=None, label_in=True, ly=0):
    """Chi tiết phẳng, góc trên-trái (x, y). Toạ độ đặc trưng tính từ góc DƯỚI-TRÁI của chi tiết (như bản vẽ)."""
    X = lambda u: x + u
    Y = lambda v: y + h - v
    pg.rect(x, y, w, h, sw=0.35)
    for f in feats:
        k = f[0]
        if k == 'hole':
            _, cx, cy, d = f; pg.circ(X(cx), Y(cy), d / 2); pg.center(X(cx), Y(cy), d / 2)
            pg.t(X(cx) + d / 2 + 1, Y(cy) - d / 2 - 0.4, f'Ø{str(d).replace(".", ",")}', 2)
        elif k == 'slot':
            _, cx, cy, ww, hh = f; pg.rect(X(cx - ww / 2), Y(cy + hh / 2), ww, hh, sw=0.3, rx=min(ww, hh) / 2)
        elif k == 'cut':
            _, cx, cy, ww, hh = f; pg.rect(X(cx - ww / 2), Y(cy + hh / 2), ww, hh, sw=0.3)
            pg.line(X(cx - ww / 2), Y(cy + hh / 2), X(cx + ww / 2), Y(cy - hh / 2), 0.12, '1 1'); pg.line(X(cx - ww / 2), Y(cy - hh / 2), X(cx + ww / 2), Y(cy + hh / 2), 0.12, '1 1')
        elif k == 'mark':
            _, cx, cy, ww, hh, txt = f; pg.rect(X(cx - ww / 2), Y(cy + hh / 2), ww, hh, sw=0.2, dash='2 1')
            if txt: pg.t(X(cx), Y(cy) + 1, txt, 2, 'middle')
        elif k == 'circle':
            _, cx, cy, d = f; pg.circ(X(cx), Y(cy), d / 2, sw=0.2, dash='2 1')
    if label_in and w >= 20 and h >= 14:
        y = y + ly
        pg.t(x + w / 2, y + 5, name, 2.8 if w > 40 else 2.2, 'middle', 'bold')
        pg.t(x + w / 2, y + 8.6, f'{w:g} × {h:g} · {mat} · SL {qty}'.replace('.', ','), 2 if w > 40 else 1.6, 'middle')
        if note: pg.t(x + w / 2, y + 11.8, note, 1.9, 'middle')
    else:
        pg.t(x, y - 1.2, f'{name} {w:g}×{h:g} SL {qty}'.replace('.', ','), 2, 'start', 'bold')
    return X, Y

# =================== TỜ 1: HƯỚNG DẪN ===================
def page_guide():
    pg = Page('HƯỚNG DẪN DÙNG RẬP', 'In khổ A4, tỉ lệ 100 % (Actual size), tắt "Fit to page" / "Vừa trang"')
    steps = [
        'In tất cả các tờ trên giấy A4 ở tỉ lệ 100 %. Đo khung kiểm tra ở góc dưới mỗi tờ: phải đúng 50 mm.',
        'Cắt rời từng chi tiết, chừa khoảng 3 mm ngoài nét cắt.',
        'Dán rập lên mặt mica còn giấy bảo vệ (hoặc lên Formex) bằng keo dán giấy dạng thỏi hoặc băng keo 2 mặt mỏng.',
        'Chấm dùi vào tâm chữ thập rồi mới khoan: khoan mồi Ø2, sau đó khoan đúng đường kính ghi cạnh lỗ.',
        'Lỗ khoét chữ nhật (có gạch chéo): khoan 4 góc Ø3, cắt theo cạnh bằng cưa lọng hoặc dao cắt mica, giũa tới nét.',
        'Cắt mica: dùng dao rạch mica rạch 5–6 lần theo nét liền, bẻ trên mép bàn. Mica trong 2 mm rạch nhẹ tay hơn.',
        'Nét gạch chỉ để đánh dấu vị trí dán linh kiện, decal: không cắt.',
        'Bóc rập bằng cách bóc luôn lớp giấy bảo vệ mica. Với Formex, lau keo bằng khăn ẩm.',
        'Chi tiết dài hơn tờ A4 được chia nhiều tờ: chồng các dấu ghép ⊕ cùng tên lên nhau rồi dán băng keo.',
    ]
    y = 26
    pg.t(10, y, 'CÁC BƯỚC', 3.4, w='bold'); y += 6
    for i, s in enumerate(steps, 1):
        words, line, lines = s.split(' '), '', []
        for wd in words:
            if len(line) + len(wd) > 92: lines.append(line); line = wd
            else: line = (line + ' ' + wd).strip()
        lines.append(line)
        pg.t(10, y, f'{i}.', 2.8)
        for l in lines: pg.t(15, y, l, 2.8); y += 4
        y += 1
    y += 4
    pg.t(10, y, 'DANH SÁCH TỜ RẬP', 3.4, w='bold'); y += 3
    rows = [('1', 'Hướng dẫn, chi tiết cắt thẳng theo kích thước'), ('2', 'Chốt: vách P1, P2, P3, P4'), ('3', 'Chốt: kính K1, K2'),
            ('4', 'Chốt: mái, viền biển tên, đế, quầy'), ('5', 'Tủ barie VÀO + cần barie'), ('6', 'Tủ barie RA + cần barie'),
            ('7', 'Hộp camera và cột camera (2 bộ)'), ('8', 'Đảo phân làn – rập khoan và vị trí dán (nửa phía đường)'),
            ('9', 'Đảo phân làn – rập khoan và vị trí dán (nửa phía bãi)'), ('10', 'Đế: nắp thăm, lỗ mặt sau, rãnh sườn, lỗ cột đỡ cần')]
    for a, b in rows:
        pg.rect(10, y, 12, 5.5, sw=0.2); pg.rect(22, y, 120, 5.5, sw=0.2)
        pg.t(16, y + 4, a, 2.6, 'middle'); pg.t(24, y + 4, b, 2.6); y += 5.5
    y += 8
    pg.t(10, y, 'CHI TIẾT CẮT THẲNG (không cần rập, cắt theo kích thước)', 3.4, w='bold'); y += 3
    big = [('Mặt đế', '560 × 450', '1', 'Formex 5'), ('Đáy đế', '560 × 450', '1', 'MDF 3 (khoét nắp thăm: tờ 10)'),
           ('Khung trước, sau', '560 × 40', '2', 'Formex 5 (khung sau khoét lỗ: tờ 10)'), ('Khung trái, phải', '440 × 40', '2', 'Formex 5'),
           ('Sườn', '440 × 40', '2', 'Formex 5 (rãnh dây: tờ 10)'), ('Vỉa hè trái', '90 × 330', '2 lớp', 'Formex 5 + 3'),
           ('Vỉa hè phải', '70 × 330', '2 lớp', 'Formex 5 + 3'), ('Đảo phân làn', '100 × 330', '3 lớp', 'Formex 5 (khoan theo tờ 8, 9)'),
           ('Trụ góc chốt', '4 × 4 × 98', '4', 'nhôm hộp'), ('Ống cột camera', 'Ø12 × 47', '2', 'ống nhôm'), ('Que đỡ cần', 'Ø5 × 64', '2', 'inox')]
    cols = [(10, 40), (50, 30), (80, 16), (96, 100)]
    for i, r in enumerate([('Chi tiết', 'Kích thước', 'SL', 'Vật liệu / ghi chú')] + big):
        for (cx, cw), v in zip(cols, r):
            pg.rect(cx, y, cw, 5.5, sw=0.2); pg.t(cx + 1.5, y + 4, v, 2.5, w='bold' if i == 0 else 'normal')
        y += 5.5

# =================== CHỐT ===================
def page_booth():
    pg = Page('CHỐT – VÁCH DƯỚI (mica xám 3 mm)', 'P3 và P4 giống nhau. Vẽ nhìn từ mặt ngoài.')
    slots = [('slot', 45 - 27.5 + i * 5, 30, 2, 22) for i in range(12)]
    part(pg, 10, 24, 90, 92, 'P1 – Vách trước (phía đường)', 1, 'mica xám 3',
         slots + [('hole', 20, 72, 6), ('mark', 45, 30, 70, 31, '')], note='12 khe 2 × 22 · lỗ còi Ø6')
    part(pg, 108, 24, 90, 92, 'P2 – Vách sau (tháo được)', 1, 'mica xám 3',
         [('hole', 5, 5, 3.2), ('hole', 85, 5, 3.2), ('hole', 5, 87, 3.2), ('hole', 85, 87, 3.2)], note='4 lỗ M3 bắt ke góc')
    for i, (x, nm) in enumerate(((8, 'P3 – Vách bên làn ra'), (106, 'P4 – Vách bên làn vào'))):
        part(pg, x, 132, 94, 92, nm, 1, 'mica xám 3',
             [('mark', 47, 62, 64, 44, ''), ('mark', 47, 62, 60, 40, 'RC522 dán mặt trong'), ('hole', 47, 88, 5), ('slot', 47, 6, 15, 7)],
             note='lỗ LED Ø5 · khe IR 15 × 7', ly=66)
    pg.t(10, 236, 'Mép dưới mỗi vách dán xuống đế chốt; P3, P4 kẹp giữa P1, P2 (chiều rộng 94 = 100 − 2 × 3).', 2.5)
    pg.t(10, 241, 'Mặt quẹt thẻ: dán decal 64 × 44 lên mặt ngoài P3, P4 trùng khung nét gạch.', 2.5)

def page_glass():
    pg = Page('CHỐT – KÍNH (mica trong 2 mm)', 'K1: kính trước và sau; K2: kính hai bên, chừa cửa đưa thẻ rộng 36')
    part(pg, 10, 24, 82, 94, 'K1 – Kính trước', 1, 'mica trong 2')
    part(pg, 98, 24, 82, 94, 'K1 – Kính sau', 1, 'mica trong 2')
    for i in range(4):
        part(pg, 10 + i * 34, 132, 28, 94, f'K2 – Kính bên {i + 1}', 1, 'mica trong 2')
    pg.t(150, 140, 'Ráp: mỗi vách bên dùng 2 tấm K2,', 2.5); pg.t(150, 144, 'cách nhau 36 (cửa đưa thẻ).', 2.5)
    pg.t(150, 152, 'K1, K2 dán vào 4 trụ nhôm 4 × 4.', 2.5)

def page_roof():
    pg = Page('CHỐT – MÁI, VIỀN BIỂN TÊN, ĐẾ, QUẦY', 'Viền biển tên dán thành khung 108 × 118 quanh mái')
    part(pg, 10, 24, 106, 116, 'M – Mái', 1, 'mica xám 3')
    for i in range(2):
        part(pg, 124 + i * 22, 24, 16, 118, 'B1', 1, 'mica xám 3', label_in=False)
        pg.t(124 + i * 22 + 8, 90, 'B1 – viền dài 118 × 16', 2.2, 'middle', rot=-90)
    for i in range(2):
        part(pg, 168 + i * 22, 24, 16, 102, 'B2', 1, 'mica xám 3', label_in=False)
        pg.t(168 + i * 22 + 8, 80, 'B2 – viền ngắn 102 × 16', 2.2, 'middle', rot=-90)
    part(pg, 10, 152, 98, 108, 'Đ – Đế chốt', 1, 'Formex 6 (2 × 3)', [('hole', 49, 54, 16)], note='lỗ đi dây Ø16 ở tâm')
    part(pg, 120, 152, 16, 44, 'Q', 1, 'mica xám 3', label_in=False)
    part(pg, 144, 152, 16, 44, 'Q', 1, 'mica xám 3', label_in=False)
    pg.t(120, 202, 'Q – Quầy 16 × 44 (2 tấm), dán ngang', 2.3); pg.t(120, 206, 'mép trên vách bên, giữa vách.', 2.3)

# =================== TỦ BARIE ===================
def page_cabinet(word):
    pg = Page(f'TỦ BARIE {word} + CẦN BARIE (mica vàng 3 mm, cần mica trắng 4 mm)', 'C1 nhìn từ mặt ngoài phía làn; đầu servo đẩy từ trong ra qua lỗ khoét')
    feats = [('cut', 30, 64, 41.5, 20.5)] + [('hole', 30 + a, 64 + b, 3.2) for a in (-24.75, 24.75) for b in (-5, 5)] + [('slot', 30, 6, 15, 7)]
    part(pg, 10, 24, 60, 94, 'C1 – Vách phía làn', 1, 'mica vàng 3', feats, note='khoét 41,5 × 20,5')
    part(pg, 76, 24, 60, 94, 'C2 – Vách phía đảo', 1, 'mica vàng 3', [('hole', 4, 4, 3.2), ('hole', 56, 4, 3.2), ('hole', 4, 90, 3.2), ('hole', 56, 90, 3.2)], note='tháo được')
    part(pg, 142, 24, 44, 94, 'C3 – Vách trước', 1, 'mica vàng 3', [('mark', 22, 74, 36, 18, f'decal {word}')])
    part(pg, 10, 130, 44, 94, 'C4 – Vách sau', 1, 'mica vàng 3')
    part(pg, 60, 130, 54, 64, 'C5 – Nắp', 1, 'mica xám 3')
    part(pg, 120, 130, 50, 60, 'C6 – Đế', 1, 'cao su / Formex 6', [('hole', 25, 30, 12)])
    # cần barie
    x, y = 10, 238
    pg.rect(x, y, 150, 8, sw=0.35)
    for i in range(1, 8): pg.rect(x + 20 * i - 10, y, 10, 8, sw=0.15, dash='1.5 1')
    for xh in (5, 13): pg.circ(x + xh, y + 4, 1.1); pg.center(x + xh, y + 4)
    pg.t(x, y - 1.5, 'CB – Cần barie 150 × 8 (mica trắng 4) · 2 lỗ Ø2,2 · khung gạch: decal đỏ 10 × 8', 2.3, w='bold')
    pg.rect(x + 156, y - 1, 8, 10, sw=0.35); pg.t(x + 166, y + 5, 'đầu cao su 8 × 10', 2.1)
    # khối ngàm cột đỡ
    fx, fy = 170, 206
    pg.o.append(f'<polygon points="{fx},{fy} {fx},{fy+9} {fx+8},{fy+9} {fx+8},{fy} {fx+6.5},{fy} {fx+6.5},{fy+5} {fx+1.5},{fy+5} {fx+1.5},{fy}" fill="none" stroke="#000" stroke-width="0.35"/>')
    pg.t(fx - 2, fy - 2, 'Ngàm đỡ cần 8 × 9', 2.1); pg.t(fx - 2, fy + 13, 'rãnh 5 × 5, dày 10', 2.1)

# =================== CAMERA ===================
def page_camera():
    pg = Page('HỘP CAMERA VÀ CỘT CAMERA – ĐỦ CHO 2 CỘT', 'Hộp: mica trắng 2 mm; H4 mica trong 2 mm; H5 mica xám 2 mm')
    x = 10
    for i in range(2):
        part(pg, x, 24, 30, 50, 'H1 – Sau', 1, 'mica 2', [('hole', 15, 6, 4)]); x += 34
    for i in range(4):
        part(pg, x, 24, 28, 50, 'H2 – Bên', 1, 'mica 2', [('mark', 7, 25, 2, 44, '')]); x += 32
    pg.t(76, 80, 'H2: rãnh giữ bo ESP32-CAM sâu 1 (nét gạch) – khắc bằng dao, cách mép trước 6', 2.2)
    x = 10
    for i in range(2):
        part(pg, x, 92, 30, 26, 'H3 – Đáy', 1, 'mica 2', [('hole', 15, 13, 4)]); x += 34
    for i in range(2):
        part(pg, x, 92, 30, 46, 'H4 – Cửa sổ', 1, 'mica trong 2'); x += 34
    for i in range(2):
        part(pg, 10 + i * 44, 148, 40, 38, 'H5 – Mái che', 1, 'mica xám 2')
    y = 150; x = 104
    for i in range(2):
        pg.circ(x + 10, y + 10, 10, sw=0.35); pg.circ(x + 10, y + 10, 4); pg.center(x + 10, y + 10, 4)
        pg.t(x + 10, y + 25, 'Đ – Đế cột Ø20, lỗ Ø8', 1.9, 'middle'); x += 28
    for i in range(2):
        pg.rect(x, y + 6, 8, 8, sw=0.35); pg.circ(x + 4, y + 10, 2); pg.center(x + 4, y + 10, 2)
        pg.t(x + 4, y + 20, 'N 8 × 8', 2.1, 'middle'); x += 14
    pg.t(160, y + 25, 'N: mặt trên vát 15°', 1.9)
    for i in range(2):
        pg.rect(104, y + 32 + i * 7, 30, 4, sw=0.35)
    pg.t(138, y + 37, 'T – Tay đỡ đèn 30 × 4 × 4 (2 thanh)', 2.1)
    import math
    gx, gy = 30, 262
    pg.t(10, 206, 'THƯỚC ĐẶT GÓC CAMERA (cắt rời, đặt sát mép đảo khi dán cột)', 2.8, w='bold')
    L = 50
    pg.line(gx, gy, gx + L, gy, 0.35)
    a = math.radians(35.8)
    pg.line(gx, gy, gx + L * math.sin(a), gy - L * math.cos(a), 0.35)
    pg.line(gx, gy, gx, gy - L, 0.15, '2 1')
    pg.t(gx + 6, gy - 22, '35,8°', 2.8, w='bold')
    pg.t(gx - 2, gy + 5, 'mép đảo, chiều xe chạy ↑', 2.2)
    pg.t(gx + 26, gy - 40, 'hướng ống kính', 2.2)
    hx, hy = 120, 232
    pg.line(hx, hy, hx + L, hy, 0.35)
    b = math.radians(15)
    pg.line(hx, hy, hx + L * math.cos(b), hy + L * math.sin(b), 0.35)
    pg.t(hx + 30, hy + 4, '15°', 2.8, w='bold')
    pg.t(hx, hy - 3, 'phương ngang', 2.2); pg.t(hx + 20, hy + 17, 'trục ống kính chúc xuống', 2.2)

# =================== ĐẢO PHÂN LÀN (2 TỜ) ===================
ISL = dict(holes=[('H1 Ø16 – chốt', 50, 155, 16), ('H2 Ø12 – tủ VÀO', 69, 295, 12), ('H3 Ø12 – tủ RA', 31, 35, 12),
                  ('H4 Ø8 – cột camera VÀO', 90, 13, 8), ('H5 Ø8 – cột camera RA', 10, 317, 8)],
           marks=[('đế chốt 98 × 108', 50, 155, 98, 108), ('tủ VÀO 50 × 60', 69, 295, 50, 60), ('tủ RA 50 × 60', 31, 35, 50, 60)],
           circles=[(90, 13, 20), (10, 317, 20)])
def page_island(part_no):
    lo, hi = (0, 175) if part_no == 1 else (165, 330)
    pg = Page(f'ĐẢO PHÂN LÀN 100 × 330 – TỜ {part_no}/2 ({"nửa phía đường" if part_no == 1 else "nửa phía bãi"})',
              'Dán lên lớp đảo trên cùng, khoan xuyên 3 lớp đảo và mặt đế. Nét gạch: chỗ dán chốt, tủ, cột.')
    ox, oy = 55, 24             # mép trái đảo trên giấy; v = 0 (phía đường) ở dưới
    H = hi - lo
    Y = lambda v: oy + (hi - v)
    X = lambda u: ox + u
    # cạnh đảo (cắt) – chỉ vẽ phần nằm trong tờ
    pg.line(X(0), Y(hi), X(0), Y(lo), 0.35); pg.line(X(100), Y(hi), X(100), Y(lo), 0.35)
    if lo == 0: pg.line(X(0), Y(0), X(100), Y(0), 0.35)
    if hi == 330: pg.line(X(0), Y(330), X(100), Y(330), 0.35)
    # vùng ghép
    ov0, ov1 = 165, 175
    pg.rect(X(0), Y(ov1), 100, ov1 - ov0, sw=0.1, dash='1 1', fill='#f2f2f2')
    pg.t(X(50), Y(ov1) + 6, 'vùng chồng ghép 2 tờ', 2.2, 'middle')
    for (u, v) in ((-12, 170), (112, 170)):
        if lo <= v <= hi:
            pg.circ(X(u), Y(v), 3, sw=0.2); pg.center(X(u), Y(v), 3); pg.t(X(u), Y(v) + 7, 'ghép', 2, 'middle')
    for n, u, v, w, h in ISL['marks']:
        v0, v1 = v - h / 2, v + h / 2
        if v1 < lo or v0 > hi: continue
        a, b = max(v0, lo), min(v1, hi)
        pg.rect(X(u - w / 2), Y(b), w, b - a, sw=0.2, dash='2 1')
        if lo <= v <= hi: pg.t(X(u), Y(v) + 12, n, 2.2, 'middle')
    for (u, v, d) in ISL['circles']:
        if lo - 10 <= v <= hi + 10: pg.circ(X(u), Y(v), d / 2, sw=0.2, dash='2 1')
    for n, u, v, d in ISL['holes']:
        if lo <= v <= hi:
            pg.circ(X(u), Y(v), d / 2, sw=0.35); pg.center(X(u), Y(v), d / 2)
            pg.t(X(u) + d / 2 + 2, Y(v) + 1, n, 2.3, w='bold')
    # thước toạ độ dọc bên trái
    for v in range(int(lo // 10 * 10), hi + 1, 10):
        if v < lo: continue
        L = 4 if v % 50 == 0 else 2
        pg.line(X(0) - L, Y(v), X(0), Y(v), 0.15)
        if v % 50 == 0: pg.t(X(0) - 5, Y(v) + 1, str(v), 2.2, 'end')
    pg.t(X(-10), Y((lo + hi) / 2), 'khoảng cách tính từ đầu đảo phía đường', 2.2, 'middle', rot=-90)
    if part_no == 1:
        pg.t(X(50), Y(0) + 6, 'ĐẦU ĐẢO PHÍA ĐƯỜNG', 2.6, 'middle', 'bold')
        pg.t(X(50), Y(0) + 11, 'Đặt đảo lên mặt đế: mép trái cách mép đế 240, đầu đảo cách mép đế phía đường 60', 2.2, 'middle')
    else:
        pg.t(X(50), Y(330) - 3, 'ĐẦU ĐẢO PHÍA BÃI', 2.6, 'middle', 'bold')
    pg.t(X(102), Y(hi) + 16, '→ làn VÀO', 2.3); pg.t(X(-2), Y(hi) + 16, 'làn RA ←', 2.3, 'end')

# =================== ĐẾ ===================
def page_base():
    pg = Page('ĐẾ – NẮP THĂM, LỖ MẶT SAU, RÃNH SƯỜN, LỖ CỘT ĐỠ CẦN', '')
    # nắp thăm đáy: rập khoét 110 × 130 với 4 lỗ vít
    x, y = 10, 24
    pg.rect(x, y, 110, 130, sw=0.35)
    pg.line(x, y, x + 110, y + 130, 0.12, '1 1'); pg.line(x, y + 130, x + 110, y, 0.12, '1 1')
    for (u, v) in ((4, 4), (106, 4), (4, 126), (106, 126)):
        pg.circ(x + u, y + v, 1.6); pg.center(x + u, y + v)
    pg.t(x + 55, y + 60, 'KHOÉT ĐÁY 110 × 130', 3, 'middle', 'bold')
    pg.t(x + 55, y + 65, 'tâm khoét: X 290, Y 220 tính từ góc đế', 2.3, 'middle')
    pg.t(x + 55, y + 69, '(góc trái phía đường)', 2.3, 'middle')
    pg.t(x + 55, y + 76, '4 lỗ Ø3,2 bắt nắp thăm', 2.3, 'middle')
    pg.t(x + 55, y + 80, 'nắp thăm: MDF 3, 130 × 150', 2.3, 'middle')
    # khung sau: đoạn khoét 120 × 40
    x, y = 10, 168
    pg.rect(x, y, 120, 40, sw=0.2, dash='3 1.5')
    pg.t(x, y - 1.5, 'Khung sau – đoạn có lỗ (dán sao cho mép trái rập trùng X = 120 của khung sau)', 2.3, w='bold')
    pg.circ(x + 20, y + 20, 4); pg.center(x + 20, y + 20, 4); pg.t(x + 20, y + 30, 'jack DC Ø8', 2.1, 'middle')
    pg.rect(x + 40.5, y + 13.5, 19, 13, sw=0.35); pg.center(x + 50, y + 20)
    pg.t(x + 50, y + 32, 'công tắc 19 × 13', 2.1, 'middle')
    pg.rect(x + 89, y + 16.5, 12, 7, sw=0.35, rx=1)
    for d in (-14, 14): pg.circ(x + 95 + d, y + 20, 1.6); pg.center(x + 95 + d, y + 20)
    pg.t(x + 95, y + 32, 'USB 12 × 7, 2 lỗ Ø3,2', 2.1, 'middle')
    pg.t(x + 2, y + 38, 'mép dưới = đáy', 1.9)
    # rãnh sườn
    x, y = 140, 24
    pg.t(x, y - 1.5, 'Rãnh dây trên sườn (4 chỗ)', 2.3, w='bold')
    pg.o.append(f'<polyline points="{x},{y+40} {x},{y} {x+60},{y} {x+60},{y+40} {x+42},{y+40} {x+42},{y+25} {x+18},{y+25} {x+18},{y+40} {x},{y+40}" fill="none" stroke="#000" stroke-width="0.35"/>')
    pg.t(x + 30, y + 34, 'khoét 24 × 15', 2.1, 'middle'); pg.t(x + 30, y + 10, 'đoạn sườn cao 40', 2.1, 'middle')
    pg.t(x, y + 47, 'Tâm rãnh tại Y = 120 và Y = 330', 2.1); pg.t(x, y + 51, '(tính từ mép đế phía đường)', 2.1)
    # lỗ cột đỡ cần trên vỉa hè
    for i, (nm, u, v) in enumerate((('Vỉa hè PHẢI – cột đỡ cần VÀO', 5, 305), ('Vỉa hè TRÁI – cột đỡ cần RA', 85, 25))):
        x, y = 140, 92 + i * 62
        w_ = 70 if i == 0 else 90
        # vẽ góc vỉa hè 40 × 40 quanh lỗ
        u0 = max(0, u - 20); v0 = max(0, v - 20)
        pg.rect(x, y, 40, 40, sw=0.2, dash='2 1')
        cx, cy = x + (u - u0), y + 40 - (v - v0)
        pg.circ(cx, cy, 2.5); pg.center(cx, cy, 2.5)
        pg.t(x, y - 1.5, nm, 2.3, w='bold')
        if i == 0:
            pg.line(x, y, x, y + 40, 0.35); pg.t(x + 2, y + 44, 'mép vỉa hè giáp làn = cạnh trái', 2); pg.t(x + 2, y + 47.5, 'tâm cách cạnh 5, cách đầu phía đường 305', 2)
        else:
            pg.line(x + 40, y, x + 40, y + 40, 0.35); pg.line(x, y + 40, x + 40, y + 40, 0.35)
            pg.t(x, y + 44, 'cạnh phải giáp làn, cạnh dưới phía đường', 2); pg.t(x, y + 47.5, 'tâm cách cạnh phải 5, cách cạnh dưới 25', 2)
        pg.t(cx + 4, cy + 1, 'Ø5 sâu 8', 2.1)

def build(outdir):
    page_guide(); page_booth(); page_glass(); page_roof(); page_cabinet('VÀO'); page_cabinet('RA'); page_camera(); page_island(1); page_island(2); page_base()
    n = len(PAGES)
    svgs = [p.svg(i + 1, n) for i, p in enumerate(PAGES)]
    os.makedirs(outdir, exist_ok=True)
    html = '<!DOCTYPE html><html><head><meta charset="utf-8"><style>@page{size:210mm 297mm;margin:0}body{margin:0}svg{display:block;page-break-after:always}</style></head><body>' + ''.join(svgs) + '</body></html>'
    open(f'{outdir}/rap.html', 'w').write(html)
    for i, sv in enumerate(svgs): open(f'{outdir}/rap{i+1:02d}.svg', 'w').write(sv)
    from playwright.async_api import async_playwright
    async def m():
        async with async_playwright() as p:
            b = await p.chromium.launch(channel='chrome'); pg = await b.new_page(viewport={'width': 794, 'height': 1123})
            await pg.goto(f'file://{outdir}/rap.html'); await pg.wait_for_timeout(400)
            await pg.pdf(path=f'{outdir}/rap-cat-1-1-A4.pdf', width='210mm', height='297mm', print_background=True, prefer_css_page_size=True)
            for i in range(n):
                await pg.goto(f'file://{outdir}/rap{i+1:02d}.svg'); await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{outdir}/r{i+1:02d}.png')
            await b.close()
    asyncio.run(m())
    print(n, 'pages')

if __name__ == '__main__':
    build(os.path.join(HERE, 'out_rap'))
