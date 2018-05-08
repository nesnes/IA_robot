#include <Servo.h>


const int NB_SERVO = 7;

const int PUMP_PIN = 10;
const int VALVE_PIN = 11;
const int TOWER_PIN = 12;
const int TOWER_OPEN = 90;
const int TOWER_PREPARE = 140;
const int TOWER_CLOSE = 180;

const int MIN_PULSE = 550;
const int MAX_PULSE = 2450;

const int TEST_ANGLE_BEGIN = 0;
const int TEST_ANGLE_END = 255;

//coordinates of joint 0 of the arm in x,y frame.
const float X_ARM = 127;
const float Y_ARM = -308; 

Servo servos[NB_SERVO];
Servo servoTower;

int servoPositionDefault[NB_SERVO] = {90,45,45,175,90,0,180};
int servoPositionNeutral[NB_SERVO] = {90,90,90,140,90,90,90};
int servoPositionFindCube[NB_SERVO] = {140,60,0,50,180,0,90};

int servoPositionAddTowerPrepare[NB_SERVO] = {105,100,0,138,0,95,125};
int servoPositionAddTowerFinal[NB_SERVO] = {100,100,0,138,0,95,125};
int servoPositionAddTowerExit[NB_SERVO] = {115,100,0,138,0,95,125};

int servoPositionGetGolden1Prepare[NB_SERVO] = {85,110,110,105,90,25,90};
int servoPositionGetGolden1Final[NB_SERVO] = {85,110,140,105,90,25,90};
int servoPositionGetGolden2Prepare[NB_SERVO] = {108,110,115,105,110,30,120};
int servoPositionGetGolden2Final[NB_SERVO] = {108,110,140,105,110,30,120};

int servoPositionOpenBallsPrepare[NB_SERVO] = {100,50,25,150,145,90,60};
int servoPositionOpenBallsFinal[NB_SERVO] = {120,50,25,150,150,90,15};

void setup() {
  Serial.begin(9600);

  pinMode(PUMP_PIN, OUTPUT); 
  digitalWrite(PUMP_PIN, HIGH);
  pinMode(VALVE_PIN, OUTPUT); 
  digitalWrite(VALVE_PIN, HIGH);
  for(int i=0; i<NB_SERVO; i++){
    servos[i].attach(i+2, MIN_PULSE, MAX_PULSE);
  }
  
  for(int i=0; i<NB_SERVO; i++){
    servos[i].write(servoPositionDefault[i]);
  }
  servoTower.attach(TOWER_PIN, MIN_PULSE, MAX_PULSE);
  servoTower.write(TOWER_CLOSE);
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

void roaming(bool &increasingMode, int &angle){
  if(increasingMode){
    angle+=5;
  }
  else{
    angle-=5;
  }
  if(angle >= TEST_ANGLE_END){
    increasingMode = false;
  }
  if(angle <= TEST_ANGLE_BEGIN){
    increasingMode = true;
  }
}

void moveArmXYZ(float x, float y, float z, float angle = 90, int duration=300){
  int positions[NB_SERVO];
  float x2 = x*x;
  float y2 = y*y;
  float z2 = z*z;
  /*positions[0] = 119.00000f + x*-0.18002f + y*-0.17998f + z*-0.00000f + x2*-0.00180f + y2*0.00180f + z2*0.00000f;
  positions[1] = 56.68137f + x*0.37498f + y*0.37502f + z*1.07361f + x2*-0.00450f + y2*-0.00127f + z2*-0.00294f;
  positions[2] = 116.24902f + x*0.10170f + y*0.10163f + z*0.97109f + x2*-0.00098f + y2*-0.00808f + z2*-0.00318f;
  positions[3] = 85.64804f + x*-0.17995f + y*-0.18005f + z*1.09076f + x2*0.00262f + y2*-0.00772f + z2*-0.00446f;
  positions[4] = 90.00000f + x*-0.00000f + y*0.00000f + z*-0.00000f + x2*0.00000f + y2*-0.00000f + z2*0.00000f;
  positions[5] = 150.33922f + x*-0.07000f + y*-0.07000f + z*-1.24370f + x2*0.00080f + y2*0.00087f + z2*0.00462f;*/
  positions[0] = 119.00000f + x*-0.28000f + y*-0.00000f + z*-0.00000f + x2*-0.00080f + y2*0.00000f + z2*0.00000f;
  positions[1] = 83.01593f + x*0.17375f + y*0.55333f + z*0.46796f + x2*-0.00230f + y2*-0.00305f + z2*-0.00008f;
  positions[2] = 131.06413f + x*0.61292f + y*-0.53167f + z*0.62258f + x2*-0.00617f + y2*-0.00175f + z2*-0.00140f;
  positions[3] = 65.82761f + x*0.33167f + y*-0.81667f + z*1.53792f + x2*-0.00277f + y2*-0.00135f + z2*-0.00646f;
  positions[4] = 90.00000f + x*0.00000f + y*0.00000f + z*-0.00000f + x2*-0.00000f + y2*0.00000f + z2*0.00000f;
  positions[5] = 147.22141f + x*-0.26667f + y*0.06167f + z*-1.16040f + x2*0.00237f + y2*-0.00045f + z2*0.00437f;
  positions[6] = 123.02859f + x*-0.05083f + y*-0.31000f + z*0.04790f + x2*-0.00207f + y2*0.00220f + z2*-0.00021f;

  
  
  //positions[6] = 124.50000f + x*-0.22501f + y*-0.22499f + x2*-0.00015f + y2*0.00135f;
  positions[6] -= angle-90;
  setServoRecordedPosition(positions, duration);
}

void findPosition(int servoId, int angle, bool stopServo){
  if(!stopServo){
    servos[servoId].write(angle);
    char str[15];
    sprintf (str, "id : %d Pos : %d",servoId, angle);
    Serial.println(str);
  }
//  else{
//    Serial.println(servos[servoId].read());
//  }

}

void convertCart2Polar(float x, float y, float& r, float& theta){
  r = sqrt(square(x-X_ARM) + square(y - Y_ARM)) + Y_ARM;
  theta = atan2(y - Y_ARM, x-X_ARM)*180/PI;
}

/*//find value for regression
void setTestPosition(float x, float y){
 // servos[0].write(-0.1686419652f*x+110.4737435666f);
 // servos[1].write(-0.0003075787f*(x*x)+0.0784325787f*x+80.f);
 // servos[2].write(-0.0010153717f*(x*x)+0.2706844893f*x+150.f);
 // servos[3].write(-0.0002463042f*(x*x)+0.070650716f*x+155.f);
  
 // servos[4].write(90);
 // servos[5].write(90);
 // servos[6].write(90);
 // servos[0].write(105);
 // servos[1].write(-0.0023122684f*(y*y) + 0.7660990331f*y + 85.f);
 // servos[2].write(-0.0015900012f*(y*y) + 0.0995679423f*y + 168.f);
 // servos[3].write(0.0004448433*(y*y) - 0.5761801374f*y + 163.f);
  
 // servos[4].write(90);
 // servos[5].write(90);
 // servos[6].write(90);

  float r;
  float theta;

  convertCart2Polar(x, y, r, theta);
  char str[15];

  Serial.print("r : ");
  Serial.print(r);
  Serial.print(" theta ");
  Serial.println(theta);

  servos[0].write(theta);
  servos[1].write(-0.0019998649f*(r*r) + 0.5295733943f*r + 85);
  servos[2].write(-0.0019248398f*(r*r) + 0.0712263104f*r + 152);
  servos[3].write(0.0004740331f*(r*r) - 0.5326431508f*r + 130);
  servos[4].write(90);
  servos[5].write(90);
  servos[6].write(90);
}*/

void setPosition(float x, float y){
  float r;
  float theta;

  convertCart2Polar(x, y, r, theta);
  char str[15];

  Serial.print("r : ");
  Serial.print(r);
  Serial.print(" theta ");
  Serial.println(theta);
  servos[1].write(150); //go up to avoid violent movement into floor
  delay(100);

  servos[0].write(theta);
  
  servos[2].write(-0.0015900012f*(r*r) + 0.0995679423f*r + 168.f);
  servos[3].write(0.0004448433*(r*r) - 0.5761801374f*r + 163.f);
  
  servos[4].write(90);
  servos[5].write(90);
  servos[6].write(90);
  servos[1].write(-0.0023122684f*(r*r) + 0.7660990331f*r + 85.f);
}

void setServoRecordedPosition(int* positions, int duration){
  unsigned long startTime = millis();
  //Save start position
  int startPosition[NB_SERVO];
  for(int i=0; i<NB_SERVO;i++){
    startPosition[i] = servos[i].read();
  }
  //SetProgressive position
  do{
    float stepRatio = (1.f/(float)duration)*(float)(millis() - startTime);
    for(int i=0; i<NB_SERVO;i++){
      servos[i].write(startPosition[i]+(positions[i]-startPosition[i])*stepRatio);
    }
    delay(1);
  }while(millis() - startTime < duration);
  //Set final position
  for(int i=0; i<NB_SERVO;i++){
    servos[i].write(positions[i]);
  }
}

void grab(){
  int angleServo1 = servos[1].read();
  Serial.print("Servo 1 Before GRAB: ");
  Serial.println(angleServo1);
  angleServo1 -= 20;
  Serial.print("After : ");
  Serial.println(angleServo1);
  servos[1].write(angleServo1);
  int angleServo5 = servos[5].read();
  Serial.print("Servo 5 Before GRAB: ");
  Serial.println(angleServo5);
  angleServo5 += 17;
  Serial.print("After : ");
  Serial.println(angleServo5);
  servos[5].write(angleServo5);
}

void goUp(){
  int angleServo1 = servos[1].read();
  Serial.print("Servo 1 Before UP: ");
  Serial.println(angleServo1);
  angleServo1 += 5;
  Serial.print("After : ");
  Serial.println(angleServo1);
  servos[1].write(angleServo1);
}

void setPump(bool isOn){
  if(isOn){
    digitalWrite(PUMP_PIN, LOW);
  }
  else{
    digitalWrite(PUMP_PIN, HIGH);
  }  
}

void setValve(bool isOn){
  if(isOn){
    digitalWrite(VALVE_PIN, LOW);
  }
  else{
    digitalWrite(VALVE_PIN, HIGH);
  }  
}

void towerVibrate(){
  for(int i=0;i<10;i++){
    servoTower.write(TOWER_CLOSE);
    delay(50);
    servoTower.write(TOWER_CLOSE-30);
    delay(50);
  }
  servoTower.write(TOWER_CLOSE);
}

void addCurrentCube(bool startNeutral=false){
  servoTower.write(TOWER_OPEN);
  if(startNeutral)
    setServoRecordedPosition(servoPositionNeutral, 300);
  setServoRecordedPosition(servoPositionAddTowerPrepare, 500);
  setServoRecordedPosition(servoPositionAddTowerFinal, 50);
  delay(200);
  servoTower.write(TOWER_PREPARE);
  setPump(false);
  setValve(true);
  delay(200);
  setServoRecordedPosition(servoPositionAddTowerExit, 100);
  towerVibrate();
  setServoRecordedPosition(servoPositionDefault, 300);
  setValve(false);
}

int angle = TEST_ANGLE_BEGIN;
bool stopServo = false;

bool increasingMode = true; //true : angle increase, false angle decrease

void loop() {
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
    else if(!strcmp(inputString, "s")){
      stopServo = true;
      char str[15];
      sprintf (str, "Stop angle : %d", angle);
      Serial.println(str);
    }
    else if(!strcmp(inputString, "g")){
      stopServo = false;
    }
    else if(!strncmp(inputString, "setServo ",9)){
      char idSubString[3];
      char angleSubString[4];
      int index = 9;
      int i = 0;
      while(inputString[index] != ' '){
        idSubString[i] = inputString[index];
        i++;
        index++;
      }
      idSubString[i] = '\0';
      i = 0;
      while(inputString[index] != '\0'){
        angleSubString[i] = inputString[index];
        i++;
        index++;
      }
      angleSubString[i] = '\0';

      int id = atoi(idSubString);
      int angle = atoi(angleSubString);
      servos[id].write(angle);

      char str[15];
      sprintf (str, "id : %d Pos : %d",id, angle);
      Serial.println(str);     
    }
    else if(!strcmp(inputString, "getServos")){
      char strServos[100];
      strcpy(strServos, "");
      char strTemp[5];
      int value;
      for(int i=0; i< NB_SERVO; i++){
        value = servos[i].read();                
        itoa(value, strTemp, 10);
        strcat(strTemp, ";");
        strcat(strServos, strTemp);
      }
      Serial.println(strServos);
    }
    else if(!strncmp(inputString, "setPos ", 7)){// setPos xxx yyy
      char xSubString[4];
      char ySubString[4];
      int index = 7;
      int i = 0;
      while(inputString[index] != ' '){
        xSubString[i] = inputString[index];
        i++;
        index++;
      }
      xSubString[i] = '\0';
      i = 0;
      while(inputString[index] != '\0'){
        ySubString[i] = inputString[index];
        i++;
        index++;
      }
      ySubString[i] = '\0';

      float x = atof(xSubString);
      float y = atof(ySubString);

      Serial.println(xSubString);
      Serial.println(ySubString);
     
      setPosition(x,y);
    }
  /*  else if(!strncmp(inputString, "setTestPos ", 8)){// setPos xxx yyy
      char xSubString[4];
      char ySubString[4];
      int index = 8;
      int i = 0;
      while(inputString[index] != ' '){
        xSubString[i] = inputString[index];
        i++;
        index++;
      }
      xSubString[i] = '\0';
      i = 0;
      while(inputString[index] != '\0'){
        ySubString[i] = inputString[index];
        i++;
        index++;
      }
      ySubString[i] = '\0';

      float x = atof(xSubString);
      float y = atof(ySubString);

      Serial.println(xSubString);
      Serial.println(ySubString);
     
      setTestPosition(x,y);     
    }*/
    else if(!strcmp(inputString, "grab")){
      grab();
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "up")){
      goUp();
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "pump on")){
      setPump(true);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "pump off")){
      setPump(false);
      Serial.print("OK\r\n");
    }   
    else if(!strcmp(inputString, "valve open")){
      setValve(true);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "valve close")){
      setValve(false);
      Serial.print("OK\r\n");
    }      
    else if(!strcmp(inputString, "tower open")){
      servoTower.write(TOWER_OPEN);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "tower close")){
      servoTower.write(TOWER_CLOSE);
      Serial.print("OK\r\n");
    }  
    else if(!strcmp(inputString, "tower vibrate")){
      towerVibrate();
      Serial.print("OK\r\n");
    }  
    else if(!strcmp(inputString, "arm tower prepare")){
      setServoRecordedPosition(servoPositionAddTowerPrepare, 500);
      Serial.print("OK\r\n");
    }   
    else if(!strcmp(inputString, "arm tower final")){
      setServoRecordedPosition(servoPositionAddTowerFinal, 50);
      Serial.print("OK\r\n");
    }     
    else if(!strcmp(inputString, "arm default")){
      setServoRecordedPosition(servoPositionDefault, 300);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "arm ball prepare")){
      setServoRecordedPosition(servoPositionOpenBallsPrepare, 400);
      Serial.print("OK\r\n");
    }     
    else if(!strcmp(inputString, "arm ball final")){
      setServoRecordedPosition(servoPositionOpenBallsFinal, 200);
      Serial.print("OK\r\n");
    }     
    else if(!strcmp(inputString, "arm ball open")){
      setServoRecordedPosition(servoPositionOpenBallsPrepare, 400);
      setServoRecordedPosition(servoPositionOpenBallsFinal, 200);
      Serial.print("OK\r\n");
    }      
    else if(!strcmp(inputString, "arm ball retract")){
      setServoRecordedPosition(servoPositionOpenBallsPrepare, 400);
      setServoRecordedPosition(servoPositionDefault, 300);
      Serial.print("OK\r\n");
    }       
    else if(!strcmp(inputString, "arm find cube")){
      setServoRecordedPosition(servoPositionFindCube, 300);
      Serial.print("OK\r\n");
    }     
    else if(!strcmp(inputString, "arm add cube")){
      addCurrentCube();
      Serial.print("OK\r\n");
    }       
    else if(!strcmp(inputString, "arm add golden 1")){
      setServoRecordedPosition(servoPositionDefault, 300);
      setServoRecordedPosition(servoPositionGetGolden1Prepare, 500);
      setPump(true);
      setValve(false);
      setServoRecordedPosition(servoPositionGetGolden1Final, 50);
      delay(100);
      addCurrentCube();
      Serial.print("OK\r\n");
    }       
    else if(!strcmp(inputString, "arm add golden 2")){
      setServoRecordedPosition(servoPositionDefault, 300);
      setServoRecordedPosition(servoPositionGetGolden2Prepare, 500);
      setPump(true);
      setValve(false);
      setServoRecordedPosition(servoPositionGetGolden2Final, 50);
      delay(100);
      addCurrentCube();
      Serial.print("OK\r\n");
    }        
    else if(strstr(inputString, "arm xyz")){
      int x=50, y=50, z=90, angle=90;
      sscanf(inputString, "arm xyz %i %i %i %i", &x, &y, &z, &angle);
      moveArmXYZ(x,y,z, angle, 300);
      Serial.print("OK\r\n");
    }        
    else if(strstr(inputString, "arm grab")){
      int x=50, y=50, angle=90;
      int level=1;
      sscanf(inputString, "arm grab %i %i %i %i", &x, &y, &angle);
      moveArmXYZ(20,0,140, angle, 300);
      delay(200);
      moveArmXYZ(x,y,140, angle, 400);
      moveArmXYZ(x,y,40, angle, 300);
      setPump(true);
      setValve(false);
      delay(200);
      moveArmXYZ(x,y,140, angle, 300);
      moveArmXYZ(50,50,140, angle, 300);
      addCurrentCube(false);
      Serial.print("OK\r\n");
    }
    else{
      Serial.print("ERROR\r\n");
    }
    memset(inputString, '\0', INPUT_STR_SIZE);
    stringReady = false;
  }

  
  roaming(increasingMode, angle);



  
  //findPosition(0, angle, stopServo);
  //findPosition(6, angle, stopServo);
  
  
  
  delay(15);
}
