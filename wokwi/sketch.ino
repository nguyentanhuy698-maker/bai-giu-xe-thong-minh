/*
  Bãi giữ xe máy thông minh – firmware TRỤ ĐIỀU KHIỂN 2 LÀN (bản mô phỏng Wokwi)
  Đồ án 2 – HCMUTE · Nguyễn Tấn Huy, Võ Trương Thùy Dương · GVHD ThS. Nguyễn Văn Phúc

  Trong mô phỏng:
    - 2 nút xanh  = quẹt thẻ RC522 ở làn vào / làn ra (mỗi lần bấm là một thẻ khác)
    - 2 nút vàng  = cảm biến IR an toàn dưới cần barie (GIỮ nút = có xe đang đi qua)
    - 2 servo     = barie làn vào / làn ra
    - 2 LED màu   = đèn trạng thái trên mặt đọc thẻ
    - Serial      = thay cho loa DFPlayer (in ra câu loa sẽ đọc)
  Phần cứng thật: RC522 dùng SPI (SCK 18, MISO 19, MOSI 23, SS 5 / 4, RST 27), DFPlayer UART2 (16/17).

  Firmware KHÔNG tự quyết định mở barie: gửi UID lên server qua MQTT rồi chờ lệnh.
  Không có lệnh sau 5 s thì giữ barie đóng (an toàn khi mất mạng).
  Toàn bộ chương trình không dùng delay(): 2 làn chạy song song bằng máy trạng thái.
*/
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <Adafruit_NeoPixel.h>

// ===================== CẤU HÌNH =====================
#define OFFLINE_DEMO 0            // 1 = tự quyết định tại chỗ để thử nhanh, KHÔNG cần server
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
const char* MQTT_HOST = "broker.hivemq.com";   // broker công cộng để thử; khi làm thật đổi sang IP laptop
const uint16_t MQTT_PORT = 1883;
const char* TOPIC_ROOT = "hcmute-da2-baigiuxe";  // ĐỔI thành chuỗi riêng của nhóm để không trùng người khác

// ===================== CHÂN =====================
const int PIN_CARD_IN = 32, PIN_CARD_OUT = 33;   // nút giả lập quẹt thẻ
const int PIN_SERVO_IN = 25, PIN_SERVO_OUT = 26; // servo barie
const int PIN_IR_IN = 35, PIN_IR_OUT = 39;       // IR an toàn, LOW = có vật dưới cần
const int PIN_PIXELS = 13;                       // 2 LED WS2812 nối tiếp

// ===================== THÔNG SỐ =====================
const int ANGLE_CLOSED = 0, ANGLE_OPEN = 90;
const uint32_t SERVER_TIMEOUT_MS = 5000;   // chờ server tối đa
const uint32_t PASS_TIMEOUT_MS = 15000;    // mở barie mà không có xe qua thì tự đóng
const uint32_t CLOSE_DELAY_MS = 800;       // xe qua hẳn rồi mới hạ cần
const uint32_t SERVO_STEP_MS = 8;          // tốc độ cần barie (ms mỗi độ)
const uint32_t DEBOUNCE_MS = 30;
const uint32_t HEARTBEAT_MS = 5000;

const char* SIM_UIDS[] = {"6D:41:3E:C8", "EB:75:B7:F2", "A3:4F:19:7C", "2C:7D:43:0C", "D1:29:4A:73", "73:87:24:2F"};
const int SIM_UID_COUNT = sizeof(SIM_UIDS) / sizeof(SIM_UIDS[0]);

enum LaneState { IDLE, WAIT_SERVER, OPEN_WAIT_CAR, CAR_IN_GATE, CLOSE_DELAY, CLOSING };
const char* STATE_NAME[] = {"IDLE", "WAIT_SERVER", "OPEN_WAIT_CAR", "CAR_IN_GATE", "CLOSE_DELAY", "CLOSING"};

struct Lane {
  const char* key;      // "in" / "out"
  const char* name;     // tên hiển thị
  int pinCard, pinServo, pinIr, pixel;
  Servo servo;
  int angle, target;
  LaneState state;
  uint32_t tState, tCard, lastStep, lastBtnChange;
  int lastBtn, uidIdx;
  bool idleShown, passReported;
  String uid;
};
Lane lanes[2];

Adafruit_NeoPixel pixels(2, PIN_PIXELS, NEO_GRB + NEO_KHZ800);
WiFiClient net;
PubSubClient mqtt(net);
uint32_t lastReconnect = 0, lastBeat = 0;
#if OFFLINE_DEMO
int demoCount = 0;
const int DEMO_CAP = 3;
#endif

// ===================== TIỆN ÍCH =====================
void setPixel(Lane& L, uint8_t r, uint8_t g, uint8_t b) { pixels.setPixelColor(L.pixel, pixels.Color(r, g, b)); pixels.show(); }
void pixelIdle(Lane& L)  { setPixel(L, 0, 0, 40); }
void pixelBusy(Lane& L)  { setPixel(L, 0, 90, 255); }
void pixelOk(Lane& L)    { setPixel(L, 0, 200, 40); }
void pixelBad(Lane& L)   { setPixel(L, 255, 0, 0); }

bool irBlocked(Lane& L) { return digitalRead(L.pinIr) == LOW; }

void setState(Lane& L, LaneState s) {
  L.state = s; L.tState = millis(); L.idleShown = false;
  Serial.printf("[%s] -> %s\n", L.name, STATE_NAME[s]);
}

String topic(Lane& L, const char* leaf) { return String(TOPIC_ROOT) + "/lane/" + L.key + "/" + leaf; }

void speak(Lane& L, const char* sound) {
  // Thật: DFPlayer phát file mp3 tương ứng. Mô phỏng: in ra Serial.
  const char* text = "";
  if      (!strcmp(sound, "moi_qua"))    text = "Moi qua";
  else if (!strcmp(sound, "bai_day"))    text = "Bai da day, vui long quay lai sau";
  else if (!strcmp(sound, "gap_bao_ve")) text = "Vui long gap bao ve";
  else if (!strcmp(sound, "khong_khop")) text = "The va bien so khong khop, vui long gap bao ve";
  else if (!strcmp(sound, "loi_ket_noi"))text = "He thong dang ban, vui long gap bao ve";
  Serial.printf("[%s] LOA: \"%s\"\n", L.name, text);
}

void publishJson(const String& t, JsonDocument& doc) {
  char buf[200];
  size_t n = serializeJson(doc, buf, sizeof(buf));
  if (mqtt.connected()) mqtt.publish(t.c_str(), (const uint8_t*)buf, n);
  Serial.printf("  MQTT >> %s %s\n", t.c_str(), buf);
}

// ===================== QUYẾT ĐỊNH TỪ SERVER =====================
void applyDecision(Lane& L, bool open, const char* sound, const char* msg, bool manual) {
  // lệnh đến muộn hoặc sai làn: bỏ qua. Lệnh mở tay từ trang quản lý (manual) được nhận cả khi làn đang rảnh.
  if (!(L.state == WAIT_SERVER || (manual && open && L.state == IDLE))) return;
  Serial.printf("[%s] Quyet dinh sau %lu ms: %s %s\n", L.name, (unsigned long)(millis() - L.tCard), open ? "MO" : "TU CHOI", msg ? msg : "");
  speak(L, sound);
  if (open) { pixelOk(L); L.target = ANGLE_OPEN; setState(L, OPEN_WAIT_CAR); }
  else      { pixelBad(L); setState(L, IDLE); }
}

void onMqtt(char* t, byte* payload, unsigned int len) {
  JsonDocument doc;
  if (deserializeJson(doc, payload, len)) { Serial.println("JSON loi"); return; }
  for (int i = 0; i < 2; i++) {
    if (String(t) == topic(lanes[i], "cmd")) {
      const char* action = doc["action"] | "deny";
      applyDecision(lanes[i], !strcmp(action, "open"), doc["sound"] | "gap_bao_ve", doc["msg"] | "", doc["manual"] | false);
    }
  }
}

#if OFFLINE_DEMO
void localDecide(Lane& L) {   // chỉ để thử khi chưa có server
  bool isIn = !strcmp(L.key, "in");
  if (isIn && demoCount >= DEMO_CAP)      applyDecision(L, false, "bai_day", "(demo) bai day", false);
  else if (!isIn && demoCount <= 0)       applyDecision(L, false, "gap_bao_ve", "(demo) khong co xe trong bai", false);
  else { demoCount += isIn ? 1 : -1;      applyDecision(L, true, "moi_qua", "(demo)", false); }
}
#endif

// ===================== XỬ LÝ TỪNG LÀN =====================
void onCard(Lane& L) {
  if (L.state != IDLE) { Serial.printf("[%s] Dang xu ly xe truoc, bo qua the\n", L.name); return; }
  L.uid = SIM_UIDS[L.uidIdx]; L.uidIdx = (L.uidIdx + 1) % SIM_UID_COUNT;
  L.tCard = millis(); L.passReported = false;
  Serial.printf("\n[%s] Quet the %s\n", L.name, L.uid.c_str());
  pixelBusy(L);
  setState(L, WAIT_SERVER);
  JsonDocument doc; doc["uid"] = L.uid; doc["lane"] = L.key; doc["ms"] = L.tCard;
  publishJson(topic(L, "card"), doc);
#if OFFLINE_DEMO
  localDecide(L);
#endif
}

void reportPassed(Lane& L, bool passed) {
  JsonDocument doc; doc["passed"] = passed; doc["uid"] = L.uid;
  publishJson(topic(L, "ir"), doc);
}

void updateLane(Lane& L) {
  uint32_t now = millis();

  // 1) nút quẹt thẻ (chống dội, bắt cạnh xuống)
  int b = digitalRead(L.pinCard);
  if (b != L.lastBtn && now - L.lastBtnChange > DEBOUNCE_MS) {
    L.lastBtnChange = now; L.lastBtn = b;
    if (b == LOW) onCard(L);
  }

  // 2) cần barie chạy từng độ, không chặn chương trình
  if (L.angle != L.target && now - L.lastStep >= SERVO_STEP_MS) {
    L.lastStep = now; L.angle += (L.target > L.angle) ? 1 : -1; L.servo.write(L.angle);
  }

  // 3) máy trạng thái
  switch (L.state) {
    case IDLE:
      if (!L.idleShown && now - L.tState > 2000) { pixelIdle(L); L.idleShown = true; }   // giữ màu kết quả 2 s rồi về chờ
      break;
    case WAIT_SERVER:
      if (now - L.tState > SERVER_TIMEOUT_MS) {
        Serial.printf("[%s] Server khong tra loi -> giu barie dong\n", L.name);
        applyDecision(L, false, "loi_ket_noi", "timeout", false);
      }
      break;
    case OPEN_WAIT_CAR:
      if (irBlocked(L)) setState(L, CAR_IN_GATE);
      else if (now - L.tState > PASS_TIMEOUT_MS) {
        Serial.printf("[%s] Khong co xe qua, tu dong ha can\n", L.name);
        reportPassed(L, false); L.target = ANGLE_CLOSED; setState(L, CLOSING);
      }
      break;
    case CAR_IN_GATE:
      if (!irBlocked(L)) setState(L, CLOSE_DELAY);
      break;
    case CLOSE_DELAY:
      if (irBlocked(L)) setState(L, CAR_IN_GATE);
      else if (now - L.tState > CLOSE_DELAY_MS) {
        Serial.printf("[%s] IR: xe da qua, ha can\n", L.name);
        if (!L.passReported) { reportPassed(L, true); L.passReported = true; }   // chỉ báo 1 lần cho mỗi lượt
        L.target = ANGLE_CLOSED; setState(L, CLOSING);
      }
      break;
    case CLOSING:
      if (irBlocked(L)) {                            // an toàn: có vật dưới cần -> nâng lại
        Serial.printf("[%s] AN TOAN: co vat duoi can, nang lai\n", L.name);
        L.target = ANGLE_OPEN; setState(L, CAR_IN_GATE);
      } else if (L.angle == ANGLE_CLOSED) {
        setState(L, IDLE); pixelIdle(L); L.idleShown = true;
      }
      break;
  }
}

// ===================== MẠNG =====================
void ensureNetwork() {
#if !OFFLINE_DEMO
  if (WiFi.status() != WL_CONNECTED) return;          // WiFi tự kết nối lại ở nền
  if (mqtt.connected()) { mqtt.loop(); return; }
  if (millis() - lastReconnect < 3000) return;          // thử lại mỗi 3 s, không chặn 2 làn
  lastReconnect = millis();
  String id = "pillar-" + String((uint32_t)ESP.getEfuseMac(), HEX);
  Serial.printf("Ket noi MQTT %s ... ", MQTT_HOST);
  if (mqtt.connect(id.c_str())) {
    Serial.println("OK");
    for (int i = 0; i < 2; i++) mqtt.subscribe(topic(lanes[i], "cmd").c_str());
  } else Serial.printf("loi %d\n", mqtt.state());
#endif
}

void heartbeat() {
  if (millis() - lastBeat < HEARTBEAT_MS) return;
  lastBeat = millis();
  if (!mqtt.connected()) return;
  JsonDocument doc; doc["rssi"] = WiFi.RSSI(); doc["uptime"] = millis() / 1000;
  doc["in"] = STATE_NAME[lanes[0].state]; doc["out"] = STATE_NAME[lanes[1].state];
  char buf[160]; size_t n = serializeJson(doc, buf, sizeof(buf));
  mqtt.publish((String(TOPIC_ROOT) + "/pillar/status").c_str(), (const uint8_t*)buf, n);
}

// ===================== SETUP / LOOP =====================
void initLane(Lane& L, const char* key, const char* name, int pinCard, int pinServo, int pinIr, int pixel) {
  L.key = key; L.name = name; L.pinCard = pinCard; L.pinServo = pinServo; L.pinIr = pinIr; L.pixel = pixel;
  L.angle = L.target = ANGLE_CLOSED; L.state = IDLE; L.tState = L.tCard = L.lastStep = L.lastBtnChange = 0;
  L.lastBtn = HIGH; L.uidIdx = 0; L.idleShown = true; L.passReported = false;   // 2 làn dùng chung danh sách thẻ: xe vào trước thì ra trước
  pinMode(pinCard, INPUT_PULLUP);
  pinMode(pinIr, INPUT);                    // GPIO35/39 không có điện trở kéo lên trong: dùng điện trở ngoài
  L.servo.setPeriodHertz(50);
  L.servo.attach(pinServo, 500, 2400);
  L.servo.write(ANGLE_CLOSED);
}

void setup() {
  Serial.begin(115200);
  pixels.begin();
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  initLane(lanes[0], "in", "LAN VAO", PIN_CARD_IN, PIN_SERVO_IN, PIN_IR_IN, 0);
  initLane(lanes[1], "out", "LAN RA", PIN_CARD_OUT, PIN_SERVO_OUT, PIN_IR_OUT, 1);
  pixelIdle(lanes[0]); pixelIdle(lanes[1]);
  Serial.println("\n=== Tru dieu khien 2 lan - san sang ===");
#if OFFLINE_DEMO
  Serial.println("Che do OFFLINE_DEMO: tu quyet dinh tai cho, suc chua demo = 3 xe");
#else
  WiFi.begin(WIFI_SSID, WIFI_PASS);           // không chờ: 2 làn vẫn chạy trong lúc kết nối
  WiFi.setAutoReconnect(true);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);                    // lệnh từ server kèm biển số, giờ vào, phí: dài hơn 256 byte mặc định
  mqtt.setCallback(onMqtt);
  Serial.printf("Topic goc: %s\n", TOPIC_ROOT);
#endif
}

void loop() {
  ensureNetwork();
  updateLane(lanes[0]);
  updateLane(lanes[1]);
  heartbeat();
}
