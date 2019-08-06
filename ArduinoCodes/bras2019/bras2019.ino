#include <Servo.h>
#include "APDS9960.h"
APDS9960 colorSensorLeft = APDS9960();
APDS9960 colorSensorRight = APDS9960();

enum  {
  RED,
  GREEN,
  BLUE,
  OTHER,
  EMPTY
} COLOR;

enum  {
  PRESSURE_STANDARD,
  PRESSURE_VACCUM,
  PRESSURE_UNKNOWN
} PRESSURE;

enum  {
  SIDE_LEFT,
  SIDE_RIGHT,
  SIDE_MIDDLE
} SIDE;

struct PresureSensor{
  int clkPin;
  int dataPin;
  PresureSensor(int clk, int data){
    clkPin = clk;
    dataPin = data;
  }
};

PresureSensor pressureSensorL(A6,A4);
PresureSensor pressureSensorM(A6,A5);
PresureSensor pressureSensorR(A6,A7);

bool enableAutoFloorGrab = false;
int autoFloorGrabStateLeft = 1;
int autoFloorGrabStateRight = 1;
int autoFloorGrabCurrentColorLeft = EMPTY;
int autoFloorGrabCurrentColorRight = EMPTY;
long autoFloorGrabActionStartTimeLeft = 0;
long autoFloorGrabActionStartTimeRight = 0;
int autoFloorGrabActionTimeoutLeft = 0;
int autoFloorGrabActionTimeoutRight = 0;

int stockL[3] = {EMPTY, EMPTY, EMPTY};
int stockR[3] = {EMPTY, EMPTY, EMPTY};
int stockM[3] = {EMPTY, EMPTY, EMPTY};

const int NB_SERVO_ARM_R = 3;
const int pinNumberServo_R[NB_SERVO_ARM_R] = {7,8,9};
Servo servos_R[NB_SERVO_ARM_R];
const int pinNumberPump_R = 11;
int positionServo_R_Default[NB_SERVO_ARM_R] = {130,0,110};
int positionServo_R_WallGrab[NB_SERVO_ARM_R] = {175,50,150};
int positionServo_R_FloorGrab_Prepare[NB_SERVO_ARM_R] = {120,180,180};
int positionServo_R_FloorGrab[NB_SERVO_ARM_R] = {150,180,130};
int positionServo_R_Stock_1[NB_SERVO_ARM_R] = {60,0,100};
int positionServo_R_Stock_2[NB_SERVO_ARM_R] = {77,0,100};
int positionServo_R_Stock_3[NB_SERVO_ARM_R] = {100,0,90};
int positionServo_R_Stock_Prepare_Deposit[NB_SERVO_ARM_R] = {90,30,80};
int positionServo_R_Stock_Prepare[NB_SERVO_ARM_R] = {100,30,60};

const int NB_SERVO_ARM_L = 3;
const int pinNumberServo_L[NB_SERVO_ARM_L] = {13,3,2};
Servo servos_L[NB_SERVO_ARM_L];
const int pinNumberPump_L = 10;
int positionServo_L_Default[NB_SERVO_ARM_L] = {130,0,110};
int positionServo_L_WallGrab[NB_SERVO_ARM_L] = {175,50,150};
int positionServo_L_FloorGrab_Prepare[NB_SERVO_ARM_L] = {120,180,180};
int positionServo_L_FloorGrab[NB_SERVO_ARM_L] = {155,180,140};
int positionServo_L_Stock_1[NB_SERVO_ARM_L] = {60,0,100};
int positionServo_L_Stock_2[NB_SERVO_ARM_L] = {77,0,100};
int positionServo_L_Stock_3[NB_SERVO_ARM_L] = {100,0,90};
int positionServo_L_Stock_Prepare_Deposit[NB_SERVO_ARM_L] = {90,30,80};
int positionServo_L_Stock_Prepare[NB_SERVO_ARM_L] = {100,30,60};

const int NB_SERVO_ARM_M = 3;
const int pinNumberServo_M[NB_SERVO_ARM_M] = {4,5,6};
Servo servos_M[NB_SERVO_ARM_M];
const int pinNumberPump_M = 10;
int positionServo_M_Default[NB_SERVO_ARM_M] = {30,175,100};
int positionServo_M_WallGrab[NB_SERVO_ARM_M] = {123,95,40};
int positionServo_M_WallGrab_Lift[NB_SERVO_ARM_M] = {90,110,40};
int positionServo_M_Stock_1[NB_SERVO_ARM_M] = {125,155,50};
int positionServo_M_Stock_2[NB_SERVO_ARM_M] = {103,180,50};
int positionServo_M_Stock_3[NB_SERVO_ARM_M] = {80,180,90};
int positionServo_M_Stock_Prepare_Deposit[NB_SERVO_ARM_M] = {70,170,110};
int positionServo_M_Stock_Prepare[NB_SERVO_ARM_M] = {80,180,90};

const int MIN_PULSE = 500;//550
const int MAX_PULSE = 2500;//2450


void setup() {
  Serial.begin(115200);

  // Setup Arm R
  for(int i=0; i<NB_SERVO_ARM_R; i++){
    servos_R[i].attach(pinNumberServo_R[i], MIN_PULSE, MAX_PULSE);
  }
  setServoRecordedPosition(positionServo_R_Default, servos_R, NB_SERVO_ARM_R, 0);
  pinMode(pinNumberPump_R, OUTPUT); 
  digitalWrite(pinNumberPump_R, HIGH);

  // Setup Arm L
  for(int i=0; i<NB_SERVO_ARM_L; i++){
    servos_L[i].attach(pinNumberServo_L[i], MIN_PULSE, MAX_PULSE);
  }
  setServoRecordedPosition(positionServo_L_Default, servos_L, NB_SERVO_ARM_R, 0);

  pinMode(pinNumberPump_L, OUTPUT); 
  digitalWrite(pinNumberPump_L, HIGH);

  // Setup Arm M
  for(int i=0; i<NB_SERVO_ARM_M; i++){
    servos_M[i].attach(pinNumberServo_M[i], MIN_PULSE, MAX_PULSE);
  }
  setServoRecordedPosition(positionServo_M_Default, servos_M, NB_SERVO_ARM_M, 0);
  pinMode(pinNumberPump_M, OUTPUT); 
  digitalWrite(pinNumberPump_M, HIGH);

  // Initialize APDS-9960
  colorSensorLeft.init(A1, A0);
  colorSensorLeft.enableLightSensor(false);
  colorSensorLeft.setProximityGain(GGAIN_2X);
  colorSensorLeft.enableProximitySensor(false);
  colorSensorRight.init(A3, A2);
  colorSensorRight.enableLightSensor(false);
  colorSensorRight.setProximityGain(GGAIN_2X);
  colorSensorRight.enableProximitySensor(false);
  delay(500); // color sensor init and calib

  //Initialize Pressure sensors
  pinMode(pressureSensorL.clkPin, OUTPUT);
  pinMode(pressureSensorM.clkPin, OUTPUT);
  pinMode(pressureSensorR.clkPin, OUTPUT);
  pinMode(pressureSensorL.dataPin, INPUT);
  pinMode(pressureSensorM.dataPin, INPUT);
  pinMode(pressureSensorR.dataPin, INPUT);
}

int getPresure(PresureSensor* sensor)
{
  char line[50];
  sprintf(line, "Pressure clk %i data %i ", sensor->clkPin, sensor->dataPin);
  Serial.print(line);
  digitalWrite(sensor->clkPin, LOW);
  delayMicroseconds(1);
  // wait for the chip to become ready:
  while (digitalRead(sensor->dataPin) == HIGH);
  unsigned long value = 0;
  for (int i = 23; i > -1; i--){ //bitWrite23 =bit24 
    digitalWrite(sensor->clkPin, HIGH);
    delayMicroseconds(1);
    digitalWrite(sensor->clkPin, LOW);
    if (digitalRead(sensor->dataPin) == HIGH){bitSet(value, i);}
  }  
  digitalWrite(sensor->clkPin, HIGH);
  delayMicroseconds(1);
  digitalWrite(sensor->clkPin, LOW);
  delayMicroseconds(1);
  Serial.println(value);
  if(value == 8388608)
    return PRESSURE_VACCUM;
  return PRESSURE_UNKNOWN; // todos 1 = 1677215
}

int getColor(APDS9960* sensor){
  uint16_t red_light = 0;
  uint16_t green_light = 0;
  uint16_t blue_light = 0;
  uint8_t prox = 0;
  if (sensor->readRedLight(red_light) &&
      sensor->readGreenLight(green_light) &&
      sensor->readBlueLight(blue_light) &&
      sensor->readProximity(prox)) {
       /*Serial.println(red_light);
       Serial.println(green_light);
       Serial.println(blue_light);
       Serial.println(prox);*/
      if(prox<155)
        return EMPTY;
      if(red_light>green_light*1.5f && red_light > blue_light*1.5f && red_light > 50)
        return RED;
      if(green_light>red_light*1.5f && green_light > blue_light*1.5f && green_light > 50)
        return GREEN;
      if(blue_light>red_light*1.5f && blue_light > green_light*1.5f && blue_light > 50)
        return BLUE;
  }
  return OTHER;
}

#define INPUT_STR_SIZE 100
char inputString[INPUT_STR_SIZE];
boolean stringReady = false;

void readSerial() {
  int i=0;
  while (Serial.available()) {
    delay(3);
    char inChar = (char)Serial.read();
    if (inChar == '\r' || inChar == '\n' || i>INPUT_STR_SIZE-2) {
      break;
    }
    inputString[i++] = inChar;
  }
  inputString[i+1] = '\0';
  stringReady = i > 0;
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

void setValve(const int vavlePin, bool isOn){
  if(isOn){
    digitalWrite(vavlePin, LOW);
  }
  else{
    digitalWrite(vavlePin, HIGH);
  }  
}

void runAutoFloorGrab(int side){//async
  if(!enableAutoFloorGrab)
    return;

  long* autoFloorGrabActionStartTime = &autoFloorGrabActionStartTimeLeft;
  int* autoFloorGrabActionTimeout = &autoFloorGrabActionTimeoutLeft;
  int* autoFloorGrabState = &autoFloorGrabStateLeft;
  int* autoFloorGrabCurrentColor = &autoFloorGrabCurrentColorLeft;
  APDS9960* colorSensor = &colorSensorLeft;
  const int* NB_SERVO_ARM = &NB_SERVO_ARM_L;
  auto servos = &servos_L;
  auto positionServo_Default = &positionServo_L_Default;
  auto positionServo_FloorGrab_Prepare = &positionServo_L_FloorGrab_Prepare;
  auto positionServo_FloorGrab = &positionServo_L_FloorGrab;
  auto positionServo_Stock_Prepare_Deposit = &positionServo_L_Stock_Prepare_Deposit;
  auto positionServo_Stock_1 = &positionServo_L_Stock_1;
  auto positionServo_Stock_2 = &positionServo_L_Stock_2;
  auto positionServo_Stock_3 = &positionServo_L_Stock_3;
  int *pinNumberPump = &pinNumberPump_L;
  auto stock = &stockL;
  if(side == SIDE_RIGHT){
    autoFloorGrabActionStartTime = &autoFloorGrabActionStartTimeRight;
    autoFloorGrabActionTimeout = &autoFloorGrabActionTimeoutRight;
    autoFloorGrabState = &autoFloorGrabStateRight;
    autoFloorGrabCurrentColor = &autoFloorGrabCurrentColorRight;
    colorSensor = &colorSensorRight;
    NB_SERVO_ARM = &NB_SERVO_ARM_R;
    servos = &servos_R;
    positionServo_Default = &positionServo_R_Default;
    positionServo_FloorGrab_Prepare = &positionServo_R_FloorGrab_Prepare;
    positionServo_FloorGrab = &positionServo_R_FloorGrab;
    positionServo_Stock_Prepare_Deposit = &positionServo_R_Stock_Prepare_Deposit;
    positionServo_Stock_1 = &positionServo_R_Stock_1;
    positionServo_Stock_2 = &positionServo_R_Stock_2;
    positionServo_Stock_3 = &positionServo_R_Stock_3;
    pinNumberPump = &pinNumberPump_R;
    stock = &stockR;
  }
  else if(side == SIDE_LEFT){
    
  }
  else
    return;

  
  /*char line[75];
  sprintf(line,"side %i, state %i, timeout %i, color %i", side, *autoFloorGrabState, *autoFloorGrabActionTimeout, getColor(colorSensor)); 
  Serial.println(line);*/
  
  if(*autoFloorGrabState !=0){
    if(*autoFloorGrabActionStartTime > 0 && *autoFloorGrabActionTimeout > 0){
      //handle timer
      long diff = millis() - (*autoFloorGrabActionStartTime);
      *autoFloorGrabActionStartTime = millis();
      *autoFloorGrabActionTimeout -= diff;
    }
    else if(*autoFloorGrabState == 1 && (*stock)[2]==EMPTY){
      //detect object an prepare
      int color = getColor(colorSensor);
      if(color == RED || color == GREEN || color == BLUE){
        *autoFloorGrabCurrentColor = color;
        setServoRecordedPosition(*positionServo_FloorGrab_Prepare, *servos, *NB_SERVO_ARM, 0);
        *autoFloorGrabActionStartTime = millis();
        *autoFloorGrabActionTimeout = 750;
        *autoFloorGrabState = 2;
      }
    }
    else if(*autoFloorGrabState == 2){
      //grab
      setPump(*pinNumberPump, 1);
      setServoRecordedPosition(*positionServo_FloorGrab, *servos, *NB_SERVO_ARM, 0);
      *autoFloorGrabActionStartTime = millis();
      *autoFloorGrabActionTimeout = 400;
      *autoFloorGrabState = 3;
    }
    else if(*autoFloorGrabState == 3){
      //prepare stock
      //if(vaccum not validated) state 1 and position default
      setServoRecordedPosition(*positionServo_Stock_Prepare_Deposit, *servos, *NB_SERVO_ARM, 0);
      *autoFloorGrabActionStartTime = millis();
      *autoFloorGrabActionTimeout = 750;
      *autoFloorGrabState = 4;
    }
    else if(*autoFloorGrabState == 4){
      //stock
      for(int j=0;j<3;j++){
        if((*stock)[j] == EMPTY){
          (*stock)[j] = *autoFloorGrabCurrentColor;
          if(j==0)
            setServoRecordedPosition(*positionServo_Stock_1, *servos, *NB_SERVO_ARM, 0);
          else if(j==1)
            setServoRecordedPosition(*positionServo_Stock_2, *servos, *NB_SERVO_ARM, 0);
          else if(j==2)
            setServoRecordedPosition(*positionServo_Stock_3, *servos, *NB_SERVO_ARM, 0);
          break;
        }
      }
      *autoFloorGrabActionStartTime = millis();
      *autoFloorGrabActionTimeout = 500;
      *autoFloorGrabState = 5;
    }
    else if(*autoFloorGrabState == 5){
      //default
      setPump(*pinNumberPump, 0);
      setServoRecordedPosition(*positionServo_Default, *servos, *NB_SERVO_ARM, 500);
      *autoFloorGrabActionStartTime = millis();
      *autoFloorGrabActionTimeout = 100;
      *autoFloorGrabState = 6;
    }
    else if(*autoFloorGrabState == 6){
      *autoFloorGrabState = 1;
    }
  }
}

void loop() {
  //getPresure(&pressureSensorL);
  //getPresure(&pressureSensorM);
  //getPresure(&pressureSensorR);
  runAutoFloorGrab(SIDE_LEFT);//async
  runAutoFloorGrab(SIDE_RIGHT);//async
  readSerial();
  if(stringReady){
    if(inputString[0] == '#' && inputString[1] != '\0'){ 
      //message starting with #, ignored
    }
    else if(!strcmp(inputString, "id")){
      char line[25];
      sprintf(line, "BrasRobotTheo\r\n");
      Serial.print(line);
    }       
    else if(strstr(inputString, "setArmServo")){
      char side;
      int servo=50, angle=50;
      sscanf(inputString, "setArmServo %c %i %i", &side, &servo, &angle);
      if(servo >=0 && servo < NB_SERVO_ARM_R && side=='R')
        servos_R[servo].write(angle);
      if(servo >=0 && servo < NB_SERVO_ARM_L && side=='L')
        servos_L[servo].write(angle);
      if(servo >=0 && servo < NB_SERVO_ARM_M && side=='M')
        servos_M[servo].write(angle);
      Serial.print("OK\r\n");
    } 
    else if(!strcmp(inputString, "getServos")){
      char strServos[100];
      strcpy(strServos, "");
      char strTemp[5];
      int value;
      strcat(strServos, "R:");
      for(int i=0; i< NB_SERVO_ARM_R; i++){
        value = servos_R[i].read();                
        itoa(value, strTemp, 10);
        strcat(strTemp, ", ");
        strcat(strServos, strTemp);
      }
      strcat(strServos, "L:");
      for(int i=0; i< NB_SERVO_ARM_L; i++){
        value = servos_L[i].read();                
        itoa(value, strTemp, 10);
        strcat(strTemp, ", ");
        strcat(strServos, strTemp);
      }
      strcat(strServos, " M:");
      for(int i=0; i< NB_SERVO_ARM_M; i++){
        value = servos_M[i].read();                
        itoa(value, strTemp, 10);
        strcat(strTemp, ", ");
        strcat(strServos, strTemp);
      }
      Serial.println(strServos);
    }      
    else if(strstr(inputString, "pump on")){
      char side;
      sscanf(inputString, "pump on %c", &side);
      if(side=='R' || side=='A')
        setPump(pinNumberPump_R, 1);
      if(side=='L' || side=='A')
        setPump(pinNumberPump_L, 1);
      if(side=='M' || side=='A')
        setPump(pinNumberPump_M, 1);
      Serial.print("OK\r\n");
    }      
    else if(strstr(inputString, "pump off")){
      char side;
      sscanf(inputString, "pump off %c", &side);
      if(side=='R' || side=='A')
        setPump(pinNumberPump_R, 0);
      if(side=='L' || side=='A')
        setPump(pinNumberPump_L, 0);
      if(side=='M' || side=='A')
        setPump(pinNumberPump_M, 0);
      Serial.print("OK\r\n");
    }
    else if(strstr(inputString, "arm enableAutoGrab")){
      enableAutoFloorGrab = true;
      autoFloorGrabStateLeft = 1;
      autoFloorGrabStateRight = 1;
      autoFloorGrabCurrentColorLeft = EMPTY;
      autoFloorGrabCurrentColorRight = EMPTY;
      autoFloorGrabActionStartTimeLeft = 0;
      autoFloorGrabActionStartTimeRight = 0;
      autoFloorGrabActionTimeoutLeft = 0;
      autoFloorGrabActionTimeoutRight = 0;
      setServoRecordedPosition(positionServo_L_Default, servos_L, NB_SERVO_ARM_L, 250);
      setServoRecordedPosition(positionServo_R_Default, servos_R, NB_SERVO_ARM_R, 250);
      Serial.print("OK\r\n");
    }  
    else if(strstr(inputString, "arm disableAutoGrab")){
      enableAutoFloorGrab = false;
      setServoRecordedPosition(positionServo_L_Default, servos_L, NB_SERVO_ARM_L, 250);
      setServoRecordedPosition(positionServo_R_Default, servos_R, NB_SERVO_ARM_R, 250);
      Serial.print("OK\r\n");
    } 
    else if(strstr(inputString, "arm default")){
      char side;
      sscanf(inputString, "arm default %c", &side);
      if(side=='R')
        setServoRecordedPosition(positionServo_R_Default, servos_R, NB_SERVO_ARM_R, 500);
      if(side=='L')
        setServoRecordedPosition(positionServo_L_Default, servos_L, NB_SERVO_ARM_L, 500);
      if(side=='M')
        setServoRecordedPosition(positionServo_M_Default, servos_M, NB_SERVO_ARM_M, 500);
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_Default, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_Default, servos_L, NB_SERVO_ARM_L, 0);
        setServoRecordedPosition(positionServo_M_Default, servos_M, NB_SERVO_ARM_M, 0);
      }
      Serial.print("OK\r\n");
    }   
    else if(strstr(inputString, "arm wallGrab")){
      char side;
      sscanf(inputString, "arm wallGrab %c", &side);
      if(side=='R')
        setServoRecordedPosition(positionServo_R_WallGrab, servos_R, NB_SERVO_ARM_R, 500);
      if(side=='L')
        setServoRecordedPosition(positionServo_L_WallGrab, servos_L, NB_SERVO_ARM_L, 500);
      if(side=='M')
        setServoRecordedPosition(positionServo_M_WallGrab, servos_M, NB_SERVO_ARM_M, 500);
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_WallGrab, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_WallGrab, servos_L, NB_SERVO_ARM_L, 0);
        setServoRecordedPosition(positionServo_M_WallGrab, servos_M, NB_SERVO_ARM_M, 0);
      }
      Serial.print("OK\r\n");
    }    
    else if(strstr(inputString, "arm floorGrabPrepare")){
      char side;
      sscanf(inputString, "arm floorGrabPrepare %c", &side);
      if(side=='R'){
        setServoRecordedPosition(positionServo_R_FloorGrab_Prepare, servos_R, NB_SERVO_ARM_R, 500);
      }
      if(side=='L'){
        setServoRecordedPosition(positionServo_L_FloorGrab_Prepare, servos_L, NB_SERVO_ARM_L, 500);
      }
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_FloorGrab_Prepare, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_FloorGrab_Prepare, servos_L, NB_SERVO_ARM_L, 0);   
      }
      Serial.print("OK\r\n");
    }  
    else if(strstr(inputString, "arm floorGrab")){
      char side;
      sscanf(inputString, "arm floorGrab %c", &side);
      if(side=='R'){
        setServoRecordedPosition(positionServo_R_FloorGrab, servos_R, NB_SERVO_ARM_R, 150);
      }
      if(side=='L'){
        setServoRecordedPosition(positionServo_L_FloorGrab, servos_L, NB_SERVO_ARM_L, 150);
      }
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_FloorGrab, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_FloorGrab, servos_L, NB_SERVO_ARM_L, 0);      
      }
      Serial.print("OK\r\n");
    }  
    else if(strstr(inputString, "arm stockPrepare")){
      char side;
      sscanf(inputString, "arm stockPrepare %c", &side);
      if(side=='R')
        setServoRecordedPosition(positionServo_R_Stock_Prepare, servos_R, NB_SERVO_ARM_R, 500);
      if(side=='L')
        setServoRecordedPosition(positionServo_L_Stock_Prepare, servos_L, NB_SERVO_ARM_L, 500);
      if(side=='M')
        setServoRecordedPosition(positionServo_M_Stock_Prepare, servos_M, NB_SERVO_ARM_M, 500);
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_Stock_Prepare, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_Stock_Prepare, servos_L, NB_SERVO_ARM_L, 0);
        setServoRecordedPosition(positionServo_M_Stock_Prepare, servos_M, NB_SERVO_ARM_M, 0);
      }
      Serial.print("OK\r\n");
    } 
    else if(strstr(inputString, "arm stockDepositPrepare")){
      char side;
      sscanf(inputString, "arm stockDepositPrepare %c", &side);
      if(side=='R')
        setServoRecordedPosition(positionServo_R_Stock_Prepare_Deposit, servos_R, NB_SERVO_ARM_R, 500);
      if(side=='L')
        setServoRecordedPosition(positionServo_L_Stock_Prepare_Deposit, servos_L, NB_SERVO_ARM_L, 500);
      if(side=='M'){
        setServoRecordedPosition(positionServo_M_WallGrab_Lift, servos_M, NB_SERVO_ARM_M, 300);
        setServoRecordedPosition(positionServo_M_Stock_Prepare_Deposit, servos_M, NB_SERVO_ARM_M, 500);
      }
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_Stock_Prepare_Deposit, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_Stock_Prepare_Deposit, servos_L, NB_SERVO_ARM_L, 0);
        setServoRecordedPosition(positionServo_M_WallGrab_Lift, servos_M, NB_SERVO_ARM_M, 300);
        setServoRecordedPosition(positionServo_M_Stock_Prepare_Deposit, servos_M, NB_SERVO_ARM_M, 0);
      }
      Serial.print("OK\r\n");
    } 
    else if(strstr(inputString, "arm stock1")){
      char side;
      sscanf(inputString, "arm stock1 %c", &side);
      if(side=='R')
        setServoRecordedPosition(positionServo_R_Stock_1, servos_R, NB_SERVO_ARM_R, 500);
      if(side=='L')
        setServoRecordedPosition(positionServo_L_Stock_1, servos_L, NB_SERVO_ARM_L, 500);
      if(side=='M')
        setServoRecordedPosition(positionServo_M_Stock_1, servos_M, NB_SERVO_ARM_M, 500);
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_Stock_1, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_Stock_1, servos_L, NB_SERVO_ARM_L, 0);
        setServoRecordedPosition(positionServo_M_Stock_1, servos_M, NB_SERVO_ARM_M, 0);
      }
      Serial.print("OK\r\n");
    }   
    else if(strstr(inputString, "arm stock2")){
      char side;
      sscanf(inputString, "arm stock2 %c", &side);
      if(side=='R')
        setServoRecordedPosition(positionServo_R_Stock_2, servos_R, NB_SERVO_ARM_R, 500);
      if(side=='L')
        setServoRecordedPosition(positionServo_L_Stock_2, servos_L, NB_SERVO_ARM_L, 500);
      if(side=='M')
        setServoRecordedPosition(positionServo_M_Stock_2, servos_M, NB_SERVO_ARM_M, 500);
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_Stock_2, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_Stock_2, servos_L, NB_SERVO_ARM_L, 0);
        setServoRecordedPosition(positionServo_M_Stock_2, servos_M, NB_SERVO_ARM_M, 0);
      }
      Serial.print("OK\r\n");
    }   
    else if(strstr(inputString, "arm stock3")){
      char side;
      sscanf(inputString, "arm stock3 %c", &side);
      if(side=='R')
        setServoRecordedPosition(positionServo_R_Stock_3, servos_R, NB_SERVO_ARM_R, 500);
      if(side=='R')
        setServoRecordedPosition(positionServo_L_Stock_3, servos_L, NB_SERVO_ARM_L, 500);
      if(side=='M')
        setServoRecordedPosition(positionServo_M_Stock_3, servos_M, NB_SERVO_ARM_M, 500);
      if(side=='A'){
        setServoRecordedPosition(positionServo_R_Stock_3, servos_R, NB_SERVO_ARM_R, 0);
        setServoRecordedPosition(positionServo_L_Stock_3, servos_L, NB_SERVO_ARM_L, 0);
        setServoRecordedPosition(positionServo_M_Stock_3, servos_M, NB_SERVO_ARM_M, 0);
      }
      Serial.print("OK\r\n");
    } 
    else{
      Serial.print("ERROR\r\n");
    }
    memset(inputString, '\0', INPUT_STR_SIZE);
    stringReady = false;
  }
  delay(1);
}
