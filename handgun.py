#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>

// --- ハードウェアのピン設定 (ESP32-C3 SuperMini用) ---
const int IR_SEND_PIN = 4;
const int TRIGGER_PIN = 2; // 発射ボタン
const int LED_PIN = 8;     // ★ESP32-C3基板上の青色LEDを使用

// IR送信オブジェクトの作成
IRsend irsend(IR_SEND_PIN);

// --- 送信データの設定 ---
const uint32_t SHOT_CODE = 0xEF10FE01; // ★受信機と同じコード

// --- ボタンの状態管理 ---
int lastButtonState = HIGH;

void setup() {
  Serial.begin(115200);
  delay(3000); // ★シリアル通信安定化のための待機

  irsend.begin(); // ★IR送信の初期化
 
  pinMode(TRIGGER_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT); // ★LEDピンを出力に設定
 
  digitalWrite(LED_PIN, LOW); // 初期は消灯

  Serial.println("--- レーザー 射出準備完了 (無限弾薬モード) ---");
}

void loop() {
  int currentButtonState = digitalRead(TRIGGER_PIN);

  // ==========================================
  // ① 発射の処理
  // ==========================================
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    Serial.println("発射！ (無限弾)");
     
    // ★赤外線送信 (IRremoteESP8266仕様)
    irsend.sendNEC(SHOT_CODE);

    // ★発射時のLEDフラッシュ（マズルフラッシュ）
    digitalWrite(LED_PIN, HIGH); // 一瞬だけ点灯させる
    delay(50);                   // 50ミリ秒だけ待つ
    digitalWrite(LED_PIN, LOW);  // すぐに消す
  }

  // 状態の保存
  lastButtonState = currentButtonState;

  delay(20); // チャタリング防止
}

