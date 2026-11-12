/*
  Bãi giữ xe máy thông minh – firmware CAMERA BIỂN SỐ (ESP32-CAM AI-Thinker, OV2640)
  Đồ án 2 – HCMUTE · Nguyễn Tấn Huy, Võ Trương Thùy Dương · GVHD ThS. Nguyễn Văn Phúc

  Mỗi làn 1 con. Nạp 2 lần, mỗi lần đổi CAM_NAME ("cam-vao" / "cam-ra").
  Server (laptop) lấy ảnh khi có thẻ quẹt:   http://cam-vao.local/capture   (hoặc http://<IP>/capture)
  Xem trực tiếp để căn góc camera:            http://cam-vao.local:81/stream
  Trạng thái (JSON):                          http://cam-vao.local/status

  Board: "AI Thinker ESP32-CAM" (gói esp32 của Espressif). Nạp qua đế ESP32-CAM-MB (cổng micro USB)
  hoặc USB-TTL: nối IO0 xuống GND rồi nhấn RST để vào chế độ nạp, nạp xong bỏ dây IO0 và nhấn RST.
  Nguồn: 5 V ≥ 500 mA vào chân 5V. Cấp yếu thì camera hay báo "Brownout detector was triggered".
*/
#include <WiFi.h>
#include <ESPmDNS.h>
#include "esp_camera.h"
#include "esp_http_server.h"

// ===================== CẤU HÌNH =====================
const char* CAM_NAME  = "cam-vao";        // "cam-vao" cho làn vào, "cam-ra" cho làn ra
const char* WIFI_SSID = "TEN_WIFI";
const char* WIFI_PASS = "MAT_KHAU_WIFI";
const framesize_t FRAME = FRAMESIZE_SVGA; // 800 × 600: đủ chi tiết cho biển số ở 145 mm, ảnh ≈ 30–60 kB
const int JPEG_QUALITY = 12;              // 10–15; nhỏ hơn = nét hơn, ảnh nặng hơn
const bool FLIP_V = false, MIRROR_H = false;  // lật ảnh nếu camera gắn ngược

// ===================== CHÂN AI-THINKER (cố định trên bo) =====================
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22
#define FLASH_LED 4       // đèn flash trắng trên bo: tắt, vì đã có đèn LED chiếu biển số riêng
#define RED_LED 33        // LED đỏ nhỏ mặt sau, sáng khi LOW: báo đã vào Wi-Fi

httpd_handle_t webHttpd = NULL, streamHttpd = NULL;
uint32_t shots = 0;

bool initCamera() {
  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0; c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0 = Y2_GPIO_NUM; c.pin_d1 = Y3_GPIO_NUM; c.pin_d2 = Y4_GPIO_NUM; c.pin_d3 = Y5_GPIO_NUM;
  c.pin_d4 = Y6_GPIO_NUM; c.pin_d5 = Y7_GPIO_NUM; c.pin_d6 = Y8_GPIO_NUM; c.pin_d7 = Y9_GPIO_NUM;
  c.pin_xclk = XCLK_GPIO_NUM; c.pin_pclk = PCLK_GPIO_NUM; c.pin_vsync = VSYNC_GPIO_NUM; c.pin_href = HREF_GPIO_NUM;
  c.pin_sccb_sda = SIOD_GPIO_NUM; c.pin_sccb_scl = SIOC_GPIO_NUM; c.pin_pwdn = PWDN_GPIO_NUM; c.pin_reset = RESET_GPIO_NUM;
  c.xclk_freq_hz = 20000000; c.pixel_format = PIXFORMAT_JPEG;
  c.frame_size = FRAME; c.jpeg_quality = JPEG_QUALITY;
  c.fb_count = psramFound() ? 2 : 1;
  c.fb_location = psramFound() ? CAMERA_FB_IN_PSRAM : CAMERA_FB_IN_DRAM;
  c.grab_mode = CAMERA_GRAB_LATEST;      // /capture luôn trả khung mới nhất, không trả khung cũ trong bộ đệm
  esp_err_t err = esp_camera_init(&c);
  if (err != ESP_OK) { Serial.printf("Camera loi 0x%x (kiem tra cap camera, nguon 5 V)\n", err); return false; }
  sensor_t* s = esp_camera_sensor_get();
  s->set_vflip(s, FLIP_V); s->set_hmirror(s, MIRROR_H);
  return true;
}

// GET /capture -> 1 ảnh JPEG
esp_err_t captureHandler(httpd_req_t* req) {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) { httpd_resp_send_500(req); return ESP_FAIL; }
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  esp_err_t r = httpd_resp_send(req, (const char*)fb->buf, fb->len);
  Serial.printf("/capture #%lu: %u byte\n", (unsigned long)++shots, (unsigned)fb->len);
  esp_camera_fb_return(fb);
  return r;
}

// GET /status -> JSON
esp_err_t statusHandler(httpd_req_t* req) {
  char buf[200];
  snprintf(buf, sizeof(buf), "{\"name\":\"%s\",\"ip\":\"%s\",\"rssi\":%d,\"uptime\":%lu,\"shots\":%lu,\"psram\":%s}",
           CAM_NAME, WiFi.localIP().toString().c_str(), WiFi.RSSI(), (unsigned long)(millis() / 1000),
           (unsigned long)shots, psramFound() ? "true" : "false");
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, buf, strlen(buf));
}

// GET :81/stream -> MJPEG để căn góc camera bằng trình duyệt
#define BOUNDARY "frame"
esp_err_t streamHandler(httpd_req_t* req) {
  httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=" BOUNDARY);
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  char part[64];
  while (true) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) return ESP_FAIL;
    size_t hl = snprintf(part, sizeof(part), "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", (unsigned)fb->len);
    esp_err_t r = httpd_resp_send_chunk(req, "\r\n--" BOUNDARY "\r\n", strlen("\r\n--" BOUNDARY "\r\n"));
    if (r == ESP_OK) r = httpd_resp_send_chunk(req, part, hl);
    if (r == ESP_OK) r = httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);
    esp_camera_fb_return(fb);
    if (r != ESP_OK) return r;     // trình duyệt đóng tab
  }
}

void startServers() {
  httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
  httpd_uri_t cap = {"/capture", HTTP_GET, captureHandler, NULL};
  httpd_uri_t st = {"/status", HTTP_GET, statusHandler, NULL};
  if (httpd_start(&webHttpd, &cfg) == ESP_OK) { httpd_register_uri_handler(webHttpd, &cap); httpd_register_uri_handler(webHttpd, &st); }
  cfg.server_port = 81; cfg.ctrl_port += 1;      // stream chạy server riêng để /capture không bị chặn khi đang xem
  httpd_uri_t sm = {"/stream", HTTP_GET, streamHandler, NULL};
  if (httpd_start(&streamHttpd, &cfg) == ESP_OK) httpd_register_uri_handler(streamHttpd, &sm);
}

void setup() {
  Serial.begin(115200);
  pinMode(FLASH_LED, OUTPUT); digitalWrite(FLASH_LED, LOW);
  pinMode(RED_LED, OUTPUT); digitalWrite(RED_LED, HIGH);
  Serial.printf("\n=== %s ===\n", CAM_NAME);
  if (!initCamera()) { delay(3000); ESP.restart(); }
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);            // tắt tiết kiệm điện Wi-Fi: ảnh về nhanh, ổn định hơn
  WiFi.setHostname(CAM_NAME);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Ket noi Wi-Fi");
  uint32_t t = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(300); Serial.print('.');
    if (millis() - t > 20000) { Serial.println(" that bai, khoi dong lai"); ESP.restart(); }
  }
  digitalWrite(RED_LED, LOW);
  MDNS.begin(CAM_NAME);
  startServers();
  Serial.printf("\nOK  http://%s/capture   http://%s.local/capture   stream: http://%s:81/stream\n",
                WiFi.localIP().toString().c_str(), CAM_NAME, WiFi.localIP().toString().c_str());
}

void loop() {
  static uint32_t last = 0;
  if (millis() - last > 10000) {            // mất Wi-Fi quá 10 s thì khởi động lại
    last = millis();
    if (WiFi.status() != WL_CONNECTED) { Serial.println("Mat Wi-Fi, khoi dong lai"); ESP.restart(); }
  }
  delay(50);
}
