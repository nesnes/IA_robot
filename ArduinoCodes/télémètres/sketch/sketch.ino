#define MODE_I2C
#ifndef MODE_I2C
  #define MODE_SERIAL
#endif

#include <Wire.h>

int numberOfSensor = 5;
float measureTab[5] = { 0.f, 0.f, 0.f, 0.f, 0.f};
int tabSensor[5][2] = {
  //trigger, echo
  {10, 11},
  {8, 9},
  {2, 3},
  {12, 13},
  {6, 7}
 };

/* I2C communication */
#ifdef MODE_I2C
  #define I2C_BUFFER_IN_SIZE 40
  #define I2C_BUFFER_OUT_SIZE 30
  
  volatile char i2cInBuffer[I2C_BUFFER_IN_SIZE];
  volatile char i2cOutBuffer[I2C_BUFFER_OUT_SIZE];
  volatile boolean i2cReceiveFlag = false;
  volatile boolean i2cSendFlag = false;
  void i2cReceiveEvent(int howMany) {
    if(howMany>1){
      Wire.read();//ignore first byte
      Wire.readBytes((char*)i2cInBuffer, howMany-1);
      i2cInBuffer[howMany-1]='\0';
      i2cReceiveFlag = true;
    }
    else if(howMany==1)
      Wire.read();
  }
  
  void i2cRequestEvent() {
    if(i2cSendFlag){
      Wire.write((char*)i2cOutBuffer);
      memset(i2cOutBuffer, '\0', I2C_BUFFER_OUT_SIZE);
      i2cSendFlag = false;
    }
    else
      Wire.write("");
  }
#endif

/* Serial communication */
#ifdef MODE_SERIAL
  #define SERIAL_BUFFER_IN_SIZE 32
  #define SERIAL_BUFFER_OUT_SIZE 32
  volatile char serialInBuffer[SERIAL_BUFFER_IN_SIZE];
  volatile char serialOutBuffer[SERIAL_BUFFER_OUT_SIZE];
  volatile boolean serialReadFlag = false;
  volatile boolean serialSendFlag = false;
  
  void readSerial() {
    int i=0;
    while (Serial.available()) {
      delay(3);
      char inChar = (char)Serial.read();
      if (inChar == '\r' || inChar == '\n' || i>SERIAL_BUFFER_IN_SIZE-2) {
        break;
      }
      serialInBuffer[i++] = inChar;
    }
    serialInBuffer[i+1] = '\0';
    serialReadFlag = i > 0;
  }
  
  void sendSerial(){
    if(serialSendFlag){
      Serial.print((char*)serialOutBuffer);
      serialSendFlag=false;
    }
  }
#endif

void setup() {
  #ifdef MODE_I2C
  Wire.begin(8);                //i2c address
  Wire.onRequest(i2cRequestEvent);
  Wire.onReceive(i2cReceiveEvent);
  #endif
  #ifdef MODE_SERIAL
  Serial.begin(115200);
  #endif
}



/* Sensor functions */
void getDistanceMultipleSRF05(float* outMeasure) {
  //setup
  float maxDist = 1000;//mm
  int maxDuration = maxDist*5.8;
  for(int i=0;i<numberOfSensor;i++){
    pinMode(tabSensor[i][0], OUTPUT); // triggerPin
    pinMode(tabSensor[i][1], INPUT); // echoPin
  }

  float duration[numberOfSensor];
  unsigned long inTime[numberOfSensor];
  bool echoDone[numberOfSensor];
  for(int i=0;i<numberOfSensor;i++) {
    duration[i] = 0;
    inTime[i] = 0;
    echoDone[i] = false;
  }

  //trigger
  for(int i=0;i<numberOfSensor;i++)
    digitalWrite(tabSensor[i][0], LOW);
  delayMicroseconds(2);
  for(int i=0;i<numberOfSensor;i++)
    digitalWrite(tabSensor[i][0], HIGH);
  delayMicroseconds(10);
  for(int i=0;i<numberOfSensor;i++)
    digitalWrite(tabSensor[i][0], LOW);

  //echo
  //pulseIn(echoPin, HIGH, maxDuration);
  int echoCount = 0;
  unsigned long startTime = micros();
  while(echoCount<numberOfSensor && micros() - startTime < maxDuration){
    for(int i=0;i<numberOfSensor;i++){
      if(digitalRead(tabSensor[i][1]) == 1){
        if(inTime[i] == 0)
          inTime[i] = micros();
      }
      else if(inTime[i] != 0 && !echoDone[i]){
        duration[i] = micros() - inTime[i];
        echoDone[i] = true;
        echoCount++;
      }
    }
  }
  for(int i=0;i<numberOfSensor;i++){
    if(duration[i]>0){
      outMeasure[i] = duration[i]*0.17241379; //1/5.8;//mm
    }
    else
      outMeasure[i] = 0;
  }
}

float getDistanceSRF05(int pins[2]) {
  //setup
  float maxDist = 1000;//mm
  int maxDuration = maxDist*5.8;
  int triggerPin = pins[0];
  int echoPin = pins[1];
  pinMode(triggerPin, OUTPUT);
  pinMode(echoPin, INPUT);

  //trigger
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);

  //echo
  float duration = pulseIn(echoPin, HIGH, maxDuration);
  if(duration>0){
    float distance = duration*0.17241379; //1/5.8;//mm
    return distance;
  }
  else
    return maxDist;
}

void updateMeasure() {
  for (int i=0;i<numberOfSensor;i++){
    float dist = getDistanceSRF05(tabSensor[i]);
    measureTab[i] = measureTab[i]*0.4 + dist*0.6;
  }
}


/* Board commands */
void executeOrder(volatile boolean &readReady, char* readBuffer, volatile boolean &writeReady, char* writeBuffer, int readBufferSize){
  if(readReady){
    if(readBuffer[0] == '#' && readBuffer[1] != '\0'){ 
      //message starting with #, ignored
    }
    else if(strstr(readBuffer, "id")){
      sprintf(writeBuffer, "CollisionDetectionTheo\r\n");
      writeReady = true;
    }
    else if(strstr(readBuffer, "distances get")){
      /*char v0[5], v1[5], v2[5], v3[5], v4[5];
      dtostrf(measureTab[0], 4, 0, v0);
      dtostrf(measureTab[1], 4, 0, v1);
      dtostrf(measureTab[2], 4, 0, v2);
      dtostrf(measureTab[3], 4, 0, v3);
      dtostrf(measureTab[4], 4, 0, v4);
      sprintf(writeBuffer, "%s;%s;%s;%s;%s\r\n", v0, v1, v2, v3, v4);*/
      sprintf(writeBuffer, "dist %i;%i;%i;%i;%i\r\n",
      (int)measureTab[0],
      (int)measureTab[1],
      (int)measureTab[2],
      (int)measureTab[3],
      (int)measureTab[4]);
      writeReady = true;
    }
    else{
      sprintf(writeBuffer, "ERROR\r\n");
      writeReady = true;
    }
    memset(readBuffer, '\0', readBufferSize);
    readReady=false;
  }
}


void loop() {
  getDistanceMultipleSRF05(measureTab); // measure telemeter all at once (fast: 6ms max)
  #ifdef MODE_I2C
    executeOrder(i2cReceiveFlag, i2cInBuffer, i2cSendFlag, i2cOutBuffer, I2C_BUFFER_IN_SIZE);
  #endif
  
  #ifdef MODE_SERIAL
    readSerial();
    executeOrder(serialReadFlag, serialInBuffer, serialSendFlag, serialOutBuffer, SERIAL_BUFFER_IN_SIZE);
    sendSerial();
  #endif
  delay(5);
}
