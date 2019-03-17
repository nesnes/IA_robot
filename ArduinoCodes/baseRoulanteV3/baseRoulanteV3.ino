#define MODE_I2C
#ifndef MODE_I2C
  #define MODE_SERIAL
  #define SERIAL_DEBUG
#endif

#include "math.h"
#include <Wire.h>
#include "utils.h"

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

#define MOTOR_ENCODER
#ifndef MOTOR_ENCODER
  //Encoder declaration
  #include "Encoder.h"
  Encoder encoder_left(2, A0, true);
  Encoder encoder_right(3, 4, true);
  void int_encoder_left(){encoder_left.update();}
  void int_encoder_right(){encoder_right.update();}
#else
  #define encoder_left motor_left
  #define encoder_right motor_right
#endif

//Motor declaration
#define MOTOR_USE_TIMER
#ifdef MOTOR_USE_TIMER
  #include <TimerOne.h>
#endif
#define MOTOR_L_PWM 5
#define MOTOR_L_DIR 7
#define MOTOR_R_PWM 6
#define MOTOR_R_DIR 8
#define MIN_PULSE 500
#define MAX_PULSE 2500
#include "Motor.h"
Motor motor_left(MOTOR_L_PWM, MOTOR_L_DIR, 0, false);
Motor motor_right(MOTOR_R_PWM, MOTOR_R_DIR, 0, true);
void updateMotors(){interrupts ();motor_left.spinUpdate();motor_right.spinUpdate();}

//Asserv declaration
#include "Asserv.h"

void setup() {
  #ifndef MOTOR_ENCODER
    //encoder interrupts
    attachInterrupt(0, int_encoder_left, RISING);
    attachInterrupt(1, int_encoder_right, RISING);
  #endif

    pinMode(LED_BUILTIN, OUTPUT);
    
    #ifdef MOTOR_USE_TIMER
      Timer1.initialize(100);
      Timer1.attachInterrupt(updateMotors);
    #endif
    
    #ifdef MODE_I2C
      Wire.begin(7);                //i2c address
      Wire.onRequest(i2cRequestEvent);
      Wire.onReceive(i2cReceiveEvent);
    #endif
  
    #ifdef MODE_SERIAL               
      Serial.begin(115200);
    #endif
    
}

void cleanInputs(){
    #ifdef MODE_SERIAL
      memset(serialInBuffer, '\0', SERIAL_BUFFER_IN_SIZE);
      serialReadFlag = false;
    #endif
    #ifdef MODE_I2C
      memset(i2cInBuffer, '\0', I2C_BUFFER_IN_SIZE);
      i2cReceiveFlag = false;
    #endif
}

int blinkCount=0;
bool blinkStatus=false;
void executeOrder(volatile boolean &readReady, char* readBuffer, volatile boolean &writeReady, char* writeBuffer, int readBufferSize, bool launchBlocking = false){
  if(50 == blinkCount++){
    blinkStatus = !blinkStatus;
    digitalWrite(LED_BUILTIN, blinkStatus);
    blinkCount = 0;
  }
  bool waitForNonBlocking = false;
  bool exitFromBlocking = false;
  if(readReady){
    if(readBuffer[0] == '#' && readBuffer[1] != '\0'){
      //ignore
    }
    else if(strstr(readBuffer, "id")){
      sprintf(writeBuffer, "MovingBaseAlexandreV3\r\n"); //max 32 bit (with \r\n)
      writeReady = true;
    }
    else if(strstr(readBuffer, "move enable")){
      movementEnabaled = true;
      sprintf(writeBuffer,"move OK\r\n");
      writeReady = true;
    }
    else if(strstr(readBuffer, "move disable")){
      movementEnabaled = false;
      sprintf(writeBuffer,"move OK\r\n");
      writeReady = true;
    }
    else if(strstr(readBuffer, "pos set ")){
      int xPos=0, yPos=0, Angle=0;
      int res = sscanf(readBuffer, "pos set %i %i %i", &xPos, &yPos, &Angle);
      absoluteX = (float)(xPos)/10.0f;
      absoluteY = (float)(yPos)/10.0f;
      absoluteAngle = Angle;
      Encodeurs_Reset();
      sprintf(writeBuffer,"pos OK\r\n");
      writeReady=true;
    }
    else if(strstr(readBuffer, "pos getXY")){
      sprintf(writeBuffer,"pos %i %i %i %i\r\n",(int)(absoluteX*10.0f), (int)(absoluteY*10.0f), (int)(absoluteAngle), (int)(getSpeed())*10);
      writeReady=true;
    }
    else if(strstr(readBuffer, "pos getDA")){
      sprintf(writeBuffer,"pos %i %i %i\r\n",(int)(currentDistance*10.0f), (int)(currentAngle), (int)(getSpeed())*10);
      writeReady=true;
    }
    else if(strstr(readBuffer, "move XY ")) { //absolute X, Y, Angle
      if(!launchBlocking)
        waitForNonBlocking = true;
      else {
        exitFromBlocking = true;
        float xPos=0, yPos=0, Angle=0, vitesse=0.4;
        int i_xPos=0, i_yPos=0, i_Angle=0, i_vitesse=0.4;
        sscanf(readBuffer, "move XY %i %i %i %i", &i_xPos, &i_yPos, &i_Angle, &i_vitesse);
        sprintf(writeBuffer,"move OK\r\n");
        xPos = (float)(i_xPos)/10.0f;
        yPos = (float)(i_yPos)/10.0f;
        Angle = (float)(i_Angle);
        vitesse = (float)(i_vitesse)/10.0f;
        writeReady=true;
        if(!PIDEnabled){
          if(vitesse != 0) targetSpeed = vitesse;
          if(vitesse != 0) targetSpeedRotation = vitesse;
          cleanInputs();
          goTo(xPos, yPos, Angle);
          emergencyStop = false;
        }
      }
    }
    else if(strstr(readBuffer, "move DA ")) { //relative Distance Angle
      if(!launchBlocking)
        waitForNonBlocking = true;
      else {
        exitFromBlocking = true;
        float distance=0, angle=0, vitesse=0.4;
        int int_distance=0, int_angle=0, int_vitesse=4;
        int res = sscanf(readBuffer, "move DA %i %i %i", &int_distance, &int_angle, &int_vitesse);
        sprintf(writeBuffer,"move OK\r\n");
        distance = (float)(int_distance)/10.0f;
        angle = int_angle;
        vitesse = (float)(int_vitesse)/10.0f;
        writeReady=true;
        if(!PIDEnabled) {
          cleanInputs();
          if(vitesse != 0) targetSpeed = vitesse;
          if(vitesse != 0) targetSpeedRotation = vitesse;
          if(distance !=0) move(distance);
          if(angle != 0) turn(angle);
          emergencyStop = false;
        }
      }
    }
    else if(strstr(readBuffer, "move status")){
      if(PIDEnabled) {
        if(staticCount < staticMax)
          sprintf(writeBuffer,"move running\r\n");
        else
          sprintf(writeBuffer,"move stuck\r\n");
      }
      else
        sprintf(writeBuffer,"move finished\r\n");
      writeReady=true;
    }
    else if(strstr(readBuffer, "speed get")){
      sprintf(writeBuffer,"speed %.1f\r\n",getSpeed());
      writeReady=true;
    }
    else if(strstr(readBuffer, "move break")){
      emergencyStop = true;
      sprintf(writeBuffer,"move OK\r\n");
      writeReady=true;
    }
    else if(strstr(readBuffer, "move RM ")) { //relative Distance Angle
      if(!launchBlocking)
        waitForNonBlocking = true;
      else {
        exitFromBlocking = true;
        int i_distance=0, i_vitesse=4;
        float distance=0, vitesse=0.4;
        sscanf(readBuffer, "move RM %i %i", &i_distance, &i_vitesse);
        sprintf(writeBuffer, "move OK\r\n");
        vitesse = (float)(i_vitesse)/10.0f;
        writeReady=true;
        if(!PIDEnabled) {
          cleanInputs();
          if(vitesse != 0) targetSpeed = vitesse;
          if(vitesse != 0) targetSpeedRotation = vitesse;
          if(distance !=0) move(distance/10.0f);
          emergencyStop = false;
        }
      }
    }
    else if(strstr(readBuffer, "support XY")){
      sprintf(writeBuffer,"support 1\r\n");
      writeReady=true;
    }
    else if(strstr(readBuffer, "support Path")){
      sprintf(writeBuffer,"support 0\r\n");
      writeReady=true;
    }
    else if(!waitForNonBlocking){
      sprintf(writeBuffer, "ERROR\r\n");
      writeReady = true;
    }
    if(!waitForNonBlocking && !exitFromBlocking){
        cleanInputs();
    }
    memset(readBuffer, '\0', readBufferSize);
    readReady=false;
  }
}


void executionLoop(bool launchBlocking = false){
    #ifdef MODE_I2C
      executeOrder(i2cReceiveFlag, i2cInBuffer, i2cSendFlag, i2cOutBuffer, I2C_BUFFER_IN_SIZE, launchBlocking);
    #endif
    
    #ifdef MODE_SERIAL
      readSerial();
      executeOrder(serialReadFlag, serialInBuffer, serialSendFlag, serialOutBuffer, SERIAL_BUFFER_IN_SIZE, launchBlocking);
      sendSerial();
    #endif
  
    #ifndef MOTOR_USE_TIMER
      updateMotors();
    #endif

    PIDLoop(); 
}

void loop(){
    executionLoop(true);
    //delay(1);
}


