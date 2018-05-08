#include <Wire.h>
#include <Servo.h>

#include "SparkFun_APDS9960.h"

#define STEPPER_MOTOR_DIRECTION_PIN 12
#define STEPPER_MOTOR_STEP_PIN 11
//400*16 = 6400
#define STEPPER_MOTOR_STEP_COUNT 6400
#define STEPPER_MOTOR_STEP_PER_SLOT 800


#define BALL_CANNON_SERVO_PIN 4
#define BALL_CANNON_SERVO_OPEN 55  
#define BALL_CANNON_SERVO_CLOSE 3
Servo ballCannonServo;


#define BALL_TRAP_SERVO_PIN 2
#define BALL_TRAP_SERVO_OPEN 130  
#define BALL_TRAP_SERVO_CLOSE 255
Servo ballTrapServo;

#define BALL_RECUPERATEUR_SERVO_PIN 3
#define BALL_RECUPERATEUR_SERVO_EMPTY 0  
#define BALL_RECUPERATEUR_SERVO_OPEN 80
#define BALL_RECUPERATEUR_SERVO_GATHER 100  
#define BALL_RECUPERATEUR_SERVO_CLOSE 255
Servo ballRecuperateurServo;

#define MOTOR1_SPEED_PIN 6 // ENA
#define MOTOR1_DIR_A_PIN A1 // IN1
#define MOTOR1_DIR_B_PIN A0 // IN2

#define MOTOR2_SPEED_PIN 8 // ENB
#define MOTOR2_DIR_A_PIN 7 // IN3
#define MOTOR2_DIR_B_PIN 5 // IN4

SparkFun_APDS9960 colorSensor = SparkFun_APDS9960();
uint16_t ambient_light = 0;
uint16_t red_light = 0;
uint16_t green_light = 0;
uint16_t blue_light = 0;
uint8_t prox = 0;


enum  {
  GREEN,
  ORANGE,
  UNKOWN,
  EMPTY
} BALL_COLOR;

int stepperBallColors[8];
int currentStepperIndex = 0;
int currentBacStepperIndex = 0;

void spinStepper(int step, bool forward=true, bool slow=false){
  for(int i=0;i<step;i++){
    if(i%2)
      digitalWrite(STEPPER_MOTOR_STEP_PIN, HIGH); 
    else
      digitalWrite(STEPPER_MOTOR_STEP_PIN, LOW);
    if(slow)
      delayMicroseconds(5000);
    else 
      delayMicroseconds(2000);
  }
}

void setup() {
  // Initialize Serial port
  Serial.begin(9600);
  
  // Initialize APDS-9960
  colorSensor.init();
  colorSensor.enableLightSensor(false);
  colorSensor.setProximityGain(GGAIN_2X);
  colorSensor.enableProximitySensor(false);
  delay(500); // color sensor init and calib

  // Stepper motor
  pinMode(STEPPER_MOTOR_STEP_PIN, OUTPUT);
  pinMode(STEPPER_MOTOR_DIRECTION_PIN, OUTPUT);
  digitalWrite(STEPPER_MOTOR_DIRECTION_PIN, HIGH); 

  // Servo motor
  ballCannonServo.attach(BALL_CANNON_SERVO_PIN);
  ballCannonServo.write(BALL_CANNON_SERVO_CLOSE);

  ballTrapServo.attach(BALL_TRAP_SERVO_PIN);
  ballTrapServo.write(BALL_TRAP_SERVO_CLOSE);

  ballRecuperateurServo.attach(BALL_RECUPERATEUR_SERVO_PIN);
  ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_CLOSE);

  // DC motor
  pinMode(MOTOR1_SPEED_PIN, OUTPUT);
  pinMode(MOTOR1_DIR_A_PIN, OUTPUT);
  pinMode(MOTOR1_DIR_B_PIN, OUTPUT);
  digitalWrite(MOTOR1_DIR_B_PIN, LOW); //FLIP to change DIR
  digitalWrite(MOTOR1_DIR_A_PIN, HIGH); //FLIP to change DIR
  analogWrite(MOTOR1_SPEED_PIN, 0);

  
  pinMode(MOTOR2_SPEED_PIN, OUTPUT);
  pinMode(MOTOR2_DIR_A_PIN, OUTPUT);
  pinMode(MOTOR2_DIR_B_PIN, OUTPUT);
  digitalWrite(MOTOR2_DIR_B_PIN, LOW); //FLIP to change DIR
  digitalWrite(MOTOR2_DIR_A_PIN, HIGH); //FLIP to change DIR
  analogWrite(MOTOR2_SPEED_PIN, 0);

  //Stepper balls
  for(int i=0;i<8;i++)
    stepperBallColors[i] = EMPTY;
}

void setBallColor(int color){
  stepperBallColors[currentStepperIndex] = color;
}

void incrementBallIndex(){
  currentStepperIndex++;
  if(currentStepperIndex>=8)
    currentStepperIndex=0;
  currentBacStepperIndex--;
  if(currentBacStepperIndex<0)
    currentBacStepperIndex=7;
}

int getBallIndexAtCannon(){
  int index = currentBacStepperIndex+3;
  if(index>=8)
    index-=8;
  return index;
}

int getBallIndexAtTrap(){
  int index = currentBacStepperIndex+4;
  if(index>=8)
    index-=8;
  return index;
}

int getBallIndexAtGather(){
  int index = currentBacStepperIndex+1;
  if(index>=8)
    index-=8;
  return index;
}

int getBallColorAtCannon(){
  return stepperBallColors[getBallIndexAtCannon()];
}

int getBallColorAtTrap(){
  return stepperBallColors[getBallIndexAtTrap()];
}

int getBallColorAtGather(){
  return stepperBallColors[getBallIndexAtGather()];
}

int getBallProximity(){
  if(colorSensor.readProximity(prox)){
      return prox;
  }
  return 0;
}

int getBallColor(){
  if (colorSensor.readRedLight(red_light) &&
      colorSensor.readGreenLight(green_light) &&
      colorSensor.readBlueLight(blue_light)) {
    /*Serial.print(" Red: ");
    Serial.print(red_light);
    Serial.print(" Green: ");
    Serial.print(green_light);
    Serial.print(" Blue: ");
    Serial.println(blue_light);*/
    if(red_light>green_light && red_light > 200 && blue_light < 300)
      return ORANGE;
    if(green_light>red_light && green_light > 200 && blue_light < 300)
      return GREEN;
  } 
  if(getBallProximity() == 255)
    return UNKOWN;
  else
    return EMPTY;
}

void play() {
  
  // Read the light levels (ambient, red, green, blue)
  if (  !colorSensor.readAmbientLight(ambient_light) ||
        !colorSensor.readRedLight(red_light) ||
        !colorSensor.readGreenLight(green_light) ||
        !colorSensor.readBlueLight(blue_light) ||
        !colorSensor.readProximity(prox)) {
    Serial.println("Error reading light values");
  } else {
    Serial.print("Ambient: ");
    Serial.print(ambient_light);
    Serial.print(" Red: ");
    Serial.print(red_light);
    Serial.print(" Green: ");
    Serial.print(green_light);
    Serial.print(" Blue: ");
    Serial.println(blue_light);
    Serial.print(" Proximity: ");
    Serial.println(prox);
  }

  for(int i=0;i<1000;i++){
    if(i%2)
      digitalWrite(STEPPER_MOTOR_STEP_PIN, HIGH); 
    else
      digitalWrite(STEPPER_MOTOR_STEP_PIN, LOW); 
    delay(1);
  }
  // Wait 1 second before next reading
  delay(1000);
  
  analogWrite(MOTOR1_SPEED_PIN, 255);
  delay(1000);
  analogWrite(MOTOR1_SPEED_PIN, 0);
  
  ballCannonServo.write(BALL_CANNON_SERVO_OPEN);
  ballTrapServo.write(BALL_TRAP_SERVO_OPEN);
  ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_OPEN);
  delay(500);
  ballCannonServo.write(BALL_CANNON_SERVO_CLOSE);
  ballTrapServo.write(BALL_TRAP_SERVO_CLOSE);
  ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_CLOSE);
}

#define INPUT_STR_SIZE 32
#define OUPUT_STR_SIZE 32
char inputString[INPUT_STR_SIZE];
char outputString[OUPUT_STR_SIZE];
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

void resetOutputString(){
  memset(outputString, '\0', OUPUT_STR_SIZE);
}

void loop(){
  readSerial();
  if(stringReady){
    if(inputString[0] == '#' && inputString[1] != '\0'){ //debug message
    }
    else if(!strcmp(inputString, "id")){
      sprintf(outputString, "BallGatherAlex\r\n");
      Serial.print(outputString);
    }
    else if(!strcmp(inputString, "cannon open")){
      stepperBallColors[getBallIndexAtCannon()] = EMPTY;
      ballCannonServo.write(BALL_CANNON_SERVO_OPEN);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "cannon close")){
      ballCannonServo.write(BALL_CANNON_SERVO_CLOSE);
      Serial.print("OK\r\n");
    }
    else if(strstr(inputString, "cannon speed")){
      int speed = 0;
      sscanf(inputString, "cannon speed %i", &speed);
      analogWrite(MOTOR1_SPEED_PIN, speed);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "bac open")){
      ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_OPEN);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "bac close")){
      ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_CLOSE);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "bac gather")){
      for(int i=0;i<10;i++){
        ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_GATHER);
        delay(50);
        ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_GATHER-5);
        delay(50);
      }
      ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_GATHER);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "bac empty")){
      ballRecuperateurServo.write(BALL_RECUPERATEUR_SERVO_EMPTY);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "trap open")){
      stepperBallColors[getBallIndexAtTrap()] = EMPTY;
      ballTrapServo.write(BALL_TRAP_SERVO_OPEN);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "trap close")){
      ballTrapServo.write(BALL_TRAP_SERVO_CLOSE);
      Serial.print("OK\r\n");
    }
    else if(strstr(inputString, "stepper spin")){
      int step = 0, dir=0;
      sscanf(inputString, "stepper spin %i %i", &step, &dir);
      spinStepper(step, dir);
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "stepper slot")){
      spinStepper(STEPPER_MOTOR_STEP_PER_SLOT);
      incrementBallIndex();
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "stepper gather")){
      if(stepperBallColors[currentBacStepperIndex] == EMPTY)
        stepperBallColors[currentBacStepperIndex] = getBallColor();
      spinStepper(STEPPER_MOTOR_STEP_PER_SLOT, true, true);
      incrementBallIndex();
      Serial.print("OK\r\n");
    }
    else if(!strcmp(inputString, "ball color get")){
      sprintf(outputString, "ball color %i\r\n", getBallColor());
      Serial.print(outputString);
    }
    else if(!strcmp(inputString, "cannon color get")){
      sprintf(outputString, "ball color %i\r\n", stepperBallColors[getBallIndexAtCannon()]);
      Serial.print(outputString);
    }
    else if(!strcmp(inputString, "gather color get")){
      sprintf(outputString, "ball color %i\r\n", stepperBallColors[getBallIndexAtGather()]);
      Serial.print(outputString);
    }
    else if(!strcmp(inputString, "colors get")){
      sprintf(outputString, "%i>%i;%i;%i;%i;%i;%i;%i;%i\r\n"
      ,currentBacStepperIndex
      ,stepperBallColors[0]
      ,stepperBallColors[1]
      ,stepperBallColors[2]
      ,stepperBallColors[3]
      ,stepperBallColors[4]
      ,stepperBallColors[5]
      ,stepperBallColors[6]
      ,stepperBallColors[7]);
      Serial.print(outputString);
    }
    else if(!strcmp(inputString, "trap color get")){
      sprintf(outputString, "ball color %i\r\n", stepperBallColors[getBallIndexAtTrap()]);
      Serial.print(outputString);
    }
    else if(!strcmp(inputString, "ball proximity get")){
      sprintf(outputString, "ball proximity %i\r\n", getBallProximity());
      Serial.print(outputString);
    }
    else{
      Serial.print("ERROR\r\n");
    }
    memset(inputString, '\0', INPUT_STR_SIZE);
    stringReady = false;
  }
}

