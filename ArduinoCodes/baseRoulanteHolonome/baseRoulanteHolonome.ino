#include "BrushlessMotor.h" 

#define MODE_I2C
#ifndef MODE_I2C
  #define MODE_SERIAL
  #define SERIAL_DEBUG
#endif
#include "comunication.h"

const float wheelPerimeter = 188.495559215;//mm
const float wheelDistanceA = 120;//mm
const float wheelDistanceB = 125;//mm
const float wheelDistanceC = 123;//mm

BrushlessMotor motorA(0, wheelPerimeter, true);//9,10,11
BrushlessMotor motorB(1, wheelPerimeter, true);//5,3,2
BrushlessMotor motorC(2, wheelPerimeter, true);//8,7,6

const double motorA_angle = -60;//°
const double motorB_angle = 180;//°
const double motorC_angle =  60;//°

//--FRONT-
//-A-----C
//---\-/--
//----|---
//----B---
//--BACK--

void setup()
{
  //Serial.begin(115200);
  //Init motor
  motorA.begin();  
  motorB.begin();
  motorC.begin();

  //Init communication
  comunication_begin(7);//I2C address 7

  /*motorA.setSpeed(1);
  motorB.setSpeed(1);
  motorC.setSpeed(1);*/
}
//wheel perimeter 247mm

//In meters, degrees, m/s and °/s
double xPos = 0, yPos = 0, anglePos = 0;
double xTarget = 0, yTarget = 0, angleTarget = 0, speedTarget = 5.5, angleSpeedTarget = 50;

void updatePosition(){
  double distA = motorA.getAndResetDistanceDone();
  double distB = motorB.getAndResetDistanceDone();
  double distC = motorC.getAndResetDistanceDone();
  
  double xA = sin((motorA_angle+anglePos+90)*DEG_TO_RAD)*distA;
  double xB = sin((motorB_angle+anglePos+90)*DEG_TO_RAD)*distB;
  double xC = sin((motorC_angle+anglePos+90)*DEG_TO_RAD)*distC;

  double yA = cos((motorA_angle+anglePos+90)*DEG_TO_RAD)*distA; //motorA_angle+90 is the wheel angle
  double yB = cos((motorB_angle+anglePos+90)*DEG_TO_RAD)*distB;
  double yC = cos((motorC_angle+anglePos+90)*DEG_TO_RAD)*distC;

  xPos += (xA+xB+xC);
  yPos += (yA+yB+yC);

  double angleDoneA = (distA*360)/(2.0d*PI*(wheelDistanceA/1000.0d));
  double angleDoneB = (distB*360)/(2.0d*PI*(wheelDistanceB/1000.0d));
  double angleDoneC = (distC*360)/(2.0d*PI*(wheelDistanceC/1000.0d));

  anglePos += (angleDoneA+angleDoneB+angleDoneC)/3.0d;
  if(anglePos>180.0d) anglePos += -360.0d;
  if(anglePos<-180.0d) anglePos += 360.0d;
}


double custom_mod(double a, double n){
  return a - floor(a/n) * n;
}

double angleDiff(double a, double b){
  return custom_mod((a-b)+180, 360)-180;
}

double targetMovmentAngle = 0;
double targetSpeed_mps = 0.0;// m/s
double targetAngleSpeed_dps = 0;// °/s

double targetAngleError = 0.5; //°
double targetPosError = 0.0005; //meters
bool targetReached = true;
int targetReachedCountTarget = 0;
int targetReachedCount = 0;

//Y is forward, X is right side (motor C side)
void updateAsserv(){
  //Translation
  double xDiff = xTarget - xPos;
  double yDiff = yTarget - yPos;
  double translationError = sqrt(pow(xPos - xTarget,2) + pow(yPos - yTarget,2)); // meters
  double translationAngle = 0;
  if(xDiff!=0.f)
    translationAngle = atan2(xDiff, yDiff)*RAD_TO_DEG;
  else if(yDiff<0.f)
    translationAngle = -180;

  targetMovmentAngle = angleDiff(translationAngle, anglePos);

  targetSpeed_mps = translationError*2;
  if(abs(targetSpeed_mps)>speedTarget)
    targetSpeed_mps = targetSpeed_mps>0?speedTarget:-speedTarget;

  //Rotation
  double rotationError = angleDiff(angleTarget,anglePos);
  targetAngleSpeed_dps = rotationError*5;
  if(abs(targetAngleSpeed_dps)>angleSpeedTarget)
    targetAngleSpeed_dps = targetAngleSpeed_dps>0?angleSpeedTarget:-angleSpeedTarget;

  if(translationError>targetPosError || fabs(rotationError)>targetAngleError){
    targetReached = false;
    targetReachedCount=0;
  }
  else{
    if(targetReachedCount >= targetReachedCountTarget)
      targetReached = true;  
    targetReachedCount++;
    targetAngleSpeed_dps=0;
    targetSpeed_mps=0;
  }
}

void printCharts(){
  //Position
  Serial.print(xPos*1000);Serial.print(" ");
  Serial.print(yPos*1000);Serial.print(" ");
  Serial.print(xTarget*1000);Serial.print(" ");
  Serial.print(yTarget*1000);Serial.print(" ");

  //Angle
  Serial.print(anglePos);Serial.print(" ");
  Serial.print(angleTarget);Serial.print(" ");
  Serial.print(targetMovmentAngle);Serial.print(" ");

  //Angle Speed
  Serial.print(targetAngleSpeed_dps);Serial.print(" ");
  Serial.print(angleSpeedTarget);Serial.print(" ");

  //Position Speed
  Serial.print(targetSpeed_mps*1000);Serial.print(" ");
  Serial.print(speedTarget*1000);Serial.print(" ");

  //Motor Speed
  Serial.print(motorA.getSpeed()*1000);Serial.print(" ");
  Serial.print(motorA.getPower()*1000);Serial.print(" ");
  //Serial.print(motorB.getSpeed()*1000);Serial.print(" ");
  //Serial.print(motorC.getSpeed()*1000);Serial.print(" ");
  Serial.print("\r\n");
}

bool movementEnabled = false;
bool emergencyStop = false;
bool manualMode = false;
void control(){
  //Update position
  updatePosition();
  //Serial.print("Position\t");Serial.print(xPos);Serial.print("\t");Serial.print(yPos);Serial.print("\t");Serial.print(anglePos);Serial.print("\n");

  //double daTargetDistance = sqrt(pow(xpos - xTarget,2) + pow(ypos - yTarget,2)); // meters
  //double daTargetAngle = angleDiff(angleTarget,angle);

  /* Compute speeds with asserv:
   *  targetMovmentAngle
   *  targetSpeed_mps
   *  targetAngleSpeed_dps
   */
   if(!manualMode)
    updateAsserv();
  #ifdef SERIAL_DEBUG
    printCharts();
  #endif
  
  
  //Compute translation
  double speedA = targetSpeed_mps * sin((targetMovmentAngle-motorA_angle)*DEG_TO_RAD);
  double speedB = targetSpeed_mps * sin((targetMovmentAngle-motorB_angle)*DEG_TO_RAD);
  double speedC = targetSpeed_mps * sin((targetMovmentAngle-motorC_angle)*DEG_TO_RAD);

  //Compute Rotation
  double arcLengthA = 2.0d*PI*(wheelDistanceA/1000.d)*(targetAngleSpeed_dps/360.0d); // arcLength in meters.
  double arcLengthB = 2.0d*PI*(wheelDistanceB/1000.d)*(targetAngleSpeed_dps/360.0d); // arcLength in meters.
  double arcLengthC = 2.0d*PI*(wheelDistanceC/1000.d)*(targetAngleSpeed_dps/360.0d); // arcLength in meters.
  double speedAngleA = arcLengthA; 
  double speedAngleB = arcLengthB;
  double speedAngleC = arcLengthC;
  
  //Serial.print(speedA*1000.0d);Serial.print("\t");Serial.print(arcLength*1000.0d);Serial.print("\n");
  
  speedA += speedAngleA;
  speedB += speedAngleB;
  speedC += speedAngleC;


  //Serial.print(speedA*1000000.f);Serial.print("\t");Serial.print(speedB*1000000.f);Serial.print("\t");Serial.print(speedC*1000000.f);Serial.print("\n");
  //Serial.print(motorA.m_currSleep);Serial.print("\t");Serial.print(motorB.m_currSleep==0);Serial.print("\t");Serial.print(motorC.m_currSleep);Serial.print("\n");
  
  //Drive motors
  if(!emergencyStop && movementEnabled){
    motorA.setSpeed(speedA);
    motorB.setSpeed(speedB);
    motorC.setSpeed(speedC);
  }
  else{
    motorA.setSpeed(0);
    motorB.setSpeed(0);
    motorC.setSpeed(0);
  }
}

int controlFrequency = 30; //Hz

void executeOrder(){
  comunication_read();
  if(comunication_msgAvailable()){
    if(comunication_InBuffer[0] == '#' && comunication_InBuffer[1] != '\0'){
      //ignore
    }
    else if(strstr(comunication_InBuffer, "id")){
      sprintf(comunication_OutBuffer, "MovingBaseAlexandreV4");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "move enable")){
      movementEnabled = true;
      sprintf(comunication_OutBuffer, "move OK");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "move disable")){
      movementEnabled = false;
      sprintf(comunication_OutBuffer, "move OK");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "pos set ")){
      int x_pos=0, y_pos=0, angle_pos=0;
      int res = sscanf(comunication_InBuffer, "pos set %i %i %i", &y_pos, &x_pos, &angle_pos);
      xPos = (float)(x_pos)/1000.0f;
      yPos = (float)(y_pos)/1000.0f;
      anglePos = angle_pos;
      xTarget = xPos;
      yTarget = yPos;
      angleTarget = anglePos;
      sprintf(comunication_OutBuffer, "pos OK");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "pos getXY")){
      sprintf(comunication_OutBuffer,"pos %i %i %i %i",(int)(yPos*1000.0f), (int)(xPos*1000.0f), (int)(anglePos), (int)(targetSpeed_mps*10));
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "pos getDA")){
      sprintf(comunication_OutBuffer, "ERROR");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "move XY ")){
      int i_x_pos=0, i_y_pos=0, i_angle=0, i_speed_pos=1;
      sscanf(comunication_InBuffer, "move XY %i %i %i %i", &i_y_pos, &i_x_pos, &i_angle, &i_speed_pos);
      xTarget = (float)(i_x_pos)/1000.0f;
      yTarget = (float)(i_y_pos)/1000.0f;
      angleTarget = (float)(i_angle);
      speedTarget = (float)(i_speed_pos)/10.0f;
      angleSpeedTarget = speedTarget * 90;
      emergencyStop = false;
      targetReached = false;
      sprintf(comunication_OutBuffer,"move OK");
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "move DA")){
      sprintf(comunication_OutBuffer, "ERROR");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "move status")){
      if(targetReached)
        sprintf(comunication_OutBuffer, "move finished");//max 29 Bytes
      else
        sprintf(comunication_OutBuffer, "move running");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "speed get")){
      sprintf(comunication_OutBuffer,"speed %.1f",targetSpeed_mps);
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "move break")){
      emergencyStop = true;
      sprintf(comunication_OutBuffer,"move OK");
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "move RM")){
      int i_distance=0, i_vitesse=4;
      sscanf(comunication_InBuffer, "move RM %i %i", &i_distance, &i_vitesse);
      sprintf(comunication_OutBuffer,"ERROR");
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "support XY")){
      sprintf(comunication_OutBuffer,"support 1");
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "support Path")){
      sprintf(comunication_OutBuffer,"support 0");
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "manual enable")){
      manualMode=true;
      sprintf(comunication_OutBuffer,"manual OK");
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "manual disable")){
      manualMode=false;
      targetMovmentAngle = 0;
      targetSpeed_mps = 0;
      targetAngleSpeed_dps = 0;
      xTarget = xPos;
      yTarget = yPos;
      angleTarget = anglePos;
      sprintf(comunication_OutBuffer,"manual OK");
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "manual set ")){
      int i_move_angle=0, i_move_speed=0, i_angle_speed=0;
      sscanf(comunication_InBuffer, "manual set %i %i %i", &i_move_angle, &i_move_speed, &i_angle_speed);
      targetMovmentAngle = i_move_angle;
      targetSpeed_mps = (float)(i_move_speed)/10.0f;
      targetAngleSpeed_dps = i_angle_speed;
      emergencyStop = false;
      sprintf(comunication_OutBuffer,"manual OK");
      comunication_write();//async
    }
    else{
      sprintf(comunication_OutBuffer,"ERROR");
      comunication_write();//async
    }
    comunication_cleanInputs();
  }
}

unsigned long lastControlMillis = 0;
float sinCounter = 0;
void loop()
{
  //Read commands
  executeOrder();
  
  //Run control loop
  unsigned long currMillis = millis();
  int controlMillis = 1000/controlFrequency;
  if(currMillis - lastControlMillis >= controlMillis){
    lastControlMillis = currMillis;
    control();
  }

  //Spin motors
  motorA.spin();
  motorB.spin();
  motorC.spin();
}
