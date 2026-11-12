// Phối cảnh lắp ráp – mô hình bãi giữ xe 1:10 dựng từ linh kiện thật
// Đơn vị: mm. Vỏ mô hình theo tỉ lệ 1:10; linh kiện điện tử vẽ đúng kích thước thật.
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';

const qs = new URLSearchParams(location.search);
const UI = qs.get('ui') !== '0';
const FONT = 'Inter, "Segoe UI", Arial, sans-serif';

// ---------- renderer ----------
const wrap = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.localClippingEnabled = true;
wrap.appendChild(renderer.domElement);
const labelRenderer = new CSS2DRenderer();
labelRenderer.domElement.className = 'labels';
wrap.appendChild(labelRenderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeef0f2);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.55;
scene.add(new THREE.HemisphereLight(0xffffff, 0x9a9a92, 0.9));
const sun = new THREE.DirectionalLight(0xfff6e8, 2.1);
sun.position.set(320, 620, 380); sun.castShadow = true;
sun.shadow.mapSize.set(4096, 4096);
Object.assign(sun.shadow.camera, { left: -420, right: 420, top: 420, bottom: -420, near: 10, far: 1700 });
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.6;
scene.add(sun);
const under = new THREE.DirectionalLight(0xffffff, 0.8); under.position.set(-200, -400, 300); scene.add(under);

// ---------- helpers ----------
const std = (color, roughness = 0.6, metalness = 0, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness, metalness, ...extra });
function tex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
function box(w, h, d, mat, x = 0, y = 0, z = 0, parent = scene, r = null) {
  const rad = r === null ? Math.min(1.2, w / 4, h / 4, d / 4) : Math.min(r, w / 2.01, h / 2.01, d / 2.01);
  const m = new THREE.Mesh(rad > 0.2 ? new RoundedBoxGeometry(w, h, d, 3, rad) : new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
}
function cyl(rt, rb, h, mat, x = 0, y = 0, z = 0, parent = scene, seg = 32) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat);
  m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
}
function limb(a, b, r, mat, parent) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), len = A.distanceTo(B);
  const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, Math.max(0.1, len - 2 * r), 4, 12), mat);
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  m.castShadow = true; parent.add(m); return m;
}
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
// hộp có 6 mặt, mặt trên (+Y) dán texture
function topTex(w, h, d, side, topMap, x, y, z, parent) {
  const top = std(0xffffff, 0.5, 0.1, { map: topMap });
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [side, side, top, side, side, side]);
  m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; parent.add(m); return m;
}

// ---------- vật liệu: vỏ (có thể nhìn xuyên) và linh kiện ----------
const SHELL = [];   // vật liệu vỏ: bật "nhìn xuyên vỏ" sẽ làm trong suốt
const shell = (m) => { m.userData.baseOpacity = m.opacity; m.userData.baseTransparent = m.transparent; SHELL.push(m); return m; };
const C = { anthracite: 0x353a40, silver: 0xb9bec4, yellow: 0xf0b000, white: 0xf2f2ee, asphalt: '#3a3d41', concrete: '#c7c6c0', lot: '#8e9194' };
const M = {
  mdf: shell(std(0xd8d3c8, 0.85)),
  skirt: shell(std(0x9c8f7a, 0.8)),
  concrete: shell(std(0xc4c3bd, 0.9)),
  islandTop: std(0xb7b8b3, 0.9),
  anth: shell(std(C.anthracite, 0.5, 0.25)),
  silver: std(C.silver, 0.3, 0.85),
  yellow: shell(std(C.yellow, 0.42, 0.05)),
  capGray: shell(std(0x5a5f66, 0.45, 0.3)),
  cream: shell(std(0xece6d8, 0.5)),
  black: new THREE.MeshPhysicalMaterial({ color: 0x0b0d10, roughness: 0.15, metalness: 0.1, clearcoat: 1 }),
  rubberRed: std(0xc0262d, 0.7),
  rubber: std(0x1b1c1e, 0.85),
  glass: new THREE.MeshPhysicalMaterial({ color: 0xa9cfe0, roughness: 0.05, transparent: true, opacity: 0.28 }),
  pcbGreen: std(0x1f6b3a, 0.55), pcbBlue: std(0x1d4f9c, 0.5), pcbBlack: std(0x16181b, 0.5),
  metal: std(0xc9ccd0, 0.3, 0.9), brass: std(0xc8a24a, 0.35, 0.9), header: std(0x111214, 0.6),
  servo: std(0x1c1d20, 0.55), screw: std(0x5c94d6, 0.4),
};

// ---------- nền: đế + vạch sơn ----------
const S = 4;
const groundTex = tex(560 * S, 450 * S, (g) => {
  g.scale(S, S);
  g.fillStyle = C.concrete; g.fillRect(0, 0, 560, 450);
  g.fillStyle = C.lot; g.fillRect(0, 0, 560, 60);
  g.strokeStyle = '#f4f4f0'; g.lineWidth = 2;
  for (let x = 30; x <= 530; x += 40) { g.beginPath(); g.moveTo(x, 4); g.lineTo(x, 50); g.stroke(); }
  g.beginPath(); g.moveTo(30, 50); g.lineTo(530, 50); g.stroke();
  g.fillStyle = C.asphalt; g.fillRect(90, 60, 150, 330); g.fillRect(340, 60, 150, 330); g.fillRect(0, 390, 560, 60);
  for (let i = 0; i < 9000; i++) {
    const x = Math.random() * 560, y = 60 + Math.random() * 390;
    if ((x > 90 && x < 240) || (x > 340 && x < 490) || y > 390) { g.fillStyle = Math.random() < 0.5 ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.12)'; g.fillRect(x, y, 0.8, 0.8); }
  }
  g.fillStyle = '#f4f4f0';
  [[90, 60], [237, 60], [340, 60], [487, 60]].forEach(([x, y]) => g.fillRect(x, y, 3, 330));
  g.fillRect(340, 96, 150, 5); g.fillRect(90, 349, 150, 5);
  [[340, 60], [90, 365]].forEach(([x0, y0]) => {
    g.save(); g.beginPath(); g.rect(x0, y0, 150, 25); g.clip();
    g.strokeStyle = 'rgba(240,176,0,0.85)'; g.lineWidth = 3;
    for (let k = -150; k < 300; k += 14) { g.beginPath(); g.moveTo(x0 + k, y0); g.lineTo(x0 + k + 25, y0 + 25); g.stroke(); }
    g.restore();
  });
  const arrow = (cx, cy, up) => {
    g.save(); g.translate(cx, cy); if (!up) g.rotate(Math.PI);
    g.fillStyle = '#f4f4f0'; g.beginPath();
    g.moveTo(0, -24); g.lineTo(13, -6); g.lineTo(5, -6); g.lineTo(5, 22); g.lineTo(-5, 22); g.lineTo(-5, -6); g.lineTo(-13, -6); g.closePath(); g.fill(); g.restore();
  };
  const word = (t, cx, cy, flip) => { g.save(); g.translate(cx, cy); if (flip) g.rotate(Math.PI); g.fillStyle = '#f4f4f0'; g.font = `800 20px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(t, 0, 0); g.restore(); };
  arrow(380, 418, true); word('VÀO', 440, 418, false);
  arrow(200, 92, false); word('RA', 140, 92, true);
});
const groundMat = shell(new THREE.MeshStandardMaterial({ map: groundTex, roughness: 0.92 }));
const above = new THREE.Group(); scene.add(above);          // mọi thứ trên mặt đế
const baseG = new THREE.Group(); scene.add(baseG);          // đế và khoang điện
const ground = new THREE.Mesh(new THREE.PlaneGeometry(560, 450), groundMat);
ground.rotation.x = -Math.PI / 2; ground.position.set(-10, 0.05, 0); ground.receiveShadow = true; baseG.add(ground);
const topPlate = box(560, 5, 450, M.mdf, -10, -2.5, 0, baseG, 0);
// khung đế cao 40 mm (khoang điện), đáy tháo được
[[-10, 222.5, 560, 5], [-10, -222.5, 560, 5]].forEach(([x, z, w, d]) => box(w, 40, d, M.skirt, x, -25, z, baseG, 0));
[[-287.5, 0], [267.5, 0]].forEach(([x, z]) => box(5, 40, 440, M.skirt, x, -25, z, baseG, 0));
const bottomPanel = box(560, 3, 450, M.skirt, -10, -46.5, 0, baseG, 0);
// vỉa hè
box(70, 8, 330, M.concrete, 235, 4, 0, above);
box(90, 8, 330, M.concrete, -245, 4, 0, above);
// đảo phân làn
const stripe = (len) => { const t = tex(256, 32, (g, w, h) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#1c1d1f' : '#f0b000'; g.fillRect(i * 32, 0, 32, h); } }); t.wrapS = THREE.RepeatWrapping; t.repeat.set(len / 80, 1); return shell(std(0xffffff, 0.6, 0, { map: t })); };
const islTop = shell(M.islandTop);
const island = new THREE.Mesh(new THREE.BoxGeometry(100, 15, 330), [stripe(330), stripe(330), islTop, islTop, stripe(100), stripe(100)]);
island.position.set(0, 7.5, 0); island.castShadow = island.receiveShadow = true; above.add(island);
const ISL = 15;

// ---------- danh mục linh kiện (để đánh dấu khi chọn trong bảng) ----------
const PARTS = {};
function part(id, obj) { (PARTS[id] = PARTS[id] || []).push(obj); return obj; }

// ---------- mô hình từng linh kiện thật (kích thước mm thật) ----------
function texPCB(w, h, color, draw) { return tex(w * 8, h * 8, (g, W, H) => { g.fillStyle = color; g.fillRect(0, 0, W, H); g.scale(8, 8); draw && draw(g); }); }
function pins(n, x0, y, z0, dz, parent, h = 8.5) { for (let i = 0; i < n; i++) box(2.5, h, 2.5, M.header, x0, y, z0 + i * dz, parent, 0); }

// ESP32 DevKit 38 chân: 55 × 28 mm, nằm trên 2 hàng header cái
function esp32Dev(parent) {
  const g = new THREE.Group(); parent.add(g);
  const t = texPCB(28, 55, '#141619', (c) => {
    c.fillStyle = '#d6d9dc'; c.font = `bold 2.2px ${FONT}`;
    for (let i = 0; i < 19; i++) { c.fillStyle = '#c8a24a'; c.beginPath(); c.arc(1.6, 3 + i * 2.54, 0.8, 0, 7); c.arc(26.4, 3 + i * 2.54, 0.8, 0, 7); c.fill(); }
    c.fillStyle = '#2a2d31'; c.fillRect(10, 47, 8, 8);
  });
  topTex(28, 1.6, 55, M.pcbBlack, t, 0, 10.2, 0, g);
  box(18, 3.2, 25.5, M.metal, 0, 12.6, -10, g, 0.3);                         // vỏ kim loại module WROOM
  box(18, 1, 6, M.pcbBlack, 0, 11.5, -25, g, 0);                            // anten
  box(8, 2.8, 6, M.metal, 0, 12.4, 26, g, 0.4);                              // cổng micro-USB
  [-4, 4].forEach((x) => box(3.5, 1.8, 3.5, std(0x222222, 0.6), x, 11.9, 20, g, 0.2)); // nút EN, BOOT
  pins(19, -12.7, 4.6, -22.9, 2.54, g); pins(19, 12.7, 4.6, -22.9, 2.54, g);  // header cái
  return g;
}
// DFPlayer Mini: 20 × 20 mm, khe thẻ nhớ
function dfplayer(parent) {
  const g = new THREE.Group(); parent.add(g);
  box(20, 1.2, 20, M.pcbBlack, 0, 9.1, 0, g, 0);
  box(14, 2, 15, M.metal, 1, 10.7, -1, g, 0.3);
  pins(8, -8.9, 4.6, -8.9, 2.54, g); pins(8, 8.9, 4.6, -8.9, 2.54, g);
  return g;
}
// RC522: 60 × 40 mm, mặt anten vẽ bằng texture
function rc522(parent) {
  const g = new THREE.Group(); parent.add(g);
  const t = texPCB(60, 40, '#1d4f9c', (c) => {
    c.strokeStyle = '#c9a646'; c.lineWidth = 0.7;
    for (let k = 0; k < 4; k++) { rr(c, 4 + k * 1.6, 4 + k * 1.6, 40 - k * 3.2, 32 - k * 3.2, 5); c.stroke(); }
    c.fillStyle = '#111'; c.fillRect(46, 15, 6, 6);
    c.fillStyle = '#e8ecf2'; c.font = `bold 3px ${FONT}`; c.fillText('RFID-RC522', 8, 38.5);
    for (let i = 0; i < 8; i++) { c.fillStyle = '#c8a24a'; c.beginPath(); c.arc(57.5, 6 + i * 2.54 * 1.2, 0.8, 0, 7); c.fill(); }
  });
  const side = M.pcbBlue;
  const m = new THREE.Mesh(new THREE.BoxGeometry(60, 1.6, 40), [side, side, std(0xffffff, 0.5, 0.1, { map: t }), side, side, side]);
  m.castShadow = true; g.add(m);
  for (let i = 0; i < 8; i++) box(2.5, 2.5, 8, M.header, 28, -2, -11 + i * 3, g, 0);   // 8 chân hàn sẵn
  return g;
}
// Servo MG996R: thân 40,7 × 19,7 × 37, tai bắt vít 54,5, trục ra 42,9
function mg996r(parent) {
  const g = new THREE.Group(); parent.add(g);          // gốc = tâm trục; trục hướng +X
  const body = box(37, 19.7, 40.7, M.servo, -21.5, 0, 10.3, g, 1);
  box(2.5, 19.7, 54.5, M.servo, -11, 0, 10.3, g, 0.5);                     // tai bắt vít
  const lab = new THREE.Mesh(new THREE.PlaneGeometry(14, 16), std(0xffffff, 0.5, 0, { map: tex(140, 160, (c, w, h) => { c.fillStyle = '#7d3c98'; c.fillRect(0, 0, w, h); c.fillStyle = '#111'; c.fillRect(10, 10, w - 20, h - 50); c.fillStyle = '#fff'; c.font = `bold 26px ${FONT}`; c.save(); c.translate(w / 2, h / 2 - 20); c.rotate(-Math.PI / 2); c.textAlign = 'center'; c.fillText('MG996R', 0, 9); c.restore(); }) }));
  lab.position.set(-21.5, 9.9, 10.3); lab.rotation.x = -Math.PI / 2; lab.rotation.z = Math.PI / 2; g.add(lab);
  cyl(6, 6, 3, M.servo, -1.5, 0, 0, g).rotation.z = Math.PI / 2;
  cyl(2.9, 2.9, 4, M.brass, 2, 0, 0, g, 16).rotation.z = Math.PI / 2;     // trục răng đồng
  cyl(3.5, 3.5, 2.5, std(0xe8e8e8, 0.5), 4.8, 0, 0, g, 24).rotation.z = Math.PI / 2; // cánh tay servo (horn)
  return { g, body };
}
// Cảm biến hồng ngoại FC-51: 31 × 14 mm, 2 LED thò ra đầu
function fc51(parent) {
  const g = new THREE.Group(); parent.add(g);          // gốc = đầu có LED; thân kéo về -X
  box(31, 1.6, 14, M.pcbBlue, -15.5, 0, 0, g, 0);
  cyl(2.5, 2.5, 6, std(0xf0f0f0, 0.2, 0, { transparent: true, opacity: 0.85 }), 2, 3, -3.5, g, 16).rotation.z = Math.PI / 2;
  cyl(2.5, 2.5, 6, std(0x111111, 0.3), 2, 3, 3.5, g, 16).rotation.z = Math.PI / 2;
  cyl(2.4, 2.4, 3, std(0x2f6fd6, 0.4), -17, 2.3, 0, g, 16);               // biến trở chỉnh tầm
  box(5, 2, 3, M.pcbBlack, -10, 1.8, 0, g, 0);
  pins(3, -30, 0, -2.54, 2.54, g, 6);
  return g;
}
// Module còi chủ động (3 chân VCC, I/O, GND): 33 × 13 mm
function buzzer(parent) {
  const g = new THREE.Group(); parent.add(g);
  box(33, 1.6, 13, M.pcbBlue, 0, 0, 0, g, 0);
  cyl(6, 6, 9.5, std(0x111214, 0.5), 6, 5.6, 0, g);
  pins(3, -15, -2, -2.54, 2.54, g, 6);
  return g;
}
// Loa hộp 3 W ≈ 70 × 30 × 16 (tai bắt vít mỗi đầu)
function speaker(parent) {
  const g = new THREE.Group(); parent.add(g);          // mặt loa hướng +Z
  box(70, 30, 16, std(0x161719, 0.7), 0, 0, 0, g, 2);
  [-38, 38].forEach((x) => box(8, 30, 2, std(0x161719, 0.7), x, 0, 7, g, 1));
  const cone = new THREE.Mesh(new THREE.CircleGeometry(12, 32), std(0x242629, 0.8)); cone.position.set(0, 0, 8.1); g.add(cone);
  cyl(4, 4, 1, std(0x0e0f10, 0.5), 0, 0, 8.4, g).rotation.x = Math.PI / 2;
  return g;
}
// ESP32-CAM: 27 × 40,5 mm, camera OV2640 cáp cam
function esp32cam(parent) {
  const g = new THREE.Group(); parent.add(g);          // mặt camera hướng +Z, bo đứng
  const t = texPCB(27, 40, '#121417', (c) => { c.fillStyle = '#b7bcc1'; c.fillRect(2, 4, 13, 9); c.fillStyle = '#d58a2a'; c.fillRect(8, 14, 9, 12); c.fillStyle = '#e8ecf2'; c.font = `bold 3.2px ${FONT}`; c.fillText('ESP32-CAM', 5, 37); c.fillStyle = '#fffbe0'; c.fillRect(19, 30, 4, 4); });
  const side = M.pcbBlack;
  const b = new THREE.Mesh(new THREE.BoxGeometry(27, 40.5, 1.6), [side, side, side, side, std(0xffffff, 0.5, 0.1, { map: t }), side]);
  g.add(b);
  box(8.5, 8.5, 5, M.pcbBlack, 0, 8, 3.3, g, 0.5);                       // module camera
  cyl(3.4, 3.4, 4, std(0x0b0b0c, 0.2), 0, 8, 7.5, g, 24).rotation.x = Math.PI / 2;
  cyl(2, 2, 0.6, std(0x264a7a, 0.05, 0.6), 0, 8, 9.6, g, 24).rotation.x = Math.PI / 2;
  for (let i = 0; i < 8; i++) { box(2.5, 2.5, 8, M.header, -11.4, -17 + i * 2.54, -4.8, g, 0); box(2.5, 2.5, 8, M.header, 11.4, -17 + i * 2.54, -4.8, g, 0); }
  return g;
}
// Đèn LED USB đã cắt đầu cắm: ≈ 60 × 13 × 6, 6 bóng
function ledBar(parent) {
  const g = new THREE.Group(); parent.add(g);          // mặt sáng hướng +Z
  box(60, 13, 6, new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.15, transmission: 0.6, transparent: true, opacity: 0.6 }), 0, 0, 0, g, 3);
  for (let i = 0; i < 6; i++) box(5, 5, 1.2, std(0xfff4c8, 0.3, 0, { emissive: 0xfff2c0, emissiveIntensity: 1.4 }), -22.5 + i * 9, 0, 2.2, g, 0.5);
  return g;
}
// Mạch hạ áp DC-DC ra 5 V (có jack DC, cổng USB, cầu đấu): ≈ 62 × 27
function buckModule(parent) {
  const g = new THREE.Group(); parent.add(g);          // jack DC hướng -Z
  box(27, 1.6, 62, M.pcbBlue, 0, 0, 0, g, 0);
  box(12, 12, 12, std(0xb9bcc0, 0.35, 0.7), 0, 6.8, 2, g, 1);              // cuộn cảm "330"
  cyl(4, 4, 8, std(0x2a2c30, 0.5, 0.4), -7, 4.8, 20, g);
  cyl(5, 5, 10, std(0x2a2c30, 0.5, 0.4), 6, 5.8, -14, g);
  box(9, 11, 14, std(0x161616, 0.6), 0, 6.3, -26, g, 1);                   // jack DC
  box(13, 6, 14, M.metal, -3, 3.8, 26, g, 0.5);                            // cổng USB ra
  [[-9, -10], [9, 24]].forEach(([x, z]) => box(8, 9, 10, std(0x2f77c9, 0.5), x, 5.3, z, g, 0.5)); // cầu đấu vít
  return g;
}
// PCB đục lỗ 7 × 9 cm hai mặt
function perfboard(parent) {
  const t = texPCB(70, 90, '#2e7d43', (c) => { c.fillStyle = '#c8b58a'; for (let i = 0; i < 26; i++) for (let j = 0; j < 34; j++) { c.beginPath(); c.arc(3 + i * 2.54, 3 + j * 2.54, 0.7, 0, 7); c.fill(); } });
  return topTex(70, 1.6, 90, M.pcbGreen, t, 0, 0, 0, parent);
}
// LED WS2812 trên bo tròn Ø 10
function ws2812(parent, color = 0x22c55e) {
  const g = new THREE.Group(); parent.add(g);
  cyl(5, 5, 1.2, M.pcbBlack, 0, 0, 0, g, 24).rotation.x = Math.PI / 2;
  box(5, 5, 1.6, std(color, 0.3, 0, { emissive: color, emissiveIntensity: 2 }), 0, 0, 1.4, g, 0.4);
  return g;
}

// ---------- 1. CHỐT NHÂN VIÊN (vỏ mica) + linh kiện bên trong ----------
const booth = new THREE.Group(); booth.position.set(0, ISL, 10); above.add(booth);
const BW = 90, BD = 100, WALL = 92, GLASS_TOP = 196, T = 3;
box(98, 6, 108, M.silver, 0, 3, 0, booth);
box(BW, WALL, T, M.anth, 0, 6 + WALL / 2, BD / 2 - 1.5, booth, 1);
box(BW, WALL, T, M.anth, 0, 6 + WALL / 2, -BD / 2 + 1.5, booth, 1);
[1, -1].forEach((s) => box(T, WALL, BD, M.anth, s * (BW / 2 - 1.5), 6 + WALL / 2, 0, booth, 1));
const gy0 = 6 + WALL + 4, gh = GLASS_TOP - gy0;
[1, -1].forEach((s) => { const g = new THREE.Mesh(new THREE.BoxGeometry(BW - 6, gh, 2), M.glass); g.position.set(0, gy0 + gh / 2, s * (BD / 2 - 1.5)); booth.add(g); part('mica', g); });
[1, -1].forEach((s) => [[-BD / 2 + 3, -18], [18, BD / 2 - 3]].forEach(([z0, z1]) => { const g = new THREE.Mesh(new THREE.BoxGeometry(2, gh, z1 - z0), M.glass); g.position.set(s * (BW / 2 - 1.5), gy0 + gh / 2, (z0 + z1) / 2); booth.add(g); part('mica', g); }));
[[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sz]) => box(4, GLASS_TOP - 6, 4, M.silver, sx * (BW / 2 - 2), 6 + (GLASS_TOP - 6) / 2, sz * (BD / 2 - 2), booth));
[1, -1].forEach((s) => box(16, 4, 44, M.silver, s * (BW / 2 + 5), 6 + WALL + 2, 0, booth, 1));
box(BW + 16, 6, BD + 16, M.anth, 0, GLASS_TOP + 3, 0, booth, 2);
const signTexB = tex(640, 80, (g, w, h) => { g.fillStyle = '#353a40'; g.fillRect(0, 0, w, h); g.fillStyle = '#f0b000'; g.font = `800 46px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('BÃI GIỮ XE · PARKING', w / 2, h / 2 + 2); });
box(BW + 18, 16, BD + 18, M.anth, 0, GLASS_TOP + 14, 0, booth, 2);
const signMat = shell(std(0xffffff, 0.5, 0.1, { map: signTexB }));
[1, -1].forEach((s) => { const p = new THREE.Mesh(new THREE.PlaneGeometry(BW + 10, 12), signMat); p.position.set(0, GLASS_TOP + 14, s * (BD / 2 + 9.2)); if (s < 0) p.rotation.y = Math.PI; booth.add(p); });
[1, -1].forEach((s) => box(BW + 0.5, 6, 1, M.yellow, 0, 14, s * (BD / 2), booth, 0));
// lưới loa (khe) và lỗ còi trên vách trước
const grillTex = tex(310, 120, (g, w, h) => { g.fillStyle = '#353a40'; g.fillRect(0, 0, w, h); g.fillStyle = '#0d0f11'; for (let i = 0; i < 12; i++) rr(g, 14 + i * 24.5, 14, 10, 92, 5), g.fill(); });
const grill = new THREE.Mesh(new THREE.PlaneGeometry(62, 24), shell(std(0xffffff, 0.6, 0, { map: grillTex }))); grill.position.set(0, 36, BD / 2 + 0.2); booth.add(grill);
const hole = new THREE.Mesh(new THREE.CircleGeometry(3, 20), std(0x0d0f11, 0.8)); hole.position.set(-25, 78, BD / 2 + 0.2); booth.add(hole);
// mặt đọc thẻ in trên vách hai bên
const cardTex = (t) => tex(320, 220, (g, w, h) => {
  g.fillStyle = '#101214'; rr(g, 0, 0, w, h, 18); g.fill();
  g.strokeStyle = '#2f8cff'; g.lineWidth = 6; rr(g, 8, 8, w - 16, h - 16, 14); g.stroke();
  g.strokeStyle = '#ffffff'; g.lineWidth = 7; [24, 44, 64].forEach((r) => { g.beginPath(); g.arc(w / 2 - 70, h / 2, r, -0.9, 0.9); g.stroke(); });
  g.fillStyle = '#fff'; g.font = `800 34px ${FONT}`; g.textAlign = 'left'; g.fillText('QUẸT THẺ', w / 2 - 16, h / 2 - 2); g.font = `600 26px ${FONT}`; g.fillText(t, w / 2 - 16, h / 2 + 36);
});
const statusLeds = [];
[1, -1].forEach((s) => {
  const lane = s > 0 ? 'Làn vào' : 'Làn ra';
  const face = new THREE.Mesh(new THREE.PlaneGeometry(64, 44), shell(std(0xffffff, 0.3, 0.1, { map: cardTex(lane) })));
  face.position.set(s * (BW / 2 + 0.25), 70, 0); face.rotation.y = s * Math.PI / 2; booth.add(face);
  // RC522 dán mặt trong vách, cách mặt ngoài 3 mm mica
  const r = part('rc522', rc522(booth)); r.position.set(s * (BW / 2 - T - 1), 70, 0); r.rotation.order = 'ZYX'; r.rotation.y = Math.PI / 2; r.rotation.z = -s * Math.PI / 2;
  // LED trạng thái WS2812 ngay trên mặt đọc thẻ
  const l = part('ws2812', ws2812(booth, 0x22c55e)); l.position.set(s * (BW / 2 + 0.3), 96, 0); l.rotation.y = s * Math.PI / 2; statusLeds.push(l);
  // IR xe tới: chân vách, nhìn ngang qua làn ở độ cao 27 mm so với mặt đường
  const ir = part('fc51', fc51(booth)); ir.position.set(s * (BW / 2 + 2), 12, 0); ir.rotation.y = s > 0 ? 0 : Math.PI;
});
const spk = part('speaker', speaker(booth)); spk.position.set(0, 36, BD / 2 - T - 8.5);
const bz = part('buzzer', buzzer(booth)); bz.position.set(-31, 78, 36.5); bz.rotation.x = Math.PI / 2;
// lỗ đi dây xuống đế
cyl(8, 8, 0.4, std(0x0d0f11, 0.8), 0, 6.3, 0, booth, 24);

// ---------- 2. TỦ BARIE + SERVO + IR AN TOÀN ----------
const armTex = tex(600, 32, (g, w, h) => { for (let i = 0; i < 15; i++) { g.fillStyle = i % 2 ? '#d32f2f' : '#ffffff'; g.fillRect(i * 40, 0, 40, h); } });
const armMat = std(0xffffff, 0.35, 0.05, { map: armTex });
const signTex = (t) => tex(200, 100, (g, w, h) => { g.fillStyle = '#16191c'; rr(g, 0, 0, w, h, 14); g.fill(); g.fillStyle = '#ffffff'; g.font = `800 56px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(t, w / 2, h / 2 + 3); });
const arms = [];
function cabinet(cx, cz, dir, word, facing) {
  const g = new THREE.Group(); g.position.set(cx, ISL, cz); above.add(g);
  box(50, 6, 60, M.rubber, 0, 3, 0, g);
  // vỏ 5 mặt mica 3 mm (vẽ từng tấm để nhìn xuyên được)
  box(50, 94, T, M.yellow, 0, 53, 30 - 1.5, g, 0.6); box(50, 94, T, M.yellow, 0, 53, -30 + 1.5, g, 0.6);
  box(T, 94, 60, M.yellow, dir * 23.5, 53, 0, g, 0.6); box(T, 94, 60, M.yellow, -dir * 23.5, 53, 0, g, 0.6);
  box(54, 5, 64, M.capGray, 0, 102.5, 0, g);
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(36, 18), shell(std(0xffffff, 0.5, 0, { map: signTex(word) })));
  sign.position.set(0, 80, facing * 30.2); if (facing < 0) sign.rotation.y = Math.PI; g.add(sign);
  // servo: tai bắt vít áp mặt trong vách phía làn, đầu trục thò qua lỗ khoét 41 × 20
  const sv = mg996r(g); part('mg996r', sv.g);
  sv.g.position.set(dir * 33, 70, -8 * dir); if (dir < 0) sv.g.rotation.y = Math.PI;
  cyl(9, 9, 4, M.silver, dir * 31.5, 70, -8 * dir, g).rotation.z = Math.PI / 2;     // nắp che trục
  // cần barie gắn vào cánh tay servo
  const pivot = new THREE.Group(); pivot.position.set(cx + dir * 38, ISL + 70, cz - 8 * dir); above.add(pivot);
  box(150, 8, 4, armMat, dir * 75, 0, 0, pivot);
  box(8, 10, 6, M.rubberRed, dir * 152, 0, 0, pivot);
  arms.push({ pivot, dir, t: 0 });
  // IR an toàn dưới cần barie, nhìn ngang qua làn
  const ir = part('fc51', fc51(g)); ir.position.set(dir * 27, 12, 0); if (dir < 0) ir.rotation.y = Math.PI;
  // cột đỡ đầu cần
  const px = cx + dir * 186;
  cyl(2.5, 2.5, 62, M.silver, px, 8 + 31, cz, above); box(4, 10, 10, M.rubber, px, 8 + 64, cz, above);
  return g;
}
cabinet(19, -130, 1, 'VÀO', 1);
cabinet(-19, 130, -1, 'RA', -1);

// ---------- 3. CỘT CAMERA: ESP32-CAM + đèn LED chiếu biển ----------
const camHeads = [];
const POLE = 50;
function camPole(x, z, target, side) {
  cyl(6, 6, POLE, M.silver, x, ISL + POLE / 2, z, above);
  cyl(10, 10, 3, M.silver, x, ISL + 1.5, z, above);
  const head = new THREE.Group(); head.position.set(x, ISL + POLE + 32, z); above.add(head);
  head.lookAt(new THREE.Vector3(...target));
  // hộp camera mica 2 mm: ngoài 34 × 50 × 28, cửa sổ mica trong phía trước
  const W = 34, H = 50, D = 28;
  box(W, H, 2, M.cream, 0, 0, -D / 2 + 1, head, 0.8);
  [-1, 1].forEach((s) => box(2, H, D, M.cream, s * (W / 2 - 1), 0, 0, head, 0.8));
  box(W, 2, D, M.cream, 0, -H / 2 + 1, 0, head, 0.8);
  box(W + 6, 2, D + 10, M.capGray, 0, H / 2 + 1, 4, head, 0.8);               // mái che
  const win = new THREE.Mesh(new THREE.BoxGeometry(W - 4, H - 4, 1.5), M.glass); win.position.set(0, 0, D / 2 - 0.75); head.add(win); part('mica', win);
  const cam = part('esp32cam', esp32cam(head)); cam.position.set(0, -1, 2);
  box(8, 8, 8, M.silver, 0, -H / 2 - 4, -4, head);
  // đèn LED trên tay đỡ lệch sang bên 30 mm, thấp hơn 30 mm để không chói ngược vào camera
  box(4, 4, 30, M.silver, x, ISL + POLE - 6, z + side * 15, above, 0);
  const lb = new THREE.Group(); lb.position.set(x, ISL + POLE - 6, z + side * 30); above.add(lb);
  lb.lookAt(new THREE.Vector3(...target));
  part('ledbar', ledBar(lb));
  camHeads.push(head);
}
camPole(40, 152, [125, 58, 34], 1);
camPole(-40, -152, [-125, 58, -34], -1);

// ---------- 4. KHOANG ĐIỆN DƯỚI ĐẾ ----------
const bay = new THREE.Group(); scene.add(bay);
const pcbG = new THREE.Group(); pcbG.position.set(0, -38, 5); bay.add(pcbG);          // bo chính dưới chốt, trên 4 trụ đồng 6 mm
part('perfboard', perfboard(pcbG));
[[-31, -41], [31, -41], [-31, 41], [31, 41]].forEach(([x, z]) => cyl(2.5, 2.5, 6, M.brass, x, -4, z, pcbG, 6));
const e32 = part('esp32', esp32Dev(pcbG)); e32.position.set(-15, 0.8, 2); e32.rotation.y = Math.PI;   // cổng USB quay về phía sau (-Z)
const dfp = part('dfplayer', dfplayer(pcbG)); dfp.position.set(12, 0.8, -22);
cyl(5, 5, 20, std(0x24282e, 0.4, 0.4), 22, 11, 14, pcbG, 20);                    // tụ 1000 µF nguồn servo
cyl(4, 4, 13, std(0x24282e, 0.4, 0.4), 22, 7.5, 28, pcbG, 20);
for (let i = 0; i < 7; i++) box(5, 9, 7.6, std(0x2fa35a, 0.5), 30, 5.3, -36 + i * 9.5, pcbG, 0.4);   // cầu đấu 2–3 chân
for (let i = 0; i < 6; i++) box(2.5, 8, 2.5 * 4, M.header, -32, 4.8, -30 + i * 12, pcbG, 0);         // header ra RC522, IR, loa…
const buck = part('buck', buckModule(bay)); buck.position.set(-150, -40, -190);
// công tắc + jack DC lộ ra mặt sau đế
box(14, 9, 6, std(0x111214, 0.6), -122, -25, -225.5, bay, 1);
box(10, 6, 2, std(0xd32f2f, 0.4), -122, -25, -228.5, bay, 0.5);
// nắp thăm dưới đáy (mở để nạp code / thay thẻ nhớ)
const hatch = box(110, 1, 130, std(0x857a68, 0.7), 0, -48.6, 5, baseG, 0);

// ---------- 5. ĐƯỜNG DÂY ----------
const wires = new THREE.Group(); scene.add(wires);
const W_COL = { power: 0xd32f2f, signal: 0xf0b000, spi: 0x2f8cff, cam: 0xff7a1a };
function wire(points, color, r = 1.3) {
  const curve = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)), false, 'catmullrom', 0.05);
  const m = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(24, points.length * 16), r, 8), std(color, 0.45, 0, { emissive: color, emissiveIntensity: 0.25 }));
  wires.add(m); return m;
}
// nguồn 12 V → mạch hạ áp → bo chính (5 V)
wire([[-150, -32, -160], [-150, -14, -120], [-60, -14, -60], [-35, -28, -25]], W_COL.power, 1.8);
// bo chính → chốt: RC522 ×2 (SPI), WS2812, loa, còi, IR xe tới (lên qua lỗ Ø 16 ở sàn chốt)
wire([[0, -24, 0], [0, -6, 10], [1, 22, 10], [10, 50, 10], [39, 85, 10]], W_COL.spi);
wire([[2, -24, 0], [2, -6, 10], [-1, 22, 10], [-10, 50, 10], [-39, 85, 10]], W_COL.spi);
wire([[-3, -24, 2], [-3, -6, 12], [-3, 22, 14], [-2, 40, 36], [0, 51, 40]], W_COL.signal, 1);
wire([[4, -24, 2], [4, -6, 12], [3, 22, 14], [-15, 70, 36], [-25, 93, 38]], W_COL.signal, 1);
[1, -1].forEach((s) => { wire([[s * 3, 22, 8], [s * 15, 26, 8], [s * 28, 27, 10]], W_COL.signal, 1); wire([[s * 2, 30, 10], [s * 28, 95, 10], [s * 43, 111, 10]], W_COL.signal, 0.8); });
// bo chính → tủ barie (servo 3 dây + IR an toàn), lên qua lỗ sàn tủ
wire([[32, -26, -20], [32, -10, -60], [19, -10, -130], [19, 20, -130], [26, 70, -135], [30, 85, -138]], W_COL.power, 1.5);
wire([[-32, -26, 30], [-32, -10, 70], [-19, -10, 130], [-19, 20, 130], [-26, 70, 135], [-30, 85, 138]], W_COL.power, 1.5);
[[1, -130], [-1, 130]].forEach(([d, z]) => wire([[d * 19, 20, z + 2], [d * 22, 26, z], [d * 30, 27, z]], W_COL.signal, 1));
// 5 V lên cột camera (trong ống Ø 12)
wire([[10, -26, 40], [10, -10, 120], [40, -10, 152], [40, 30, 152], [40, 92, 152]], W_COL.cam, 1.2);
wire([[-10, -26, -30], [-10, -10, -120], [-40, -10, -152], [-40, 30, -152], [-40, 92, -152]], W_COL.cam, 1.2);
// cáp USB nối dài từ ESP32 ra mặt sau đế (nạp code không cần tháo đáy)
wire([[15, -28, -26], [15, -20, -120], [-60, -22, -200], [-60, -25, -222]], 0x444a52, 1.6);
box(12, 8, 4, std(0x24282e, 0.5), -60, -25, -225, bay, 1);
wires.visible = false;
const CLIP = new THREE.Plane(new THREE.Vector3(0, -1, 0), 20);   // khoang điện: chỉ vẽ dây dưới mặt đảo
// đường bao khung đế (thấy rõ khi xem khoang điện)
const baseEdges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(560, 48, 450)), new THREE.LineBasicMaterial({ color: 0x5b4f3c }));
baseEdges.position.set(-10, -24, 0); baseEdges.visible = false; scene.add(baseEdges);
// tia nhìn của camera làn vào tới biển số sau (chỉ hiện ở góc nhìn camera)
const sight = new THREE.Group(); sight.visible = false; scene.add(sight);
{
  const c = new THREE.Vector3(40, ISL + POLE + 32, 152);
  const corners = [[-11, -8], [11, -8], [11, 8], [-11, 8]].map(([dx, dy]) => new THREE.Vector3(125 + dx, 58 + dy, 34.5));
  const mat = new THREE.LineDashedMaterial({ color: 0x2f8cff, dashSize: 4, gapSize: 3 });
  corners.forEach((q) => { const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints([c, q]), mat); l.computeLineDistances(); sight.add(l); });
  const d = document.createElement('div'); d.className = 'lbl'; d.innerHTML = '<span>↗</span>Tia nhìn: lệch 36° so với pháp tuyến biển số, cách 145 mm';
  const o = new CSS2DObject(d); o.position.set(85, 80, 95); sight.add(o);
}

// ---------- xe máy mô hình (đồ chơi 1:10, để thử camera) ----------
function plateTex(l1, l2) { return tex(220, 160, (g, w, h) => { g.fillStyle = '#ffffff'; rr(g, 0, 0, w, h, 14); g.fill(); g.strokeStyle = '#111'; g.lineWidth = 8; rr(g, 6, 6, w - 12, h - 12, 10); g.stroke(); g.fillStyle = '#111'; g.font = `800 58px ${FONT}`; g.textAlign = 'center'; g.fillText(l1, w / 2, 70); g.fillText(l2, w / 2, 134); }); }
function bike(color, l1, l2) {
  const b = new THREE.Group();
  const paint = std(color, 0.28, 0.35); const tire = std(0x151618, 0.9);
  [-62, 62].forEach((z) => { const w = new THREE.Mesh(new THREE.TorusGeometry(19, 6, 16, 40), tire); w.rotation.y = Math.PI / 2; w.position.set(0, 25, z); w.castShadow = true; b.add(w); cyl(13, 13, 5, M.silver, 0, 25, z, b, 24).rotation.z = Math.PI / 2; });
  box(30, 8, 86, M.rubber, 0, 34, 0, b);
  box(42, 44, 72, paint, 0, 62, 38, b, 14);
  box(34, 70, 18, paint, 0, 70, -42, b, 8).rotation.x = -0.18;
  box(28, 10, 60, std(0x1c1c1e, 0.8), 0, 89, 30, b, 5);
  box(40, 14, 22, paint, 0, 106, -52, b, 6);
  cyl(2, 2, 66, M.silver, 0, 108, -56, b, 12).rotation.z = Math.PI / 2;
  box(22, 5, 3, std(0xd71920, 0.3, 0, { emissive: 0xd71920, emissiveIntensity: 0.6 }), 0, 76, 75, b);
  box(24, 3, 12, M.rubber, 0, 50, 78, b);
  const plate = new THREE.Mesh(new THREE.PlaneGeometry(22, 16), std(0xffffff, 0.4, 0, { map: plateTex(l1, l2) })); plate.position.set(0, 58, 81); b.add(plate);
  b.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  return b;
}
const bikes = new THREE.Group(); above.add(bikes);
const b1 = bike(0xa8202a, '59-X1', '123.45'); b1.position.set(125, 0, -47); bikes.add(b1);
const b2 = bike(0x2b5c8f, '59-T2', '678.90'); b2.position.set(-125, 0, 47); b2.rotation.y = Math.PI; bikes.add(b2);
[[-190, 0x3a3f45], [-10, 0xd9d9d4], [170, 0x1f4e79]].forEach(([x, c], i) => { const pb = bike(c, '59-K' + (i + 3), '2' + i + '4.1' + i); pb.position.set(x, 0, -197); pb.scale.setScalar(0.9); pb.rotation.y = Math.PI / 2; bikes.add(pb); });

// ---------- đường kích thước (TCVN: mũi tên, chữ số trên đường kích thước, đơn vị mm) ----------
const dims = {};
const dimMat = new THREE.LineBasicMaterial({ color: 0x1c2127 });
function dim(view, a, b, off, text) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), O = new THREE.Vector3(...off);
  const g = new THREE.Group(); g.visible = false;
  const A2 = A.clone().add(O), B2 = B.clone().add(O);
  const ext = O.clone().normalize().multiplyScalar(4);
  const line = (p, q) => g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([p, q]), dimMat));
  line(A.clone().add(O.clone().multiplyScalar(0.15)), A2.clone().add(ext)); line(B.clone().add(O.clone().multiplyScalar(0.15)), B2.clone().add(ext));
  line(A2, B2);
  const dirv = B2.clone().sub(A2).normalize(), n = ext.clone().normalize().multiplyScalar(2.6);
  [[A2, dirv], [B2, dirv.clone().negate()]].forEach(([p, d]) => { line(p, p.clone().addScaledVector(d, 8).add(n)); line(p, p.clone().addScaledVector(d, 8).sub(n)); });
  const el = document.createElement('div'); el.className = 'dimt'; el.textContent = text;
  const lab = new CSS2DObject(el); lab.position.copy(A2.clone().add(B2).multiplyScalar(0.5)); g.add(lab);
  scene.add(g); (dims[view] = dims[view] || []).push(g);
}
// hình chiếu bằng (nhìn từ trên, trục Z hướng xuống màn hình)
dim('top', [-290, 0, -225], [270, 0, -225], [0, 0, -28], '560');
dim('top', [270, 0, -225], [270, 0, 225], [28, 0, 0], '450');
dim('top', [50, 0, 190], [200, 0, 190], [0, 0, 45], '150 (làn vào)');
dim('top', [-200, 0, 190], [-50, 0, 190], [0, 0, 45], '150 (làn ra)');
dim('top', [-50, 0, 190], [50, 0, 190], [0, 0, 45], '100');
dim('top', [-45, 0, -60], [45, 0, -60], [0, 0, -10], '90');
dim('top', [-58, 0, -40], [-58, 0, 60], [-8, 0, 0], '100');
dim('top', [210, 0, -165], [210, 0, 165], [0, 0, 0], '330 (đảo)');
// hình chiếu đứng (nhìn từ phía đường vào, +Z)
dim('front', [100, 0, 230], [100, 15, 230], [70, 0, 0], '15');
dim('front', [-58, 0, 230], [-58, 231, 230], [-40, 0, 0], '231');
dim('front', [200, 0, 230], [200, 85, 230], [30, 0, 0], '85 (trục barie)');
dim('front', [120, 0, 230], [120, 27, 230], [0, 0, 0], '27 (IR)');
dim('front', [-40, 0, 230], [-40, 97, 230], [-115, 0, 0], '97 (tâm camera)');
dim('front', [-290, -48, 230], [-290, 0, 230], [-22, 0, 0], '48 (đế)');
dim('front', [-45, 230, 230], [45, 230, 230], [0, 18, 0], '90');

// ---------- chú thích số ----------
let showLabels = qs.get('labels') !== '0';
const LABEL_DEFS = [
  ['1', 'Chốt: vỏ mica 3 mm, kính mica trong 2 mm', [0, 262, 10], ['persp', 'booth', 'iso']],
  ['2', 'RC522 sau vách (đọc xuyên mica)', [60, 92, 10], ['persp', 'booth']],
  ['3', 'Tủ barie: servo MG996R', [44, 130, -130], ['persp', 'barrier']],
  ['4', 'ESP32-CAM trong hộp mica', [40, 132, 165], ['persp', 'camera']],
  ['5', 'Đèn LED chiếu biển số', [40, 50, 185], ['persp', 'camera']],
  ['6', 'IR xe tới (FC-51)', [72, 38, 10], ['booth']],
  ['7', 'IR an toàn dưới cần (FC-51)', [72, 30, -130], ['barrier']],
  ['8', 'Loa 3 W + còi', [0, 60, 72], ['booth']],
  ['9', 'Bo chính: ESP32 + DFPlayer', [0, -12, 5], ['bay']],
  ['10', 'Mạch hạ áp 12 V → 5 V', [-200, -10, -150], ['bay']],
  ['11', 'Jack DC, công tắc, cổng USB nạp code', [-40, -40, -250], ['bay']],
];
const labels = LABEL_DEFS.map(([n, t, p, vs]) => { const d = document.createElement('div'); d.className = 'lbl'; d.innerHTML = `<span>${n}</span>${t}`; const o = new CSS2DObject(d); o.position.set(...p); o.userData.views = vs; scene.add(o); return o; });

// ---------- camera và các góc nhìn ----------
const pcam = new THREE.PerspectiveCamera(32, 1, 2, 5000);
const ocam = new THREE.OrthographicCamera(-1, 1, 1, -1, -3000, 3000);
let cam = pcam;
const controls = new OrbitControls(pcam, renderer.domElement); controls.enableDamping = true;
const VIEWS = {
  persp:   { name: 'Phối cảnh tổng thể', type: 'p', pos: [430, 470, 760], tgt: [-20, 30, 0], fov: 30, xray: false, wires: false, bay: false },
  booth:   { name: 'Chốt – nhìn xuyên vỏ', type: 'p', pos: [340, 250, 420], tgt: [0, 80, 10], fov: 30, xray: true, wires: true, bay: false },
  barrier: { name: 'Tủ barie – servo và IR an toàn', type: 'p', pos: [300, 170, -420], tgt: [25, 60, -130], fov: 30, xray: true, wires: true, bay: false },
  camera:  { name: 'Cột camera – ESP32-CAM và đèn LED', type: 'p', pos: [190, 330, 470], tgt: [80, 60, 95], fov: 28, xray: true, wires: false, bay: false },
  bay:     { name: 'Khoang điện dưới đế', type: 'p', pos: [360, 170, 460], tgt: [-50, -30, -30], fov: 30, xray: true, wires: true, bay: true },
  front:   { name: 'Hình chiếu đứng – nhìn từ đường vào', type: 'o', dir: [0, 0, 1], tgt: [-10, 90, 0], up: [0, 1, 0], xray: false, wires: false, bay: false },
  top:     { name: 'Hình chiếu bằng – nhìn từ trên', type: 'o', dir: [0, 1, 0], tgt: [-10, 0, 0], up: [0, 0, -1], xray: false, wires: false, bay: false },
  iso:     { name: 'Hình chiếu trục đo, nhìn xuyên', type: 'o', dir: [1, 0.9, 1], tgt: [-10, 40, 0], up: [0, 1, 0], xray: true, wires: true, bay: false },
};
const ORTHO_W = 760, ORTHO_H = 560;
let current = qs.get('view') && VIEWS[qs.get('view')] ? qs.get('view') : 'persp';
let xray = false;
function setXray(on) {
  xray = on;
  SHELL.forEach((m) => { m.transparent = on ? true : m.userData.baseTransparent; m.opacity = on ? 0.16 : m.userData.baseOpacity; m.depthWrite = !on; m.needsUpdate = true; });
  M.glass.opacity = on ? 0.1 : 0.28;
  document.getElementById('btn-xray') && document.getElementById('btn-xray').classList.toggle('on', on);
}
function setWires(on) { wires.visible = on; const b = document.getElementById('btn-wires'); if (b) b.classList.toggle('on', on); document.getElementById('legend').style.display = on ? 'flex' : 'none'; }
function size() {
  const w = wrap.clientWidth, h = wrap.clientHeight;
  renderer.setSize(w, h); labelRenderer.setSize(w, h);
  pcam.aspect = w / h; pcam.updateProjectionMatrix();
  const mmpp = Math.max(ORTHO_W / w, ORTHO_H / h);
  ocam.left = -w * mmpp / 2; ocam.right = w * mmpp / 2; ocam.top = h * mmpp / 2; ocam.bottom = -h * mmpp / 2; ocam.updateProjectionMatrix();
  return mmpp;
}
let MMPP = 1;
function setView(key) {
  current = key; const v = VIEWS[key];
  if (v.type === 'p') { cam = pcam; pcam.fov = v.fov; pcam.position.set(...v.pos); pcam.up.set(0, 1, 0); controls.object = pcam; controls.target.set(...v.tgt); controls.enableRotate = true; }
  else { cam = ocam; const d = new THREE.Vector3(...v.dir).normalize(); ocam.up.set(...v.up); ocam.zoom = key === 'iso' ? 0.85 : 1; ocam.position.set(...v.tgt).addScaledVector(d, 1500); controls.object = ocam; controls.target.set(...v.tgt); controls.enableRotate = key === 'iso'; }
  MMPP = size(); cam.lookAt(controls.target); controls.update();
  setXray(v.xray); setWires(v.wires);
  bikes.visible = key === 'persp' || key === 'camera';
  const showAbove = !v.bay;
  above.visible = !v.bay;
  groundMat.opacity = v.bay ? 0.12 : groundMat.opacity;
  hatch.visible = !v.bay; bottomPanel.visible = true;
  if (v.bay) { SHELL.forEach((m) => { m.opacity = 0.1; }); M.skirt.opacity = 0.35; groundMat.opacity = 0.15; }
  baseEdges.visible = !!v.bay; sight.visible = key === 'camera';
  wires.children.forEach((w) => { w.material.clippingPlanes = v.bay ? [CLIP] : []; w.material.needsUpdate = true; });
  Object.entries(dims).forEach(([vk, arr]) => arr.forEach((g) => (g.visible = vk === key)));
  labels.forEach((l) => (l.visible = showLabels && l.userData.views.includes(key)));
  document.querySelectorAll('[data-view]').forEach((b) => b.classList.toggle('on', b.dataset.view === key));
  document.getElementById('tb-view').textContent = v.name;
  document.getElementById('tb-scale').textContent = v.type === 'o' && key !== 'iso' ? 'Cùng tỉ lệ cho các hình chiếu' : 'Không theo tỉ lệ';
  document.getElementById('scalebar').style.display = v.type === 'o' && key !== 'iso' ? 'flex' : 'none';
  const note = document.getElementById('note'); if (note) note.innerHTML = NOTES[key] || '';
  if (!showAbove) {}
}
window.setView = setView;

// ghi chú lắp ráp cho từng góc nhìn
const NOTES = {
  persp: 'Vỏ mô hình theo tỉ lệ 1:10, linh kiện điện tử vẽ đúng kích thước thật. Bấm một linh kiện trong bảng để xem vị trí lắp.',
  booth: '<b>Lắp chốt:</b> 2 RC522 dán mặt trong 2 vách bên (mica 3 mm, RC522 đọc xuyên được tới ~3 cm), tâm cao 70 mm. LED WS2812 khoét lỗ Ø 6 ngay trên mặt đọc thẻ. Loa bắt 2 vít vào vách trước, khoét 12 khe 4 × 22 mm. IR xe tới gắn ở chân vách, đầu LED thò ra ngoài 3 mm. Dây đi qua lỗ Ø 16 ở sàn xuống đế.',
  barrier: '<b>Lắp tủ barie:</b> khoét vách phía làn lỗ 41 × 20 mm ở độ cao 70 mm so với mặt đảo; đẩy đầu servo qua lỗ, bắt 4 vít M3 qua tai servo vào vách. Cần barie (mica 8 × 4 × 150) bắt 2 vít vào cánh tay servo. IR an toàn thò qua lỗ ở chân tủ, cao 27 mm so với mặt đường, chỉnh biến trở để thấy xe trong khoảng 15 cm.',
  camera: '<b>Lắp cột camera:</b> ống nhôm Ø 12 cao 50 mm, dây 5 V/GND đi trong ống. Cột ở mép đảo, sau chỗ xe dừng 116 mm; ESP32-CAM đứng trong hộp mica 34 × 50 × 28 mm, tâm cao 97 mm, xoay chéo khoảng 36° vào đuôi xe. Đèn LED đặt trên tay đỡ lùi sau camera 30 mm và thấp hơn 38 mm, để ánh phản quang của biển số không dội thẳng vào ống kính. Che đèn flash có sẵn trên ESP32-CAM.',
  bay: '<b>Khoang điện:</b> đế cao 48 mm (mặt 5 mm + khung 40 mm + đáy 3 mm). Bo chính 7 × 9 cm đặt ngay dưới chốt để dây SPI tới RC522 ngắn hơn 20 cm. Mạch hạ áp, jack DC 12 V, công tắc và cổng USB nối dài (để nạp code) nằm ở mặt sau. Nắp thăm 110 × 130 mm dưới đáy để thay thẻ nhớ DFPlayer.',
  front: 'Hình chiếu đứng theo phương pháp chiếu góc thứ nhất; kích thước tính bằng mm so với mặt đường (mặt trên đế).',
  top: 'Hình chiếu bằng; kích thước ngoài đế 560 × 450 mm.',
  iso: 'Hình chiếu trục đo, vỏ trong suốt để thấy vị trí linh kiện và đường dây.',
};

// ---------- bảng linh kiện ----------
const BOM = [
  ['esp32', 'ESP32 DevKit 38 chân', '1', '55 × 28', 'Bo chính dưới đế', 'bay'],
  ['esp32cam', 'ESP32-CAM OV2640 (+ đế nạp MB)', '2', '40,5 × 27', 'Hộp camera trên cột (đế MB chỉ dùng lúc nạp)', 'camera'],
  ['rc522', 'RFID RC522 + thẻ MIFARE', '2', '60 × 40', 'Mặt trong 2 vách bên chốt', 'booth'],
  ['mg996r', 'Servo MG996R', '2', '40,7 × 19,7 × 42,9', 'Trong tủ barie, trục cao 85 mm', 'barrier'],
  ['fc51', 'Cảm biến hồng ngoại FC-51', '4', '31 × 14', '2 ở chân chốt (xe tới), 2 ở chân tủ barie (an toàn)', 'booth'],
  ['dfplayer', 'DFPlayer Mini', '1', '20 × 20', 'Trên bo chính', 'bay'],
  ['speaker', 'Loa hộp 3 W', '1', '≈ 70 × 30 × 16', 'Vách trước chốt', 'booth'],
  ['buzzer', 'Module còi chủ động', '1', '33 × 13', 'Vách trước chốt', 'booth'],
  ['ledbar', 'Đèn LED USB (cắt đầu cắm)', '2', '≈ 60 × 13', 'Tay đỡ trên cột camera', 'camera'],
  ['buck', 'Mạch hạ áp DC-DC ra 5 V', '1', '≈ 62 × 27', 'Mặt sau khoang điện', 'bay'],
  ['perfboard', 'PCB đục lỗ 2 mặt', '1', '70 × 90', 'Bo chính dưới chốt', 'bay'],
  ['mica', 'Mica trong 2 mm', '1 tấm', 'A4', 'Kính chốt, cửa sổ hộp camera', 'booth'],
  ['ws2812', 'LED WS2812 (vật tư phụ)', '2', 'Ø 10', 'Trên mặt đọc thẻ', 'booth'],
];
let hl = null;
function highlight(id) {
  if (hl) { scene.remove(hl); hl = null; }
  const objs = PARTS[id]; if (!objs) return;
  const bb = new THREE.Box3(); objs.forEach((o) => bb.expandByObject(o));
  hl = new THREE.Box3Helper(bb.expandByScalar(2), 0xff2d55); scene.add(hl);
  document.querySelectorAll('[data-part]').forEach((b) => b.classList.toggle('on', b.dataset.part === id));
}
window.highlight = highlight;

// ---------- giao diện ----------
if (UI) {
  const list = document.getElementById('views');
  [['Phối cảnh', ['persp', 'booth', 'barrier', 'camera', 'bay']], ['Hình chiếu kỹ thuật', ['front', 'top', 'iso']]].forEach(([title, keys]) => {
    const h = document.createElement('div'); h.className = 'grp'; h.textContent = title; list.appendChild(h);
    keys.forEach((k) => { const b = document.createElement('button'); b.dataset.view = k; b.textContent = VIEWS[k].name; b.onclick = () => { highlight(null); setView(k); }; list.appendChild(b); });
  });
  const bom = document.getElementById('bom');
  bom.innerHTML = BOM.map(([id, n, q, s, w]) => `<button data-part="${id}"><b>${n}</b> <em>×${q}</em><small>${s} mm · ${w}</small></button>`).join('');
  bom.querySelectorAll('button').forEach((b) => b.onclick = () => { const row = BOM.find((r) => r[0] === b.dataset.part); setView(row[5]); highlight(row[0]); });
  document.getElementById('btn-labels').onclick = (e) => { showLabels = !showLabels; e.target.classList.toggle('on', showLabels); setView(current); };
  document.getElementById('btn-labels').classList.toggle('on', showLabels);
  document.getElementById('btn-xray').onclick = () => setXray(!xray);
  document.getElementById('btn-wires').onclick = () => setWires(!wires.visible);
  document.getElementById('btn-arms').onclick = () => { armsUp = !armsUp; };
} else document.body.classList.add('noui');
if (qs.get('tb') === '0') document.body.classList.add('notb');

let armsUp = qs.get('arms') === '1';
window.addEventListener('resize', () => { MMPP = size(); });
setView(current);
if (qs.get('part')) highlight(qs.get('part'));

const sb = document.getElementById('sb-bar');
let blink = 0;
function tick() {
  arms.forEach((a) => { a.t += ((armsUp ? 1 : 0) - a.t) * 0.08; a.pivot.rotation.z = a.dir * a.t * (Math.PI / 2) * 0.97; });
  blink += 0.03; statusLeds.forEach((l, i) => l.children[1].material.emissiveIntensity = 1.2 + Math.sin(blink + i) * 0.8);
  controls.update();
  if (cam === ocam) sb.style.width = (100 / (MMPP / ocam.zoom)) + 'px';
  renderer.render(scene, cam); labelRenderer.render(scene, cam);
  requestAnimationFrame(tick);
}
tick();
window.__ready = true;
