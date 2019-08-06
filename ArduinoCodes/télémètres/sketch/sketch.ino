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

void setup() {
  Serial.begin(9600);
}

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
unsigned long time;
void loop() {
  //time = millis(); // measure telemeter update time
  //updateMeasure(); // measure telemeter one at a time (slow: 24ms max)
  getDistanceMultipleSRF05(measureTab); // measure telemeter all at once (fast: 6ms max)
  //time = millis() - time; // measure telemeter update time
  //Serial.println(time); // display telemeter update time
  readSerial();
  if(stringReady){
    if(inputString[0] == '#' && inputString[1] != '\0'){ 
      //message starting with #, ignored
    }
    else if(!strcmp(inputString, "id")){
      char line[25];
      sprintf(line, "CollisionDetectionTheo\r\n");
      Serial.print(line);
    }
    else if(!strcmp(inputString, "distances get")){
      char line[45], v0[12], v1[12], v2[12], v3[12], v4[12];
      dtostrf(measureTab[0], 4, 2, v0);
      dtostrf(measureTab[1], 4, 2, v1);
      dtostrf(measureTab[2], 4, 2, v2);
      dtostrf(measureTab[3], 4, 2, v3);
      dtostrf(measureTab[4], 4, 2, v4);
      sprintf(line, "distances %s;%s;%s;%s;%s\r\n", v0, v1, v2, v3, v4);
      Serial.print(line);
    }
    else {
      Serial.print("ERROR\r\n");
    }
    memset(inputString, '\0', INPUT_STR_SIZE);
    stringReady = false;
  }
  delay(15);
}
