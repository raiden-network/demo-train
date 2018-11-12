#include <avr/wdt.h>

// defines pins numbers
const int trigPin = 6;
const int echoPin = 7;
// defines variables
long duration;
float distance;
bool measuring;
int value = 9;

// 0: Power is Off, 
// 1: Power is On
int powerSensor = 0;

// 0: not measuring,
// 1: object is not close,
// 2: object is close
int barrierSensor = 0;

// 0: request Sensor Data/'ACK Signal' 
// 1: power Track off
// 2: power Track on
// 3: turn barrier measuring off
// 4: turn barrier measuring on
// 5: Keepalive signal
// 6: request arduino reset
int inByte = 0;

int maxTriggerDistance = 20;

void setup() {
 pinMode(3, OUTPUT); //make the pin (3) as output
 pinMode(13, OUTPUT); //make the LED pin (13) as output
 pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
 pinMode(echoPin, INPUT); // Sets the echoPin as an Input
 Serial.begin(9600); // Starts the serial communication
 measuring = false;
 establishContact();
 //Aktiviere Watchdog mit 8s Zeitkonstante
 wdt_enable(WDTO_8S);
}

void loop() {
 int data;
  
 if (Serial.available() > 0){
   inByte = Serial.read();

   switch (inByte) {
    //  send Sensor data
    case 0:
      updateSensorData();
      delayMicroseconds(10);
      sendAck();
      sendSensorData();
      break;
    //  Turn Train power off
    case 1:
      turnPowerOff();
      sendAck();
      break;
      //  Turn Train power on
    case 2:
      turnPowerOn();
      sendAck();
      break;
    case 3:
      measuring = false;
      sendAck();
      break;
    case 4:
      measuring = true;
      sendAck();
      break;
    case 5:
      // received keepalive, reset the watchdog timer
      wdt_reset();
      sendAck();
      break;
    default:
      break;
  }
}

 if (measuring == true){
   int value = getAverage();
   if (value < maxTriggerDistance){
     barrierSensor = 2;
   }
   else {
     barrierSensor = 1;
   }
 }
 else {
   barrierSensor = 0;
   delayMicroseconds(10);
 }
}

void establishContact() {
  while (Serial.available() <= 0) {
     sendHandshake();
    delay(300);
  }

  while (true) {
   if (Serial.available() > 0){
     inByte = Serial.read();
//   we expect the ACK from the client
     if (inByte == 0){
      sendAck();
      break;
     }
    }
  }
}

void sendSensorData() {
  Serial.write(powerSensor);
  Serial.write(barrierSensor);
}

void sendAck() {
  Serial.write('A'); 
}

void sendHandshake(){
  Serial.write('H'); 
}

void turnPowerOff() {
  digitalWrite(3, LOW);
}

void turnPowerOn() {
  digitalWrite(3, HIGH);
}

void updateSensorData() {
  if (digitalRead(3) == HIGH) {
    powerSensor = 1;
  } else {
    powerSensor = 0;
  }
}


int getDistance(){
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration*0.034/2;
  // Prints the distance on the Serial Monitor

  return(distance);
}

int getAverage(){ 

int i;
float avg;
float measure;

  avg = getDistance();
  for (i=0; i<10; i++){
    measure=getDistance();
    avg=(0.8*avg) + (0.2*measure);
    delayMicroseconds(1000);
    }
  return(avg);
}
