# Hình học mô hình 1:10 (mm). Gốc O: góc đế phía đường – bên trái. X sang phải, Y vào trong bãi, Z lên trên.
# Mặt trên đế (mặt đường) Z = 0. Khớp với phối cảnh lap-rap-3d.html: X = x3d + 290, Y = 225 − z3d.

BASE = dict(L=560, W=450, top=5, skirt=40, bottom=3)        # đế: mặt 5 + khung 40 + đáy 3 = cao 48
H_BASE = BASE['top'] + BASE['skirt'] + BASE['bottom']
ISL_H = 15
LANE_OUT = (90, 240); LANE_IN = (340, 490); ISLAND = (240, 340, 60, 390)
STREET = (0, 60); LOT = (390, 450)
BOOTH_C = (290, 215)            # tâm chốt
CAB_IN = (309, 355); CAB_OUT = (271, 95)
PIVOT_IN = (347, 365); PIVOT_OUT = (233, 85)      # trục servo / gốc cần (X, Y); cao Z = 85
POST_IN = (495, 365); POST_OUT = (85, 85)
CAM_IN = (330, 73); CAM_OUT = (250, 377)
PLATE_IN = (415, 191)          # tâm biển số sau xe làn vào khi dừng đọc thẻ (X, Y), cao 58
ARM_Z = 85; CAM_Z = 97

def B(name, x0, x1, y0, y1, z0, z1, **kw):
    return dict(t='box', n=name, x0=x0, x1=x1, y0=y0, y1=y1, z0=z0, z1=z1, **kw)
def VC(name, cx, cy, r, z0, z1, **kw):
    return dict(t='vcyl', n=name, cx=cx, cy=cy, r=r, z0=z0, z1=z1, **kw)

def assembly():
    S = []
    S.append(B('đế', 0, 560, 0, 450, -48, 0))
    S.append(B('vỉa hè trái', 0, 90, 60, 390, 0, 8))
    S.append(B('vỉa hè phải', 490, 560, 60, 390, 0, 8))
    S.append(B('đảo', 240, 340, 60, 390, 0, 15))
    bx, by = BOOTH_C
    S.append(B('đế chốt', bx - 49, bx + 49, by - 54, by + 54, 15, 21))
    S.append(B('vách chốt', bx - 45, bx + 45, by - 50, by + 50, 21, 113))
    S.append(B('quầy', bx - 58, bx - 42, by - 22, by + 22, 113, 117))
    S.append(B('quầy', bx + 42, bx + 58, by - 22, by + 22, 113, 117))
    S.append(B('kính chốt', bx - 45, bx + 45, by - 50, by + 50, 117, 211, glass=True))
    S.append(B('mái', bx - 53, bx + 53, by - 58, by + 58, 211, 217))
    S.append(B('biển tên', bx - 54, bx + 54, by - 59, by + 59, 217, 233))
    for (cx, cy), d, pv, post in ((CAB_IN, 1, PIVOT_IN, POST_IN), (CAB_OUT, -1, PIVOT_OUT, POST_OUT)):
        S.append(B('đế tủ', cx - 25, cx + 25, cy - 30, cy + 30, 15, 21))
        S.append(B('tủ barie', cx - 25, cx + 25, cy - 30, cy + 30, 21, 115))
        S.append(B('nắp tủ', cx - 27, cx + 27, cy - 32, cy + 32, 115, 120))
        hx = cx + d * 25
        S.append(B('nắp trục', min(hx, hx + d * 4), max(hx, hx + d * 4), pv[1] - 9, pv[1] + 9, 76, 94))
        x0, x1 = (pv[0], post[0]) if d > 0 else (post[0], pv[0])
        S.append(B('cần barie', x0, x1, pv[1] - 2, pv[1] + 2, 81, 89))
        S.append(VC('cột đỡ cần', post[0], post[1], 2.5, 8, 72))
        S.append(B('ngàm đỡ', post[0] - 4, post[0] + 4, post[1] - 5, post[1] + 5, 72, 81))
    for (cx, cy), d in ((CAM_IN, 1), (CAM_OUT, -1)):
        S.append(VC('đế cột', cx, cy, 10, 15, 18))
        S.append(VC('cột camera', cx, cy, 6, 18, 65))
        S.append(B('khối nối', cx - 4, cx + 4, cy - 4, cy + 4, 65, 72))
        S.append(B('hộp camera', cx - 17, cx + 17, cy - 14, cy + 14, 72, 122))
        S.append(B('mái che', cx - 20, cx + 20, cy - 19, cy + 19, 122, 124))
        ly0, ly1 = (cy - 30, cy) if d > 0 else (cy, cy + 30)
        S.append(B('tay đỡ đèn', cx - 2, cx + 2, ly0, ly1, 57, 61))
        ly = cy - 30 if d > 0 else cy + 30
        S.append(B('đèn LED', cx - 30, cx + 30, ly - 3, ly + 3, 52.5, 65.5))
    return S
