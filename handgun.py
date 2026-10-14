#include <Arduino.h>
#include <FastLED.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>

// --- ハードウェアのピン設定 (ESP32-C3 SuperMini用) ---
const int IR_SEND_PIN = 4;
const int TRIGGER_PIN = 2; // 発射ボタン
const int RELOAD_PIN = 7;  // リロードスイッチ

// --- LEDテープの設定 ---
#define numberOfLEDs 60
#define controlPin 8       // LEDテープの信号ピン (元のLED_PINの位置)
CRGB leds[numberOfLEDs];

// IR送信オブジェクトの作成
IRsend irsend(IR_SEND_PIN);

// --- 送信データの設定 ---
const uint32_t SHOT_CODE = 0xEF10FE01; // 受信機と同じコード

// --- 弾薬（ゲームシステム）の設定 ---
const int MAX_AMMO = 10;    
int currentAmmo = MAX_AMMO;

// --- ボタンの状態管理 ---
int lastButtonState = HIGH;
int lastReloadState = HIGH;

// --- LED点滅用の時間管理 ---
unsigned long previousMillis = 0; 
const long blinkInterval = 250;   // 点滅スピード（0.25秒）
bool ledState = LOW;              // 弾切れ時の点滅用

void setup() {
  Serial.begin(115200);
  delay(3000);

  irsend.begin(); 

  pinMode(TRIGGER_PIN, INPUT_PULLUP);
  pinMode(RELOAD_PIN, INPUT_PULLUP);

  // FastLEDの初期化
  FastLED.addLeds<WS2812B, controlPin, GRB>(leds, numberOfLEDs);
  FastLED.setBrightness(100); // 全体の明るさ（0〜255）
  FastLED.clear();
  FastLED.show();

  Serial.println("--- レーザー銃 (LEDテープ版) 準備完了 ---");
}

void loop() {
  int currentButtonState = digitalRead(TRIGGER_PIN);
  int currentReloadState = digitalRead(RELOAD_PIN);
  
  unsigned long currentMillis = millis();

  // ==========================================
  // ① 発射の処理
  // ==========================================
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    if (currentAmmo > 0) {
      currentAmmo--;
      Serial.print("発射！ 残弾: ");
      Serial.println(currentAmmo);
     
      // 赤外線送信
      irsend.sendNEC(SHOT_CODE);

      // ★マズルフラッシュ（発射時にLEDテープ全体を一瞬白く光らせる）
      fill_solid(leds, numberOfLEDs, CRGB::White);
      FastLED.show();
      delay(50); // 50ミリ秒点灯
      FastLED.clear();
      FastLED.show();

    } else {
      Serial.println("カチッ...（弾切れ！リロードしてください）");
    }
  }

  // ==========================================
  // ② リロードの処理
  // ==========================================
  if (lastReloadState == HIGH && currentReloadState == LOW) {
    if (currentAmmo < MAX_AMMO) {
      currentAmmo = MAX_AMMO;
      Serial.println("シャコンッ！ リロード完了！");
     
      // リロード完了時はLEDテープを消灯状態にリセット
      FastLED.clear();
      FastLED.show();
      ledState = LOW;
    }
  }

  // ==========================================
  // ③ 弾切れ時のLEDテープ点滅処理
  // ==========================================
  if (currentAmmo == 0) {
    if (currentMillis - previousMillis >= blinkInterval) {
      previousMillis = currentMillis;
     
      ledState = !ledState;

      if (ledState) {
        fill_solid(leds, numberOfLEDs, CRGB::Red); // 弾切れ時は赤で点滅
      } else {
        fill_solid(leds, numberOfLEDs, CRGB::Black); // 消灯
      }
      FastLED.show();
    }
  }

  // 状態の保存
  lastButtonState = currentButtonState;
  lastReloadState = currentReloadState;

  delay(20); // チャタリング防止
}

