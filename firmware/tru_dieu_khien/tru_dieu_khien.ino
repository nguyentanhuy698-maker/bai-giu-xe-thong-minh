/*
  Bãi giữ xe máy thông minh – firmware TRỤ ĐIỀU KHIỂN 2 LÀN (bản PHẦN CỨNG THẬT)
  Đồ án 2 – HCMUTE · Nguyễn Tấn Huy, Võ Trương Thùy Dương · GVHD ThS. Nguyễn Văn Phúc

  Cùng logic với bản Wokwi (wokwi/sketch.ino), chỉ thay nút giả lập bằng linh kiện thật:
    - 2 đầu đọc RC522 chung bus SPI     (SCK 18, MISO 19, MOSI 23, SS 5 / 4, RST 27)
    - 2 servo MG996R làm barie           (GPIO25 / 26, nguồn 5 V riêng)
    - 2 IR phát hiện xe tới              (GPIO34 / 36)
    - 2 IR an toàn dưới cần barie        (GPIO35 / 39)
    - DFPlayer Mini + loa 3 W            (UART2: GPIO16 = RX2 nối TX DFPlayer, GPIO17 = TX2 qua 1 kΩ nối RX DFPlayer)
    - Module còi chủ động 3 chân VCC/I-O/GND (GPIO14, cấp 3,3 V)
    - 2 LED WS2812 trạng thái            (GPIO13)

  Firmware KHÔNG tự quyết định mở barie: gửi UID lên server qua MQTT rồi chờ lệnh.
  Không có lệnh sau 5 s thì giữ barie đóng. Không dùng delay(): 2 làn chạy song song bằng máy trạng thái.

  Thư viện (Arduino IDE → Library Manager):
    MFRC522 (GithubCommunity), PubSubClient (Nick O'Leary), ArduinoJson 7.x (Benoit Blanchon),
    ESP32Servo (Kevin Harrington), Adafruit NeoPixel, DFRobotDFPlayerMini
  Board: "ESP32 Dev Module" (gói esp32 của Espressif).

  Thử từng khối khi chưa có server: mở Serial Monitor 115200, gõ lệnh rồi Enter (gõ "h" để xem danh sách).
*/
#include <WiFi.h>
#include <SPI.h>
#include <MFRC522.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <Adafruit_NeoPixel.h>
#include <DFRobotDFPlayerMini.h>

// ===================== CẤU HÌNH (sửa cho đúng mạng của nhóm) =====================
#define OFFLINE_DEMO 0                 // 1 = ESP32 tự quyết định tại chỗ, không cần server (để thử mạch)
#define REQUIRE_CAR_FOR_CARD 0         // 1 = chỉ nhận thẻ khi IR "xe tới" đang thấy xe
#define BUZZER_ACTIVE_LOW 1            // module còi 3 chân (transistor PNP sẵn trên bo) kêu khi I/O = LOW; còi tự nối qua NPN thì đặt 0
const char* WIFI_SSID = "TEN_WIFI";
const char* WIFI_PASS = "MAT_KHAU_WIFI";
const char* MQTT_HOST = "192.168.1.10";       // IP laptop chạy Mosquitto (xem bằng ipconfig)
const uint16_t MQTT_PORT = 1883;
const char* MQTT_USER = "";                   // để trống nếu Mosquitto cho phép vào không cần tài khoản
const char* MQTT_PASS = "";
const char* TOPIC_ROOT = "hcmute-da2-baigiuxe"; // phải trùng server_mock.py và trang quản lý

// ===================== CHÂN (theo bảng nối chân trong báo cáo) =====================
const int PIN_SPI_SCK = 18, PIN_SPI_MISO = 19, PIN_SPI_MOSI = 23;
const int PIN_RFID_SS_IN = 5, PIN_RFID_SS_OUT = 4, PIN_RFID_RST = 27;
const int PIN_SERVO_IN = 25, PIN_SERVO_OUT = 26;
const int PIN_ARRIVE_IN = 34, PIN_ARRIVE_OUT = 36;   // IR xe tới, LOW = có xe
const int PIN_IR_IN = 35, PIN_IR_OUT = 39;           // IR an toàn dưới cần, LOW = có vật
const int PIN_DF_RX = 16, PIN_DF_TX = 17;            // UART2 của ESP32
const int PIN_BUZZER = 14;
const int PIN_PIXELS = 13;

// ===================== THÔNG SỐ =====================
const int ANGLE_CLOSED = 0, ANGLE_OPEN = 90;   // chỉnh theo cách gắn cần barie trên mô hình
const uint32_t SERVER_TIMEOUT_MS = 5000;       // chờ server tối đa
const uint32_t PASS_TIMEOUT_MS = 15000;        // mở barie mà không có xe qua thì tự đóng
const uint32_t CLOSE_DELAY_MS = 800;           // xe qua hẳn rồi mới hạ cần
const uint32_t SERVO_STEP_MS = 8;              // tốc độ cần barie (ms mỗi độ)
const uint32_t RFID_POLL_MS = 60;              // mỗi đầu đọc được hỏi 1 lần mỗi 120 ms
const uint32_t SAME_CARD_MS = 3000;            // thẻ để yên trên đầu đọc: không tính là quẹt lần nữa
const uint32_t ARRIVE_DEBOUNCE_MS = 200;
const uint32_t HEARTBEAT_MS = 5000;
const uint8_t DF_VOLUME = 25;                  // 0..30

// Âm thanh: thẻ nhớ microSD có thư mục /mp3 chứa 0001.mp3 ... 0005.mp3 (tạo bằng tools/tao_am_thanh.py)
struct Sound { const char* key; uint8_t track; const char* text; };
const Sound SOUNDS[] = {
  {"moi_qua",     1, "Moi qua"},
  {"bai_day",     2, "Bai da day, vui long quay lai sau"},
  {"gap_bao_ve",  3, "Vui long gap bao ve"},
  {"khong_khop",  4, "The va bien so khong khop, vui long gap bao ve"},
  {"loi_ket_noi", 5, "He thong dang ban, vui long gap bao ve"},
};
const int SOUND_COUNT = sizeof(SOUNDS) / sizeof(SOUNDS[0]);

enum LaneState { IDLE, WAIT_SERVER, OPEN_WAIT_CAR, CAR_IN_GATE, CLOSE_DELAY, CLOSING };
const char* STATE_NAME[] = {"IDLE", "WAIT_SERVER", "OPEN_WAIT_CAR", "CAR_IN_GATE", "CLOSE_DELAY", "CLOSING"};

struct Lane {
  const char* key;      // "in" / "out"
  const char* name;     // tên hiển thị trên Serial
  MFRC522* rfid;
  bool rfidOk;
  int pinServo, pinIr, pinArrive, pixel;
  Servo servo;
  int angle, target;
  LaneState state;
  uint32_t tState, tCard, lastStep, tArriveChange, tLastUid;
  bool idleShown, passReported, carHere, arriveRaw;
  String uid, lastUid;
};
Lane lanes[2];

MFRC522 rfidIn(PIN_RFID_SS_IN, PIN_RFID_RST);
MFRC522 rfidOut(PIN_RFID_SS_OUT, PIN_RFID_RST);
Adafruit_NeoPixel pixels(2, PIN_PIXELS, NEO_GRB + NEO_KHZ800);
HardwareSerial dfSerial(2);
DFRobotDFPlayerMini dfp;
bool dfOk = false;
WiFiClient net;
PubSubClient mqtt(net);
uint32_t lastReconnect = 0, lastBeat = 0, lastPoll = 0;
int pollIdx = 0;
// còi kêu theo nhịp mà không chặn chương trình
int beepLeft = 0; bool beepOn = false; uint32_t tBeep = 0;
#if OFFLINE_DEMO
int demoCount = 0;
const int DEMO_CAP = 3;
#endif

// ===================== TIỆN ÍCH =====================
void setPixel(Lane& L, uint8_t r, uint8_t g, uint8_t b) { pixels.setPixelColor(L.pixel, pixels.Color(r, g, b)); pixels.show(); }
void pixelIdle(Lane& L) { setPixel(L, 0, 0, 40); }
void pixelBusy(Lane& L) { setPixel(L, 0, 90, 255); }
void pixelOk(Lane& L)   { setPixel(L, 0, 200, 40); }
void pixelBad(Lane& L)  { setPixel(L, 255, 0, 0); }

bool irBlocked(Lane& L) { return digitalRead(L.pinIr) == LOW; }

void setState(Lane& L, LaneState s) {
  L.state = s; L.tState = millis(); L.idleShown = false;
  Serial.printf("[%s] -> %s\n", L.name, STATE_NAME[s]);
}

String topic(Lane& L, const char* leaf) { return String(TOPIC_ROOT) + "/lane/" + L.key + "/" + leaf; }

void buzzerWrite(bool on) { digitalWrite(PIN_BUZZER, (on != (bool)BUZZER_ACTIVE_LOW) ? HIGH : LOW); }

void beep(int times) { beepLeft = times * 2; beepOn = false; tBeep = 0; }

void updateBuzzer() {
  if (beepLeft <= 0) return;
  if (millis() - tBeep < 150) return;
  tBeep = millis(); beepOn = !beepOn; beepLeft--;
  buzzerWrite(beepOn);
  if (beepLeft == 0) buzzerWrite(false);
}

void speak(Lane& L, const char* sound) {
  for (int i = 0; i < SOUND_COUNT; i++) {
    if (strcmp(SOUNDS[i].key, sound)) continue;
    Serial.printf("[%s] LOA %04d.mp3: \"%s\"\n", L.name, SOUNDS[i].track, SOUNDS[i].text);
    if (dfOk) dfp.playMp3Folder(SOUNDS[i].track);
    return;
  }
  Serial.printf("[%s] LOA: khong co file cho \"%s\"\n", L.name, sound);
}

void publishJson(const String& t, JsonDocument& doc) {
  char buf[256];
  size_t n = serializeJson(doc, buf, sizeof(buf));
  if (mqtt.connected()) mqtt.publish(t.c_str(), (const uint8_t*)buf, n);
  Serial.printf("  MQTT >> %s %s\n", t.c_str(), buf);
}

String uidToString(MFRC522::Uid& u) {
  String s;
  for (byte i = 0; i < u.size; i++) {
    if (i) s += ':';
    if (u.uidByte[i] < 0x10) s += '0';
    s += String(u.uidByte[i], HEX);
  }
  s.toUpperCase();
  return s;
}

// ===================== QUYẾT ĐỊNH TỪ SERVER =====================
void applyDecision(Lane& L, bool open, const char* sound, const char* msg, bool manual) {
  // lệnh đến muộn hoặc sai làn: bỏ qua. Lệnh mở tay từ trang quản lý (manual) được nhận cả khi làn đang rảnh.
  if (!(L.state == WAIT_SERVER || (manual && open && L.state == IDLE))) return;
  Serial.printf("[%s] Quyet dinh sau %lu ms: %s %s\n", L.name, (unsigned long)(millis() - L.tCard), open ? "MO" : "TU CHOI", msg ? msg : "");
  speak(L, sound);
  if (open) { pixelOk(L); L.target = ANGLE_OPEN; setState(L, OPEN_WAIT_CAR); }
  else {
    pixelBad(L); setState(L, IDLE);
    if (!strcmp(sound, "khong_khop")) beep(3);       // thẻ và biển số không khớp: còi + đèn đỏ
  }
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
void localDecide(Lane& L) {   // chỉ để thử mạch khi chưa có server
  bool isIn = !strcmp(L.key, "in");
  if (isIn && demoCount >= DEMO_CAP)      applyDecision(L, false, "bai_day", "(demo) bai day", false);
  else if (!isIn && demoCount <= 0)       applyDecision(L, false, "gap_bao_ve", "(demo) khong co xe trong bai", false);
  else { demoCount += isIn ? 1 : -1;      applyDecision(L, true, "moi_qua", "(demo)", false); }
}
#endif

// ===================== XỬ LÝ TỪNG LÀN =====================
void onCard(Lane& L, const String& uid) {
  if (L.state != IDLE) { Serial.printf("[%s] Dang xu ly xe truoc, bo qua the %s\n", L.name, uid.c_str()); return; }
#if REQUIRE_CAR_FOR_CARD
  if (!L.carHere) { Serial.printf("[%s] Chua co xe truoc barie, bo qua the %s\n", L.name, uid.c_str()); return; }
#endif
  L.uid = uid; L.tCard = millis(); L.passReported = false;
  Serial.printf("\n[%s] Quet the %s\n", L.name, uid.c_str());
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

// Hỏi lần lượt từng đầu đọc (2 RC522 chung SPI, mỗi lần chỉ nói chuyện với 1 con)
void pollRfid() {
  if (millis() - lastPoll < RFID_POLL_MS) return;
  lastPoll = millis();
  Lane& L = lanes[pollIdx]; pollIdx ^= 1;
  if (!L.rfidOk) return;
  MFRC522& r = *L.rfid;
  if (!r.PICC_IsNewCardPresent() || !r.PICC_ReadCardSerial()) return;
  String uid = uidToString(r.uid);
  r.PICC_HaltA(); r.PCD_StopCrypto1();
  if (uid == L.lastUid && millis() - L.tLastUid < SAME_CARD_MS) { L.tLastUid = millis(); return; }
  L.lastUid = uid; L.tLastUid = millis();
  onCard(L, uid);
}

// IR "xe tới": báo server để có thể chụp sẵn ảnh trước khi khách quẹt thẻ
void updateArrive(Lane& L) {
  bool raw = digitalRead(L.pinArrive) == LOW;
  if (raw != L.arriveRaw) { L.arriveRaw = raw; L.tArriveChange = millis(); }
  if (raw != L.carHere && millis() - L.tArriveChange > ARRIVE_DEBOUNCE_MS) {
    L.carHere = raw;
    JsonDocument doc; doc["car"] = raw;
    publishJson(topic(L, "arrive"), doc);
  }
}

void updateLane(Lane& L) {
  uint32_t now = millis();
  updateArrive(L);

  // cần barie chạy từng độ, không chặn chương trình
  if (L.angle != L.target && now - L.lastStep >= SERVO_STEP_MS) {
    L.lastStep = now; L.angle += (L.target > L.angle) ? 1 : -1; L.servo.write(L.angle);
  }

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
  Serial.printf("Ket noi MQTT %s:%u ... ", MQTT_HOST, MQTT_PORT);
  bool ok = strlen(MQTT_USER) ? mqtt.connect(id.c_str(), MQTT_USER, MQTT_PASS) : mqtt.connect(id.c_str());
  if (ok) {
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
  doc["rfid_in"] = lanes[0].rfidOk; doc["rfid_out"] = lanes[1].rfidOk; doc["audio"] = dfOk;
  char buf[200]; size_t n = serializeJson(doc, buf, sizeof(buf));
  mqtt.publish((String(TOPIC_ROOT) + "/pillar/status").c_str(), (const uint8_t*)buf, n);
}

// ===================== THỬ TỪNG KHỐI QUA SERIAL =====================
void printHelp() {
  Serial.println(F("Lenh Serial (go roi Enter):"));
  Serial.println(F("  v / r       : gia lap quet the o lan vao / lan ra (the TEST:01, TEST:02)"));
  Serial.println(F("  mv / mr     : mo barie lan vao / lan ra nhu lenh mo tay"));
  Serial.println(F("  s1 .. s5    : phat thu file am thanh 0001..0005"));
  Serial.println(F("  b           : thu coi (3 tieng)"));
  Serial.println(F("  i           : in trang thai cam bien, dau doc the, mang"));
  Serial.println(F("  h           : in lai danh sach lenh"));
}

void printStatus() {
  for (int i = 0; i < 2; i++) {
    Lane& L = lanes[i];
    Serial.printf("[%s] RC522 %s | xe toi: %s | IR an toan: %s | servo %d do | %s\n", L.name,
                  L.rfidOk ? "OK" : "KHONG THAY", L.carHere ? "CO XE" : "trong", irBlocked(L) ? "CO VAT" : "trong",
                  L.angle, STATE_NAME[L.state]);
  }
  Serial.printf("DFPlayer: %s | WiFi: %s (%s, %d dBm) | MQTT: %s\n", dfOk ? "OK" : "KHONG THAY",
                WiFi.status() == WL_CONNECTED ? "da noi" : "chua noi", WiFi.localIP().toString().c_str(), WiFi.RSSI(),
                mqtt.connected() ? "da noi" : "chua noi");
}

void handleSerial() {
  if (!Serial.available()) return;
  String c = Serial.readStringUntil('\n'); c.trim(); c.toLowerCase();
  if (c == "v") onCard(lanes[0], "TEST:01");
  else if (c == "r") onCard(lanes[1], "TEST:02");
  else if (c == "mv") applyDecision(lanes[0], true, "moi_qua", "mo tay qua Serial", true);
  else if (c == "mr") applyDecision(lanes[1], true, "moi_qua", "mo tay qua Serial", true);
  else if (c.length() == 2 && c[0] == 's' && c[1] >= '1' && c[1] <= '5') { int k = c[1] - '0'; speak(lanes[0], SOUNDS[k - 1].key); }
  else if (c == "b") beep(3);
  else if (c == "i") printStatus();
  else if (c.length()) printHelp();
}

// ===================== SETUP / LOOP =====================
// 2 RC522 chung chân RST: PCD_Init() của thư viện để chân RST ở INPUT (thả nổi). Chân trôi về LOW là cả 2 đầu đọc
// cùng vào chế độ ngủ, đọc thẻ lúc được lúc không. Vì vậy luôn kéo RST lên HIGH trước và sau mỗi lần khởi tạo.
void holdRfidRst() { pinMode(PIN_RFID_RST, OUTPUT); digitalWrite(PIN_RFID_RST, HIGH); }

bool initRfid(MFRC522& r, const char* name) {
  holdRfidRst();
  r.PCD_Init();
  holdRfidRst();
  byte v = r.PCD_ReadRegister(MFRC522::VersionReg);
  bool ok = (v == 0x91 || v == 0x92 || v == 0x88 || v == 0x12);   // 0x00 hoặc 0xFF = chưa nối dây / sai chân SS
  Serial.printf("RC522 %s: version 0x%02X -> %s\n", name, v, ok ? "OK" : "KHONG THAY (kiem tra day, nguon 3,3 V, chan SS)");
  return ok;
}

void initLane(Lane& L, const char* key, const char* name, MFRC522* rfid, int pinServo, int pinIr, int pinArrive, int pixel) {
  L.key = key; L.name = name; L.rfid = rfid; L.pinServo = pinServo; L.pinIr = pinIr; L.pinArrive = pinArrive; L.pixel = pixel;
  L.angle = L.target = ANGLE_CLOSED; L.state = IDLE; L.tState = L.tCard = L.lastStep = L.tArriveChange = L.tLastUid = 0;
  L.idleShown = true; L.passReported = false; L.carHere = false; L.arriveRaw = false;
  pinMode(pinIr, INPUT);          // GPIO34–39 không có điện trở kéo lên trong: module IR đã có sẵn trên board
  pinMode(pinArrive, INPUT);
  L.servo.setPeriodHertz(50);
  L.servo.attach(pinServo, 500, 2400);
  L.servo.write(ANGLE_CLOSED);
  L.rfidOk = initRfid(*rfid, name);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);
  pinMode(PIN_BUZZER, OUTPUT); buzzerWrite(false);
  pixels.begin();
  SPI.begin(PIN_SPI_SCK, PIN_SPI_MISO, PIN_SPI_MOSI);
  pinMode(PIN_RFID_SS_IN, OUTPUT); digitalWrite(PIN_RFID_SS_IN, HIGH);    // nhả cả 2 đầu đọc khỏi bus trước khi khởi tạo
  pinMode(PIN_RFID_SS_OUT, OUTPUT); digitalWrite(PIN_RFID_SS_OUT, HIGH);
  pinMode(PIN_RFID_RST, OUTPUT); digitalWrite(PIN_RFID_RST, LOW); delay(5);  // reset cứng cả 2 RC522 một lần
  digitalWrite(PIN_RFID_RST, HIGH); delay(50);
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  Serial.println("\n=== Tru dieu khien 2 lan (phan cung that) ===");
  initLane(lanes[0], "in", "LAN VAO", &rfidIn, PIN_SERVO_IN, PIN_IR_IN, PIN_ARRIVE_IN, 0);
  initLane(lanes[1], "out", "LAN RA", &rfidOut, PIN_SERVO_OUT, PIN_IR_OUT, PIN_ARRIVE_OUT, 1);
  pixelIdle(lanes[0]); pixelIdle(lanes[1]);

  dfSerial.begin(9600, SERIAL_8N1, PIN_DF_RX, PIN_DF_TX);
  dfOk = dfp.begin(dfSerial, true, true);
  if (dfOk) dfp.volume(DF_VOLUME);
  Serial.printf("DFPlayer: %s\n", dfOk ? "OK" : "KHONG THAY (kiem tra the nho, day RX/TX, dien tro 1 kOhm)");

#if OFFLINE_DEMO
  Serial.println("Che do OFFLINE_DEMO: tu quyet dinh tai cho, suc chua demo = 3 xe");
#else
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);           // không chờ: 2 làn vẫn chạy trong lúc kết nối
  WiFi.setAutoReconnect(true);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);                    // lệnh từ server kèm biển số, giờ vào, phí: dài hơn 256 byte mặc định
  mqtt.setCallback(onMqtt);
  Serial.printf("Topic goc: %s\n", TOPIC_ROOT);
#endif
  printHelp();
}

void loop() {
  ensureNetwork();
  pollRfid();
  updateLane(lanes[0]);
  updateLane(lanes[1]);
  updateBuzzer();
  heartbeat();
  handleSerial();
}
