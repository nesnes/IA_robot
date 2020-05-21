#include <Servo.h>

#define MODE_I2C
#ifndef MODE_I2C
  #define MODE_SERIAL
  //#define SERIAL_DEBUG
#endif
#include "comunication.h"

enum  {
  SIDE_LEFT,
  SIDE_RIGHT,
  SIDE_MIDDLE
} SIDE;


const int SERVO_LEFT=8;
const int SERVO_RIGHT=7;
Servo servoLeft, servoRight;

const int NB_SERVO_ARM_M = 5;
const int pinNumberServo_M[NB_SERVO_ARM_M] = {2,3,4,5,6};
Servo servos_M[NB_SERVO_ARM_M];
const int pinNumberPump_M = 10;
int positionServo_M_DefaultOut[NB_SERVO_ARM_M] = {90,90,90,90,90};//Z 40 90 90 90 90 140 0
int positionServo_M_Default[NB_SERVO_ARM_M] = {50,90,140,50,90};//Z 40 10 150 60 90 140 0


const int MIN_PULSE = 500;//550
const int MAX_PULSE = 2500;//2450


void setup() {
  //Init communication
  comunication_begin(6);//I2C address 6

  servoLeft.attach(SERVO_LEFT, MIN_PULSE, MAX_PULSE);
  servoLeft.write(90);
  servoRight.attach(SERVO_RIGHT, MIN_PULSE, MAX_PULSE);
  servoRight.write(90);

  // Setup Arm M
  for(int i=0; i<NB_SERVO_ARM_M; i++){
    servos_M[i].attach(pinNumberServo_M[i], MIN_PULSE, MAX_PULSE);
  }
  setServoRecordedPosition(positionServo_M_DefaultOut, servos_M, NB_SERVO_ARM_M, 0);
  delay(500);
  setServoRecordedPosition(positionServo_M_Default, servos_M, NB_SERVO_ARM_M, 500);
  pinMode(pinNumberPump_M, OUTPUT); 
  digitalWrite(pinNumberPump_M, HIGH);
}

void setServoRecordedPosition(int* positions, Servo* servos, int servoCount, int duration){
  unsigned long startTime = millis();
  //Save start position
  int startPosition[servoCount];
  for(int i=0; i<servoCount;i++){
    startPosition[i] = servos[i].read();
  }
  //SetProgressive position
  do{
    float stepRatio = (1.f/(float)duration)*(float)(millis() - startTime);
    for(int i=0; i<servoCount;i++){
      servos[i].write(startPosition[i]+(positions[i]-startPosition[i])*stepRatio);
    }
    delay(1);
  }while(millis() - startTime < duration);
  //Set final position
  for(int i=0; i<servoCount;i++){
    servos[i].write(positions[i]);
  }
}

void setPump(const int pumpPin, bool isOn){
  if(isOn){
    digitalWrite(pumpPin, LOW);
  }
  else{
    digitalWrite(pumpPin, HIGH);
  }  
}

void executeOrder(){
  comunication_read();
  if(comunication_msgAvailable()){
    if(comunication_InBuffer[0] == '#' && comunication_InBuffer[1] != '\0'){
      //ignore
    }
    else if(!strcmp(comunication_InBuffer, "id")){
      sprintf(comunication_OutBuffer, "BrasRobotTheo");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "setServo")){
      int servo=50, angle=50;
      sscanf(comunication_InBuffer, "setServo %i %i", &servo, &angle);
      if(servo >=0 && servo < NB_SERVO_ARM_M)
        servos_M[servo].write(angle);
      sprintf(comunication_OutBuffer, "OK");//max 29 Bytes
      comunication_write();//async
    }
    else if(!strcmp(comunication_InBuffer, "getServos")){
      char strTemp[5];
      int value;
      strcat(comunication_OutBuffer, " M:");
      for(int i=0; i< NB_SERVO_ARM_M; i++){
        value = servos_M[i].read();                
        itoa(value, strTemp, 10);
        strcat(strTemp, ", ");
        strcat(comunication_OutBuffer, strTemp);
      }
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "Z ")){
      int a1=90,a2=90,a3=90,a4=90,a5=90,t=0;
      sscanf(comunication_InBuffer, "Z %i %i %i %i %i %i",&a1,&a2,&a3,&a4,&a5,&t);
      int pose[NB_SERVO_ARM_M];
      pose[0]=a1;
      pose[1]=a2;
      pose[2]=a3;
      pose[3]=a4;
      pose[4]=a5;
      sprintf(comunication_OutBuffer, "OK");//max 29 Bytes
      comunication_write();//async
      setServoRecordedPosition(pose, servos_M, NB_SERVO_ARM_M, t);
    }
    else if(!strcmp(comunication_InBuffer, "pump on")){
      setPump(pinNumberPump_M, 1);
      sprintf(comunication_OutBuffer, "OK");//max 29 Bytes
      comunication_write();//async
    }      
    else if(!strcmp(comunication_InBuffer, "pump off")){
      setPump(pinNumberPump_M, 0);
      sprintf(comunication_OutBuffer, "OK");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "setLeft")){
      sprintf(comunication_OutBuffer, "OK");//max 29 Bytes
      comunication_write();//async
      int angle=90;
      sscanf(comunication_InBuffer, "setLeft %i", &angle);
      servoLeft.write(angle);
    }
    else if(strstr(comunication_InBuffer, "setRight")){
      sprintf(comunication_OutBuffer, "OK");//max 29 Bytes
      comunication_write();//async
      int angle=90;
      sscanf(comunication_InBuffer, "setRight %i", &angle);
      servoRight.write(180-angle);
    }

    
    else{
      sprintf(comunication_OutBuffer,"ERROR");
      comunication_write();//async
    }
    comunication_cleanInputs();
  }
}    

void loop() {
  executeOrder();
}
