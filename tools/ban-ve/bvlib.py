# Thư viện vẽ bản vẽ kỹ thuật khổ A3 ngang (đơn vị mm trên giấy) theo TCVN 7285 / 7286 / 8-20, chiếu góc thứ nhất
import math
from html import escape

FONT = "DejaVu Sans, Arial, sans-serif"
W_THICK, W_THIN = 0.5, 0.25

class Sheet:
    def __init__(self, no, title, scale, total, material='—'):
        self.no, self.title, self.scale, self.total, self.material = no, title, scale, total, material
        self.out = []
        self.k = 1.0

    # ---------- nét ----------
    def line(self, x1, y1, x2, y2, w=W_THIN, kind='solid', color='#000'):
        dash = {'solid': '', 'hidden': 'stroke-dasharray="2.4 1.2"', 'center': 'stroke-dasharray="10 1.5 1 1.5"', 'phantom': 'stroke-dasharray="10 1.5 1 1.5 1 1.5"'}[kind]
        self.out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{w}" {dash} stroke-linecap="round"/>')

    def rect(self, x, y, w, h, sw=W_THICK, fill='none', kind='solid', rx=0):
        dash = {'solid': '', 'hidden': 'stroke-dasharray="2.4 1.2"', 'phantom': 'stroke-dasharray="10 1.5 1 1.5 1 1.5"'}[kind]
        self.out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="#000" stroke-width="{sw}" {dash}/>')

    def circle(self, cx, cy, r, sw=W_THICK, fill='none', kind='solid'):
        dash = 'stroke-dasharray="2.4 1.2"' if kind == 'hidden' else ''
        self.out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="#000" stroke-width="{sw}" {dash}/>')

    def poly(self, pts, sw=W_THICK, fill='none', close=True, kind='solid'):
        dash = 'stroke-dasharray="2.4 1.2"' if kind == 'hidden' else ''
        p = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
        tag = 'polygon' if close else 'polyline'
        self.out.append(f'<{tag} points="{p}" fill="{fill}" stroke="#000" stroke-width="{sw}" {dash} stroke-linejoin="round"/>')

    def text(self, x, y, s, size=3.5, anchor='start', weight='normal', rot=0, color='#000', italic=False):
        tr = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ''
        st = ' font-style="italic"' if italic else ''
        self.out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}"{st}{tr}>{escape(str(s))}</text>')

    def raw(self, s): self.out.append(s)

    def cross(self, cx, cy, r):  # đường tâm chữ thập cho lỗ tròn
        self.line(cx - r - 1.5, cy, cx + r + 1.5, cy, kind='center')
        self.line(cx, cy - r - 1.5, cx, cy + r + 1.5, kind='center')

    def hatch(self, x, y, w, h, step=1.5, ang=45):
        cid = f'c{len(self.out)}'
        self.out.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#{cid})">')
        d = w + h
        k = -h
        while k < w:
            self.line(x + k, y + h, x + k + h, y, w=0.18)
            k += step
        self.out.append('</g>')

    # ---------- kích thước (mũi tên kín, chữ số phía trên đường kích thước) ----------
    def _arrow(self, x, y, ang):
        L, Wd = 2.5, 0.85
        a = math.radians(ang)
        bx, by = x - L * math.cos(a), y - L * math.sin(a)
        nx, ny = -math.sin(a) * Wd, math.cos(a) * Wd
        self.out.append(f'<polygon points="{x:.2f},{y:.2f} {bx+nx:.2f},{by+ny:.2f} {bx-nx:.2f},{by-ny:.2f}" fill="#000"/>')

    def dim(self, x1, y1, x2, y2, off, text=None, size=3.0, ext=True, flip_text=False):
        """Kích thước thẳng giữa 2 điểm; off > 0 dời đường kích thước sang trái chiều P1→P2."""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = uy, -ux
        if off < 0: pass
        a1 = (x1 + nx * off, y1 + ny * off); a2 = (x2 + nx * off, y2 + ny * off)
        if ext:
            s = 1 if off > 0 else -1
            g = 1.0
            self.line(x1 + nx * g * s, y1 + ny * g * s, a1[0] + nx * 1.8 * s, a1[1] + ny * 1.8 * s)
            self.line(x2 + nx * g * s, y2 + ny * g * s, a2[0] + nx * 1.8 * s, a2[1] + ny * 1.8 * s)
        ang = math.degrees(math.atan2(dy, dx))
        if L >= 8:
            self.line(*a1, *a2)
            self._arrow(a2[0], a2[1], ang); self._arrow(a1[0], a1[1], ang + 180)
        else:  # khoảng hẹp: mũi tên từ ngoài vào
            self.line(a1[0] - ux * 6, a1[1] - uy * 6, a2[0] + ux * 6, a2[1] + uy * 6)
            self._arrow(a1[0], a1[1], ang); self._arrow(a2[0], a2[1], ang + 180)
        t = text if text is not None else fmt(L / self.k)
        mx, my = (a1[0] + a2[0]) / 2, (a1[1] + a2[1]) / 2
        tang = ang
        if tang > 90.1 or tang < -90.1: tang += 180
        nnx, nny = math.sin(math.radians(tang)), -math.cos(math.radians(tang))
        px, py = mx + nnx * 0.9, my + nny * 0.9
        if L < 8 and not flip_text:
            px, py = a2[0] + ux * 4 + nnx * 0.9, a2[1] + uy * 4 + nny * 0.9
        self.text(px, py, t, size=size, anchor='middle', rot=tang)

    def dh(self, x1, x2, y, off, text=None, **kw):  # kích thước ngang, off âm = phía trên
        self.dim(x1, y, x2, y, -off, text, **kw)

    def dv(self, x, y1, y2, off, text=None, **kw):  # kích thước đứng, off dương = bên phải
        top, bot = min(y1, y2), max(y1, y2)
        self.dim(x, bot, x, top, -off, text, **kw)

    def ordx(self, ox, y0, y1, xs, k, size=2.6):
        """Ghi kích thước toạ độ theo X: đường gióng từ y0 tới y1, chữ số dựng đứng ở cuối."""
        for X in xs:
            px = ox + X * k
            self.line(px, y0, px, y1)
            self.text(px - 0.6, y1 + (1 if y1 > y0 else -1) * 0.8 + (len(str(X)) * size * 0.6 if y1 > y0 else 0), str(X), size=size, rot=-90, anchor='start')
        self.out.append(f'<circle cx="{ox:.2f}" cy="{(y0 + y1) / 2:.2f}" r="0.9" fill="none" stroke="#000" stroke-width="0.25"/>')

    def ordy(self, oy, x0, x1, ys, k, size=2.6):
        for Y in ys:
            py = oy - Y * k
            self.line(x0, py, x1, py)
            self.text(x1 - 0.8 if x1 < x0 else x1 + 0.8, py + size * 0.35, str(Y), size=size, anchor='end' if x1 < x0 else 'start')

    def diam(self, cx, cy, r, text, ang=45, lead=8):
        a = math.radians(-ang)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        ex, ey = cx + (r + lead) * math.cos(a), cy + (r + lead) * math.sin(a)
        self.line(px, py, ex, ey); self._arrow(px, py, math.degrees(math.atan2(py - ey, px - ex)))
        self.line(ex, ey, ex + 2 + len(text) * 1.75, ey)
        self.text(ex + 1, ey - 0.8, text, size=3)

    def leader(self, x, y, tx, ty, s, size=3, anchor='start'):
        self.line(x, y, tx, ty); self.out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.6" fill="#000"/>')
        e = tx + (1 if anchor == 'start' else -1) * (len(s) * size * 0.52 + 1)
        self.line(tx, ty, e, ty)
        self.text(tx + (0.5 if anchor == 'start' else -0.5), ty - 0.8, s, size=size, anchor=anchor)

    def balloon(self, x, y, bx, by, n):
        self.line(x, y, bx, by); self.out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.6" fill="#000"/>')
        self.circle(bx, by, 3.2, sw=W_THIN, fill='#fff'); self.text(bx, by + 1.25, n, size=3.4, anchor='middle')

    def label(self, x, y, s, size=3.5):  # tên hình chiếu, gạch chân
        self.text(x, y, s, size=size, anchor='middle', weight='bold')

    # ---------- bảng ----------
    def table(self, x, y, cols, rows, rh=5.5, size=2.7, head=True, wrap=None):
        widths = [c[1] for c in cols]
        tw = sum(widths)
        yy = y
        allrows = ([[c[0] for c in cols]] if head else []) + rows
        for i, r in enumerate(allrows):
            h = rh
            lines_per = []
            for j, cell in enumerate(r):
                ls = wraptext(str(cell), widths[j], size)
                lines_per.append(ls)
            nmax = max(len(l) for l in lines_per)
            h = max(rh, nmax * size * 1.18 + 1.8)
            xx = x
            for j, ls in enumerate(lines_per):
                for k, l in enumerate(ls):
                    self.text(xx + 1, yy + size + 0.9 + k * size * 1.18, l, size=size, weight='bold' if (head and i == 0) else 'normal')
                xx += widths[j]
            self.line(x, yy + h, x + tw, yy + h, w=W_THICK if (head and i == 0) else W_THIN)
            yy += h
        self.rect(x, y, tw, yy - y, sw=W_THICK)
        xx = x
        for wd in widths[:-1]:
            xx += wd; self.line(xx, y, xx, yy)
        return yy

    # ---------- khung, khung tên ----------
    def frame(self):
        self.rect(20, 5, 395, 287, sw=0.7)
        # khung tên 140 × 32 (mẫu dùng trong trường)
        x, y = 275, 260
        self.rect(x, y, 140, 32, sw=0.7)
        for yy in (y + 8, y + 16, y + 24): self.line(x, yy, x + 70, yy)
        for xx in (x + 18, x + 50, x + 70): self.line(xx, y, xx, y + 24)
        self.line(x + 70, y, x + 70, y + 24, w=0.7)
        self.line(x, y + 24, x + 140, y + 24, w=0.7)
        self.line(x + 110, y, x + 110, y + 24); self.line(x + 110, y + 8, x + 140, y + 8); self.line(x + 110, y + 16, x + 140, y + 16)
        cells = [('Người vẽ', 'Nguyễn Tấn Huy'), ('Người vẽ', 'Võ T. Thùy Dương'), ('Kiểm tra', 'ThS. Nguyễn Văn Phúc')]
        for i, (a, b) in enumerate(cells):
            self.text(x + 1, y + 5.4 + i * 8, a, size=2.6); self.text(x + 19, y + 5.4 + i * 8, b, size=2.6)
            self.text(x + 51, y + 5.4 + i * 8, '11/2026', size=2.5)
        # tên bản vẽ
        tl = wraptext(self.title, 38, 3.0, f=0.66)
        n = min(len(tl), 3)
        y0 = y + 10.5 - (n - 1) * 1.9
        for i, l in enumerate(tl[:3]):
            self.text(x + 90, y0 + i * 3.8, l, size=3.0, anchor='middle', weight='bold')
        mt = f'Vật liệu: {self.material}'
        self.text(x + 90, y + 22.4, mt, size=min(2.4, 38 / (len(mt) * 0.5)), anchor='middle')
        self.text(x + 111, y + 3.4, 'Tỉ lệ', size=2.2); self.text(x + 125, y + 6.6, self.scale, size=3.4 if len(self.scale) < 7 else 2.5, anchor='middle', weight='bold')
        self.text(x + 111, y + 11.4, 'Số bản vẽ', size=2.2); self.text(x + 125, y + 14.6, f'BV-{self.no:02d}', size=3.4, anchor='middle', weight='bold')
        self.text(x + 111, y + 19.4, 'Số tờ', size=2.2); self.text(x + 125, y + 22.6, f'{self.no}/{self.total}', size=3.4, anchor='middle', weight='bold')
        self.text(x + 70, y + 29.4, 'ĐH CÔNG NGHỆ KỸ THUẬT TP.HCM · KHOA ĐIỆN – ĐIỆN TỬ · ĐỒ ÁN 2: BÃI GIỮ XE MÁY THÔNG MINH', size=2.35, anchor='middle', weight='bold')
        # ô đánh dấu góc chiếu thứ nhất
        gx, gy = 258, 286
        self.poly([(gx - 10, gy - 2.5), (gx - 10, gy + 2.5), (gx - 4, gy + 4), (gx - 4, gy - 4)], sw=W_THIN)
        self.circle(gx + 3, gy, 4, sw=W_THIN); self.circle(gx + 3, gy, 2, sw=W_THIN)
        self.line(gx - 12, gy, gx + 8, gy, kind='center')
        self.text(gx - 2, gy - 5.5, 'Chiếu góc thứ nhất (E)', size=2, anchor='middle')

    def svg(self):
        self.frame()
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297"><rect width="420" height="297" fill="#fff"/>' + ''.join(self.out) + '</svg>'


def fmt(v):
    r = round(v, 1)
    s = f'{r:.1f}'.rstrip('0').rstrip('.')
    return s.replace('.', ',')


def wraptext(s, width_mm, size, f=0.55):
    maxc = max(4, int(width_mm / (size * f)))
    out = []
    for para in s.split('\n'):
        words, cur = para.split(' '), ''
        for w in words:
            if len(cur) + len(w) + (1 if cur else 0) <= maxc: cur = (cur + ' ' + w) if cur else w
            else:
                if cur: out.append(cur)
                cur = w
        out.append(cur)
    return out


class View:
    """Một hình chiếu: đổi toạ độ mô hình (mm) sang toạ độ giấy theo tỉ lệ k, gốc (ox, oy)."""
    def __init__(self, sh, ox, oy, k, axes):
        self.sh, self.ox, self.oy, self.k, self.axes = sh, ox, oy, k, axes
        sh.k = k
    def p(self, a, b):  # a ngang (sang phải), b đứng (lên trên)
        self.sh.k = self.k
        return self.ox + a * self.k, self.oy - b * self.k
