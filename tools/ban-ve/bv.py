import base64, math, os
from bvlib import Sheet, View, W_THICK, W_THIN, fmt
from geom import *
import proj

TOTAL = 11
SHEETS = []
def sheet(no, title, scale, material='—'):
    s = Sheet(no, title, scale, TOTAL, material); SHEETS.append(s); return s

def img(sh, path, x, y, w, h):
    b = base64.b64encode(open(path, 'rb').read()).decode()
    sh.raw(f'<image href="data:image/png;base64,{b}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>')

def notes(sh, x, y, title, items, size=2.8, width=240):
    from bvlib import wraptext
    sh.text(x, y, title, size=3.2, weight='bold'); y += 5
    for i, t in enumerate(items, 1):
        ls = wraptext(t, width - 6, size)
        sh.text(x, y, f'{i}.', size=size)
        for l in ls:
            sh.text(x + 4.5, y, l, size=size); y += size * 1.35
        y += 0.6
    return y

ASM = assembly()

# =====================================================================================
# BV-01  BẢN VẼ LẮP CHUNG
# =====================================================================================
def bv01():
    sh = sheet(1, 'BẢN VẼ LẮP CHUNG MÔ HÌNH BÃI GIỮ XE', '1:5', 'Formex, mica')
    k = 0.2
    fx, fy = 32, 72                    # gốc hình chiếu đứng (X=0, Z=0)
    tx, ty = 32, 196                   # gốc hình chiếu bằng (X=0, Y=0)
    lx = 32 + 560 * k + 24             # gốc hình chiếu cạnh
    proj.draw(sh, ASM, 'front', fx, fy, k)
    proj.draw(sh, ASM, 'top', tx, ty, k)
    proj.draw(sh, ASM, 'left', lx, fy, k)
    v = View(sh, fx, fy, k, None)
    # kích thước hình chiếu đứng
    sh.dh(fx, fx + 560 * k, fy + 48 * k, 7, '560')
    sh.dv(fx, fy - 233 * k, fy + 48 * k, -14, '281')
    sh.dv(fx, fy, fy + 48 * k, -6, '48')
    sh.dv(fx + 560 * k, fy - 85 * k, fy, 6, '85')
    sh.dv(fx + 560 * k, fy - 233 * k, fy, 13, '233')
    # hình chiếu bằng
    sh.dh(tx, tx + 560 * k, ty, 7, '560')
    sh.dv(tx + 560 * k, ty - 450 * k, ty, 6, '450')
    for a, b in ((90, 240), (240, 340), (340, 490)):
        sh.dh(tx + a * k, tx + b * k, ty - 450 * k, -4, str(b - a))
    # hình chiếu cạnh
    sh.dh(lx, lx + 450 * k, fy + 48 * k, 7, '450')
    sh.label(fx + 56, 18, 'HÌNH CHIẾU ĐỨNG')
    sh.label(tx + 56, ty - 450 * k - 10, 'HÌNH CHIẾU BẰNG')
    sh.label(lx + 45, 18, 'HÌNH CHIẾU CẠNH')
    # số vị trí
    B = sh.balloon
    p = lambda X, Z: (fx + X * k, fy - Z * k)
    B(*p(20, -24), fx - 9, fy + 2, '1')
    B(*p(290, 200), fx + 56, 26, '4')
    B(*p(330, 95), fx + 95, 30, '8')
    B(*p(271, 60), fx + 30, 34, '5')
    B(*p(150, 85), fx + 20, 44, '6')
    q = lambda X, Y: (tx + X * k, ty - Y * k)
    B(*q(45, 300), tx - 9, ty - 70, '2')
    B(*q(290, 370), tx + 40, ty - 96, '3')
    B(*q(495, 365), tx + 112, ty - 96, '7')
    B(*q(330, 43), tx + 85, ty + 4, '9')
    # hình minh hoạ
    img(sh, 'os.path.join(os.path.dirname(__file__), "img_persp.png")', 172, 100, 98, 72)
    sh.rect(172, 100, 98, 72, sw=W_THIN)
    sh.text(221, 177, 'Hình minh hoạ (không theo tỉ lệ)', size=2.6, anchor='middle', italic=True)
    # bảng kê
    cols = [('VT', 7), ('Tên gọi', 44), ('SL', 7), ('Vật liệu / quy cách', 52), ('Bản vẽ', 22)]
    rows = [
        ['1', 'Đế (mặt, khung, đáy)', '1', 'Formex 5 mm; đáy MDF 3 mm', 'BV-03'],
        ['2', 'Vỉa hè', '2', 'Formex 5 + 3 mm dán chồng', 'BV-02'],
        ['3', 'Đảo phân làn', '1', 'Formex 5 mm × 3 lớp, decal sọc', 'BV-02'],
        ['4', 'Chốt nhân viên', '1', 'Mica 3 mm xám; kính mica trong 2 mm', 'BV-04, 05'],
        ['5', 'Tủ barie', '2', 'Mica vàng 3 mm', 'BV-06'],
        ['6', 'Cần barie 150 × 8 × 4', '2', 'Mica trắng 4 mm, decal đỏ', 'BV-06'],
        ['7', 'Cột đỡ đầu cần', '2', 'Que inox Ø5 + khối mica', 'BV-06'],
        ['8', 'Cột và hộp camera', '2', 'Ống nhôm Ø12 × 1; mica 2 mm', 'BV-07'],
        ['9', 'Đèn LED chiếu biển', '2', 'Đèn LED USB 6 bóng, cắt đầu', 'BV-07'],
        ['10', 'Servo MG996R', '2', '40,7 × 19,7 × 42,9', 'BV-06, 10'],
        ['11', 'Đầu đọc RC522 + thẻ', '2', '60 × 40', 'BV-04, 10'],
        ['12', 'ESP32-CAM OV2640', '2', '27 × 40,5 × 4,5', 'BV-07, 10'],
        ['13', 'Cảm biến IR FC-51', '4', '31,3 × 14,2 × 6,6', 'BV-04, 06'],
        ['14', 'Loa 3 W 4 Ω', '1', '70 × 31 × 16,8', 'BV-04'],
        ['15', 'Module còi chủ động', '1', '34,3 × 13,3 × 11,5', 'BV-04'],
        ['16', 'LED WS2812 bo Ø10', '2', '—', 'BV-04'],
        ['17', 'Bo mạch chính', '1', 'PCB đục lỗ 70 × 90, 2 mặt', 'BV-08'],
        ['18', 'ESP32 DevKit 38 chân', '1', '55 × 28', 'BV-08, 10'],
        ['19', 'DFPlayer Mini + thẻ nhớ', '1', '20 × 20', 'BV-08'],
        ['20', 'Mạch hạ áp 12 → 5 V 5 A', '1', 'XY-3606, ≈ 63 × 27', 'BV-03'],
        ['21', 'Adapter 12 V 3 A, jack 5,5/2,1', '1', '—', 'BV-03, 09'],
        ['22', 'Công tắc bập bênh KCD1', '1', 'Lỗ khoét 19 × 13', 'BV-03'],
    ]
    sh.text(278, 13, 'BẢNG KÊ CHI TIẾT VÀ LINH KIỆN', size=3.2, weight='bold')
    sh.table(278, 16, cols, rows, rh=5.2, size=2.5)
    notes(sh, 24, 216, 'YÊU CẦU KỸ THUẬT', [
        'Kích thước tính bằng mm. Độ cao tính từ mặt đường (mặt trên của đế), trừ khi ghi khác.',
        'Vỏ mô hình theo tỉ lệ 1:10 so với bãi xe thật; linh kiện điện tử dùng kích thước thật (BV-10).',
        'Mica cắt laser theo BV-05, BV-06, BV-07; sai lệch cắt ±0,3. Dán bằng keo dán mica chuyên dụng, kẹp giữ 10 phút.',
        'Dung sai lắp ghép chung ±0,5. Lỗ bắt vít M3 khoan Ø3,2; lỗ đi dây theo BV-02.',
        'Màu: làn xe xám đậm RAL 7024; đảo, vỉa hè xám nhạt RAL 7035; tủ barie vàng RAL 1003; chốt xám than RAL 7016.',
        'Toàn bộ dây đi dưới đế; không để dây lộ trên mặt mô hình.',
    ], size=2.6, width=245)
    return sh

# =====================================================================================
# BV-02  MẶT BẰNG BỐ TRÍ, VẠCH SƠN, LỖ ĐI DÂY
# =====================================================================================
def bv02():
    sh = sheet(2, 'MẶT BẰNG BỐ TRÍ, VẠCH SƠN VÀ LỖ ĐI DÂY', '1:2', 'Formex 5 mm')
    k = 0.5
    ox, oy = 44, 240
    P = lambda X, Y: (ox + X * k, oy - Y * k)
    # đế
    sh.rect(*P(0, 450), 560 * k, 450 * k, sw=0.7)
    # vùng: đường, bãi, làn, vỉa hè, đảo
    for (x0, x1, y0, y1) in ((0, 90, 60, 390), (490, 560, 60, 390)):
        sh.rect(*P(x0, y1), (x1 - x0) * k, (y1 - y0) * k, sw=W_THICK)
    sh.rect(*P(240, 390), 100 * k, 330 * k, sw=W_THICK)
    sh.line(*P(0, 60), *P(560, 60), w=W_THIN); sh.line(*P(0, 390), *P(560, 390), w=W_THIN)
    # vạch kẻ làn 3 mm, vạch dừng 5 mm, ô gạch chéo cấm dừng
    for X in (90, 237, 340, 487):
        sh.rect(*P(X, 390), 3 * k, 330 * k, sw=W_THIN)
    sh.rect(*P(340, 354), 150 * k, 5 * k, sw=W_THIN, fill='#000')     # vạch dừng làn vào (trước barie)
    sh.rect(*P(90, 101), 150 * k, 5 * k, sw=W_THIN, fill='#000')      # vạch dừng làn ra
    for (x0, y0) in ((340, 365), (90, 60)):
        sh.rect(*P(x0, y0 + 25), 150 * k, 25 * k, sw=W_THIN)
        for t in range(0, 175, 10):
            a = (x0 + t - 25, y0); b = (x0 + t, y0 + 25)
            # cắt trong ô
            xa, ya = max(a[0], x0), y0 + (max(a[0], x0) - a[0])
            xb, yb = min(b[0], x0 + 150), y0 + 25 - (b[0] - min(b[0], x0 + 150))
            if xa < xb: sh.line(*P(xa, ya), *P(xb, yb), w=0.18)
    # bãi đỗ: vạch ô 40 mm
    for X in range(30, 531, 40): sh.line(*P(X, 446), *P(X, 400), w=W_THIN)
    sh.line(*P(30, 400), *P(530, 400), w=W_THIN)
    sh.text(*P(280, 425), 'KHU ĐỂ XE', size=3, anchor='middle')
    sh.text(*P(280, 25), 'ĐƯỜNG', size=3, anchor='middle')
    # mũi tên chữ
    sh.text(*P(445, 30), 'VÀO ↑', size=3.4, anchor='middle', weight='bold')
    sh.text(*P(140, 30), 'RA ↓', size=3.4, anchor='middle', weight='bold')
    # khối trên đảo (nét mảnh, mặt cắt chân)
    bx, by = BOOTH_C
    sh.rect(*P(bx - 49, by + 54), 98 * k, 108 * k, sw=W_THIN)
    sh.rect(*P(bx - 45, by + 50), 90 * k, 100 * k, sw=W_THICK)
    sh.text(*P(bx, by + 30), 'CHỐT', size=3, anchor='middle', weight='bold')
    for (cx, cy), lab in ((CAB_IN, 'TỦ VÀO'), (CAB_OUT, 'TỦ RA')):
        sh.rect(*P(cx - 25, cy + 30), 50 * k, 60 * k, sw=W_THICK)
        sh.text(*P(cx, cy + 14), lab, size=2.4, anchor='middle')
    for pv, post, d in ((PIVOT_IN, POST_IN, 1), (PIVOT_OUT, POST_OUT, -1)):
        x0, x1 = sorted((pv[0], post[0]))
        sh.rect(*P(x0, pv[1] + 2), (x1 - x0) * k, 4 * k, sw=W_THIN, kind='phantom')
        sh.circle(*P(*post), 2.5 * k, sw=W_THICK); sh.cross(*P(*post), 2.5 * k)
    for c in (CAM_IN, CAM_OUT):
        sh.circle(*P(*c), 10 * k, sw=W_THIN); sh.circle(*P(*c), 6 * k, sw=W_THICK); sh.cross(*P(*c), 6 * k)
    # lỗ đi dây xuyên đế (và đảo)
    holes = [('H1', BOOTH_C, 8, 'Ø16 – chốt'), ('H2', CAB_IN, 6, 'Ø12 – tủ vào'), ('H3', CAB_OUT, 6, 'Ø12 – tủ ra'),
             ('H4', CAM_IN, 4, 'Ø8 – cột camera vào'), ('H5', CAM_OUT, 4, 'Ø8 – cột camera ra')]
    for name, (hx, hy), r, _ in holes:
        sh.circle(*P(hx, hy), r * k, sw=W_THICK, fill='#fff'); sh.cross(*P(hx, hy), r * k)
    # kích thước toạ độ (ghi theo gốc O, phương pháp toạ độ)
    sh.text(ox - 4.5, oy + 4, 'O', size=3, weight='bold')
    sh.ordx(ox, oy + 1, oy + 6, [0, 85, 90, 240, 250, 271, 290, 309, 330, 340, 415, 490, 495, 560], k, size=2.2)
    sh.ordy(oy, ox - 1, ox - 6, [0, 60, 73, 85, 95, 191, 215, 355, 365, 377, 390, 450], k, size=2.2)
    # bảng toạ độ
    cols = [('Ký hiệu', 12), ('Chi tiết', 34), ('X', 9), ('Y', 9), ('Ghi chú', 21)]
    rows = [['C', 'Tâm chốt', '290', '215', '90 × 100'], ['T1', 'Tâm tủ barie vào', '309', '355', '50 × 60'],
            ['T2', 'Tâm tủ barie ra', '271', '95', '50 × 60'], ['S1', 'Trục servo vào', '347', '365', 'cao 85'],
            ['S2', 'Trục servo ra', '233', '85', 'cao 85'], ['K1', 'Cột camera vào', '330', '73', 'Ø12'],
            ['K2', 'Cột camera ra', '250', '377', 'Ø12'], ['D1', 'Cột đỡ cần vào', '495', '365', 'Ø5'],
            ['D2', 'Cột đỡ cần ra', '85', '85', 'Ø5'], ['B', 'Biển số xe vào khi dừng', '415', '191', 'cao 58']]
    sh.text(328, 13, 'TOẠ ĐỘ TÂM CÁC CHI TIẾT (gốc O)', size=3, weight='bold')
    y = sh.table(328, 16, cols, rows, rh=5, size=2.4)
    cols2 = [('Lỗ', 8), ('Ø', 9), ('Vị trí', 22), ('Dây đi qua', 46)]
    rows2 = [['H1', 'Ø16', 'tâm chốt', 'SPI ×2, loa, còi, LED, IR ×2'], ['H2', 'Ø12', 'tâm tủ vào', 'servo, IR an toàn'],
             ['H3', 'Ø12', 'tâm tủ ra', 'servo, IR an toàn'], ['H4', 'Ø8', 'tâm cột K1', '5 V, GND camera + đèn'],
             ['H5', 'Ø8', 'tâm cột K2', '5 V, GND camera + đèn']]
    sh.text(328, y + 7, 'LỖ ĐI DÂY XUYÊN ĐẢO VÀ MẶT ĐẾ', size=3, weight='bold')
    y = sh.table(328, y + 10, cols2, rows2, rh=5, size=2.4)
    notes(sh, 328, y + 8, 'GHI CHÚ', [
        'Vạch làn rộng 3, vạch dừng rộng 5, màu trắng; ô cấm dừng gạch chéo 45° bước 10, màu vàng.',
        'Khoan lỗ H1–H5 xuyên cả đảo (15) và mặt đế (5) trước khi dán đảo.',
        'Vạch dừng làn vào đặt cách trục barie 5 mm về phía đường.',
        'Vỉa hè cao 8, đảo cao 15 so với mặt đường.',
    ], size=2.4, width=85)
    return sh

# =====================================================================================
# BV-03  ĐẾ VÀ KHOANG ĐIỆN
# =====================================================================================
def bv03():
    sh = sheet(3, 'ĐẾ MÔ HÌNH VÀ KHOANG ĐIỆN', '1:4', 'Formex 5 mm, MDF 3 mm')
    k = 0.25
    # ---- hình chiếu bằng nhìn từ dưới lên (đã tháo đáy) ----
    ox, oy = 34, 150
    P = lambda X, Y: (ox + X * k, oy - Y * k)
    sh.label(ox + 70, 22, 'KHUNG ĐẾ – NHÌN TỪ TRÊN, ĐÃ BỎ MẶT ĐẾ')
    sh.rect(*P(0, 450), 560 * k, 450 * k, sw=0.7)
    sh.rect(*P(5, 445), 550 * k, 440 * k, sw=W_THIN)      # mép trong khung 5 mm
    # sườn tăng cứng
    for X in (180, 400):
        sh.rect(*P(X - 2.5, 445), 5 * k, 440 * k, sw=W_THICK)
        for Y in (120, 330):
            sh.rect(*P(X - 2.5, Y + 12), 5 * k, 24 * k, sw=W_THIN, fill='#fff')
    # bo mạch, mạch hạ áp, lỗ đi dây
    bx, by = BOOTH_C[0], 220
    sh.rect(*P(bx - 35, by + 45), 70 * k, 90 * k, sw=W_THICK)
    sh.text(*P(bx, by + 2), 'BO CHÍNH', size=2.2, anchor='middle')
    sh.text(*P(bx, by - 8), '70 × 90', size=2.2, anchor='middle')
    sh.rect(*P(126, 446), 27 * k, 63 * k, sw=W_THICK)
    sh.text(*P(139, 400), 'HẠ ÁP', size=2, anchor='middle')
    for (hx, hy), r in ((BOOTH_C, 8), (CAB_IN, 6), (CAB_OUT, 6), (CAM_IN, 4), (CAM_OUT, 4)):
        sh.circle(*P(hx, hy), r * k, sw=W_THIN); sh.cross(*P(hx, hy), r * k)
    # chân cao su
    for X, Y in ((30, 30), (530, 30), (30, 420), (530, 420)):
        sh.circle(*P(X, Y), 10 * k, sw=W_THIN, kind='hidden')
    sh.dh(ox, ox + 560 * k, oy, 6, '560')
    sh.dv(ox + 560 * k, oy - 450 * k, oy, 6, '450')
    sh.dh(ox, ox + 180 * k, oy - 450 * k, -4, '180'); sh.dh(ox, ox + 400 * k, oy - 450 * k, -9, '400')
    sh.dh(ox + 255 * k, ox + 325 * k, oy - 265 * k, -3, '70')
    sh.dv(ox + 255 * k, oy - 265 * k, oy - 175 * k, -3, '90')
    sh.leader(ox + 180 * k, oy - 120 * k, ox + 30, oy - 20, 'Sườn 5 × 40, rãnh dây 24 × 15', size=2.4)
    sh.leader(ox + 30 * k, oy - 30 * k, ox + 6, oy + 14, '4 chân cao su Ø20', size=2.4)
    # ---- mặt cắt A-A (dọc theo trục X qua tâm chốt) ----
    ax, ay = 34, 196
    k2 = 0.25
    sh.label(ax + 70, ay - 22, 'MẶT CẮT A–A')
    Q = lambda X, Z: (ax + X * k2, ay - Z * k2)
    sh.hatch(*Q(0, 0), 560 * k2, 5 * k2, step=0.8); sh.rect(*Q(0, 0), 560 * k2, 5 * k2, sw=W_THICK)
    sh.hatch(*Q(0, -45), 560 * k2, 3 * k2, step=0.8); sh.rect(*Q(0, -45), 560 * k2, 3 * k2, sw=W_THICK)
    for X0 in (0, 555): sh.hatch(*Q(X0, -5), 5 * k2, 40 * k2, step=0.8); sh.rect(*Q(X0, -5), 5 * k2, 40 * k2, sw=W_THICK)
    for X in (180, 400): sh.rect(*Q(X - 2.5, -5), 5 * k2, 40 * k2, sw=W_THICK)
    sh.rect(*Q(255, -32), 70 * k2, 1.6 * k2, sw=W_THICK)
    sh.rect(*Q(240, 15), 100 * k2, 15 * k2, sw=W_THIN)
    sh.dv(ax, ay, ay + 48 * k2, -5, '48')
    sh.dv(ax + 560 * k2, ay - 0, ay - 5 * k2, 9, '5')
    sh.dv(ax + 560 * k2, ay + 45 * k2, ay + 48 * k2, 4, '3')
    # vị trí mặt cắt trên hình chiếu bằng
    sh.line(ox - 6, oy - 220 * k, ox + 560 * k + 2, oy - 220 * k, kind='center')
    sh.text(ox - 7, oy - 220 * k - 1.5, 'A', size=3.2, weight='bold'); sh.text(ox + 560 * k + 1, oy - 220 * k + 4, 'A', size=3.2, weight='bold')
    # ---- mặt sau đế: lỗ jack, công tắc, cổng USB (tỉ lệ 1:1) ----
    rx, ry = 200, 40
    sh.label(rx + 45, ry - 10, 'MẶT SAU ĐẾ – CHI TIẾT LỖ KHOÉT (1:1)')
    sh.rect(rx, ry, 120, 40, sw=W_THICK)
    sh.text(rx + 60, ry + 46, 'Tấm khung sau (phía bãi), dày 5, cao 40', size=2.5, anchor='middle')
    # jack DC
    jx = rx + 20; sh.circle(jx, ry + 20, 4, sw=W_THICK); sh.cross(jx, ry + 20, 4); sh.diam(jx, ry + 20, 4, 'Ø8 – jack DC 5,5/2,1', ang=-50, lead=9)
    # công tắc
    sx = rx + 50; sh.rect(sx - 9.5, ry + 13.5, 19, 13, sw=W_THICK); sh.cross(sx, ry + 20, 0)
    sh.dh(sx - 9.5, sx + 9.5, ry + 13.5, -4, '19'); sh.dv(sx + 9.5, ry + 13.5, ry + 26.5, 4, '13')
    # USB nối dài
    ux = rx + 95; sh.rect(ux - 6, ry + 16.5, 12, 7, sw=W_THICK, rx=1)
    for dxh in (-14, 14): sh.circle(ux + dxh, ry + 20, 1.6, sw=W_THICK); sh.cross(ux + dxh, ry + 20, 1.6)
    sh.dh(ux - 14, ux + 14, ry + 20, -9, '28'); sh.dh(ux - 6, ux + 6, ry + 23.5, 4, '12')
    sh.leader(ux - 14, ry + 20, ux - 30, ry + 33, '2 lỗ Ø3,2 bắt cổng USB nối dài', size=2.3)
    sh.dh(rx, jx, ry + 40, 5, '20'); sh.dh(rx, sx, ry + 40, 10, '50'); sh.dh(rx, ux, ry + 40, 15, '95')
    sh.dv(rx + 120, ry + 20, ry + 40, 5, '20')
    sh.text(rx, ry - 2, 'Gốc đo: mép trái tấm khung sau; khoảng cách X tính từ X = 120 trên mặt bằng', size=2.2)
    # ---- nắp thăm ----
    nx, ny = 200, 115
    sh.label(nx + 45, ny - 8, 'NẮP THĂM DƯỚI ĐÁY (1:2)')
    sh.rect(nx, ny, 110 * 0.5 + 30, 130 * 0.5 + 10, sw=W_THIN, kind='phantom')
    sh.rect(nx + 15, ny + 5, 55, 65, sw=W_THICK)
    for dx_, dy_ in ((4, 4), (51, 4), (4, 61), (51, 61)):
        sh.circle(nx + 15 + dx_, ny + 5 + dy_, 1.6 * 0.5 * 2, sw=W_THICK); sh.cross(nx + 15 + dx_, ny + 5 + dy_, 1.6)
    sh.dh(nx + 15, nx + 70, ny + 70, 6, '110'); sh.dv(nx + 70, ny + 5, ny + 70, 6, '130')
    sh.text(nx + 42, ny + 40, 'Khoét đáy 110 × 130', size=2.3, anchor='middle')
    sh.text(nx + 42, ny + 44, 'tâm tại X 290, Y 220', size=2.3, anchor='middle')
    sh.leader(nx + 19, ny + 9, nx + 30, ny + 18, '4 vít M3 × 8', size=2.3)
    notes(sh, 200, 205, 'GHI CHÚ', [
        'Mặt đế Formex 5 mm 560 × 450; khung bao và 2 sườn Formex 5 mm cao 40, dán keo + vít M3 × 12 mỗi 100 mm.',
        'Đáy MDF 3 mm bắt vít M3 × 8 vào khung, có nắp thăm 110 × 130 dưới bo chính để thay thẻ nhớ DFPlayer.',
        'Rãnh đi dây trên sườn: 24 × 15, cạnh dưới cách đáy 0 (dây nằm trên đáy).',
        'Mạch hạ áp đặt sát mặt sau, jack DC thò qua lỗ Ø8; nguồn 12 V vào → 5 V ra cầu đấu bo chính bằng dây 20 AWG.',
        'Bo chính bắt 4 trụ đồng M3 × 6 xuống đáy, ngay dưới chốt để dây SPI tới RC522 ngắn hơn 20 cm.',
    ], size=2.5, width=200)
    return sh

# =====================================================================================
# Dụng cụ vẽ chung cho các cụm
# =====================================================================================
def ortho(sh, boxes, view, ox, oy, k, glass=()):
    """boxes: (tên, u0,u1, v0,v1, h0,h1[, kiểu]) hệ toạ độ cục bộ; view: front (ngang u, đứng h, nhìn từ −v),
    side (ngang −v… nhìn từ −u: ngang = v đảo), top (ngang u, đứng v)."""
    if view == 'front': order = sorted(boxes, key=lambda b: -b[3])
    elif view == 'side': order = sorted(boxes, key=lambda b: -b[1])
    else: order = sorted(boxes, key=lambda b: b[6])
    for b in order:
        n, u0, u1, v0, v1, h0, h1 = b[:7]
        style = b[7] if len(b) > 7 else ''
        fill = 'none' if style == 'glass' else '#fff'
        sw = W_THIN if style in ('glass', 'thin') else W_THICK
        if view == 'front': a0, a1, c0, c1 = u0, u1, h0, h1
        elif view == 'side': a0, a1, c0, c1 = -v1, -v0, h0, h1
        else: a0, a1, c0, c1 = u0, u1, v0, v1
        sh.rect(ox + a0 * k, oy - c1 * k, (a1 - a0) * k, (c1 - c0) * k, sw=sw, fill=fill)

def panel(sh, x, y, w, h, k, name, qty, mat, feats=(), dims=True, note=None, outline=True):
    """Vẽ tấm phẳng (khai triển) gốc trái-dưới tại (x, y+h*k) theo tỉ lệ k. feats: ('hole', cx, cy, d) | ('slot', cx, cy, w, h) | ('mark', cx, cy, w, h, text) | ('rect', x0, y0, w, h)."""
    X = lambda u: x + u * k
    Y = lambda v: y + (h - v) * k
    if outline: sh.rect(x, y, w * k, h * k, sw=W_THICK)
    for f in feats:
        if f[0] == 'hole':
            _, cx, cy, d = f; sh.circle(X(cx), Y(cy), d / 2 * k, sw=W_THICK); sh.cross(X(cx), Y(cy), d / 2 * k)
        elif f[0] == 'slot':
            _, cx, cy, ww, hh = f; sh.rect(X(cx - ww / 2), Y(cy + hh / 2), ww * k, hh * k, sw=W_THICK, rx=min(ww, hh) * k / 2)
        elif f[0] == 'cut':
            _, cx, cy, ww, hh = f; sh.rect(X(cx - ww / 2), Y(cy + hh / 2), ww * k, hh * k, sw=W_THICK)
        elif f[0] == 'mark':
            _, cx, cy, ww, hh, t = f; sh.rect(X(cx - ww / 2), Y(cy + hh / 2), ww * k, hh * k, sw=W_THIN, kind='phantom')
            if t: sh.text(X(cx), Y(cy) + 1, t, size=2.2, anchor='middle')
    if dims:
        sh.k = k
        sh.dh(x, x + w * k, y + h * k, 5, fmt(w))
        sh.dv(x + w * k, y, y + h * k, 5, fmt(h))
    sh.text(x, y - 2.2, f'{name}  ×{qty}', size=2.9, weight='bold')
    sh.text(x, y - 5.6, mat, size=2.3) if False else None
    if note: sh.text(x + w * k / 2, y + h * k + 11, note, size=2.3, anchor='middle')
    return X, Y

# =====================================================================================
# BV-04  CHỐT NHÂN VIÊN – LẮP RÁP VÀ BỐ TRÍ LINH KIỆN
# =====================================================================================
BOOTH = [
    ('đế', -49, 49, -54, 54, 0, 6), ('vách', -45, 45, -50, 50, 6, 98),
    ('quầy', -58, -42, -22, 22, 98, 102), ('quầy', 42, 58, -22, 22, 98, 102),
    ('kính', -45, 45, -50, 50, 102, 196, 'glass'),
    ('trụ', -45, -41, -50, -46, 98, 196), ('trụ', 41, 45, -50, -46, 98, 196), ('trụ', -45, -41, 46, 50, 98, 196), ('trụ', 41, 45, 46, 50, 98, 196),
    ('mái', -53, 53, -58, 58, 196, 202), ('biển', -54, 54, -59, 59, 202, 218),
]
def bv04():
    sh = sheet(4, 'CHỐT NHÂN VIÊN – LẮP RÁP VÀ BỐ TRÍ LINH KIỆN', '1:2', 'Mica 3 mm, mica trong 2 mm')
    k = 0.5
    fx, fy = 84, 135          # hình chiếu đứng (nhìn từ đường)
    ortho(sh, BOOTH, 'front', fx, fy, k)
    # chi tiết trên vách trước: lưới loa, lỗ còi
    for i in range(12):
        cx = -27.5 + i * 5
        sh.rect(fx + (cx - 1) * k, fy - 47 * k, 2 * k, 22 * k, sw=W_THIN, rx=0.5)
    sh.circle(fx - 25 * k, fy - 78 * k, 3 * k, sw=W_THIN); sh.cross(fx - 25 * k, fy - 78 * k, 3 * k)
    sh.text(fx, fy - 210 * k, 'BÃI GIỮ XE · PARKING', size=2.4, anchor='middle', weight='bold')
    sh.label(fx, 14, 'HÌNH CHIẾU ĐỨNG')
    sh.k = k
    sh.dh(fx - 49 * k, fx + 49 * k, fy, 6, '98'); sh.dh(fx - 58 * k, fx + 58 * k, fy, 11, '116'); sh.dh(fx - 54 * k, fx + 54 * k, fy - 218 * k, -4, '108')
    for h, off in ((6, -6), (98, -11), (196, -16), (218, -21)):
        sh.dv(fx - 54 * k, fy - h * k, fy, off, str(h))
    sh.dv(fx + 58 * k, fy - 102 * k, fy - 98 * k, 5, '4')
    # hình chiếu cạnh (nhìn từ trái = từ làn ra), đặt bên phải
    sx, sy = 180, 135
    ortho(sh, BOOTH, 'side', sx, sy, k)
    sh.rect(sx - 32 * k, sy - 90 * k, 64 * k, 44 * k, sw=W_THIN, kind='phantom')
    sh.text(sx, sy - 66 * k, 'mặt quẹt thẻ', size=2.2, anchor='middle')
    sh.circle(sx, sy - 94 * k, 2.5 * k, sw=W_THIN); sh.cross(sx, sy - 94 * k, 2.5 * k)
    sh.rect(sx - 7.5 * k, sy - 15.5 * k, 15 * k, 7 * k, sw=W_THIN, rx=1)
    sh.line(sx - 18 * k, sy - 102 * k, sx - 18 * k, sy - 196 * k, w=W_THIN); sh.line(sx + 18 * k, sy - 102 * k, sx + 18 * k, sy - 196 * k, w=W_THIN)
    sh.label(sx, 14, 'HÌNH CHIẾU CẠNH')
    sh.k = k
    sh.dh(sx - 50 * k, sx + 50 * k, sy, 6, '100'); sh.dh(sx - 18 * k, sx + 18 * k, sy - 150 * k, 0, '36')
    sh.dh(sx - 32 * k, sx + 32 * k, sy - 46 * k, 3, '64')
    sh.dv(sx + 50 * k, sy - 68 * k, sy, 6, '68'); sh.dv(sx + 50 * k, sy - 94 * k, sy, 12, '94'); sh.dv(sx + 50 * k, sy - 12 * k, sy, 18, '12')
    sh.leader(sx, sy - 94 * k, sx + 34, sy - 70, 'lỗ Ø5 LED WS2812', size=2.3)
    sh.leader(sx + 7 * k, sy - 12 * k, sx + 34, sy - 4, 'khe 15 × 7 IR xe tới', size=2.3)
    sh.leader(sx + 10 * k, sy - 150 * k, sx + 34, sy - 92, 'cửa đưa thẻ rộng 36', size=2.3)
    # hình chiếu bằng
    tx, ty = 84, 218
    ortho(sh, BOOTH, 'top', tx, ty, k)
    sh.rect(tx - 45 * k, ty - 50 * k, 90 * k, 100 * k, sw=W_THIN, kind='hidden')
    sh.label(tx, 162, 'HÌNH CHIẾU BẰNG')
    sh.k = k
    sh.dh(tx - 53 * k, tx + 53 * k, ty + 58 * k, 5, '106'); sh.dv(tx + 53 * k, ty - 58 * k, ty + 58 * k, 5, '116')
    # mặt cắt D-D: nhìn từ trong ra vách trước, thấy linh kiện
    dx, dy = 180, 232
    sh.label(dx, 162, 'MẶT CẮT D–D (nhìn vào vách trước)')
    sh.rect(dx - 49 * k, dy - 6 * k, 98 * k, 6 * k, sw=W_THICK)
    for s_ in (-1, 1):
        x0 = dx + (s_ * 45 - (3 if s_ > 0 else 0)) * k
        sh.hatch(x0, dy - 98 * k, 3 * k, 92 * k, step=0.7); sh.rect(x0, dy - 98 * k, 3 * k, 92 * k, sw=W_THICK)
        # RC522 sát vách (nhìn cạnh)
        rx_ = dx + s_ * 41 * k - (1.6 * k if s_ > 0 else 0)
        sh.rect(rx_, dy - 88 * k, 1.6 * k, 40 * k, sw=W_THICK, fill='#fff')
        # IR xe tới
        sh.rect(dx + (s_ * 45 - (31 if s_ > 0 else 0)) * k, dy - 13 * k, 31 * k, 1.6 * k, sw=W_THICK, fill='#fff')
        # WS2812
        sh.rect(dx + (s_ * 42 - (1.2 if s_ > 0 else 0)) * k, dy - 99 * k, 1.2 * k, 10 * k, sw=W_THICK, fill='#fff')
    sh.rect(dx - 45 * k, dy - 98 * k, 90 * k, 92 * k, sw=W_THIN)          # vách trước phía sau
    sh.rect(dx - 35 * k, dy - 51.5 * k, 70 * k, 31 * k, sw=W_THICK, fill='#fff')   # loa
    sh.circle(dx, dy - 36 * k, 12 * k, sw=W_THIN)
    sh.rect(dx + (-25 - 17) * k, dy - 84.5 * k, 34.3 * k, 13.3 * k, sw=W_THICK, fill='#fff')  # còi
    sh.circle(dx - 25 * k, dy - 78 * k, 6 * k, sw=W_THIN)
    sh.circle(dx, dy - 3 * k, 8 * k, sw=W_THIN, kind='hidden')
    B = sh.balloon
    B(dx + 41 * k, dy - 68 * k, dx + 32, dy - 52, '11')
    B(dx + 30 * k, dy - 36 * k, dx + 32, dy - 30, '14')
    B(dx - 25 * k, dy - 78 * k, dx - 32, dy - 52, '15')
    B(dx - 30 * k, dy - 12 * k, dx - 36, dy - 8, '13')
    B(dx + 42 * k, dy - 94 * k, dx + 32, dy - 62, '16')
    sh.k = k
    sh.dv(dx + 49 * k, dy - 36 * k, dy, 14, '36'); sh.dv(dx + 49 * k, dy - 78 * k, dy, 20, '78')
    sh.dh(dx - 25 * k, dx, dy - 98 * k, -4, '25')
    # bảng bố trí linh kiện
    cols = [('VT', 7), ('Linh kiện', 30), ('Gắn vào', 30), ('Toạ độ / cách gắn', 50)]
    rows = [['11', 'RC522 (×2)', 'mặt trong 2 vách bên', 'tâm cao 68, giữa vách; băng keo xốp 2 mặt dày 1, mặt anten áp vách'],
            ['16', 'WS2812 Ø10 (×2)', 'mặt trong 2 vách bên', 'tâm lỗ Ø5 cao 94, giữa vách; keo nến'],
            ['13', 'IR FC-51 xe tới (×2)', 'chân 2 vách bên', 'LED thò qua khe 15 × 7 cao 12; bắt 1 vít M3 vào ke'],
            ['14', 'Loa 3 W', 'mặt trong vách trước', 'tâm cao 36, giữa vách; băng keo xốp 2 mặt quanh viền loa'],
            ['15', 'Module còi', 'mặt trong vách trước', 'lỗ Ø6 tâm cao 78, lệch trái 25; còi áp lỗ'],
            ['—', 'Bó dây', 'sàn chốt', 'xuống đế qua lỗ H1 Ø16 tại tâm']]
    sh.text(250, 13, 'BỐ TRÍ LINH KIỆN TRONG CHỐT', size=3.2, weight='bold')
    y = sh.table(250, 16, cols, rows, rh=5, size=2.45)
    notes(sh, 250, y + 8, 'YÊU CẦU KỸ THUẬT', [
        'Kích thước cao tính từ mặt đảo. Hình chiếu cạnh nhìn từ làn ra; vách bên làn vào đối xứng.',
        'Vách dưới mica xám 3 mm dán hộp; vách sau bắt 4 vít M3 vào ke góc để mở bảo trì.',
        'Kính mica trong 2 mm kẹp giữa 4 trụ nhôm vuông 4 × 4; mỗi vách bên chừa cửa đưa thẻ rộng 36.',
        'RC522 đọc xuyên mica 3 mm tới khoảng 25–30 mm: không dán kim loại, giấy bạc lên vùng mặt quẹt thẻ.',
        'Mặt quẹt thẻ 64 × 44 in decal đen, viền xanh, chữ QUẸT THẺ; tâm trùng tâm RC522.',
    ], size=2.5, width=160)
    return sh

# =====================================================================================
# BV-05  CHỐT – KHAI TRIỂN TẤM MICA (1:1, in đúng tỉ lệ để làm dưỡng cắt)
# =====================================================================================
def bv05():
    sh = sheet(5, 'CHỐT NHÂN VIÊN – KHAI TRIỂN TẤM CẮT MICA', '1:1', 'Mica 3 mm, mica trong 2 mm')
    k = 1
    slots = [('slot', 45 - 27.5 + i * 5, 30, 2, 22) for i in range(12)]
    X, Y = panel(sh, 26, 22, 90, 92, k, 'P1 – Vách trước', 1, '', slots + [('hole', 20, 72, 6), ('mark', 45, 30, 70, 31, '')])
    sh.k = 1; sh.dv(X(20), Y(72), Y(0), -9, '72'); sh.dv(X(10), Y(30), Y(0), -4, '30')
    sh.text(X(45), Y(12), 'viền loa 70 × 31 (mặt trong)', size=2.2, anchor='middle')
    sh.dh(X(0), X(20), Y(72), -8, '20')
    sh.leader(X(45), Y(41), X(52), Y(85), '12 khe 2 × 22, bước 5', size=2.3)
    X, Y = panel(sh, 132, 22, 90, 92, k, 'P2 – Vách sau (tháo được)', 1, '', [('hole', 5, 5, 3.2), ('hole', 85, 5, 3.2), ('hole', 5, 87, 3.2), ('hole', 85, 87, 3.2)])
    sh.leader(X(85), Y(87), X(60), Y(70), '4 lỗ Ø3,2 cách mép 5', size=2.3)
    X, Y = panel(sh, 238, 22, 94, 92, k, 'P3 – Vách bên làn ra (P4 làn vào: đối xứng)', 2, '',
                 [('mark', 47, 62, 64, 44, ''), ('mark', 47, 62, 60, 40, 'RC522 60 × 40 (mặt trong)'), ('hole', 47, 88, 5), ('slot', 47, 6, 15, 7)])
    sh.k = 1; sh.dv(X(94), Y(62), Y(0), 12, '62'); sh.dv(X(94), Y(88), Y(0), 18, '88'); sh.dh(X(0), X(47), Y(0), 11, '47')
    sh.dh(X(15), X(79), Y(40), 4, '64')
    # hàng 2
    X, Y = panel(sh, 26, 140, 82, 94, k, 'K1 – Kính trước, sau', 2, '')
    X, Y = panel(sh, 124, 140, 28, 94, k, 'K2 – Kính bên', 4, '')
    X, Y = panel(sh, 168, 140, 16, 44, k, 'Q – Quầy', 2, '')
    k2 = 0.5
    X, Y = panel(sh, 200, 140, 98, 108, k2, 'Đ – Đế chốt (vẽ 1:2)', 1, '', [('hole', 49, 54, 16)])
    sh.k = k2; sh.diam(X(49), Y(54), 8 * k2, 'Ø16', ang=30, lead=8)
    X, Y = panel(sh, 270, 140, 106, 116, k2, 'M – Mái (vẽ 1:2)', 1, '')
    # bảng cắt vật liệu
    cols = [('Ký hiệu', 14), ('Tên tấm', 30), ('Kích thước', 22), ('SL', 7), ('Vật liệu', 32)]
    rows = [['P1', 'Vách trước', '90 × 92', '1', 'Mica xám 3'], ['P2', 'Vách sau', '90 × 92', '1', 'Mica xám 3'],
            ['P3, P4', 'Vách bên', '94 × 92', '2', 'Mica xám 3'], ['K1', 'Kính trước, sau', '82 × 94', '2', 'Mica trong 2'],
            ['K2', 'Kính bên', '28 × 94', '4', 'Mica trong 2'], ['Q', 'Quầy', '16 × 44', '2', 'Mica xám 3'],
            ['Đ', 'Đế chốt', '98 × 108', '1', 'Formex 6 (2 × 3)'], ['M', 'Mái', '106 × 116', '1', 'Mica xám 3 + Formex 3'],
            ['B', 'Viền biển tên', '108 × 16 / 112 × 16', '2 + 2', 'Mica xám 3, decal vàng'],
            ['T', 'Trụ góc', '4 × 4 × 98', '4', 'Nhôm hộp vuông 4 × 4']]
    sh.text(26, 254, 'BẢNG CẮT VẬT LIỆU – CHỐT', size=3.0, weight='bold')
    sh.table(26, 256, cols, rows[:5], rh=4.6, size=2.3)
    sh.table(140, 256, cols, rows[5:], rh=4.6, size=2.3, head=True)
    sh.text(26, 289, 'Bản vẽ in khổ A3, tỉ lệ 100 % để dùng làm dưỡng cắt cho các tấm vẽ 1:1. Kiểm tra bằng cạnh P1 = 90 mm trước khi cắt.', size=2.2)
    notes(sh, 335, 150, 'GHI CHÚ', ['Viền biển tên B: 2 tấm 108 × 16 và 2 tấm 112 × 16 dán thành khung quanh mái.',
                                    'Trụ góc T dài 98 (từ quầy tới mái), kính kẹp trong rãnh keo.'], size=2.3, width=75)
    return sh

# =====================================================================================
# BV-06  TỦ BARIE VÀ CẦN BARIE
# =====================================================================================
CAB = [('đế', -25, 25, -30, 30, 0, 6), ('vỏ', -25, 25, -30, 30, 6, 100), ('nắp', -27, 27, -32, 32, 100, 105)]
def bv06():
    sh = sheet(6, 'TỦ BARIE, CẦN BARIE VÀ CỘT ĐỠ – LÀN VÀO', '1:1, 1:2', 'Mica vàng 3 mm, mica trắng 4 mm')
    k = 0.5
    # hình chiếu nhìn từ phía làn (ngang = độ sâu v, phải = phía bãi)
    fx, fy = 52, 78
    for b in CAB:
        n, u0, u1, v0, v1, h0, h1 = b
        sh.rect(fx + v0 * k, fy - h1 * k, (v1 - v0) * k, (h1 - h0) * k, sw=W_THICK, fill='#fff')
    sh.rect(fx - 20.75 * k, fy - 74.25 * k, 41.5 * k, 20.5 * k, sw=W_THICK)         # lỗ khoét đầu servo
    sh.circle(fx + 10.3 * k, fy - 70 * k, 9 * k, sw=W_THICK, fill='#fff'); sh.cross(fx + 10.3 * k, fy - 70 * k, 9 * k)
    sh.rect(fx + (10.3 - 2) * k, fy - 74 * k, 4 * k, 8 * k, sw=W_THICK, fill='#fff')   # tiết diện cần 4 × 8
    for dv_ in (-24.75, 24.75):
        for dh_ in (-5, 5): sh.circle(fx + dv_ * k, fy - (70 + dh_) * k, 1.6 * k, sw=W_THIN)
    sh.rect(fx - 7.5 * k, fy - 15.5 * k, 15 * k, 7 * k, sw=W_THIN, rx=1)
    sh.label(fx, 14, 'NHÌN TỪ PHÍA LÀN (1:2)')
    sh.k = k
    sh.dh(fx - 32 * k, fx + 32 * k, fy, 6, '64'); sh.dv(fx + 32 * k, fy - 105 * k, fy, 6, '105')
    sh.dv(fx - 32 * k, fy - 70 * k, fy, -6, '70'); sh.dv(fx - 32 * k, fy - 12 * k, fy, -12, '12')
    sh.dh(fx, fx + 10.3 * k, fy - 105 * k, -4, '10,3')
    # hình chiếu cạnh (nhìn từ phía đường): ngang = u, phải = phía làn
    sx, sy = 132, 78
    for b in CAB:
        n, u0, u1, v0, v1, h0, h1 = b
        sh.rect(sx + u0 * k, sy - h1 * k, (u1 - u0) * k, (h1 - h0) * k, sw=W_THICK, fill='#fff')
    sh.rect(sx - 9 * k, sy - 89 * k, 18 * k, 18 * k, sw=W_THIN)
    sh.text(sx, sy - 77 * k, 'VÀO', size=2.6, anchor='middle', weight='bold')
    sh.rect(sx + 25 * k, sy - 79 * k, 4 * k, 18 * k, sw=W_THICK, fill='#fff')     # nắp trục
    sh.rect(sx + 29 * k, sy - 89 * k, 60 * k, 8 * k, sw=W_THICK, fill='#fff')     # cần (cắt lìa)
    bxk = sx + 89 * k
    sh.poly([(bxk, sy - 91 * k), (bxk + 1.2, sy - 87 * k), (bxk - 1.2, sy - 83 * k), (bxk, sy - 79 * k)], sw=W_THIN, close=False)
    sh.text(bxk + 3, sy - 84 * k, '… dài 150', size=2.4)
    sh.rect(sx + 25 * k, sy - 17 * k, 2 * k, 10 * k, sw=W_THIN)                  # đầu LED IR
    sh.label(sx + 10, 14, 'NHÌN TỪ PHÍA ĐƯỜNG (1:2)')
    sh.k = k
    sh.dh(sx - 27 * k, sx + 27 * k, sy, 6, '54'); sh.dv(sx - 27 * k, sy - 85 * k, sy, -6, '85')
    sh.dv(sx - 27 * k, sy - 100 * k, sy, -12, '100')
    # hình chiếu bằng
    tx, ty = 132, 125
    sh.rect(tx - 27 * k, ty - 32 * k, 54 * k, 64 * k, sw=W_THICK)
    sh.rect(tx + 25 * k, ty - (10.3 + 9) * k, 4 * k, 18 * k, sw=W_THICK)
    sh.rect(tx + 29 * k, ty - (10.3 + 2) * k, 60 * k, 4 * k, sw=W_THICK)
    sh.text(tx + 32, ty - 7, 'cần barie', size=2.3)
    sh.line(tx + 25 * k, ty - 32 * k - 3, tx + 25 * k, ty + 32 * k + 3, kind='center')
    sh.label(tx + 10, 103, 'HÌNH CHIẾU BẰNG (1:2)')
    sh.k = k
    sh.dh(tx - 27 * k, tx + 27 * k, ty + 32 * k, 5, '54'); sh.dv(tx - 27 * k, ty - 32 * k, ty + 32 * k, -5, '64')
    sh.dv(tx + 29 * k, ty - 10.3 * k, ty, 14, '10,3')
    # ---- khai triển tấm 1:1 ----
    k1 = 1
    feats = [('cut', 30, 64, 41.5, 20.5)] + [('hole', 30 + a, 64 + b, 3.2) for a in (-24.75, 24.75) for b in (-5, 5)] + [('slot', 30, 6, 15, 7)]
    X, Y = panel(sh, 180, 26, 60, 94, k1, 'C1 – Vách phía làn', 1, '', feats)
    sh.k = 1; sh.dv(X(60), Y(64), Y(0), 12, '64'); sh.dh(X(5.25), X(54.75), Y(69), -8, '49,5'); sh.dv(X(0), Y(69), Y(59), -4, '10')
    sh.dh(X(9.25), X(50.75), Y(53.75), 4, '41,5'); sh.dv(X(50.75), Y(74.25), Y(53.75), 9, '20,5')
    sh.leader(X(30), Y(6), X(36), Y(22), 'khe 15 × 7 IR an toàn', size=2.3)
    X, Y = panel(sh, 258, 26, 60, 94, k1, 'C2 – Vách phía đảo (tháo được)', 1, '', [('hole', 4, 4, 3.2), ('hole', 56, 4, 3.2), ('hole', 4, 90, 3.2), ('hole', 56, 90, 3.2)])
    X, Y = panel(sh, 336, 26, 44, 94, k1, 'C3, C4 – Vách trước, sau', 2, '', [('mark', 22, 74, 36, 18, 'decal VÀO')])
    X, Y = panel(sh, 180, 148, 54, 64, k1, 'C5 – Nắp', 1, '')
    X, Y = panel(sh, 250, 148, 50, 60, k1, 'C6 – Đế cao su', 1, '', [('hole', 25, 30, 12)])
    # cần barie 150 × 8
    ax, ay = 30, 222
    sh.text(ax, ay - 15, 'CB – Cần barie ×2  (mica trắng 4 mm, 1:1)', size=2.9, weight='bold')
    sh.rect(ax, ay, 150, 8, sw=W_THICK)
    for i in range(1, 8): sh.rect(ax + 20 * i - 10, ay, 10, 8, sw=W_THIN, fill='#ddd')
    for xh in (5, 13): sh.circle(ax + xh, ay + 4, 1.1, sw=W_THICK); sh.cross(ax + xh, ay + 4, 1.1)
    sh.rect(ax + 150, ay - 1, 8, 10, sw=W_THICK)
    sh.k = 1; sh.dh(ax, ax + 150, ay + 8, 6, '150'); sh.dh(ax, ax + 13, ay, -4, '13'); sh.dh(ax, ax + 5, ay, -9, '5')
    sh.dv(ax + 158, ay - 1, ay + 9, 4, '10'); sh.dh(ax + 150, ax + 158, ay + 9, 12, '8')
    sh.text(ax + 75, ay + 22, 'Sọc đỏ decal 10 × 8 bước 20; 2 lỗ Ø2,2 bắt vít M2 vào cánh tay servo; đầu cao su đỏ 8 × 10 × 6', size=2.3, anchor='middle')
    # cột đỡ đầu cần
    px_, py_ = 338, 160
    sh.text(px_, py_ - 3, 'CĐ – Cột đỡ ×2 (1:1)', size=2.9, weight='bold')
    sh.rect(px_ + 10 - 2.5, py_ + 9, 5, 64 * 0.5, sw=W_THICK)
    sh.text(px_ + 16, py_ + 30, 'que inox Ø5 × 64 (vẽ 1:2)', size=2.2)
    sh.poly([(px_ + 6, py_), (px_ + 6, py_ + 9), (px_ + 14, py_ + 9), (px_ + 14, py_), (px_ + 12.5, py_), (px_ + 12.5, py_ + 5), (px_ + 7.5, py_ + 5), (px_ + 7.5, py_)], sw=W_THICK)
    sh.k = 1; sh.dh(px_ + 7.5, px_ + 12.5, py_, -3, '5'); sh.dv(px_ + 14, py_, py_ + 9, 3, '9')
    notes(sh, 252, 222, 'GHI CHÚ', [
        'Tủ làn ra đối xứng gương qua mặt phẳng dọc tâm đảo; decal RA.',
        'Lỗ bắt servo: khoảng cách lỗ servo cỡ chuẩn 49,5 × 10; lấy dấu lại theo tai servo thật trước khi khoan.',
        'Đẩy đầu servo qua lỗ khoét, bắt 4 vít M3 × 12 + đai ốc; trục servo cao 85 so với mặt đường.',
        'Lắp cần ở vị trí servo 0° = cần nằm ngang; 90° = cần dựng đứng.',
        'Chỉnh biến trở IR an toàn để báo có vật trong khoảng 15 cm.',
    ], size=2.3, width=110)
    return sh

# =====================================================================================
# BV-07  CỘT CAMERA, HỘP CAMERA, ĐÈN CHIẾU BIỂN SỐ
# =====================================================================================
def bv07():
    sh = sheet(7, 'CỘT CAMERA, HỘP ESP32-CAM VÀ ĐÈN CHIẾU BIỂN SỐ', '1:1, 1:2', 'Ống nhôm Ø12, mica 2 mm')
    # ---- cụm lắp, nhìn ngang (1:1), chưa xoay góc ----
    ox, oy = 62, 140    # mặt đảo
    k = 1
    sh.label(ox + 10, 14, 'CỤM CỘT CAMERA (1:1)')
    sh.rect(ox - 10, oy - 3, 20, 3, sw=W_THICK)                                   # đế cột
    sh.rect(ox - 6, oy - 50, 12, 47, sw=W_THICK); sh.line(ox, oy + 2, ox, oy - 52, kind='center')
    sh.line(ox - 5, oy - 50, ox - 5, oy - 3, kind='hidden'); sh.line(ox + 5, oy - 50, ox + 5, oy - 3, kind='hidden')
    # khối nối vát 15°
    sh.poly([(ox - 4, oy - 50), (ox + 4, oy - 50), (ox + 4, oy - 57 + 1.07), (ox - 4, oy - 57 - 1.07)], sw=W_THICK)
    # hộp camera nghiêng 15°
    cx, cy = ox, oy - 82
    a = math.radians(15)
    def R(px, py):  # xoay quanh tâm hộp, chúc xuống về phía trước (+x)
        dx, dy = px - cx, py - cy
        return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)
    box_pts = [R(cx - 14, cy - 25), R(cx + 14, cy - 25), R(cx + 14, cy + 25), R(cx - 14, cy + 25)]
    sh.poly(box_pts, sw=W_THICK, fill='#fff')
    sh.poly([R(cx - 18, cy - 27), R(cx + 20, cy - 27), R(cx + 20, cy - 25), R(cx - 18, cy - 25)], sw=W_THICK, fill='#fff')
    sh.poly([R(cx + 4, cy - 20.5), R(cx + 5.6, cy - 20.5), R(cx + 5.6, cy + 20), R(cx + 4, cy + 20)], sw=W_THIN)   # bo ESP32-CAM
    lx, ly = R(cx + 14, cy - 6)
    sh.circle(lx, ly, 3.4, sw=W_THIN)
    e1 = R(cx + 14, cy - 6); e2 = R(cx + 70, cy - 6)
    sh.line(*e1, *e2, kind='center')
    sh.line(e1[0], e1[1], e1[0] + 55, e1[1], kind='center')
    sh.text(e1[0] + 40, e1[1] + 9, '15°', size=3)
    sh.text(e1[0] + 22, e1[1] - 2, 'trục ống kính', size=2.3)
    # tay đỡ đèn LED (lùi sau 30, cao 44 trên mặt đảo)
    sh.rect(ox - 36, oy - 46, 30, 4, sw=W_THICK); sh.rect(ox - 42, oy - 50.5, 6, 13, sw=W_THICK)
    sh.text(ox - 40, oy - 54, 'đèn LED', size=2.3, anchor='middle')
    sh.k = 1
    sh.dv(ox + 22, oy - 50, oy, 30, '50'); sh.dv(ox + 22, oy - 82, oy, 38, '82')
    sh.dv(ox - 44, oy - 44, oy, -6, '44'); sh.dh(ox - 36, ox - 6, oy, 8, '30')
    sh.dh(ox - 10, ox + 10, oy, 16, 'Ø20')
    sh.text(ox + 30, oy - 70, 'tâm ống kính cao 97', size=2.3)
    sh.text(ox + 30, oy - 66, 'so với mặt đường', size=2.3)
    # ---- nhìn từ phía biển số (1:1) ----
    fx, fy = 155, 140
    sh.label(fx, 14, 'NHÌN TỪ PHÍA BIỂN SỐ (1:1)')
    sh.rect(fx - 10, fy - 3, 20, 3, sw=W_THICK); sh.rect(fx - 6, fy - 50, 12, 47, sw=W_THICK)
    sh.rect(fx - 4, fy - 57, 8, 7, sw=W_THICK)
    sh.rect(fx - 17, fy - 107, 34, 50, sw=W_THICK, fill='#fff')
    sh.rect(fx - 15, fy - 105, 30, 46, sw=W_THIN)
    sh.rect(fx - 20, fy - 109, 40, 2, sw=W_THICK, fill='#fff')
    sh.rect(fx - 13.5, fy - 101, 27, 40.5, sw=W_THIN, kind='phantom')
    sh.circle(fx, fy - 88, 3.4, sw=W_THICK); sh.cross(fx, fy - 88, 3.4)
    sh.k = 1
    sh.dh(fx - 17, fx + 17, fy - 57, 5, '34'); sh.dv(fx + 17, fy - 107, fy - 57, 5, '50')
    sh.dh(fx - 15, fx + 15, fy - 105, -6, '30 (cửa sổ)'); sh.dh(fx - 20, fx + 20, fy - 109, -12, '40')
    sh.leader(fx - 13.5, fy - 70, fx - 40, fy - 62, 'ESP32-CAM 27 × 40,5', size=2.3, anchor='end')
    sh.leader(fx + 3, fy - 90, fx + 26, fy - 116, 'ống kính OV2640', size=2.3)
    # ---- sơ đồ góc nhìn (1:2) ----
    gx, gy = 30, 180
    sh.label(gx + 55, gy - 2, 'SƠ ĐỒ ĐẶT CAMERA LÀN VÀO (1:2)')
    k2 = 0.5
    cam = (gx + 10, gy + 70); plate = (cam[0] + 85 * k2, cam[1] - 118 * k2)
    sh.circle(*cam, 6 * k2, sw=W_THICK); sh.cross(*cam, 3)
    sh.rect(plate[0] - 11 * k2, plate[1] - 1, 22 * k2, 2, sw=W_THICK, fill='#000')
    sh.line(*cam, *plate, kind='center')
    sh.line(cam[0], cam[1], cam[0], cam[1] - 75, kind='center')
    sh.text(cam[0] + 3, cam[1] - 40, '35,8°', size=2.8)
    sh.text(cam[0] - 4, cam[1] + 4, 'K1 (330; 73)', size=2.3, anchor='end')
    sh.text(plate[0] + 8, plate[1] + 1, 'biển số sau (415; 191)', size=2.3)
    sh.k = k2
    sh.dh(cam[0], plate[0], cam[1], 6, '85'); sh.dv(plate[0], plate[1], cam[1], 14, '118')
    sh.text((cam[0] + plate[0]) / 2 - 12, (cam[1] + plate[1]) / 2, '145', size=2.8)
    # mặt cắt đứng theo tia nhìn
    vx, vy = gx + 105, gy + 70
    sh.line(vx, vy, vx + 145 * k2, vy, w=W_THIN)
    sh.line(vx, vy, vx, vy - 39 * k2 - 5, kind='center')
    sh.circle(vx, vy - 39 * k2, 1.5, sw=W_THICK)
    sh.rect(vx + 145 * k2 - 1, vy - 7 * k2 - 1, 2, 14 * k2, sw=W_THICK, fill='#000')
    sh.line(vx, vy - 39 * k2, vx + 145 * k2, vy, kind='center')
    sh.text(vx + 18, vy - 15, '15°', size=2.8)
    sh.k = k2
    sh.dv(vx, vy - 39 * k2, vy, -5, '39'); sh.dh(vx, vx + 145 * k2, vy, 6, '145')
    sh.text(vx + 36, vy - 26, 'cao 97 → biển cao 58', size=2.3, anchor='middle')
    # ---- khai triển tấm hộp camera (1:1) ----
    X, Y = panel(sh, 210, 26, 30, 50, 1, 'H1 – Sau', 1, '', [('hole', 15, 6, 4)])
    X, Y = panel(sh, 254, 26, 28, 50, 1, 'H2 – Bên', 2, '', [('mark', 7, 25, 2, 44, '')])
    sh.leader(X(7), Y(40), X(14), Y(46), 'rãnh 2 sâu 1 giữ bo', size=2.1)
    X, Y = panel(sh, 300, 26, 30, 26, 1, 'H3 – Đáy', 1, '', [('hole', 15, 13, 4)])
    X, Y = panel(sh, 344, 26, 30, 46, 1, 'H4 – Cửa sổ (trong)', 1, '')
    X, Y = panel(sh, 300, 92, 40, 38, 1, 'H5 – Mái che', 1, '')
    X, Y = panel(sh, 354, 92, 8, 8, 1, 'N – Khối nối', 1, '', [('hole', 4, 4, 4)])
    sh.text(354, 112, 'mặt trên vát 15°', size=2.2)
    X, Y = panel(sh, 210, 92, 20, 20, 1, 'Đ – Đế cột', 2, '', [('hole', 10, 10, 8)], dims=False, outline=False)
    sh.circle(X(10), Y(10), 10, sw=W_THICK)
    sh.k = 1; sh.dh(X(0), X(20), Y(0), 5, 'Ø20'); sh.diam(X(10), Y(10), 4, 'Ø8', ang=30, lead=6)
    X, Y = panel(sh, 252, 100, 30, 4, 1, 'T – Tay đỡ đèn 4 × 4', 2, '')
    notes(sh, 210, 150, 'GHI CHÚ', [
        'Ống nhôm Ø12 × 1, dài 47; dán vào đế Đ, dây 5 V + GND (và tín hiệu đèn) đi trong ống xuống lỗ H4/H5.',
        'Hộp camera ngoài 34 × 50 × 28, mica trắng 2 mm; cửa sổ mica trong 30 × 46; mái che xám 40 × 38 nhô trước 6.',
        'ESP32-CAM cắm đứng trong 2 rãnh của tấm H2, ống kính sát cửa sổ; tháo đế nạp MB, cấp 5 V qua chân 5V/GND.',
        'Dán băng đen che đèn flash có sẵn trên ESP32-CAM để không chói biển số.',
        'Xoay cột 35,8° về phía làn trước khi dán đế; khối nối N vát 15° cho camera chúc xuống.',
        'Đèn LED gắn trên tay đỡ T lùi sau camera 30, cao 44 so với mặt đảo; điều khiển qua transistor S8050 từ GPIO13 của ESP32-CAM.',
        'Biển số tỉ lệ 1:10 (19 × 14) chiếm khoảng 200 điểm ảnh ở độ phân giải 1600 × 1200 tại khoảng cách 145.',
    ], size=2.3, width=200)
    return sh

# =====================================================================================
# BV-08  BO MẠCH CHÍNH (PCB ĐỤC LỖ 70 × 90)
# =====================================================================================
ESP_L = ['CLK', 'SD0', 'SD1', '15', '2', '0', '4', '16', '17', '5', '18', '19', 'GND', '21', 'RX', 'TX', '22', '23', 'GND']
ESP_R = ['5V', 'GND', 'SD3', 'SD2', '13', 'GND', '12', '14', '27', '26', '25', '33', '32', '35', '34', '39', '36', 'EN', '3V3']
USED = {'4', '5', '13', '14', '16', '17', '18', '19', '23', '25', '26', '27', '34', '35', '36', '39', '5V', '3V3', 'GND'}
def bv08():
    sh = sheet(8, 'BO MẠCH CHÍNH – BỐ TRÍ LINH KIỆN TRÊN PCB ĐỤC LỖ', '2:1', 'PCB đục lỗ 2 mặt 70 × 90')
    k = 2
    ox, oy = 40, 222
    X = lambda u: ox + u * k
    Y = lambda v: oy - v * k
    col = lambda n: 3 + (n - 1) * 2.54
    sh.rect(X(0), Y(90), 70 * k, 90 * k, sw=0.7)
    for n in range(1, 27):
        for m in range(1, 35):
            sh.raw(f'<circle cx="{X(col(n)):.2f}" cy="{Y(col(m)):.2f}" r="0.45" fill="#bbb"/>')
    for (u, v) in ((3, 3), (67, 3), (3, 87), (67, 87)):
        pass
    sh.text(X(col(1)) - 1, Y(col(1)) + 5, 'A1', size=2.2)
    # ESP32 38 chân trên 2 hàng header cái, cổng USB ra mép trên
    sh.rect(X(19.5), Y(88.9), 28 * k, 55 * k, sw=W_THICK, fill='none', kind='phantom')
    sh.rect(X(27.5), Y(90.6), 12 * k, 6 * k, sw=W_THIN)
    sh.text(X(33.5), Y(91.5), 'USB', size=2.4, anchor='middle')
    sh.text(X(33.5), Y(62), 'ESP32 DevKit', size=2.6, anchor='middle', weight='bold')
    sh.text(X(33.5), Y(58.5), '38 chân', size=2.4, anchor='middle', weight='bold')
    for i in range(19):
        yy = col(33 - i)
        for c, lab, side in ((8, ESP_L[i], -1), (18, ESP_R[i], 1)):
            used = lab in USED
            sh.rect(X(col(c)) - 1.9, Y(yy) - 1.9, 3.8, 3.8, sw=W_THIN, fill='#222' if used else '#fff')
            sh.text(X(col(c)) + side * 3.2, Y(yy) + 0.9, lab, size=2.0, anchor='start' if side > 0 else 'end', weight='bold' if used else 'normal')
    # DFPlayer
    sh.rect(X(47.6), Y(34.6), 20 * k, 20 * k, sw=W_THICK, kind='phantom')
    sh.text(X(57.6), Y(25.3), 'DFPlayer', size=2.5, anchor='middle', weight='bold')
    DF_L = ['VCC', 'RX', 'TX', 'DACR', 'DACL', 'SPK1', 'GND', 'SPK2']; DF_R = ['BUSY', 'USB−', 'USB+', 'AD2', 'AD1', 'IO2', 'GND', 'IO1']
    for i in range(8):
        yy = col(13 - i)
        for c, lab, side in ((19, DF_L[i], 1), (26, DF_R[i], -1)):
            used = lab in ('VCC', 'RX', 'TX', 'SPK1', 'SPK2', 'GND')
            sh.rect(X(col(c)) - 1.9, Y(yy) - 1.9, 3.8, 3.8, sw=W_THIN, fill='#222' if used else '#fff')
            sh.text(X(col(c)) + side * 3.0, Y(yy) + 0.9, lab, size=1.9, anchor='start' if side > 0 else 'end')
    # cầu đấu vít KF301 5,08 dọc mép dưới
    TB = [('J1', ['+5V', 'GND'], 'NGUỒN 5 V'), ('J2', ['+5V', 'GND', 'S'], 'SERVO VÀO'), ('J3', ['+5V', 'GND', 'S'], 'SERVO RA'),
          ('J4', ['+5V', 'GND'], 'CAM VÀO'), ('J5', ['+5V', 'GND'], 'CAM RA')]
    xx = 4.5
    for name, pins_, lab in TB:
        w_ = len(pins_) * 5.08
        sh.rect(X(xx), Y(10), w_ * k, 7.5 * k, sw=W_THICK, fill='#fff')
        for j, pn in enumerate(pins_):
            cxp = xx + 2.54 + j * 5.08
            sh.circle(X(cxp), Y(5.4), 1.6, sw=W_THIN); sh.text(X(cxp), Y(8.0) + 0.6, pn, size=1.8, anchor='middle')
        sh.text(X(xx + w_ / 2), Y(10) - 1.2, f'{name} {lab}', size=1.9, anchor='middle', weight='bold')
        xx += w_ + 0.6
    # tụ, cầu chì, điện trở
    for (u, v, n) in ((14, 18, 'C1'), (27, 18, 'C2')):
        sh.circle(X(u), Y(v), 5 * k, sw=W_THICK); sh.text(X(u), Y(v) + 1, f'{n} 1000 µF', size=2, anchor='middle')
    sh.rect(X(36), Y(22), 6 * k, 8 * k, sw=W_THICK, rx=2); sh.text(X(39), Y(17) + 0.8, 'F1', size=2, anchor='middle')
    sh.text(X(39), Y(13.4) + 0.8, '4 A', size=1.9, anchor='middle')
    for (u, v, n) in ((53, 37.5, 'R1 1k'), (63, 37.5, 'R2 330')):
        sh.rect(X(u - 3), Y(v + 1), 6 * k, 2 * k, sw=W_THICK); sh.text(X(u), Y(v + 2.2), n, size=1.9, anchor='middle')
    # header đực 2,54 mép trái
    HDR = [('H1', 26, ['SS', 'SCK', 'MOSI', 'MISO', 'RST', 'GND', '3V3'], 'RC522 VÀO | RA'),
           ('H2', 18, ['VCC', 'GND', 'OUT', 'VCC', 'GND', 'OUT'], 'IR TỚI | IR AN TOÀN'),
           ('H3', 12, ['SPK+', 'SPK−', 'GND', 'DIN'], 'LOA, CÒI, LED')]
    for name, r0, labs, title in HDR:
        for i, lb in enumerate(labs):
            for c in (1, 2):
                sh.rect(X(col(c)) - 1.9, Y(col(r0 + len(labs) - 1 - i)) - 1.9, 3.8, 3.8, sw=W_THIN, fill='#555')
            sh.text(X(col(2)) + 3, Y(col(r0 + len(labs) - 1 - i)) + 0.8, lb, size=1.8)
        sh.text(X(col(1)) - 2.5, Y(col(r0 + len(labs) - 1)) - 3, f'{name} {title}', size=2.0, weight='bold')
    sh.k = k
    sh.dh(X(0), X(70), Y(0), 8, '70'); sh.dv(X(70), Y(90), Y(0), 8, '90')
    sh.dh(X(col(8)), X(col(18)), Y(90), -6, '25,4')
    sh.dv(X(0), Y(col(33)), Y(col(15)), -8, '45,72')
    sh.text(X(35), Y(-12), 'Lưới lỗ 2,54; lỗ A1 cách 2 mép 3. Ô đen: chân dùng; ô trắng: chân để trống.', size=2.4, anchor='middle')
    # bảng nối dây trên bo
    cols = [('Đường', 22), ('Từ chân ESP32', 22), ('Tới', 62), ('Ghi chú', 30)]
    rows = [['SS vào / ra', 'GPIO5 / GPIO4', 'H1 SS (RC522 vào / ra)', 'mỗi RC522 1 chân'],
            ['SCK, MOSI, MISO', 'GPIO18, 23, 19', 'H1 cả 2 hàng (chung bus)', 'dây ≤ 20 cm'],
            ['RST RC522', 'GPIO27', 'H1 RST cả 2 hàng', ''],
            ['IR xe tới vào / ra', 'GPIO34 / GPIO36', 'H2 OUT hàng 1 (vào), hàng 2 (ra)', 'chân chỉ vào'],
            ['IR an toàn vào / ra', 'GPIO35 / GPIO39', 'H2 OUT', 'chân chỉ vào'],
            ['Servo vào / ra', 'GPIO25 / GPIO26', 'J2 S / J3 S', 'PWM 50 Hz'],
            ['DFPlayer RX', 'GPIO17 (TX2)', 'qua R1 1 kΩ → DF RX', 'giảm nhiễu'],
            ['DFPlayer TX', 'GPIO16 (RX2)', 'DF TX', ''],
            ['Loa', '—', 'DF SPK1, SPK2 → H3 SPK+, SPK−', 'loa 4–8 Ω, ≤ 3 W'],
            ['Còi', 'GPIO14', 'H3 (VCC = 3V3)', 'kích mức thấp'],
            ['LED WS2812', 'GPIO13', 'qua R2 330 Ω → H3 DIN', 'nối tiếp 2 LED'],
            ['+5 V', 'VIN', 'J1 → F1 4 A → VIN, J2, J3, J4, J5, DF VCC, LED', 'đường đồng dày, dây 20 AWG'],
            ['+3V3', '3V3', 'H1, H2 VCC, còi', '≤ 200 mA'],
            ['GND', 'GND', 'chung toàn bộ', '']]
    sh.text(212, 13, 'BẢNG NỐI DÂY TRÊN BO', size=3.2, weight='bold')
    y = sh.table(212, 16, cols, rows, rh=5, size=2.3)
    notes(sh, 212, y + 8, 'YÊU CẦU KỸ THUẬT', [
        'Hàn header cái cho ESP32 và DFPlayer để thay được; không hàn trực tiếp module.',
        'Khoảng cách 2 hàng chân ESP32: 25,4 (loại rộng) hoặc 22,86 (loại hẹp) – đo bo thật, nếu 22,86 dời hàng phải sang trái 1 lỗ.',
        'Đường +5 V và GND tới J2, J3 đi dây đồng 0,8 mm hoặc dây 20 AWG ở mặt dưới; C1, C2 đặt sát J2, J3.',
        'Bo bắt 4 trụ đồng M3 × 6 tại 4 góc (cách mép 3), mặt hàn quay xuống đáy đế.',
    ], size=2.4, width=195)
    return sh

# =====================================================================================
# BV-09  SƠ ĐỒ NỐI DÂY
# =====================================================================================
def comp(sh, x, y, w, title, pins, side='r', sub=None):
    """Hộp linh kiện có chân; pins: [(tên chân, nhãn mạng)]; trả về toạ độ đầu dây theo tên chân."""
    h = 8 + len(pins) * 5
    sh.rect(x, y, w, h, sw=W_THICK, fill='#fff')
    sh.text(x + w / 2, y + 4.5, title, size=2.6, anchor='middle', weight='bold')
    if sub: sh.text(x + w / 2, y + h + 3.5, sub, size=2.1, anchor='middle', italic=True)
    out = {}
    for i, (pn, net) in enumerate(pins):
        py = y + 10 + i * 5
        if side == 'r':
            sh.text(x + w - 1.2, py + 0.9, pn, size=2.2, anchor='end')
            sh.line(x + w, py, x + w + 10, py, w=W_THICK)
            if net: tag(sh, x + w + 10, py, net, 1)
        else:
            sh.text(x + 1.2, py + 0.9, pn, size=2.2)
            if net or pn in ('RX', 'DIN', 'DOUT'): sh.line(x - 10, py, x, py, w=W_THICK)
            if net: tag(sh, x - 10, py, net, -1)
        out[pn] = (x + w + 10 if side == 'r' else x - 10, py)
    return out

def tag(sh, x, y, net, d):
    L = len(net) * 1.25 + 3
    if d > 0: pts = [(x, y), (x + 2, y - 2), (x + 2 + L, y - 2), (x + 2 + L, y + 2), (x + 2, y + 2)]
    else: pts = [(x, y), (x - 2, y - 2), (x - 2 - L, y - 2), (x - 2 - L, y + 2), (x - 2, y + 2)]
    sh.poly(pts, sw=W_THIN, fill='#fff')
    sh.text(x + d * (2 + L / 2), y + 0.8, net, size=2.0, anchor='middle')

def bv09():
    sh = sheet(9, 'SƠ ĐỒ NỐI DÂY TOÀN HỆ THỐNG', 'Không tỉ lệ', '—')
    comp(sh, 40, 14, 34, 'RC522 VÀO', [('SDA', 'SS_V'), ('SCK', 'SCK'), ('MOSI', 'MOSI'), ('MISO', 'MISO'), ('RST', 'RST'), ('3.3V', '+3V3'), ('GND', 'GND')], 'r')
    comp(sh, 40, 66, 34, 'RC522 RA', [('SDA', 'SS_R'), ('SCK', 'SCK'), ('MOSI', 'MOSI'), ('MISO', 'MISO'), ('RST', 'RST'), ('3.3V', '+3V3'), ('GND', 'GND')], 'r')
    yy = 118
    for t, net in (('IR XE TỚI VÀO', 'IRT_V'), ('IR XE TỚI RA', 'IRT_R'), ('IR AN TOÀN VÀO', 'IRA_V'), ('IR AN TOÀN RA', 'IRA_R')):
        comp(sh, 40, yy, 34, t, [('VCC', '+3V3'), ('GND', 'GND'), ('OUT', net)], 'r', None); yy += 25
    comp(sh, 40, yy, 34, 'MODULE CÒI', [('VCC', '+3V3'), ('GND', 'GND'), ('I/O', 'COI')], 'r', 'kêu khi I/O = 0')
    # ESP32
    ex, ey = 168, 14
    left = [('GPIO5', 'SS_V'), ('GPIO4', 'SS_R'), ('GPIO18', 'SCK'), ('GPIO23', 'MOSI'), ('GPIO19', 'MISO'), ('GPIO27', 'RST'),
            ('GPIO34', 'IRT_V'), ('GPIO36', 'IRT_R'), ('GPIO35', 'IRA_V'), ('GPIO39', 'IRA_R'), ('GPIO14', 'COI'), ('3V3', '+3V3')]
    right = [('GPIO25', 'SV_V'), ('GPIO26', 'SV_R'), ('GPIO17 TX2', 'TX2'), ('GPIO16 RX2', 'DF_TX'), ('GPIO13', 'LED'), ('VIN', '+5V'), ('GND', 'GND')]
    h = 8 + max(len(left), len(right)) * 5
    sh.rect(ex, ey, 46, h, sw=0.7, fill='#fff')
    sh.text(ex + 23, ey + 4.5, 'ESP32 DevKit 38 chân', size=2.7, anchor='middle', weight='bold')
    for i, (pn, net) in enumerate(left):
        py = ey + 10 + i * 5; sh.text(ex + 1.2, py + 0.9, pn, size=2.2); sh.line(ex - 10, py, ex, py, w=W_THICK); tag(sh, ex - 10, py, net, -1)
    for i, (pn, net) in enumerate(right):
        py = ey + 10 + i * 5; sh.text(ex + 46 - 1.2, py + 0.9, pn, size=2.2, anchor='end'); sh.line(ex + 46, py, ex + 56, py, w=W_THICK); tag(sh, ex + 56, py, net, 1)
    # bên phải: servo, DFPlayer, LED
    rx = 262
    comp(sh, rx, 14, 34, 'SERVO MG996R VÀO', [('S (cam)', 'SV_V'), ('+ (đỏ)', '+5V'), ('− (nâu)', 'GND')], 'l')
    comp(sh, rx, 42, 34, 'SERVO MG996R RA', [('S (cam)', 'SV_R'), ('+ (đỏ)', '+5V'), ('− (nâu)', 'GND')], 'l')
    p = comp(sh, rx, 70, 34, 'DFPLAYER MINI', [('RX', None), ('TX', 'DF_TX'), ('VCC', '+5V'), ('GND', 'GND'), ('SPK1', None), ('SPK2', None)], 'l')
    # R1 giữa TX2 và RX
    x0, y0 = p['RX']
    sh.rect(x0 - 12, y0 - 1.3, 7, 2.6, sw=W_THICK, fill='#fff'); sh.text(x0 - 8.5, y0 - 2.2, 'R1 1k', size=1.9, anchor='middle')
    sh.line(x0 - 5, y0, x0, y0, w=W_THICK); sh.line(x0 - 16, y0, x0 - 12, y0, w=W_THICK); tag(sh, x0 - 16, y0, 'TX2', -1)
    # loa
    s1, s2 = p['SPK1'], p['SPK2']
    lx = rx + 52
    sh.line(rx + 34, s1[1], lx, s1[1], w=W_THICK); sh.line(rx + 34, s2[1], lx, s2[1], w=W_THICK)
    sh.rect(lx, s1[1] - 2, 5, s2[1] - s1[1] + 4, sw=W_THICK, fill='#fff')
    sh.poly([(lx + 5, s1[1] - 2), (lx + 11, s1[1] - 6), (lx + 11, s2[1] + 6), (lx + 5, s2[1] + 2)], sw=W_THICK)
    sh.text(lx + 14, (s1[1] + s2[1]) / 2 + 1, 'LOA 3 W 4 Ω', size=2.2)
    # chú ý: SPK nằm phía phải hộp, vẽ lại dây ra phải
    q = comp(sh, rx, 116, 34, 'WS2812 VÀO', [('DIN', None), ('5V', '+5V'), ('GND', 'GND'), ('DOUT', None)], 'l')
    r = comp(sh, rx, 148, 34, 'WS2812 RA', [('DIN', None), ('5V', '+5V'), ('GND', 'GND')], 'l')
    x0, y0 = q['DIN']
    sh.rect(x0 - 12, y0 - 1.3, 7, 2.6, sw=W_THICK, fill='#fff'); sh.text(x0 - 8.5, y0 - 2.2, 'R2 330', size=1.9, anchor='middle')
    sh.line(x0 - 5, y0, x0, y0, w=W_THICK); sh.line(x0 - 16, y0, x0 - 12, y0, w=W_THICK); tag(sh, x0 - 16, y0, 'LED', -1)
    a, b = q['DOUT'], r['DIN']
    sh.line(a[0], a[1], a[0] - 4, a[1], w=W_THICK); sh.line(a[0] - 4, a[1], a[0] - 4, b[1], w=W_THICK); sh.line(a[0] - 4, b[1], b[0], b[1], w=W_THICK)
    # nguồn
    py_ = 196
    sh.text(150, py_ - 6, 'KHỐI NGUỒN', size=3, weight='bold')
    def blk(x, w, t, sub=''):
        sh.rect(x, py_, w, 16, sw=W_THICK, fill='#fff'); sh.text(x + w / 2, py_ + 7, t, size=2.4, anchor='middle', weight='bold')
        if sub: sh.text(x + w / 2, py_ + 12, sub, size=2.0, anchor='middle')
    blk(150, 28, 'ADAPTER', '12 V 3 A'); blk(190, 20, 'SW1', 'KCD1'); blk(222, 34, 'HẠ ÁP', 'XY-3606 5 V 5 A'); blk(268, 16, 'F1', '4 A')
    for x1, x2 in ((178, 190), (210, 222), (256, 268)):
        sh.line(x1, py_ + 8, x2, py_ + 8, w=W_THICK); sh._arrow(x2, py_ + 8, 0)
    sh.line(284, py_ + 8, 294, py_ + 8, w=W_THICK); tag(sh, 294, py_ + 8, '+5V', 1)
    sh.text(161, py_ + 22, 'jack DC 5,5/2,1', size=2.0, anchor='middle')
    sh.text(239, py_ + 22, 'C1, C2 1000 µF sát J2, J3', size=2.0, anchor='middle')
    # camera
    cx = 150; cy_ = 244
    sh.text(cx, cy_ - 14, 'MỖI CỘT CAMERA (×2, đặt trong hộp camera)', size=3, weight='bold')
    comp(sh, cx, cy_, 36, 'ESP32-CAM', [('5V', '+5V'), ('GND', 'GND'), ('GPIO13', None)], 'r')
    gx_, gy_ = cx + 46, cy_ + 20
    sh.rect(gx_, gy_ - 1.3, 7, 2.6, sw=W_THICK, fill='#fff'); sh.text(gx_ + 3.5, gy_ - 2.2, '1k', size=1.9, anchor='middle')
    sh.line(gx_ + 7, gy_, gx_ + 14, gy_, w=W_THICK)
    sh.circle(gx_ + 18, gy_, 4, sw=W_THICK); sh.text(gx_ + 18, gy_ + 8.5, 'Q1 S8050', size=2.0, anchor='middle')
    sh.line(gx_ + 14, gy_, gx_ + 16, gy_, w=W_THICK)
    sh.line(gx_ + 19, gy_ - 3.4, gx_ + 19, gy_ - 12, w=W_THICK); sh.line(gx_ + 19, gy_ + 3.4, gx_ + 19, gy_ + 9, w=W_THICK)
    tag(sh, gx_ + 19, gy_ + 9, 'GND', 1) if False else sh.text(gx_ + 21, gy_ + 12, 'GND', size=2.0)
    sh.rect(gx_ + 14, gy_ - 22, 10, 10, sw=W_THICK, fill='#fff'); sh.text(gx_ + 19, gy_ - 16, 'LED', size=1.9, anchor='middle')
    sh.line(gx_ + 19, gy_ - 22, gx_ + 19, gy_ - 26, w=W_THICK); sh.text(gx_ + 21, gy_ - 24, '+5V', size=2.0)
    sh.text(gx_ + 30, gy_ - 16, 'đèn LED USB 6 bóng', size=2.0)
    notes(sh, 262, 226, 'GHI CHÚ', [
        'Nối theo nhãn mạng: các đầu cùng tên là cùng một dây. Mũi nhãn chỉ chiều tín hiệu.',
        'RC522, IR, còi dùng 3,3 V; không cấp 5 V cho RC522.',
        'Servo, DFPlayer, LED, ESP32-CAM lấy 5 V từ mạch hạ áp, không lấy từ chân 5V của ESP32.',
        'GND của mọi khối nối chung tại J1.',
        'Màu dây: đỏ +5 V, cam +3V3, đen GND, vàng tín hiệu, xanh dương SPI.',
    ], size=2.3, width=150)
    return sh

# =====================================================================================
# BV-10  KÍCH THƯỚC CHUẨN CỦA LINH KIỆN (1:1)
# =====================================================================================
def bv10():
    sh = sheet(10, 'KÍCH THƯỚC CHUẨN CỦA LINH KIỆN ĐIỆN TỬ', '1:1', '—')
    sh.k = 1
    def title(x, y, t): sh.text(x, y, t, size=2.8, weight='bold')
    # MG996R – hình chiếu cạnh
    x, y = 30, 30; title(x, y - 11, 'Servo MG996R')
    sh.rect(x + 6.65, y + 5.9, 40.7, 37, sw=W_THICK)
    sh.rect(x, y + 13, 54, 2.5, sw=W_THICK)
    sh.rect(x + 6.65 + 10.3 - 3, y, 6, 5.9, sw=W_THICK)
    sh.line(x + 6.65 + 10.3, y - 2, x + 6.65 + 10.3, y + 45, kind='center')
    sh.dh(x + 6.65, x + 47.35, y + 42.9, 5, '40,7'); sh.dh(x, x + 54, y + 42.9, 11, '54')
    sh.dv(x + 54, y, y + 42.9, 5, '42,9'); sh.dh(x + 6.65, x + 16.95, y, -4, '10,3')
    sh.text(x, y + 57, 'dày 19,7; lỗ tai 49,5 × 10', size=2.3)
    # RC522
    x, y = 110, 26; title(x, y - 4, 'RFID RC522')
    sh.rect(x, y, 60, 40, sw=W_THICK)
    for k_ in range(3): sh.rect(x + 5 + k_ * 2, y + 5 + k_ * 2, 38 - k_ * 4, 30 - k_ * 4, sw=W_THIN, rx=4)
    for i in range(8): sh.circle(x + 57, y + 7.5 + i * 2.54 * 1.0, 0.6, sw=W_THIN)
    sh.dh(x, x + 60, y + 40, 5, '60'); sh.dv(x + 60, y, y + 40, 6, '40')
    sh.text(x, y + 52, 'dày PCB 1,6; 8 chân bước 2,54 trên cạnh 40', size=2.3)
    # ESP32 DevKit 38
    x, y = 200, 26; title(x, y - 4, 'ESP32 DevKit 38 chân')
    sh.rect(x, y, 55, 28, sw=W_THICK)
    sh.rect(x + 3, y + 5, 25.5, 18, sw=W_THIN)
    sh.rect(x + 50, y + 10, 6, 8, sw=W_THIN)
    for i in range(19):
        sh.circle(x + 4.6 + i * 2.54, y + 1.3, 0.55, sw=W_THIN); sh.circle(x + 4.6 + i * 2.54, y + 26.7, 0.55, sw=W_THIN)
    sh.dh(x, x + 55, y + 28, 5, '55'); sh.dv(x + 55, y, y + 28, 7, '28')
    sh.dv(x, y + 1.3, y + 26.7, -4, '25,4')
    sh.text(x, y + 40, 'loại hẹp: 2 hàng chân cách 22,86 – đo bo thật', size=2.3)
    # ESP32-CAM
    x, y = 290, 26; title(x, y - 4, 'ESP32-CAM')
    sh.rect(x, y, 27, 40.5, sw=W_THICK)
    sh.rect(x + 9, y + 4, 9, 9, sw=W_THIN); sh.circle(x + 13.5, y + 8.5, 3.4, sw=W_THIN)
    sh.rect(x + 4, y + 22, 19, 14, sw=W_THIN)
    sh.dh(x, x + 27, y + 40.5, 5, '27'); sh.dv(x + 27, y, y + 40.5, 5, '40,5')
    sh.text(x, y + 52, 'dày 4,5 (±0,2)', size=2.3)
    # DFPlayer
    x, y = 350, 26; title(x, y - 4, 'DFPlayer Mini')
    sh.rect(x, y, 20, 20, sw=W_THICK); sh.rect(x + 3, y + 2, 14, 12, sw=W_THIN)
    for i in range(8): sh.circle(x + 1.3, y + 1.2 + i * 2.54, 0.5, sw=W_THIN); sh.circle(x + 18.7, y + 1.2 + i * 2.54, 0.5, sw=W_THIN)
    sh.dh(x, x + 20, y + 20, 5, '20'); sh.dv(x + 20, y, y + 20, 5, '20')
    sh.text(x, y + 32, 'dày ≈ 5', size=2.3)
    # FC-51
    x, y = 30, 100; title(x, y - 4, 'Cảm biến IR FC-51')
    sh.rect(x, y, 31.3, 14.2, sw=W_THICK)
    sh.circle(x + 33.5, y + 3.6, 2.5, sw=W_THICK); sh.circle(x + 33.5, y + 10.6, 2.5, sw=W_THICK)
    sh.circle(x + 15, y + 7.1, 1.5, sw=W_THIN); sh.cross(x + 15, y + 7.1, 1.5)
    sh.dh(x, x + 31.3, y + 14.2, 5, '31,3'); sh.dv(x + 36, y, y + 14.2, 4, '14,2')
    sh.text(x, y + 26, 'cao 6,6; lỗ Ø3; tầm 20–300 mm', size=2.3)
    # còi
    x, y = 90, 100; title(x, y - 4, 'Module còi chủ động')
    sh.rect(x, y, 34.3, 13.3, sw=W_THICK); sh.circle(x + 22, y + 6.65, 6, sw=W_THICK)
    sh.circle(x + 5, y + 6.65, 1.3, sw=W_THIN)
    sh.dh(x, x + 34.3, y + 13.3, 5, '34,3'); sh.dv(x + 34.3, y, y + 13.3, 5, '13,3')
    sh.text(x, y + 25, 'cao 11,5; lỗ Ø2,6', size=2.3)
    # loa
    x, y = 150, 100; title(x, y - 4, 'Loa hộp 3 W')
    sh.rect(x, y, 70, 31, sw=W_THICK); sh.circle(x + 35, y + 15.5, 12, sw=W_THIN)
    sh.dh(x, x + 70, y + 31, 5, '70'); sh.dv(x + 70, y, y + 31, 5, '31')
    sh.text(x, y + 43, 'dày 16,8; 4 Ω; dán bằng băng keo xốp', size=2.3)
    # mạch hạ áp
    x, y = 245, 100; title(x, y - 4, 'Mạch hạ áp XY-3606')
    sh.rect(x, y, 63, 27, sw=W_THICK); sh.rect(x + 22, y + 7, 12, 12, sw=W_THIN)
    sh.rect(x - 2, y + 9, 10, 9, sw=W_THIN); sh.rect(x + 56, y + 7, 9, 13, sw=W_THIN)
    sh.dh(x, x + 63, y + 27, 5, '63'); sh.dv(x + 65, y, y + 27, 4, '≈ 27')
    sh.text(x, y + 39, 'vào 9–36 V, ra 5,2 V 5 A', size=2.3)
    # LED USB
    x, y = 330, 100; title(x, y - 4, 'Đèn LED USB (đã cắt)')
    sh.rect(x, y, 60, 13, sw=W_THICK, rx=3)
    for i in range(6): sh.rect(x + 5 + i * 9.2, y + 4, 5, 5, sw=W_THIN)
    sh.dh(x, x + 60, y + 13, 5, '≈ 60'); sh.dv(x + 60, y, y + 13, 5, '≈ 13')
    # bảng thông số và nguồn tra cứu
    cols = [('Linh kiện', 34), ('Kích thước chuẩn (mm)', 40), ('Điện', 50), ('Nguồn tra cứu', 120)]
    rows = [['Servo MG996R', '40,7 × 19,7 × 42,9; tai 54', '4,8–7,2 V; chạy 500–900 mA, kẹt 2,5 A (6 V)', 'Tower Pro MG996R datasheet; protosupplies.com (tai 54)'],
            ['RFID RC522', '60 × 40 (39,7 × 59,9 × 3,8)', '3,3 V; 13–26 mA; đọc ≈ 25–30 mm', 'protosupplies.com; tinkered.ai; NXP MFRC522'],
            ['ESP32-CAM', '27 × 40,5 × 4,5 (±0,2)', '4,75–5,25 V', 'Ai-Thinker ESP32-CAM datasheet'],
            ['ESP32 DevKit 38 chân', '55 × 28; hàng chân 25,4 hoặc 22,86', '5 V qua VIN; ≈ 240 mA khi phát Wi-Fi', 'espboards.dev; esp32.com; Espressif DevKitM-1 PCB'],
            ['DFPlayer Mini', '20 × 20 × ≈ 5', '3,2–5 V; khuếch đại loa 3 W', 'DFRobot DFR0299 (RS 201-8086)'],
            ['IR FC-51', '31,3 × 14,2 × 6,6', '3,3–5 V; tầm 20–300 mm, góc 35°', 'leap.tardate.com #806; uelectronics.com'],
            ['Module còi chủ động', '34,28 × 13,29 × 11,5', '3,3–5 V; transistor 8550, kích mức thấp', 'techiesms.com; robogears'],
            ['Loa 3 W', '70 × 31 × 16,8', '4 Ω, 3 W', 'taydaelectronics.com A-6909'],
            ['Mạch hạ áp XY-3606', 'dài 63', 'vào 9–36 V; ra 5,2 V 5 A', 'fut-electronics; electropeak.com'],
            ['PCB đục lỗ 2 mặt', '70 × 90; bước 2,54', '—', 'quy cách thông dụng']]
    sh.text(30, 160, 'THÔNG SỐ CHUẨN VÀ NGUỒN TRA CỨU', size=3.2, weight='bold')
    sh.table(30, 163, cols, rows, rh=5.4, size=2.4)
    sh.text(30, 236, 'Linh kiện mua ở cửa hàng có thể lệch ±0,5 so với bảng; đo lại bằng thước cặp trước khi cắt các lỗ khoét lắp ghép.', size=2.4, italic=True)
    return sh

# =====================================================================================
# BV-11  VẬT TƯ PHỤ, NGÂN SÁCH NGUỒN, QUY TRÌNH LẮP RÁP VÀ KIỂM TRA
# =====================================================================================
def bv11():
    sh = sheet(11, 'VẬT TƯ PHỤ, NGUỒN ĐIỆN, QUY TRÌNH LẮP RÁP VÀ KIỂM TRA', '—', '—')
    cols = [('Vật tư', 48), ('Quy cách', 34), ('SL', 12), ('Dùng cho', 32)]
    rows = [['Vít + đai ốc', 'M3 × 8', '24', 'đáy, vách sau, nắp thăm'], ['Vít + đai ốc', 'M3 × 12', '16', 'servo, khung đế'],
            ['Vít', 'M2 × 6', '4', 'cần barie vào horn'], ['Trụ đồng', 'M3 × 6', '4', 'bo chính'],
            ['Header cái', '1 × 19 / 1 × 8', '2 / 2', 'ESP32, DFPlayer'], ['Header đực', '2 × 7, 2 × 6, 2 × 4', '1 bộ', 'H1, H2, H3'],
            ['Cầu đấu KF301', '2P / 3P, bước 5,08', '3 / 2', 'J1–J5'], ['Tụ hoá', '1000 µF 10 V', '2', 'C1, C2'],
            ['Điện trở', '1 kΩ / 330 Ω', '3 / 1', 'R1, Q1 ×2 / R2'], ['Transistor', 'S8050', '2', 'đèn LED camera'],
            ['Cầu chì tự phục hồi', '4 A', '1', 'F1'], ['Dây', '20 AWG đỏ, đen', '2 m', 'nguồn 5 V, servo'],
            ['Dây', '26 AWG 5 màu', '5 m', 'tín hiệu'], ['Ống co nhiệt', 'Ø2, Ø4', '1 bộ', 'mối hàn'],
            ['Ống nhôm', 'Ø12 × 1', '10 cm', 'cột camera'], ['Nhôm hộp vuông', '4 × 4', '50 cm', 'trụ chốt, tay đỡ đèn'],
            ['Que inox', 'Ø5', '15 cm', 'cột đỡ cần'], ['Cáp USB nối dài panel', 'micro-USB 30 cm', '1', 'nạp code từ mặt sau'],
            ['Thẻ nhớ microSD', '≤ 32 GB, FAT32', '1', 'DFPlayer'], ['Keo, băng keo', 'keo dán mica, băng xốp 2 mặt', '1 bộ', 'dán vỏ, RC522, loa'],
            ['Chân cao su', 'Ø20', '4', 'đáy đế'], ['Decal in', 'vạch, chữ, sọc', '1 tờ A3', 'vạch sơn, biển']]
    sh.text(26, 13, 'VẬT TƯ PHỤ', size=3.2, weight='bold')
    y1 = sh.table(26, 16, cols, rows, rh=4.6, size=2.3)
    cols2 = [('Khối', 36), ('Dòng điển hình', 24), ('Dòng lớn nhất', 24), ('Nguồn', 16)]
    rows2 = [['ESP32 (Wi-Fi)', '160 mA', '240 mA', '5 V'], ['ESP32-CAM × 2', '2 × 180', '2 × 310', '5 V'],
             ['Servo MG996R × 2', '1 × 900 (1 làn)', '2 × 900', '5 V'], ['DFPlayer + loa', '150 mA', '500 mA', '5 V'],
             ['Đèn LED USB × 2', '2 × 120', '2 × 120', '5 V'], ['WS2812 × 2', '2 × 20', '2 × 60', '5 V'],
             ['Tổng nhánh 5 V', '≈ 1,9 A', '≈ 3,5 A', 'hạ áp 5 A'],
             ['RC522 × 2, IR × 4, còi', '≈ 110 mA', '≈ 150 mA', '3V3 ESP32'],
             ['Adapter 12 V', '≈ 0,9 A', '≈ 1,6 A', '12 V 3 A']]
    sh.text(160, 13, 'NGÂN SÁCH NGUỒN', size=3.2, weight='bold')
    y2 = sh.table(160, 16, cols2, rows2, rh=4.8, size=2.3)
    notes(sh, 160, y2 + 6, '', [
        'Servo kẹt (2,5 A mỗi chiếc) vượt nhánh 5 V nếu cả hai cùng kẹt: IR an toàn và giới hạn 15 s mở cần trong firmware ngăn trường hợp này; F1 4 A ngắt khi chập.',
        'Dòng phía 12 V tính với hiệu suất mạch hạ áp ≈ 90 %.',
    ], size=2.2, width=105)
    steps = [
        ('Cắt vật liệu', 'Cắt mica theo BV-05, BV-06, BV-07 (in A3 100 % làm dưỡng); cắt Formex theo BV-02, BV-03.', 'Đủ tấm theo bảng cắt'),
        ('Làm đế', 'Dán khung, sườn; khoan lỗ H1–H5, lỗ jack, công tắc, USB; khoét nắp thăm.', 'Đế phẳng, không vênh > 1'),
        ('Sơn, dán vạch', 'Sơn làn, đảo, vỉa hè; dán decal vạch theo BV-02.', 'Vạch đúng toạ độ ±1'),
        ('Hàn bo chính', 'Theo BV-08; chưa cắm ESP32, DFPlayer. Cấp 12 V, đo J1 = 5,0–5,3 V.', '5 V đúng cực, không nóng'),
        ('Nạp firmware', 'Cắm ESP32, nạp firmware/tru_dieu_khien; Serial 115200, lệnh i.', 'In trạng thái các khối'),
        ('Lắp chốt', 'Lắp RC522, WS2812, IR, loa, còi theo BV-04; thử lệnh v, s1–s5, b.', 'RC522 0x92, loa, còi kêu'),
        ('Lắp tủ barie', 'Đặt servo 0° rồi gắn cần nằm ngang; thử lệnh mv, mr; che IR an toàn.', 'Cần mở 90°, kẹt thì nâng lại'),
        ('Lắp camera', 'Nạp ESP32-CAM, lắp hộp theo BV-07, xoay 35,8°, chúc 15°; xem ảnh biển số.', 'Biển rõ, không chói'),
        ('Đi dây, đóng đáy', 'Buộc dây theo rãnh sườn; lắp đáy và nắp thăm.', 'Không dây lộ trên mặt'),
        ('Chạy toàn hệ thống', 'Mosquitto + server_mock + trang quản lý (firmware/README.md); quẹt thẻ 2 làn.', 'Lượt xe hiện trên trang'),
    ]
    cols3 = [('Bước', 9), ('Công việc', 30), ('Nội dung', 132), ('Đạt khi', 46)]
    sh.text(26, y1 + 8, 'QUY TRÌNH LẮP RÁP VÀ KIỂM TRA', size=3.2, weight='bold')
    sh.table(26, y1 + 11, cols3, [[str(i + 1), a, b, c] for i, (a, b, c) in enumerate(steps)], rh=4.8, size=2.3)
    notes(sh, 275, 13, 'AN TOÀN ĐIỆN', [
        'Không cấp 5 V cho RC522, IR (chân OUT nối GPIO34–39 phải ≤ 3,3 V).',
        'Servo lấy nguồn từ mạch hạ áp, không lấy từ chân 5V của ESP32 (sụt áp làm ESP32 khởi động lại).',
        'Đấu GND chung trước khi cắm tín hiệu.',
        'Kiểm tra cực tính jack DC (tâm dương) trước khi cấp điện lần đầu.',
        'Không để mạch hạ áp chạm khung kim loại; để hở 5 mm thông gió.',
    ], size=2.3, width=135)
    return sh
