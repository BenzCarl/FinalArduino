#include <Servo.h>

const int rainSensorPin = 7;
const int servoPin = 8;
Servo myServo;

bool manualMode = false;
bool coverState = false;
bool lastRainState = false;
unsigned long rainStopTime = 0;
const unsigned long RAIN_STOP_DELAY = 5000;  // 5 second delay only when rain stops
bool waitingForRainStop = false;

void setup() {
  pinMode(rainSensorPin, INPUT);
  myServo.attach(servoPin);
  Serial.begin(9600);
  
  myServo.write(0);
  coverState = false;
  lastRainState = (digitalRead(rainSensorPin) == LOW);
  
  Serial.println("SYSTEM:Rain Detector Ready - Immediate close, 5s delay on stop");
  Serial.println("SYSTEM:Schedule support enabled - Rain protection always active");
  Serial.println("SYSTEM:GUI Connected Successfully");
  delay(1000);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  
  // Rain detection always active (even in manual mode) to protect clothes
  // In manual mode, it only closes on rain, doesn't auto-open when rain stops
  checkRainWithDelay();
  
  delay(100);
}

void checkRainWithDelay() {
  bool currentRainState = (digitalRead(rainSensorPin) == LOW);
  unsigned long currentTime = millis();
  
  // Rain detected - close immediately (no delay) - ALWAYS active to protect clothes
  if (currentRainState && !lastRainState) {
    // Rain just started - close immediately regardless of mode
    waitingForRainStop = false;
    if (!coverState) {
      myServo.write(90);
      coverState = true;
      Serial.println("NOTIFICATION:Rain detected! Cover CLOSED immediately");
      Serial.println("STATUS:Cover Status:CLOSED");
      Serial.println("STATUS:Rain Detection:RAINING");
    }
  }
  
  // Auto-open after rain stops - only in AUTO mode
  if (!manualMode) {
    // Rain stopped - start delay timer (only in AUTO mode)
    if (!currentRainState && lastRainState) {
      // Rain just stopped
      waitingForRainStop = true;
      rainStopTime = currentTime;
      Serial.println("NOTIFICATION:Rain stopped! Confirming in 5 seconds...");
    }
    
    // Check if delay period has passed after rain stopped
    if (waitingForRainStop && !currentRainState) {
      if (currentTime - rainStopTime >= RAIN_STOP_DELAY) {
        // Delay period passed, open the cover
        if (coverState) {
          myServo.write(0);
          coverState = false;
          Serial.println("NOTIFICATION:CONFIRMED_DRY - Cover OPENED");
          Serial.println("STATUS:Cover Status:OPEN");
          Serial.println("STATUS:Rain Detection:DRY");
        }
        waitingForRainStop = false;
      }
    }
  } else {
    // In manual mode, cancel any pending rain stop delay
    waitingForRainStop = false;
  }
  
  lastRainState = currentRainState;
}

void processCommand(String command) {
  command.toUpperCase();
  
  if (command == "OPEN") {
    manualMode = true;
    waitingForRainStop = false;  // Cancel any pending delay
    myServo.write(0);
    coverState = false;
    Serial.println("NOTIFICATION:MANUAL_OPENED - Cover opened manually");
    Serial.println("STATUS:Operation Mode:MANUAL");
    Serial.println("STATUS:Cover Status:OPEN");
  } 
  else if (command == "CLOSE") {
    manualMode = true;
    waitingForRainStop = false;  // Cancel any pending delay
    myServo.write(90);
    coverState = true;
    Serial.println("NOTIFICATION:MANUAL_CLOSED - Cover closed manually");
    Serial.println("STATUS:Operation Mode:MANUAL");
    Serial.println("STATUS:Cover Status:CLOSED");
  }
  else if (command == "AUTO") {
    manualMode = false;
    lastRainState = (digitalRead(rainSensorPin) == LOW);
    waitingForRainStop = false;
    Serial.println("NOTIFICATION:AUTO_MODE - Rain detection active");
    Serial.println("STATUS:Operation Mode:AUTO");
  }
  else if (command == "STATUS") {
    Serial.println("STATUS:Arduino Connection:Connected");
    Serial.println("STATUS:Operation Mode:" + String(manualMode ? "MANUAL" : "AUTO"));
    Serial.println("STATUS:Cover Status:" + String(coverState ? "CLOSED" : "OPEN"));
    
    bool currentRain = (digitalRead(rainSensorPin) == LOW);
    Serial.println("STATUS:Rain Detection:" + String(currentRain ? "RAINING" : "DRY"));
    Serial.println("STATUS:Confirmation Delay:5 seconds (rain stop only)");
  }
  else {
    Serial.println("ERROR:Unknown command: " + command);
  }
}

