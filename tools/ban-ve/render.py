import sys, asyncio
import os; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
import bv
fns = [getattr(bv, f'bv{i:02d}') for i in range(1, 12) if hasattr(bv, f'bv{i:02d}')]
for f in fns: f()
svgs = [s.svg() for s in bv.SHEETS]
for s, x in zip(bv.SHEETS, svgs): open(f'{OUT}/bv{s.no:02d}.svg', 'w').write(x)
html = '<!DOCTYPE html><html><head><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}body{margin:0}svg{display:block;page-break-after:always}</style></head><body>' + ''.join(svgs) + '</body></html>'
open(OUT + '/ban-ve.html', 'w').write(html)
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(channel='chrome'); pg = await b.new_page(viewport={'width': 1587, 'height': 1123})
    await pg.goto('file://' + OUT + '/ban-ve.html'); await pg.wait_for_timeout(500)
    await pg.pdf(path=OUT + '/ban-ve-ky-thuat.pdf', width='420mm', height='297mm', print_background=True, prefer_css_page_size=True)
    for s in bv.SHEETS:
      await pg.goto(f'file://{OUT}/bv{s.no:02d}.svg'); await pg.wait_for_timeout(200)
      await pg.screenshot(path=f'{OUT}/p{s.no:02d}.png')
    await b.close()
asyncio.run(m())
print(len(bv.SHEETS), 'sheets')
