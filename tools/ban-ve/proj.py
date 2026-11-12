# Chiếu các khối hộp/trụ lên 3 hình chiếu (chiếu góc thứ nhất), che khuất bằng thứ tự vẽ (xa trước, gần sau)
from bvlib import W_THICK, W_THIN

def draw(sh, shapes, view, ox, oy, k, skip=(), fill='#fff'):
    items = [s for s in shapes if s['n'] not in skip]
    if view == 'front':      # nhìn từ phía đường (−Y): ngang = X, đứng = Z, gần = Y nhỏ
        key = lambda s: -(s['y0'] if s['t'] == 'box' else s['cy'] - s['r'])
    elif view == 'top':      # nhìn từ trên: ngang = X, đứng (lên giấy) = Y, gần = Z lớn
        key = lambda s: s['z1']
    else:                    # nhìn từ trái (−X), đặt bên phải hình chiếu đứng: ngang = 450 − Y, gần = X nhỏ
        key = lambda s: -(s['x0'] if s['t'] == 'box' else s['cx'] - s['r'])
    items.sort(key=key)
    for s in items:
        g = s.get('glass')
        f = 'none' if g else fill
        sw = W_THIN if g else W_THICK
        if s['t'] == 'box':
            if view == 'front': a0, a1, b0, b1 = s['x0'], s['x1'], s['z0'], s['z1']
            elif view == 'top': a0, a1, b0, b1 = s['x0'], s['x1'], s['y0'], s['y1']
            else: a0, a1, b0, b1 = 450 - s['y1'], 450 - s['y0'], s['z0'], s['z1']
            sh.rect(ox + a0 * k, oy - b1 * k, (a1 - a0) * k, (b1 - b0) * k, sw=sw, fill=f)
        else:
            if view == 'top':
                sh.circle(ox + s['cx'] * k, oy - s['cy'] * k, s['r'] * k, sw=sw, fill=f)
            else:
                c = s['cx'] if view == 'front' else 450 - s['cy']
                sh.rect(ox + (c - s['r']) * k, oy - s['z1'] * k, 2 * s['r'] * k, (s['z1'] - s['z0']) * k, sw=sw, fill=f)
                sh.line(ox + c * k, oy - s['z1'] * k - 1, ox + c * k, oy - s['z0'] * k + 1, kind='center')
