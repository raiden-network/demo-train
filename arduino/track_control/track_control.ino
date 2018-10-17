// defines pins numbers
const int trigPin = 6;
const int echoPin = 7;
// defines variables
long duration;
float distance;
bool measuring;
int value = 9;

void setup() {
 pinMode(3, OUTPUT); //make the pin (3) as output
 pinMode(13, OUTPUT); //make the LED pin (13) as output
 pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
 pinMode(echoPin, INPUT); // Sets the echoPin as an Input
 Serial.begin(9600); // Starts the serial communication
 measuring = false;
}

void loop() {
 int data;
  
 if (Serial.available()> 0){
   data = Serial.read();
 }

 if (data == 1)  // Turn Train power on
   {
   digitalWrite(3, HIGH);
   Serial.println(digitalRead(3));
   }
  if (data == 0)  // Turn Train power off
   {
   digitalWrite(3, LOW);
   Serial.println(digitalRead(3));
   }
   
 if (data == 2){  // Start measuiring
  measuring = true;
 }

 if (measuring == true){
   int value = getAverage();
   if (value < 20){
     Serial.println(value);
     measuring = false;
   }
 }
 else {
     delayMicroseconds(10);
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
