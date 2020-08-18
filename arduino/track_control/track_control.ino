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
int inByte = 0;

int maxTriggerDistance = 20;
enum messages {
	ACK,
	REQUEST_SENSOR,
	POWER_OFF,
	POWER_ON,
	DISTANCE_MEASURE_OFF,
	DISTANCE_MEASURE_ON,
	INITIATE_HANDSHAKE
};


void setup() {
 pinMode(3, OUTPUT); //make the pin (3) as output
 pinMode(13, OUTPUT); //make the LED pin (13) as output
 pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
 pinMode(echoPin, INPUT); // Sets the echoPin as an Input
 Serial.begin(9600); // Starts the serial communication
 measuring = false;
 establishContact();
}

void loop() {
 int data;
  
 if (Serial.available() > 0){
   inByte = Serial.read();

   switch (inByte) {
    //  send Sensor data
    case REQUEST_SENSOR:
      updateSensorData();
      delayMicroseconds(10);
      sendAck();
      sendSensorData();
      break;
    //  Turn Train power off
    case POWER_OFF:
      turnPowerOff();
      sendAck();
      break;
      //  Turn Train power on
    case POWER_ON:
      turnPowerOn();
      sendAck();
      break;
    case DISTANCE_MEASURE_OFF:
      measuring = false;
      sendAck();
      break;
    case DISTANCE_MEASURE_ON:
      measuring = true;
      sendAck();
    case INITIATE_HANDSHAKE:
      measuring = false;
      establishContact();
    default:
//      if no bytes are present, the client is not expecting computation from us
//      TODO just continue loop
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
  Serial.flush();
  while (Serial.available() <= 0) {
     sendHandshake();
    delay(300);
  }

  Serial.findUntil(ACK);
  sendAck();
  Serial.flush();
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
