#include <LiquidCrystal.h>

// LCD Pins: RS, E, D4, D5, D6, D7
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

// First Rotary Encoder (Timer Control)
#define CLK 2
#define DT 3
#define SW 4

// Pushbutton to switch screen views
#define BUTTON_PIN 6

// Buzzer and LED
#define BUZZER_PIN 12
#define LED_PIN 13

// Thermistor analog pin
#define THERMISTOR_PIN A0

// ----- Globals -----
int timerSeconds = 0;
int lastClkState;
bool isCountingDown = false;
unsigned long lastUpdate = 0;
bool buttonPressed = false;

// View state
int screenView = 0;  // 0 = timer, 1 = temperature
bool lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

void setup() {
  // Rotary encoder setup
  pinMode(CLK, INPUT);
  pinMode(DT, INPUT);
  pinMode(SW, INPUT_PULLUP);

  // Buzzer and LED setup
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Pushbutton setup
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // LCD setup
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Time Ready");
  lcd.setCursor(0, 1);
  lcd.print("Time: 00:00");

  lastClkState = digitalRead(CLK);
}

void loop() {
  handleScreenToggle();

  if (screenView == 0) {
    // -------- TIMER WINDOW --------
    if (!isCountingDown) {
      handleEncoder();
      if (digitalRead(SW) == LOW && !buttonPressed) {
        buttonPressed = true;
        if (timerSeconds > 0) {
          isCountingDown = true;
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Timer Ready");
          delay(1000);
        }
      } else if (digitalRead(SW) == HIGH) {
        buttonPressed = false;
      }
      showTime(timerSeconds);
    } else {
      if (millis() - lastUpdate >= 1000) {
        lastUpdate = millis();
        if (timerSeconds > 0) {
          timerSeconds--;
          showTime(timerSeconds);
        } else {
          isCountingDown = false;
          buzzAlert();
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Time's Up!");
          delay(1000);
        }
      }
    }
  }

  else if (screenView == 1) {
    // -------- TEMPERATURE WINDOW --------
    float voltage = analogRead(THERMISTOR_PIN) * (5.0 / 1023.0);
    float temperatureC = (voltage - 0.5) * 100;  // Adjust based on your thermistor specs

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp Reading:");
    lcd.setCursor(0, 1);
    lcd.print(temperatureC, 2);
    lcd.print(" C");

    delay(500); // Refresh rate
  }
}

// ---------- FUNCTIONS ----------

void handleEncoder() {
  int currentClk = digitalRead(CLK);
  if (currentClk != lastClkState && currentClk == LOW) {
    if (digitalRead(DT) != currentClk) {
      timerSeconds += 5;
    } else {
      timerSeconds -= 5;
    }
    timerSeconds = constrain(timerSeconds, 0, 300);
  }
  lastClkState = currentClk;
}

void showTime(int secondsLeft) {
  int minutes = secondsLeft / 60;
  int seconds = secondsLeft % 60;

  lcd.setCursor(0, 1);
  lcd.print("Time: ");
  if (minutes < 10) lcd.print("0");
  lcd.print(minutes);
  lcd.print(":");
  if (seconds < 10) lcd.print("0");
  lcd.print(seconds);
  lcd.print("    ");  // clear leftover chars
}

void buzzAlert() {
  for (int i = 0; i < 8; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }

  // Flash LED until knob pressed again
  while (true) {
    digitalWrite(LED_PIN, HIGH);
    delay(300);
    digitalWrite(LED_PIN, LOW);
    delay(300);

    if (digitalRead(SW) == LOW) {
      delay(50);
      if (digitalRead(SW) == LOW) {
        while (digitalRead(SW) == LOW);
        break;
      }
    }
  }

  digitalWrite(LED_PIN, LOW);
}

void handleScreenToggle() {
  int reading = digitalRead(BUTTON_PIN);

  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading == LOW && lastButtonState == HIGH) {
      screenView = (screenView + 1) % 2;  // Toggle between 0 and 1
    }
  }

  lastButtonState = reading;
}